import tempfile
import yte
import textwrap
import pytest
import yaml
import os.path
import uuid
import shutil
import subprocess as sp
from yte.context import Context
from yte.document import Document, Subdocument

from yte.exceptions import YteError


def _process(
    yaml_str,
    outfile=None,
    disable_features=None,
    require_use_yte=False,
    base_folder=None,
):
    return yte.process_yaml(
        textwrap.dedent(yaml_str),
        outfile=outfile,
        require_use_yte=require_use_yte,
        disable_features=disable_features,
        base_folder=base_folder,
    )


def _setup_temp_folder(file_contents: dict):
    folder_path = ""
    while True:
        folder_name = f"yte_test_{uuid.uuid4().hex}"
        folder_path = os.path.join(tempfile.gettempdir(), folder_name)
        if os.path.isdir(folder_path):
            continue
        os.mkdir(folder_path)
        break
    for key in file_contents:
        file_path = os.path.join(folder_path, key.replace("/", os.path.sep))
        file_folder = os.path.dirname(file_path)
        if not os.path.isdir(file_folder):
            os.mkdir(file_folder)
        f = open(file_path, "w")
        f.write(file_contents[key])
        f.close()
    return folder_path


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


def test_templates():
    result = _process(
        """
        __templates__:
          "foo(a, b, c=1)":
            ?a:
              - ?b
              - ?c
        bar:
            ?foo("x", "y", c=2)
        """
    )
    assert result == {"bar": {"x": ["y", 2]}}


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


def test_format():
    result = _process(
        """
__definitions__:
    - test = "foo"
test: !format |-
    {test} {test}{test}"""
    )
    assert result == {"test": "foo foofoo"}


def test_disable_format():
    with pytest.raises(YteError):
        _process(
            """
__definitions__:
    - test = "foo"
test: !format |-
    {test} {test}{test}""",
            disable_features=["format"],
        )


def test_inherit():
    test_folder = _setup_temp_folder(
        {
            "a.yaml": """
__variables__:
    foo: world
    bar: hello

greet:
    message1: ?bar + " " + bar + " " + foo
    number1: 1024
    message2: !f "{bar} {foo}"
    nested:
        not_useful_to_children: 256
    nested2:
        k: 94
        not_useful_to_children: 512
    nested_arr:
        - 1
        - 2
        - ?delete
""",
            "b.yaml": """
__inherit__: a.yaml

greet:
    message1: ?bar + " " + foo
    nested2:
        not_useful_to_children: ?delete
    nested:
        not_useful_to_children: ?delete
greet2: ?"hi " + foo
""",
        }
    )
    try:
        result = _process(
            """
__inherit__: b.yaml
""",
            base_folder=test_folder,
        )
        assert result == {
            "greet": {
                "message1": "hello world",
                "number1": 1024,
                "message2": "hello world",
                "nested": {},
                "nested2": {"k": 94},
                "nested_arr": [1, 2],
            },
            "greet2": "hi world",
        }
    finally:
        shutil.rmtree(test_folder)


def test_disable_inherit():
    with pytest.raises(YteError):
        _process(
            """
__inherit__: "a.yaml"
        """,
            disable_features=["inherit"],
        )


def test_include():
    test_folder = _setup_temp_folder(
        {
            "a.yaml": """
__variables__:
    foo: world
    bar: hello

greet: ?bar + " " + bar + " " + foo
""",
            "b.yaml": """
__inherit__: a.yaml

greet: ?bar + " " + foo
greet2: ?"hi " + foo
""",
            "folder1/c.yaml": """
__inherit__: !f ../{who_should_c_inherit}.yaml
greet3: ?this["greet2"] + ", nice 2 see u"
""",
        }
    )
    try:
        result = _process(
            """
__variables__:
    who_should_c_inherit: b
a: !include a.yaml
b:
    - !include ./b.yaml
c: !include folder1/c.yaml
""",
            base_folder=test_folder,
        )
        assert result == {
            "a": {"greet": "hello hello world"},
            "b": [{"greet": "hello world", "greet2": "hi world"}],
            "c": {
                "greet": "hello world",
                "greet2": "hi world",
                "greet3": "hi world, nice 2 see u",
            },
        }
    finally:
        shutil.rmtree(test_folder)


def test_disable_include():
    with pytest.raises(YteError):
        _process(
            """
test: !include "a.yaml"
        """,
            disable_features=["include"],
        )
