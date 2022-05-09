import tempfile
import yte
import textwrap
import pytest
import yaml
import subprocess as sp
from yte.context import Context
from yte.document import Document

from yte.exceptions import YteError


def _process(yaml_str, outfile=None, disable_features=None):
    return yte.process_yaml(
        textwrap.dedent(yaml_str),
        outfile=outfile,
        disable_features=disable_features,
    )


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
    with pytest.raises(YteError):
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
    with pytest.raises(YteError):
        _process(
            """
            ?elif True:
              foo: True
            """
        )


def test_unexpected_else():
    with pytest.raises(YteError):
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
    with pytest.raises(YteError):
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


def test_simple_error():
    with pytest.raises(YteError):
        _process(
            """
            ?unknown_var
            """
        )


def test_definitions_error():
    with pytest.raises(YteError):
        _process(
            """
            __definitions__:
              - blpasd sad
            """
        )


def test_conditional_error():
    with pytest.raises(YteError):
        _process(
            """
            ?if asdkn:
              "foo"
            """
        )


def test_variables():
    result = _process(
        """
        __variables__:
          foo: "x"
          bar: 3

        ?foo: 1
        bar: ?bar
        """
    )
    assert result == {"x": 1, "bar": 3}


def test_variables_error():
    with pytest.raises(YteError):
        _process(
            """
            __variables__:
              foo: ?some error
            """
        )


def test_disable_definitions():
    with pytest.raises(YteError):
        _process(
            """
            __definitions__:
              - foo = 1
            """,
            disable_features=["definitions"],
        )


def test_disable_variables():
    with pytest.raises(YteError):
        _process(
            """
            __variables__:
              foo: 1
            """,
            disable_features=["variables"],
        )


def test_invalid_variables():
    with pytest.raises(YteError):
        _process(
            """
            __variables__:
              - foo: 1
            """,
        )


def test_doc_object():
    result = _process(
        """
        foo: 1
        other:
          bar: ?doc["foo"]
        ?f"yetanother-{doc['foo']}": 2
        other-items: ?list(doc["other"].items())
        """
    )

    assert result == {
        "foo": 1,
        "other": {"bar": 1},
        "yetanother-1": 2,
        "other-items": [("bar", 1)],
    }


@pytest.fixture
def dummy_document():
    doc = Document()
    doc.inner.inner["foo"] = "bar"
    return doc


def test_doc_items(dummy_document):
    assert list(dummy_document.items()) == [("foo", "bar")]


def test_doc_keys(dummy_document):
    assert list(dummy_document.keys()) == ["foo"]


def test_doc_len(dummy_document):
    assert len(dummy_document) == 1


def test_doc_repr(dummy_document):
    assert repr(dummy_document) == "{'foo': 'bar'}"


def test_doc_insert():
    dummy_document = Document()
    context = Context()
    context.rendered += ["foo", "bar"]
    dummy_document._insert(context, 1)
    assert dummy_document == {"foo": {"bar": 1}}


def test_doc_eq(dummy_document):
    assert dummy_document == dummy_document
    assert dummy_document == {"foo": "bar"}
    assert dummy_document != 1
