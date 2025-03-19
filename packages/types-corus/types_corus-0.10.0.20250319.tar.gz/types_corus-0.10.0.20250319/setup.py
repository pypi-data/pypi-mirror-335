from setuptools import setup

name = "types-corus"
description = "Typing stubs for corus"
long_description = '''
## Typing stubs for corus

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`corus`](https://github.com/natasha/corus) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `corus`. This version of
`types-corus` aims to provide accurate annotations for
`corus==0.10.*`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/corus`](https://github.com/python/typeshed/tree/main/stubs/corus)
directory.

This package was tested with
mypy 1.15.0,
pyright 1.1.396,
and pytype 2024.10.11.
It was generated from typeshed commit
[`45e9a79e2644e5c561dc904f40f15c6659fe3234`](https://github.com/python/typeshed/commit/45e9a79e2644e5c561dc904f40f15c6659fe3234).
'''.lstrip()

setup(name=name,
      version="0.10.0.20250319",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/corus.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['corus-stubs'],
      package_data={'corus-stubs': ['__init__.pyi', 'io.pyi', 'path.pyi', 'readme.pyi', 'record.pyi', 'sources/__init__.pyi', 'sources/bsnlp.pyi', 'sources/buriy.pyi', 'sources/corpora.pyi', 'sources/factru.pyi', 'sources/gareev.pyi', 'sources/gramru.pyi', 'sources/lenta.pyi', 'sources/librusec.pyi', 'sources/meta.pyi', 'sources/mokoron.pyi', 'sources/morphoru.pyi', 'sources/ne5.pyi', 'sources/ods.pyi', 'sources/omnia.pyi', 'sources/persons.pyi', 'sources/ria.pyi', 'sources/rudrec.pyi', 'sources/russe.pyi', 'sources/simlex.pyi', 'sources/taiga/__init__.pyi', 'sources/taiga/arzamas.pyi', 'sources/taiga/common.pyi', 'sources/taiga/fontanka.pyi', 'sources/taiga/interfax.pyi', 'sources/taiga/kp.pyi', 'sources/taiga/lenta.pyi', 'sources/taiga/magazines.pyi', 'sources/taiga/nplus1.pyi', 'sources/taiga/proza.pyi', 'sources/taiga/social.pyi', 'sources/taiga/subtitles.pyi', 'sources/toloka.pyi', 'sources/ud.pyi', 'sources/wiki.pyi', 'sources/wikiner.pyi', 'third/WikiExtractor.pyi', 'third/__init__.pyi', 'zip.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0",
      python_requires=">=3.9",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
