import os
import sys

try:
    from Cython.Build import cythonize
except ImportError:
    def build(setup_kwargs):
        pass
else:
    from setuptools import Extension
    from setuptools.dist import Distribution
    from distutils.command.build_ext import build_ext

    def build(setup_kwargs):
        extensions = [
            Extension(
                name="isobiscuit_engine.engine",
                sources=["isobiscuit_engine/engine.pyx"],
                extra_compile_args=["-O3"],
                libraries=["m"],
            )
        ]
        os.environ['CFLAGS'] = '-O3'
        setup_kwargs.update({
            'ext_modules': cythonize(
                extensions,
                language_level=3,  # Python 3 Syntax
                compiler_directives={'linetrace': True},  # Optional: Fügt Line Tracing für Debugging hinzu
            ),
            'cmdclass': {'build_ext': build_ext}  # Verwendung von distutils' build_ext für den Build-Prozess
        })
