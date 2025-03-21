import re
from pathlib import Path
from setuptools import setup, find_packages

ROOT = Path(__file__).parent
README = ROOT.joinpath("README.md").read_text()
rgx = re.compile(r"""^\s*__version__\s*=\s*["'](\d+\.\d+\.\d+)["']\s*$""")


def get_version(module_init):
    module_path = ROOT.joinpath(module_init)
    with open(module_path) as f:
        for line in f.readlines():
            m = rgx.match(line)
            if m is not None:
                return m[1]
    raise Exception("Couldn't parse version")


setup(
    name="logutils_serpucga",
    version=get_version("logutils/__init__.py"),
    description="Tools to generate pretty logs quickly using default logging library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Serbaf/logging_utils",
    author="Sergio Puche García",
    author_email="spuche@upv.es",
    license="GPL3",
    packages=find_packages(),
)
