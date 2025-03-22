from pathlib import Path

from os.path import dirname, realpath, exists
from os import mkdir
import pandas as pd


WRITE_DATA = True


def full_path(file: str) -> Path:
    return Path(dirname(realpath(file)))


def expected(f):
    def wrapped(*args, **kwargs):
        out = f(*args, **kwargs)

        folder = full_path(f.__module__) / 'resources'
        if not exists(folder):
            mkdir(folder)

        filename = f"{f.__name__}.csv"
        filepath = folder / filename

        if WRITE_DATA:
            out.to_csv(filepath, index=False)

        expec = pd.read_csv(filepath)

        pd.testing.assert_frame_equal(out, expec)

    return wrapped