from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='lip_generation',
    version='0.4.3',
    packages=find_packages(),
    install_requires=[
        'pytest',
        'setuptools',
        'numpy',
        'opencv-python',
        'tqdm',
        'torch',
        'scipy',
        'librosa',
        ],
    include_package_data=True,
)