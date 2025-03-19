from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='lipsync_seisei',
    version='0.0.2',
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
    long_description=long_description,
    long_description_content_type='text/markdown',  # This ensures Markdown rendering on PyPI
)
