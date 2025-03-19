from setuptools import setup

name = "types-WebOb"
description = "Typing stubs for WebOb"
long_description = '''
## Typing stubs for WebOb

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`WebOb`](https://github.com/Pylons/webob) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `WebOb`. This version of
`types-WebOb` aims to provide accurate annotations for
`WebOb==1.8.*`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/WebOb`](https://github.com/python/typeshed/tree/main/stubs/WebOb)
directory.

This package was tested with
mypy 1.15.0,
pyright 1.1.396,
and pytype 2024.10.11.
It was generated from typeshed commit
[`45e9a79e2644e5c561dc904f40f15c6659fe3234`](https://github.com/python/typeshed/commit/45e9a79e2644e5c561dc904f40f15c6659fe3234).
'''.lstrip()

setup(name=name,
      version="1.8.0.20250319",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/WebOb.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['webob-stubs'],
      package_data={'webob-stubs': ['__init__.pyi', '_types.pyi', 'acceptparse.pyi', 'byterange.pyi', 'cachecontrol.pyi', 'client.pyi', 'compat.pyi', 'cookies.pyi', 'datetime_utils.pyi', 'dec.pyi', 'descriptors.pyi', 'etag.pyi', 'exc.pyi', 'headers.pyi', 'multidict.pyi', 'request.pyi', 'response.pyi', 'static.pyi', 'util.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0",
      python_requires=">=3.9",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
