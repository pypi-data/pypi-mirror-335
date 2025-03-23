import argparse

from importlib_resources import files

from timol.main import Timol
from timol.reader import MoleculesReader


def cli():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "file",
        help="Path to the file to be read (e.g. xyz file). Replace with `test` to try a testing xyz file",
    )
    parser.add_argument(
        "-i",
        "--index",
        help="Additional index argument to be assed to ase's read function, using ase's syntax. For example, use `-1` for the last frame or `:10` for the first 10. Only works for file formats where ase supports indexing",
        required=False,
        default=":",
    )

    args = parser.parse_args()

    path = args.file

    if path == "test":
        path = files("timol").joinpath("test_xyz.xyz")

    mr = MoleculesReader(path, index=args.index)
    app = Timol(mr)
    reply = app.run()
