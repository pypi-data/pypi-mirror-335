import asyncio
import aiofiles.os
import logging
import tempfile
import os
from datetime import datetime, timedelta
from subprocess import Popen
from time import sleep
from typing import Callable, Optional

from techrec.config_manager import get_config
from techrec.http_retriever import download

logger = logging.getLogger("forge")
Validator = Callable[[datetime, datetime, str], bool]

def round_timefile(exact: datetime) -> datetime:
    """
    This will round the datetime, so to match the file organization structure
    """
    return datetime(exact.year, exact.month, exact.day, exact.hour)


def get_files_and_intervals(start, end, rounder=round_timefile):
    """
    both arguments are datetime objects
    returns an iterator whose elements are (filename, start_cut, end_cut)
    Cuts are expressed in seconds
    """
    if end <= start:
        raise ValueError("end < start!")

    while start <= end:
        begin = rounder(start)
        start_cut = (start - begin).total_seconds()
        if end < begin + timedelta(seconds=3599):
            end_cut = (begin + timedelta(seconds=3599) - end).total_seconds()
        else:
            end_cut = 0
        yield (begin, start_cut, end_cut)
        start = begin + timedelta(hours=1)


class InputBackend:
    def __init__(self, basepath):
        self.base = basepath
        self.log = logging.getLogger(self.__class__.__name__)

    async def search_files(self, start, end):
        # assumption: a day is not split in multiple folder
        start_dir = self.parent_dir(self.time_to_uri(start))
        end_dir = self.parent_dir(self.time_to_uri(end))

        files = {
            fpath
            for directory in {start_dir, end_dir}
            for fpath in await self.list_dir(directory)
            }
        files_date = []  # tuple of str, datetime
        for fpath in files:
            try:
                dt = self.uri_to_time(fpath)
            except Exception as exc:
                self.log.debug("Skipping %s", fpath)
                print(exc)
                continue
            if dt > end:
                continue
            files_date.append((fpath, dt))

        # The first file in the list will now be the last chunk to be added.
        files_date.sort(key=lambda fpath_dt: fpath_dt[1], reverse=True)
        final_files = []
        need_to_exit = False
        for fpath, dt in files_date:
            if need_to_exit:
                break
            if dt < start:
                need_to_exit = True
            final_files.insert(0, fpath)
        self.log.info("Relevant files: %s", ", ".join(final_files))
        return final_files
            

    async def list_dir(self, path):
        raise NotImplementedError()

    def parent_dir(self, path):
        return os.path.dirname(path)

    def time_to_uri(self, time: datetime) -> str:
        return os.path.join(
            str(self.base),
            time.strftime(get_config()["AUDIO_INPUT_FORMAT"])
        )

    def uri_to_time(self, fpath: str) -> datetime:
        return datetime.strptime(
                os.path.basename(fpath),
                get_config()["AUDIO_INPUT_FORMAT"].split('/')[-1])

    async def get_file(self, uri: str) -> str:
        return uri

class DirBackend(InputBackend):

    def uri_to_relative(self, fpath: str) -> str:
        return os.path.relpath(fpath, str(self.base))

    async def list_dir(self, path):
        files = [os.path.join(path, f) for f in await aiofiles.os.listdir(path)]
        return files



class HttpBackend(InputBackend):
    async def get_file(self, uri: str) -> str:
        self.log.info(f"downloading: {uri}")
        local = await download(
            uri,
            basic_auth=get_config()['AUDIO_INPUT_BASICAUTH'],
        )
        return local



def get_ffmpeg_cmdline(fpaths: list, backend, start: datetime, end: datetime) -> list:
    ffmpeg = get_config()["FFMPEG_PATH"]
    cmdline = [ffmpeg, "-i", "concat:%s" % "|".join(fpaths)]
    cmdline += get_config()["FFMPEG_OUT_CODEC"]

    startskip = (start - backend.uri_to_time(fpaths[0])).total_seconds()
    if startskip > 0:
        cmdline += ["-ss", "%d" % startskip]
    cmdline += ["-t", "%d" % (end - start).total_seconds()]
    return cmdline


async def create_mp3(
    start: datetime,
    end: datetime,
    outfile: str,
    options={},
    validator: Optional[Validator] = None,
    **kwargs,
):

    be = DirBackend(get_config()['AUDIO_INPUT'])
    fpaths = await be.search_files(start, end)



    # metadata date/time formatted according to
    # https://wiki.xiph.org/VorbisComment#Date_and_time
    metadata = {}
    if outfile.endswith(".mp3"):
        metadata["TRDC"] = start.replace(microsecond=0).isoformat()
        metadata["RECORDINGTIME"] = metadata["TRDC"]
        metadata["ENCODINGTIME"] = datetime.now().replace(
            microsecond=0).isoformat()
    else:
        metadata["DATE"] = start.replace(microsecond=0).isoformat()
    metadata["ENCODER"] = "https://git.lattuga.net/techbloc/techrec"
    if "title" in options:
        metadata["TITLE"] = options["title"]
    if options.get("license_uri", None) is not None:
        metadata["RIGHTS-DATE"] = start.strftime("%Y-%m")
        metadata["RIGHTS-URI"] = options["license_uri"]
    if "extra_tags" in options:
        metadata.update(options["extra_tags"])
    metadata_list = []
    for tag, value in metadata.items():
        if "=" in tag:
            logger.error('Received a tag with "=" inside, skipping')
            continue
        metadata_list.append("-metadata")
        metadata_list.append("%s=%s" % (tag, value))

    prefix, suffix = os.path.basename(outfile).split(".", 1)
    tmp_file = tempfile.NamedTemporaryFile(
        suffix=".%s" % suffix,
        prefix="forge-%s" % prefix,
        delete=False,
        # This is needed to avoid errors with the rename across different mounts
        dir=os.path.dirname(outfile),
    )
    cmd = (
        get_ffmpeg_cmdline(fpaths, be, start, end)
        + metadata_list
        + ["-y"]
        + get_config()["FFMPEG_OPTIONS"]
        + [tmp_file.name]
    )
    logger.info("Running %s", " ".join(cmd))
    p = Popen(cmd)
    if get_config()["FORGE_TIMEOUT"] == 0:
        p.wait()
    else:
        start = datetime.now()
        while (datetime.now() - start).total_seconds() < get_config()["FORGE_TIMEOUT"]:
            p.poll()
            if p.returncode is None:
                sleep(1)
            else:
                break
    if p.returncode is None:
        os.kill(p.pid, 15)
        try:
            os.remove(tmp_file.name)
        except Exception:
            pass
        raise Exception("timeout")  # TODO: make a specific TimeoutError
    if p.returncode != 0:
        raise OSError("return code was %d" % p.returncode)
    if validator is not None and not validator(start, end, tmp_file.name):
        os.unlink(tmp_file.name)
        return False
    os.rename(tmp_file.name, outfile)
    return True


def main_cmd(options):
    log = logging.getLogger("forge_main")
    outfile = os.path.abspath(os.path.join(options.cwd, options.outfile))
    log.debug("will forge an mp3 into %s" % (outfile))
    asyncio.run(create_mp3(options.starttime, options.endtime, outfile))
