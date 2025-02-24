from typing import Any, Dict


class CodeHandler:
    def __init__(self, eval_func=eval, exec_func=exec):
        self._eval_func = eval_func
        self._exec_func = exec_func

    def eval(self, expr: str, variables: Dict[str, Any]) -> None:
        return self._eval_func(expr, variables)

    def exec(self, source: str, variables: Dict[str, Any]) -> None:
        return self._exec_func(source, variables)
