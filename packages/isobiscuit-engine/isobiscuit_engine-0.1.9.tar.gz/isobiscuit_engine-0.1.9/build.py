import os
from setuptools import setup, Extension
from Cython.Build import cythonize

def build(setup_kwargs):
    print('build.py')

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
            language_level=3,
            compiler_directives={'linetrace': True}
        ),
    })

