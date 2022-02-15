import re

re_for_loop = re.compile(r"^\?for .+ in .+$")
re_if = re.compile(r"^\?if (?P<expr>.+)$")
re_elif = re.compile(r"^\?elif (?P<expr>.+)$")
re_else = re.compile(r"^\?else$")


def _process_yaml_value(yaml_value, variables: dict):
    if isinstance(yaml_value, dict):
        return _process_dict(yaml_value, variables)
    elif isinstance(yaml_value, list):
        return [_process_yaml_value(item, variables) for item in yaml_value]
    elif _is_expr(yaml_value):
        return eval(yaml_value[1:], variables)
    else:
        return yaml_value


def _is_expr(yaml_value):
    return isinstance(yaml_value, str) and yaml_value.startswith("?")


def _process_dict(yaml_value, variables):
    items = list(_process_dict_items(yaml_value, variables))
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
        raise ValueError(
            "Conditional or for loop did not consistently return map or list."
        )


def _process_dict_items(yaml_value, variables):
    conditional = Conditional()

    for key, value in yaml_value.items():
        if re_for_loop.match(key):
            yield from conditional.process_conditional(variables)
            _variables = dict(variables)
            _variables["_yte_value"] = value
            _variables["_yte_variables"] = _variables
            yield from eval(
                f"[_process_yaml_value(_yte_value, dict(_yte_variables, **locals())) "
                f"{key[1:]}]",
                _variables,
            )
        elif re_if.match(key):
            yield from conditional.process_conditional(variables)
            expr = re_if.match(key).group("expr")
            conditional.register_if(expr, value)
        elif re_elif.match(key):
            if conditional.is_empty():
                raise ValueError("Unexpected elif: no if or elif before")
            expr = re_elif.match(key).group("expr")
            conditional.register_if(expr, value)
        elif re_else.match(key):
            if conditional.is_empty():
                raise ValueError("Unexpected else: no if or elif before")
            conditional.register_else(value)
            yield from conditional.process_conditional(variables)
        else:
            yield from conditional.process_conditional(variables)
            yield {
                _process_yaml_value(key, variables): _process_yaml_value(
                    value, variables
                )
            }
    yield from conditional.process_conditional(variables)


class Conditional:
    def __init__(self):
        self.exprs = []
        self.values = []

    def process_conditional(self, variables):
        if not self.is_empty():
            variables = dict(variables)
            variables.update(self.value_dict)
            variables["_yte_variables"] = variables
            result = eval(self.conditional_expr(), variables)
            if result is not None:
                yield result
            self.exprs.clear()
            self.values.clear()

    def conditional_expr(self, index=0):
        if index < len(self.exprs):
            return (
                f"_process_yaml_value({self.value_name(index)}, _yte_variables) "
                f"if {self.exprs[index]} else {self.conditional_expr(index + 1)}"
            )
        if index < len(self.values):
            return f"_process_yaml_value({self.value_name(index)}, _yte_variables)"
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
