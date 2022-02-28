# YTE - A YAML template engine with Python expressions

[![test coverage: 100%](https://img.shields.io/badge/test%20coverage-100%25-green)](https://github.com/koesterlab/yte/blob/main/pyproject.toml#L30)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/koesterlab/yte/CI)
![PyPI](https://img.shields.io/pypi/v/yte)
[![Conda Recipe](https://img.shields.io/badge/recipe-yte-green.svg)](https://anaconda.org/conda-forge/yte)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/yte.svg)](https://anaconda.org/conda-forge/yte)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/yte.svg)](https://github.com/conda-forge/yte-feedstock)


YTE is a template engine for YAML format that utilizes the YAML structure in combination with Python expressions for enabling to dynamically build YAML documents.

## Syntax

The key idea of YTE is to rely on the YAML structure to enable conditionals, loops and other arbitrary Python expressions to dynamically render YAML files.
Python expressions are thereby declared by prepending them with a `?` anywhere in the YAML.
Any such value will be automatically evaluated by YTE, yielding plain YAML as a result.
Importantly, YTE templates are still valid YAML files (for YAML, the `?` expressions are just strings).

### Examples

```yaml
?if True:
  foo: 1
?elif False:
  bar: 2
?else:
  bar: 1
```

```yaml
?for i in range(2):
  ?f"key{i}": 1
  ?if i == 1:
      foo: True
```

```yaml
?if True:
  - a
  - b
```

```yaml
- foo
- bar
- ?if True:
    baz
  ?else:
    bar
```

<table>
  <tr>
    <th>template</th>
    <th>rendered</th>
  </tr>
  <tr>
    <td>

      <pre lang="yaml">
# the special keyword __imports__ allows to define custom import statements
__imports__:
  - from itertools import product

?for item in product([1, 2], ["a", "b"]):
  - ?f"{item}"
      </pre>

    </td>
    <td>

```yaml
- 1-a
- 1-b
- 2-a
- 2-b
```

    </td>
  </tr>
</table>

## Usage

### Command line interface

YTE comes with a command line interface.
To render any YTE template, just issue

```bash
yte < the-template.yaml > the-rendered-version.yaml
```

### Python API

Alternatively, you can invoke YTE via its Python API:

```python
from yte import process_yaml

# set some variables as a Python dictionary
variables = ...

# render a string and obtain the result as a Python dict
result = process_yaml("""
?for i in range(10):
  - ?f"item-{i}"
""", variables=variables)

# render a file and obtain the result as a Python dict
with open("the-template.yaml", "r") as template:
    result = process_yaml(template, variables=variables)

# render a file and write the result as valid YAML
with open("the-template.yaml", "r") as template, open("the-rendered-version.yaml", "w") as outfile:
    result = process_yaml(template, outfile=outfile, variables=variables)
```

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
