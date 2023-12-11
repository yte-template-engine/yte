# YTE - A YAML template engine with Python expressions

[![Docs](https://img.shields.io/badge/user-documentation-green)](https://yte-template-engine.github.io)
[![test coverage: 100%](https://img.shields.io/badge/test%20coverage-100%25-green)](https://github.com/yte-template-engine/yte/blob/main/pyproject.toml#L30)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/yte-template-engine/yte/testing.yml?branch=main)
![PyPI](https://img.shields.io/pypi/v/yte)
[![Conda Recipe](https://img.shields.io/badge/recipe-yte-green.svg)](https://anaconda.org/conda-forge/yte)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/yte.svg)](https://anaconda.org/conda-forge/yte)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/yte.svg)](https://github.com/conda-forge/yte-feedstock)


YTE is a template engine for YAML format that utilizes the YAML structure in combination with Python expressions for enabling to dynamically build YAML documents.

The key idea of YTE is to rely on the YAML structure to enable conditionals, loops and other arbitrary Python expressions to dynamically render YAML files.
Python expressions are thereby declared by prepending them with a `?` anywhere in the YAML.
Any such value will be automatically evaluated by YTE, yielding plain YAML as a result.
Importantly, YTE templates are still valid YAML files (for YAML, the `?` expressions are just strings).

Documentation of YTE can be found at https://yte-template-engine.github.io.

## Comparison with other engines

Lots of template engines are available, for example the famous generic [jinja2](https://jinja.palletsprojects.com).
The reasons to generate a YAML specific engine are

1. The YAML syntax can be exploited to simplify template expression syntax, and make it feel less foreign (i.e. fewer special characters for control flow needed) while increasing human readability.
2. Whitespace handling (which is important with YAML since it has a semantic there) becomes unnecessary (e.g. with jinja2, some [tuning](https://radeksprta.eu/posts/control-whitespace-in-ansible-templates) is required to obtain proper YAML rendering).

Of course, YTE is not the first YAML specific template engine.
Others include

* [Yglu](https://yglu.io)
* [Emrichen](https://github.com/con2/emrichen)

The main difference between YTE and these two is that YTE extends YAML with plain Python syntax instead of introducing another specialized language.
Of course, the choice is also a matter of taste.
