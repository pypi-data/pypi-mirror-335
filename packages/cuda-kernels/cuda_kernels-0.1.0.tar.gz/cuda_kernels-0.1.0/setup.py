from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import os
import platform
import subprocess
import sys

class CUDAExtension(Extension):
    def __init__(self, name, sources, *args, **kwargs):
        super().__init__(name, sources, *args, **kwargs)
        self.sources = sources

class BuildExt(build_ext):
    def run(self):
        try:
            nvcc_version = subprocess.check_output(['nvcc', '--version']).decode('utf-8')
            print(f"Found NVCC: {nvcc_version.strip()}")
        except (subprocess.SubprocessError, FileNotFoundError):
            print("NVCC not found. Make sure CUDA Toolkit is installed and in PATH.")
            sys.exit(1)
        
        cuda_extensions = [ext for ext in self.extensions if isinstance(ext, CUDAExtension)]
        
        self.build_cuda_extensions(cuda_extensions)
        
        self.extensions = [ext for ext in self.extensions if not isinstance(ext, CUDAExtension)]
        
        super().run()
    
    def build_cuda_extensions(self, extensions):
        for ext in extensions:
            self.build_cuda_extension(ext)
    
    def build_cuda_extension(self, ext):
        sources = ext.sources
        if not sources:
            return
        
        output_dir = os.path.dirname(self.get_ext_fullpath(ext.name))
        os.makedirs(output_dir, exist_ok=True)
        
        nvcc_flags = ['-O3']
        if platform.system() == 'Windows':
            nvcc_flags.extend(['--compiler-options', '/MD', '-shared'])
            lib_ext = '.dll'
        elif platform.system() == 'Darwin': 
            nvcc_flags.extend(['--compiler-options', '-fPIC', '-shared', '-Xcompiler', '-stdlib=libc++'])
            lib_ext = '.dylib'
        else:  
            nvcc_flags.extend(['--compiler-options', '-fPIC', '-shared'])
            lib_ext = '.so'
        
        ext_path = self.get_ext_fullpath(ext.name)
        print(f"Target extension path: {ext_path}")
        
        for source in sources:
            if source.endswith('.cu'):
                output_file = ext_path
                
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                cmd = ['nvcc'] + nvcc_flags + ['-o', output_file, source]
                print(f"Compiling CUDA: {' '.join(cmd)}")
                
                try:
                    self.spawn(cmd)
                except Exception as e:
                    print(f"Error compiling {source}: {e}")
                    sys.exit(1)

packages = find_packages()
print(f"Discovered packages: {packages}")

if "cuda_kernels" in packages and "cuda_kernels.autocorrelation" not in packages:
    packages.append("cuda_kernels.autocorrelation")
if "cuda_kernels" in packages and "cuda_kernels.reduction" not in packages:
    packages.append("cuda_kernels.reduction")

setup(
    name="cuda_kernels",
    version="0.1.0",
    author="Sukhman Virk",
    author_email="sukhmanvirk26@gmail.com",
    description="CUDA accelerated correlation and sum reduction functions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AstuteFern/cuda-toolkit",
    packages=packages,
    include_package_data=True,
    ext_modules=[
        CUDAExtension(
            "cuda_kernels.autocorrelation.autocorrelation_cuda",
            ["cuda_kernels/autocorrelation/autocorrelation.cu"]
        ),
        CUDAExtension(
            "cuda_kernels.reduction.reduction_cuda",
            ["cuda_kernels/reduction/reduction.cu"]
        )
    ],
    package_data={
        "cuda_kernels.autocorrelation": ["*.cu"],
        "cuda_kernels.reduction": ["*.cu"],
    },
    cmdclass={'build_ext': BuildExt},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.16.0",
    ],
)