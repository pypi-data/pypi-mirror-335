import logging
import tomllib
import os
import errno
import sys
from typing import Any

# Everything else is internal API
__all__ = ['get_config']


def get_config() -> dict:
    this_function: Any = get_config
    if not hasattr(this_function, 'instance'):
        this_function.instance = load_config()
    return this_function.instance


def load_config() -> dict:
    conf = get_default_config()
    for fpath in os.environ.get('TECHREC_CONFIG', '').split(':'):
        logging.debug("Loading config from %s", fpath)
        if not fpath:
            continue
        with open(fpath, 'rb') as buf:
            extra = tomllib.load(buf)
        conf.update(extra)

    return conf


def get_default_config() -> dict:
    conf = BASE_CONFIG
    try:
        from pkg_resources import resource_filename, resource_isdir  # type: ignore

        if resource_isdir("techrec", "pages"):
            conf['STATIC_PAGES'] = resource_filename("techrec", "pages")
            conf['STATIC_FILES'] = resource_filename("techrec", "static")
    except ImportError:
        logging.exception("Error loading resources from installed part")
    return conf

BASE_CONFIG = dict(
        HOST="localhost",
        PORT="8000",

        DEBUG=True,
        DB_URI="sqlite:///techrec.db",
        AUDIO_OUTPUT="output/",
        AUDIO_INPUT="rec/",
        AUDIO_INPUT_BASICAUTH=None,  # Could be a ("user", "pass") tuple instead
        AUDIO_INPUT_FORMAT="%Y-%m/%d/rec-%Y-%m-%d-%H-%M-%S.mp3",
        AUDIO_OUTPUT_FORMAT="techrec-%(startdt)s-%(endtime)s-%(name)s.mp3",
        FORGE_TIMEOUT=20,
        FORGE_MAX_DURATION=3600 * 5,
        FORGE_VERIFY=False,
        FORGE_VERIFY_THRESHOLD=3,
        FFMPEG_OUT_CODEC=["-acodec", "copy"],
        FFMPEG_OPTIONS=["-loglevel", "warning"],
        FFMPEG_PATH="ffmpeg",
# tag:value pairs,
        TAG_EXTRA={},
# LICENSE URI is special because date need to be added,
        TAG_LICENSE_URI=None,

        STATIC_FILES="static/",
        STATIC_PAGES="pages/",

        )
