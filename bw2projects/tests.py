import atexit
import random
import shutil
import string

import wrapt

from . import config, projects


@wrapt.decorator
def bw2test(wrapped, instance, args, kwargs):
    config.dont_warn = True
    config.is_test = True
    config.cache = {}
    tempdir = projects._use_temp_directory()
    projects.set_current("".join(random.choices(string.ascii_lowercase, k=18)))
    atexit.register(shutil.rmtree, tempdir)
    return wrapped(*args, **kwargs)
