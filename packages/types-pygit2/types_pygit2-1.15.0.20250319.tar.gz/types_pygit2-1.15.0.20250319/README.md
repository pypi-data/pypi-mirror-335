## Typing stubs for pygit2

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`pygit2`](https://github.com/libgit2/pygit2) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `pygit2`. This version of
`types-pygit2` aims to provide accurate annotations for
`pygit2==1.15.*`.

*Note:* The `pygit2` package includes type annotations or type stubs
since version 1.16.0. Please uninstall the `types-pygit2`
package if you use this or a newer version.


This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/pygit2`](https://github.com/python/typeshed/tree/main/stubs/pygit2)
directory.

This package was tested with
mypy 1.15.0,
pyright 1.1.396,
and pytype 2024.10.11.
It was generated from typeshed commit
[`45e9a79e2644e5c561dc904f40f15c6659fe3234`](https://github.com/python/typeshed/commit/45e9a79e2644e5c561dc904f40f15c6659fe3234).