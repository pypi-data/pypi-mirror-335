import numpy as np
from setuptools import setup, Extension

ext_modules = [
    Extension(
        'natinterp3d.natinterp3d_cython',
        sources=[
            'src/natinterp3d/natinterp3d_cython.pyx', 'src/natinterp3d/natural.c',
            'src/natinterp3d/delaunay.c', 'src/natinterp3d/utils.c', 'src/natinterp3d/kdtree.c'],
        include_dirs=[np.get_include()],
        extra_compile_args=['-std=c11', '-O3', '-fopenmp', '-lpthread'],
        define_macros=[
            ('NPY_NO_DEPRECATED_API', None),
            ('NPY_1_7_API_VERSION', None),
            ('USE_LIST_NODE_ALLOCATOR', None)
        ],
        libraries=['m', 'pthread'],
        extra_link_args=['-fopenmp', '-lpthread']
    )
]
setup(ext_modules=ext_modules)
