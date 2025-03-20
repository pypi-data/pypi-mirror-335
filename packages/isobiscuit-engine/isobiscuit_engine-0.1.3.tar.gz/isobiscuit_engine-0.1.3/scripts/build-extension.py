from __future__ import annotations

import os
import shutil

from pathlib import Path

from Cython.Build import cythonize
from setuptools import Distribution
from setuptools import Extension
from setuptools.command.build_ext import build_ext


COMPILE_ARGS = ["-march=native", "-O3", "-msse", "-msse2", "-mfma", "-mfpmath=sse"]
LINK_ARGS = []
INCLUDE_DIRS = []
LIBRARIES = ["m"]


def build() -> None:
    extensions = [
        Extension(
            "*",
            ["isobiscuit_engine/*.pyx"],
            extra_compile_args=COMPILE_ARGS,
            extra_link_args=LINK_ARGS,
            include_dirs=INCLUDE_DIRS,
            libraries=LIBRARIES,
        )
    ]
    ext_modules = cythonize(
        extensions,
        include_path=INCLUDE_DIRS,
        compiler_directives={"binding": True, "language_level": 3},
    )

    distribution = Distribution({
        "name": "engine",
        "ext_modules": ext_modules
    })

    cmd = build_ext(distribution)
    cmd.ensure_finalized()
    cmd.run()
    destination_dir = Path("isobiscuit_engine")
    destination_dir.mkdir(parents=True, exist_ok=True)

    for output in cmd.get_outputs():
        output = Path(output)
        relative_extension = destination_dir / output.name

        shutil.copyfile(output, relative_extension)
        mode = os.stat(relative_extension).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(relative_extension, mode)



if __name__ == "__main__":
    build()