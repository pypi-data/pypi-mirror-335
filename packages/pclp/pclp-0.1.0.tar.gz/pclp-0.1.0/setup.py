from setuptools import setup, find_packages

setup(
    name="pclp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch>=1.10",
        "torchvision>=0.11",
        "numpy>=1.20",
        "scikit-learn>=1.0",
        "tensorboard>=2.8",
        "Pillow>=9.0",
        "randaugment>=0.1.1",
        "termcolor>=1.1.0 "
    ],
    entry_points={
        "console_scripts": [
            "pclp-train=pclp.cli:main",
        ],
    },
    author="Wang Anqi",
    author_email="1326621393@qq.com",
    description="PyTorch Causal Latent Programming for Multi-Label Learning",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/palm-biaoliu/pclp",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)