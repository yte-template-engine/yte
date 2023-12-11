import re
from yte.context import Context

from yte.exceptions import YteError

re_for_loop = re.compile(r"^\?for .+ in .+$")
re_if = re.compile(r"^\?if (?P<expr>.+)$")
re_elif = re.compile(r"^\?elif (?P<expr>.+)$")
re_else = re.compile(r"^\?else$")

FEATURES = frozenset(["variables", "definitions"])


def _process_yaml_value(
    yaml_value,
    variables: dict,
    context: Context,
    disable_features: frozenset,
):
    if isinstance(yaml_value, dict):
        return _process_dict(yaml_value, variables, Context(context), disable_features)
    elif isinstance(yaml_value, list):
        result = _process_list(yaml_value, variables, context, disable_features)
        return result
    elif _is_expr(yaml_value):
        result = _process_expr(yaml_value, variables, context)
        return result
    else:
        return yaml_value


def _is_expr(yaml_value):
    return isinstance(yaml_value, str) and yaml_value.startswith("?")


def _process_expr(yaml_value, variables, context: Context):
    try:
        return eval(yaml_value[1:], variables)
    except Exception as e:
        raise YteError(e, context)


def _process_list(
    yaml_value,
    variables,
    context: Context,
    disable_features: frozenset,
):
    variables["doc"]._insert(context, [])

    def _process():
        for i, item in enumerate(yaml_value):
            _context = Context(context)
            _context.rendered.append(i)
            value = _process_yaml_value(item, variables, _context, disable_features)
            if not isinstance(item, (dict, list)):
                variables["doc"]._insert(_context, value)
            yield value

    return list(_process())


def _process_dict(
    yaml_value,
    variables,
    context: Context,
    disable_features: frozenset,
):
    items = list(_process_dict_items(yaml_value, variables, context, disable_features))
    if all(isinstance(item, dict) for item in items):
        result = dict()
        for item in items:
            result.update(item)
        return result
    elif all(isinstance(item, list) for item in items):
        return [item for sublist in items for item in sublist]
    elif len(items) == 1:
        return items[0]
    else:
        raise YteError(
            "Conditional or for loop did not consistently return map or list. "
            f"Returned: {items}",
            context,
        )


def _process_dict_items(
    yaml_value,
    variables,
    context: Context,
    disable_features: frozenset,
):
    conditional = Conditional()

    for key, value in yaml_value.items():
        key_context = Context(context)
        key_context.template.append(key)
        if key == "__definitions__":
            if "definitions" in disable_features:
                raise YteError("__definitions__ have been disabled", key_context)
            _process_definitions(value, variables, key_context)
        elif key == "__variables__":
            if "variables" in disable_features:
                raise YteError("__variables__ have been disabled", key_context)
            _process_variables(value, variables, key_context)
        elif re_for_loop.match(key):
            yield from _process_for_loop(
                key, value, variables, conditional, key_context, disable_features
            )
        elif re_if.match(key):
            yield from _process_if(
                key, value, variables, conditional, key_context, disable_features
            )
        elif re_elif.match(key):
            _process_elif(key, value, variables, conditional, key_context)
        elif re_else.match(key):
            yield from _process_else(
                value, variables, conditional, key_context, disable_features
            )
        else:
            # a normal key that will end up in the result
            yield from conditional.process_conditional(
                variables, key_context, disable_features
            )
            key_result = _process_yaml_value(
                key, variables, key_context, disable_features
            )
            key_context.rendered.append(key_result)

            value_result = _process_yaml_value(
                value, variables, key_context, disable_features
            )
            variables["doc"]._insert(key_context, value_result)

            yield {key_result: value_result}
    yield from conditional.process_conditional(variables, key_context, disable_features)


def _process_definitions(value, variables, context: Context):
    if isinstance(value, list):
        for item in value:
            try:
                exec(item, variables)
            except Exception as e:
                raise YteError(e, context)
    else:
        raise YteError(
            "__definitions__ keyword expects a list of Python statements", context
        )


def _process_variables(value, variables, context: Context):
    if isinstance(value, dict):
        for name, val in value.items():
            if _is_expr(val):
                val = _process_expr(val, variables, context)
            variables[name] = val
    else:
        raise YteError(
            "__variables__ keyword expects a map of variable names and values", context
        )


def _process_for_loop(
    key, value, variables, conditional, context: Context, disable_features: frozenset
):
    yield from conditional.process_conditional(variables, context, disable_features)
    _variables = dict(variables)
    _variables["_yte_value"] = value
    _variables["_context"] = context
    _variables["_disable_features"] = disable_features
    _variables["_yte_variables"] = _variables
    yield from eval(
        f"[_process_yaml_value(_yte_value, dict(_yte_variables, **locals()), "
        "_context, _disable_features) "
        f"{key[1:]}]",
        _variables,
    )


def _process_if(
    key, value, variables, conditional, context: Context, disable_features: frozenset
):
    yield from conditional.process_conditional(variables, context, disable_features)
    expr = re_if.match(key).group("expr")
    conditional.register_if(expr, value)


def _process_elif(key, value, variables, conditional, context: Context):
    if conditional.is_empty():
        raise YteError("Unexpected elif: no if or elif before", context)
    expr = re_elif.match(key).group("expr")
    conditional.register_if(expr, value)


def _process_else(
    value, variables, conditional, context: Context, disable_features: frozenset
):
    if conditional.is_empty():
        raise YteError("Unexpected else: no if or elif before", context)
    conditional.register_else(value)
    yield from conditional.process_conditional(variables, context, disable_features)


class Conditional:
    def __init__(self):
        self.exprs = []
        self.values = []

    def process_conditional(
        self, variables, context: Context, disable_features: frozenset
    ):
        if not self.is_empty():
            variables = dict(variables)
            variables.update(self.value_dict)
            variables["_yte_variables"] = variables
            variables["_context"] = context
            variables["_disable_features"] = disable_features
            try:
                result = eval(self.conditional_expr(), variables)
            except Exception as e:
                raise YteError(e, context)
            if result is not None:
                yield result
            self.exprs.clear()
            self.values.clear()

    def conditional_expr(self, index=0):
        if index < len(self.exprs):
            return (
                f"_process_yaml_value({self.value_name(index)}, "
                "_yte_variables, _context, _disable_features) "
                f"if {self.exprs[index]} else {self.conditional_expr(index + 1)}"
            )
        if index < len(self.values):
            return (
                f"_process_yaml_value({self.value_name(index)}, "
                "_yte_variables, _context, _disable_features)"
            )
        else:
            return "None"

    def register_if(self, expr, value):
        self.exprs.append(expr)
        self.values.append(value)

    def register_else(self, value):
        self.values.append(value)

    def is_empty(self):
        return not self.exprs

    @property
    def value_dict(self):
        return {self.value_name(i): value for i, value in enumerate(self.values)}

    def value_name(self, index):
        return f"_yte_value_{index}"
