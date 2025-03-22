#!/usr/bin/env python3

import sys
import logging
import time
import os
import unicodedata
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
from subprocess import check_output

from fastapi import APIRouter, FastAPI, HTTPException, Request, Response, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.routing import Mount

from .cli import common_pre
from .config_manager import get_config
from .db import Rec, RecDB
from .forge import create_mp3, Validator

logger = logging.getLogger("server")

common_pre(nochecks=('pytest' in sys.argv[0]))
db: RecDB
router = APIRouter()


def date_read(s):
    return datetime.fromtimestamp(int(s))


def date_write(dt):
    return dt.strftime("%s")


def rec_sanitize(rec) -> dict:
    d = rec.serialize()
    d["starttime"] = date_write(d["starttime"])
    d["endtime"] = date_write(d["endtime"])
    return d


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    common_pre()
    if get_config()["DEBUG"]:
        logging.basicConfig(level=logging.DEBUG)
    db = RecDB(get_config()["DB_URI"])
    yield


@router.get("/date/date")
def date():
    n = datetime.now()
    return JSONResponse({"unix": n.strftime("%s"), "isoformat": n.isoformat(), "ctime": n.ctime()})


def TextResponse(text: str):
    return Response(content=text, media_type="text/plain")


def abort(code, text):
    raise HTTPException(status_code=code, detail=text)


@router.get("/date/custom")
def custom(strftime: str = ""):
    n = datetime.now()
    if not strftime:
        abort(400, 'Need argument "strftime"')
    return TextResponse(n.strftime(strftime))


@router.get("/date/help")
def help():
    return TextResponse(
        "/date : get JSON dict containing multiple formats of now()\n"
        + "/custom?strftime=FORMAT : get now().strftime(FORMAT)"
    )


class CreateInfo(BaseModel):
    starttime: Optional[int] = None
    endtime: Optional[int] = None
    name: str = ""


@router.post("/api/create")
async def create(req: CreateInfo | None = None):
    ret = {}
    logger.debug("Create request %s " % req)

    if req is None:
        req = CreateInfo()
    now = datetime.now()
    start = date_read(req.starttime) if req.starttime is not None else now
    name = req.name
    end = date_read(req.endtime) if req.endtime is not None else now

    rec = Rec(name=name, starttime=start, endtime=end)
    ret = db.add(rec)

    return rec_msg(
        f"ok", rec=rec_sanitize(rec)
    )


class DeleteInfo(BaseModel):
    id: int


@router.post("/api/delete")
def delete(req: DeleteInfo):
    if db.delete(req.id):
        return rec_msg("DELETE OK")
    else:
        return rec_err("DELETE error: %s" % (db.get_err()))


def timefield_factory():
    return int(time.time())


TimeField = Field(default_factory=timefield_factory)


class UpdateInfo(BaseModel):
    name: str = ""
    starttime: int = Field(default_factory=timefield_factory)
    endtime: int = Field(default_factory=timefield_factory)
    filename: Optional[str] = None


@router.post("/api/update/{recid}")
async def update(recid: int, req: UpdateInfo):
    global db

    session = db.get_session()
    rec = session.query(Rec).get(recid)
    rec.starttime = date_read(req.starttime)
    rec.endtime = date_read(req.endtime)
    if req.name:
        rec.name = req.name
    session.commit()
    return rec_msg("Aggiornamento completato!", rec=rec_sanitize(rec))


class GenerateInfo(BaseModel):
    id: int


class GenerateResponse(BaseModel):
    status: str
    message: str


@router.post("/api/generate/{recid}")
async def api_generate(recid: int, response: Response, background_tasks: BackgroundTasks):
    global db
    # prendiamo la rec in causa
    rec = db._search(_id=recid)[0]
    session = db.get_session(rec)
    session.refresh(rec)
    if rec.ready:
        return JSONResponse({
            "status": "ready",
            "message": "The file has already been generated at %s" % rec.filename,
            "rec": rec,
        })
    if (
        get_config()["FORGE_MAX_DURATION"] > 0
        and (rec.endtime - rec.starttime).total_seconds()
        > get_config()["FORGE_MAX_DURATION"]
    ):
        return JSONResponse(
            status_code=400,
	    content=dict(
		    status="error",
		    message="The requested recording is too long"
		    + " (%d seconds)" % (rec.endtime - rec.starttime).total_seconds()
		),
        )
    rec.filename = get_config()["AUDIO_OUTPUT_FORMAT"] % {
        "time": rec.starttime.strftime(
            "%y%m%d_%H%M"
        ),  # kept for retrocompatibility, should be dropped
        "endtime": rec.endtime.strftime("%H%M"),
        "startdt": rec.starttime.strftime("%y%m%d_%H%M"),
        "enddt": rec.endtime.strftime("%y%m%d_%H%M"),
        "name": "".join(
            filter(
                lambda c: c.isalpha(),
                unicodedata.normalize("NFKD", rec.name)
                .encode("ascii", "ignore")
                .decode("ascii"),
            )
        ),
    }
    db.get_session(rec).commit()
    background_tasks.add_task(
        generate_mp3,
        db_id=recid,
        start=rec.starttime,
        end=rec.endtime,
        outfile=os.path.join(get_config()["AUDIO_OUTPUT"], rec.filename),
        options={
            "title": rec.name,
            "license_uri": get_config()["TAG_LICENSE_URI"],
            "extra_tags": get_config()["TAG_EXTRA"],
        },
    )
    logger.debug("SUBMITTED: %d" % recid)
    return rec_msg(
        "Aggiornamento completato!",
        job_id=rec.id,
        result="/output/" + rec.filename,
        rec=rec_sanitize(rec),
    )


def get_duration(fname) -> float:
    lineout = check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-i",
            fname,
        ]
    ).split(b"\n")
    duration = next(l for l in lineout if l.startswith(b"duration="))
    value = duration.split(b"=")[1]
    return float(value)


def get_validator(expected_duration_s: float, error_threshold_s: float) -> Validator:
    def validator(start, end, fpath):
        try:
            duration = get_duration(fpath)
        except Exception as exc:
            logger.exception("Error determining duration of %s", fpath)
            return False
        logger.debug(
            "expect %s to be %.1f±%.1fs, is %.1f",
            fpath,
            expected_duration_s,
            error_threshold_s,
            duration,
        )
        if duration > expected_duration_s + error_threshold_s:
            return False
        if duration < expected_duration_s - error_threshold_s:
            return False
        return True

    return validator


async def generate_mp3(db_id: int, **kwargs):
    """creates and mark it as ready in the db"""
    if get_config()["FORGE_VERIFY"]:
        validator = get_validator(
            (kwargs["end"] - kwargs["start"]).total_seconds(),
            get_config()["FORGE_VERIFY_THRESHOLD"],
        )
        retries = 10
    else:
        validator = None
        retries = 1

    for i in range(retries):
        try:
            result = await create_mp3(validator=validator, **kwargs)
        except Exception as exc:
            logger.error("Error creating audio for %d -> %s", db_id, str(exc))
            rec = db._search(_id=db_id)[0]
            rec.error = str(exc)
            db.get_session(rec).commit()
            return False
        logger.debug("Create mp3 for %d -> %s", db_id, result)
        if result:
            break
        elif i < retries - 1:
            logger.debug("waiting %d", i + 1)
            time.sleep(i + 1)  # waiting time increases at each retry
    else:
        logger.warning("Could not create mp3 for %d: validation failed", db_id)
        return False

    rec = db._search(_id=db_id)[0]
    rec.ready = True
    db.get_session(rec).commit()
    return True


@router.get("/api/ready/{recid}")
def check_job(recid: int):
    rec = db._search(_id=recid)[0]

    out = {"job_id": recid, "job_status": rec.status}

    return out


@router.get("/api/get/ongoing")
def get_ongoing():
    return {rec.id: rec_sanitize(rec) for rec in db.get_ongoing()}


@router.get("/api/get/archive")
def get_archive():
    return {rec.id: rec_sanitize(rec) for rec in db.get_archive_recent()}


@router.get("/api/help")
@router.get("/api")
def api_help():
    return Response(
        media_type="text/html",
        content="""
<h1>help</h1><hr/>
<h2>/get, /get/, /get/{id} </h2>
<h3>Get Info about rec identified by ID </h3>

<h2>/search, /search/, /search/{key}/{value}</h2>
<h3>Search rec that match key/value (or get all)</h3>

<h2>/delete/{id} </h2>
<h3>Delete rec identified by ID </h3>
<h2>/update/{id} </h2>
<h3>Not implemented.</h3>
        """,
    )


# JSON UTILS


def rec_msg(msg, status_code=200, status=True, **kwargs) -> JSONResponse:
    d = {"message": msg, "status": status}
    d.update(kwargs)
    return JSONResponse(d, status_code=status_code)


def rec_err(msg, **kwargs) -> JSONResponse:
    return rec_msg(msg,
            status=False,
            status_code=500,
            **kwargs)




@router.get("/")
def home():
    return RedirectResponse("/new.html")


@router.route("/new.html")
@router.route("/old.html")
@router.route("/archive.html")
def serve_pages(request: Request):
    page = request.url.path[1:]
    fpath = os.path.join(get_config()["STATIC_PAGES"], page)
    return FileResponse(fpath)


def main_cmd(options):
    import uvicorn

    uvicorn.run(app, host=get_config()["HOST"], port=int(get_config()["PORT"]))


app = FastAPI(lifespan=lifespan)
app.mount("/output", StaticFiles(directory=get_config()["AUDIO_OUTPUT"]))
app.mount("/static", StaticFiles(directory=get_config()["STATIC_FILES"]))
app.include_router(router)

if __name__ == "__main__":
    logger.warn("Usage of server.py is not supported anymore; use cli.py")
    import sys

    sys.exit(1)

# vim: set ts=4 sw=4 et ai ft=python:
