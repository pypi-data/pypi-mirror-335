from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

CUDA_FLAGS = []

# define cuda extensions
ext_modules = [
    CUDAExtension(
        'euler_update', [
            'euler_update_Interface.cpp',
            'euler_update_Kernel.cu',
        ],
    ),
    
]

# INSTALL_REQUIREMENTS = ['numpy', 'torch', 'torchvision', 'scikit-image', 'tqdm', 'imageio']
setup(
    # extra_compile_args={
    #     'cxx': ['-std=c++11', '-O2', '-Wall'],
    #     'nvcc': [
    #         '-std=c++11', '--expt-extended-lambda', '--use_fast_math',
    #         '-Xcompiler', '-Wall', '-gencode=arch=compute_60,code=sm_60',
    #         '-gencode=arch=compute_61,code=sm_61',
    #         '-gencode=arch=compute_70,code=sm_70',
    #         '-gencode=arch=compute_72,code=sm_72',
    #         '-gencode=arch=compute_75,code=sm_75',
    #         '-gencode=arch=compute_75,code=compute_75'
    #     ],
    # },

    extra_compile_args = {
            'cxx': ['/EHsc'],  # MSVC 兼容选项
            'nvcc': [
                '-O2',
                '-gencode=arch=compute_60,code=sm_60',
                '-gencode=arch=compute_70,code=sm_70',
                '-gencode=arch=compute_75,code=sm_75',
                '-gencode=arch=compute_80,code=sm_80',
                '-gencode=arch=compute_86,code=compute_86',
                '--expt-extended-lambda'
                ]
            },
    
    ext_modules=ext_modules,
    cmdclass={
        'build_ext': BuildExtension.with_options(no_python_abi_suffix=True)
    })
