# protein_search

[![build](https://github.com/fissoreg/protein_search/actions/workflows/build.yml/badge.svg)](https://github.com/fissoreg/protein_search/actions/workflows/build.yml)

Neural search through protein sequences using the ProtBert model and the Jina AI framework.

- ProtBert https://huggingface.co/Rostlab/prot_bert
- Jina AI https://jina.ai

## Setting up the environment

Making a new `venv` virtual environment

```
$ cd *path_to*/protein_search
$ python -m venv env
$ source venv/bin/activate
```

Installing dependencies

```
$ pip install -r requirements.txt
```

or using `make`

```
$ make deps
```

## Formatting, linting and testing

_Refer to the `Makefile` for the specific commands_

To format code following the [`black`](https://github.com/psf/black) standard
```
$ make format
```

Code linting with [`flake8`](https://github.com/PyCQA/flake8)
```
$ make lint
```

Testing
```
$ make test
```

Testing with coverage analysis
```
$ make coverage
```

Format, test and coverage
```
$ make build
```