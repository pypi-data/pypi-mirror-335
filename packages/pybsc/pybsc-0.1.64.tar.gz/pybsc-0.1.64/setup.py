
import os

from setuptools import find_packages
from setuptools import setup

version = '0.1.64'
setup_requires = []

with open('requirements.txt') as f:
    install_requires = []
    for line in f:
        req = line.split('#')[0].strip()
        install_requires.append(req)

image_install_requires = []
with open('requirements_image.txt') as f:
    image_install_requires = []
    for line in f:
        req = line.split('#')[0].strip()
        image_install_requires.append(req)

video_install_requires = []
with open('requirements_video.txt') as f:
    video_install_requires = []
    for line in f:
        req = line.split('#')[0].strip()
        video_install_requires.append(req)

tts_install_requires = []
with open('requirements_tts.txt') as f:
    tts_install_requires = []
    for line in f:
        req = line.split('#')[0].strip()
        tts_install_requires.append(req)


def listup_package_data():
    data_files = []
    for root, _, files in os.walk('pybsc/data'):
        for filename in files:
            data_files.append(
                os.path.join(
                    root[len('pybsc/'):],
                    filename))
    return data_files


setup(
    name="pybsc",
    version=version,
    description="A little useful library (like a Backscratcher).",
    author="iory",
    author_email="ab.ioryz@gmail.com",
    url="https://github.com/iory/pybsc",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=find_packages(),
    package_data={'pybsc': listup_package_data()},
    zip_safe=False,
    setup_requires=setup_requires,
    install_requires=install_requires,
    extras_require={
        'image': image_install_requires,
        'video': video_install_requires,
        'tts': tts_install_requires,
        'all': (image_install_requires
                + video_install_requires
                + tts_install_requires),
    },
    entry_points={
        "console_scripts": [
            "readable-json=pybsc.apps.readable_json:main",
        ]
    },
)
