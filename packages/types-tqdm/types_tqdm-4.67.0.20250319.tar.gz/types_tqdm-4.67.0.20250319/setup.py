from setuptools import setup

name = "types-tqdm"
description = "Typing stubs for tqdm"
long_description = '''
## Typing stubs for tqdm

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`tqdm`](https://github.com/tqdm/tqdm) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `tqdm`. This version of
`types-tqdm` aims to provide accurate annotations for
`tqdm==4.67.*`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/tqdm`](https://github.com/python/typeshed/tree/main/stubs/tqdm)
directory.

This package was tested with
mypy 1.15.0,
pyright 1.1.396,
and pytype 2024.10.11.
It was generated from typeshed commit
[`45e9a79e2644e5c561dc904f40f15c6659fe3234`](https://github.com/python/typeshed/commit/45e9a79e2644e5c561dc904f40f15c6659fe3234).
'''.lstrip()

setup(name=name,
      version="4.67.0.20250319",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/tqdm.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-requests'],
      packages=['tqdm-stubs'],
      package_data={'tqdm-stubs': ['__init__.pyi', '_dist_ver.pyi', '_main.pyi', '_monitor.pyi', '_tqdm.pyi', '_tqdm_gui.pyi', '_tqdm_notebook.pyi', '_tqdm_pandas.pyi', '_utils.pyi', 'asyncio.pyi', 'auto.pyi', 'autonotebook.pyi', 'cli.pyi', 'contrib/__init__.pyi', 'contrib/bells.pyi', 'contrib/concurrent.pyi', 'contrib/discord.pyi', 'contrib/itertools.pyi', 'contrib/logging.pyi', 'contrib/slack.pyi', 'contrib/telegram.pyi', 'contrib/utils_worker.pyi', 'dask.pyi', 'gui.pyi', 'keras.pyi', 'notebook.pyi', 'rich.pyi', 'std.pyi', 'tk.pyi', 'utils.pyi', 'version.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0",
      python_requires=">=3.9",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
