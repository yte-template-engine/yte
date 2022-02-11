import yte
import textwrap


def _process(yaml_str):
    return yte.process_yaml(textwrap.dedent(yaml_str))


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
