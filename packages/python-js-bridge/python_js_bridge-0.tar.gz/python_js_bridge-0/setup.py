import setuptools

import pyjs_bridge

setuptools.setup(
    name = "python_js_bridge",
    version = f"{pyjs_bridge.__version__}",
    description = "A bridge between Python and JavaScript",
    long_description = open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type = "text/markdown",
    author = "qaqFei",
    author_email = "qaq_fei@163.com",
    url = "https://github.com/qaqFei/pyjs_bridge",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows"
    ],
    install_requires = [],
    license = "MIT License",
    python_requires = ">=3.12.0"
)
