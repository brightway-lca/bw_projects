import hashlib
import re
import os
import unicodedata

from typing import Union
from pathlib import Path


re_slugify = re.compile(r"[^\w\s-]", re.UNICODE)
SUBSTITUTION_RE = re.compile(r"[^\w\-\.]")
MULTI_RE = re.compile(r"_{2,}")


def safe_filename(string: Union[str, bytes], add_hash: bool = True) -> str:
    """Convert arbitrary strings to make them safe for filenames. Substitutes strange
    characters, and uses unicode normalization.
    if `add_hash`, appends hash of `string` to avoid name collisions.
    From http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python"""
    safe = re.sub(
        r"[-\s]+",
        "-",
        str(re_slugify.sub("", unicodedata.normalize("NFKD", str(string))).strip()),
    )
    if add_hash:
        if isinstance(string, str):
            string = string.encode("utf8")
        safe += "." + hashlib.md5(string).hexdigest()[:8]
    return safe


def create_dir(dirpath: str) -> None:
    "Create directory tree to `dirpath`; ignore if already exists"
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)


def check_dir(directory: str) -> bool:
    """Returns ``True`` if given path is a directory and writeable,
    ``False`` otherwise."""
    return os.path.isdir(directory) and os.access(directory, os.W_OK)


def maybe_path(x: str) -> Path:
    return Path(x) if x else x
