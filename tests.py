import tempfile
import yte
import textwrap
import pytest
import yaml
import subprocess as sp


def _process(yaml_str, outfile=None):
    return yte.process_yaml(textwrap.dedent(yaml_str), outfile=outfile)


def test_ifelse():
    result = _process(
        """
    ?if True:
      foo: 1
    ?elif False:
      bar: 2
    ?else:
      bar: 1
    """
    )
    assert result == {"foo": 1}


def test_for():
    result = _process(
        """
    ?for i in range(2):
        ?f"key{i}": 1
        ?if i == 1:
            foo: True
    """
    )
    assert result == {"key0": 1, "key1": 1, "foo": True}


def test_list():
    result = _process(
        """
        - foo
        - bar
        - ?if True:
            baz
          ?else:
            bar
        """
    )
    assert result == ["foo", "bar", "baz"]


def test_if_list():
    result = _process(
        """
        ?if True:
          - a
          - b
        """
    )
    assert result == ["a", "b"]


def test_fail_mixed_loop_return():
    with pytest.raises(ValueError):
        _process(
            """
            ?for i in range(2):
              ?if i == 0:
                - foo
              ?else:
                bar: True
            """
        )


def test_unexpected_elif():
    with pytest.raises(ValueError):
        _process(
            """
            ?elif True:
              foo: True
            """
        )


def test_unexpected_else():
    with pytest.raises(ValueError):
        _process(
            """
            ?else:
              foo: True
            """
        )


def test_custom_import():
    result = _process(
        """
        __definitions__:
          - from itertools import product
        ?for a in product([1, 2], [3]):
          - a
        """
    )
    assert result == ["a"] * 2


def test_variable_definition1():
    result = _process(
        """
        __definitions__:
          - test = "foo"

        ?test:
          1
        """
    )
    assert result == {"foo": 1}


def test_variable_definition2():
    result = _process(
        """
        __definitions__:
          - foo = "bar"
          - test = "foo"

        ?f"{test}":
          1
        """
    )
    assert result == {"foo": 1}


def test_variable_definition3():
    result = _process(
        """
        __definitions__:
          - test = "foo"

        bar: ?test

        ?for item in ["foo", "baz"]:
            __definitions__:
              - and_now = "for something completely different"
            ?item: ?and_now
        """
    )
    assert result == {
        "bar": "foo",
        "foo": "for something completely different",
        "baz": "for something completely different",
    }


def test_custom_import_syntax_error():
    with pytest.raises(ValueError):
        _process(
            """
          __definitions__:
            from itertools import product
          """
        )


def test_variable_definition():
    result = _process(
        """
        __definitions__:
          - foo = 1
        ?for a in range(2):
          - ?foo
        """
    )
    assert result == [1] * 2


def test_func_definition():
    result = _process(
        """
        __definitions__:
          - |
            def foo():
                return 1
        ?for a in range(2):
          - ?foo()
        """
    )
    assert result == [1] * 2


def test_cli():
    sp.check_call("echo -e '?if True:\n  foo: 1' | yte", shell=True)


def test_colon():
    result = _process(
        """
        ?for sample in ["normal", "tumor"]:
          '?f"{sample}: observations"': 1
        """
    )
    assert result == {"normal: observations": 1, "tumor: observations": 1}


def test_colon_unquoted():
    with pytest.raises(yaml.scanner.ScannerError):
        _process(
            """
            ?for sample in ["normal", "tumor"]:
              ?f"{sample}: observations": 1
            """
        )


def test_outfile():
    with tempfile.NamedTemporaryFile(mode="w") as tmp:
        _process(
            """
            foo
            """,
            outfile=tmp,
        )
