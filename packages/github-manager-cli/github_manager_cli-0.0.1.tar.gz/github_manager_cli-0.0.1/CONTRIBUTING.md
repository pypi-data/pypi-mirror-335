# Contributing

## Issues

A good issue includes a [short, self contained, correct example](http://sscce.org/) of the problem, something like:

```
gm -v
gm: error: the following arguments are required: action, --config
```

**Warning:** you may want to remove some private information (authentication information is removed, but there may be private stuff in the messages)

## Pull Requests

Pull Requests should clearly describe two things:

1. The problem they attempt to solve
2. How the author went about solving the problem

Ideally, changes should be made in logical commits and tests added to improve the project's coverage of the GitHub Manager.

## Coding style

Githum-Manager adopts the black coding style.

To manually format the code:
```bash
tox -e lint
```

## Pre-commit plugin

To forget about coding style and let [pre-commit](https://pre-commit.com/#installation) fix your flake8/isort/black issue.

```
pre-commit install
```

That's it!

## Deprecation warning

Before removing attributes/methods, consider adding deprecation warnings instead. The [typing_extensions](https://pypi.org/project/typing-extensions/) package provides a handy decorator to add deprecation warnings.

```python
from typing_extensions import deprecated

@property
@deprecated("Use core instead")
def rate(self):
   pass

@deprecated("Deprecated in favor of the new branch protection")
def get_protected_branch(self):
   pass
```

## Automated tests

First you need to install the test dependencies:
```bash
pip install -r requirements/test.txt
```

Then you can run the tests through `pytest`.
Run a specific test with `pytest tests/tests_filename.py` or `pytest tests/`.

If you add a new test, for example `Issue139.testCompletion`, you have to run `pytest -k Issue139.testCompletion --record` to create the `tests/ReplayData/*.txt` files needed for your new test.

## Build documentation locally

```bash
pip install -r requirements/docs.txt
sphinx-build doc build
```

If you use tox:

```bash
tox -edocs
```
