import asyncio
import tempfile
import yte
import textwrap
import pytest
import yaml
import subprocess as sp
from yte.context import Context
from yte.document import Document, Subdocument

from yte.exceptions import YteError


def _process(yaml_str, outfile=None, disable_features=None, require_use_yte=False):
    return yte.process_yaml(
        textwrap.dedent(yaml_str),
        outfile=outfile,
        require_use_yte=require_use_yte,
        disable_features=disable_features,
        variables={
            "async_function": adouble,
            "async_condition": acond,
            "arange": arange,
        },
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


def test_disable_invalid_feature():
    with pytest.raises(ValueError):
        _process(
            """
            __variables__:
              foo: 1
            """,
            disable_features=["bar"],
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
          some: 2
          bar: ?this["foo"] + this["other"]["some"]
        ?f"yetanother-{this['foo']}": 2
        other-items: ?sorted(this["other"].items())
        """
    )

    assert result == {
        "foo": 1,
        "other": {"some": 2, "bar": 3},
        "yetanother-1": 2,
        "other-items": [("bar", 3), ("some", 2)],
    }


@pytest.fixture
def dummy_document():
    doc = Document()
    doc.inner.inner["foo"] = "bar"
    return doc


@pytest.fixture
def dummy_document_complex():
    doc = Document()
    doc.inner.inner["foo"] = Subdocument()
    doc.inner.inner["foo"].inner = {"bar": 1}
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


def test_doc_dpath_get(dummy_document_complex):
    assert dummy_document_complex.dpath_get("foo/bar") == 1


def test_doc_dpath_search(dummy_document_complex):
    assert dummy_document_complex.dpath_search("foo/bar") == {"foo": {"bar": 1}}


def test_doc_dpath_fallback(dummy_document_complex):
    assert dummy_document_complex["foo/bar"] == 1


def test_doc_dpath_fallback_key_error(dummy_document_complex):
    with pytest.raises(KeyError):
        dummy_document_complex["some"]


def test_require_use_yte():
    result = _process(
        """
    __use_yte__: true
    ?if True:
        foo: 1
    ?else:
        bar: 1
    """,
        require_use_yte=True,
    )
    assert result == {"foo": 1}


def test_require_use_yte_not_found():
    result = _process(
        """
    ?if True:
        foo: 1
    """,
        require_use_yte=True,
    )
    assert result == {"?if True": {"foo": 1}}


def test_require_use_yte_false():
    result = _process(
        """
    __use_yte__: false
    ?if True:
        foo: 1
    """,
        require_use_yte=True,
    )
    assert result == {"?if True": {"foo": 1}}


def test_complex_1():
    _process(
        """
    __use_yte__: true
    html:
        head:
            title: Test landing page
        body:
            div:
                class: foo
                content:
                    - p: Hello, this is some text. How do we get a tag into it? We could avoid tags and just render this as markdown.
                    - p:
                        class: bar
                        content:
                            - This is untagged text
                            - span:
                                content: This is a span
                                class: bold
                            - This is more untagged text
                    - ?if True:
                        markdown: |
                            # This is a markdown heading
                            This is some markdown text
                      ?else:
                        markdown: |
                            # This is a different markdown heading
                            This is some different markdown text
    """  # noqa: B950
    )


async def adouble(num: int):
    return num * 2


async def acond(cond: bool):
    return cond


async def arange(*args, **kwargs):
    for i in range(*args, **kwargs):
        yield i


def test_simple_async_expression():
    result = _process(
        """
        value: ?await async_function(2)
        """,
    )
    assert result == {"value": 4}


def test_async_expression_in_list():
    result = _process(
        """
        values:
          - ?await async_function(1)
          - ?await async_function(2)
          - ?await async_function(3)
        """,
    )
    assert result == {"values": [2, 4, 6]}


def test_async_for_loop():
    result = _process(
        """
        ?async for i in arange(3):
          - ?await async_function(i)
        """,
    )
    assert result == [0, 2, 4]


def test_async_if_condition_true():
    result = _process(
        """
        ?if await async_condition(True):
          result: "Condition was true"
        ?else:
          result: "Condition was false"
        """,
    )
    assert result == {"result": "Condition was true"}


def test_async_if_condition_false():
    result = _process(
        """
        ?if await async_condition(False):
          result: "Condition was true"
        ?else:
          result: "Condition was false"
        """,
    )
    assert result == {"result": "Condition was false"}


def test_nested_async_expressions():
    result = _process(
        """
        nested:
          level1:
            level2: ?await async_function(5)
        """,
    )
    assert result == {"nested": {"level1": {"level2": 10}}}


def test_async_expression_with_variables():
    result = _process(
        """
        __variables__:
          base: 5
        result: ?await async_function(base)
        """,
    )
    assert result == {"result": 10}


def test_async_expression_exception():
    with pytest.raises(Exception):
        _process(
            """
            result: ?await invalid
            """,
        )
