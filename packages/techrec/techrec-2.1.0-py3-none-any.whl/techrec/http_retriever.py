# -*- encoding: utf-8 -*-
import os
from typing import Optional, Tuple
from tempfile import mkdtemp
from logging import getLogger

import aiohttp  # type: ignore

CHUNK_SIZE = 2 ** 12

log = getLogger("http")


async def download(
    remote: str,
    staging: Optional[str] = None,
    basic_auth: Optional[Tuple[str, str]] = None,
) -> str:
    """
    This will download to AUDIO_STAGING the remote file and return the local
    path of the downloaded file
    """
    _, filename = os.path.split(remote)
    if staging:
        base = staging
    else:
        # if no staging is specified, and you want to clean the storage
        # used by techrec: rm -rf /tmp/techrec*
        base = mkdtemp(prefix="techrec-", dir="/tmp")
    local = os.path.join(base, filename)

    auth = None
    if basic_auth is not None:
       auth = aiohttp.BasicAuth(
            login=basic_auth[0], password=basic_auth[1], encoding="utf-8"
        )

    log.debug("Downloading %s with auth=%s", remote, auth)
    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.get(remote) as resp:
            if resp.status != 200:
                raise ValueError(
                    "Could not download %s: error %d" % (remote, resp.status)
                )
            with open(local, "wb") as f:
                while True:
                    chunk = await resp.content.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
    log.debug("Downloading %s complete", remote)
    return local
