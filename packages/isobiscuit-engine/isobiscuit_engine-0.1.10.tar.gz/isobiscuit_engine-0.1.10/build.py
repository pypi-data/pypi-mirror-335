import os
import shutil
from setuptools import setup, Extension
from Cython.Build import cythonize
from setuptools import setup




def build(setup_kwargs):

    extensions = [
        Extension(
            name="isobiscuit_engine.engine",
            sources=["isobiscuit_engine/engine.pyx"],
            extra_compile_args=["-O3"],
            libraries=["m"]
        )
    ]
    
    os.environ['CFLAGS'] = '-O3'

    setup_kwargs.update({
        'ext_modules': cythonize(
            extensions,
            language_level=3,
            compiler_directives={'linetrace': True},
        ),
    })

    
    setup(**setup_kwargs)

    dist_dir = os.path.join(os.getcwd(), 'build')
    if os.path.exists(dist_dir):
        for folder in os.listdir(dist_dir):
            if folder.startswith('lib.'):
                for filename in os.listdir(os.path.join(dist_dir, folder, 'isobiscuit_engine')):
                    if filename.endswith(('.so', '.pyd', '.dylib')):
                        old_path = os.path.join(dist_dir, folder, 'isobiscuit_engine', filename)
                        
                        new_path = os.path.join(dist_dir, folder, 'isobiscuit_engine', 'engine' + os.path.splitext(filename)[1])
                        shutil.move(old_path, new_path)
    exit()


