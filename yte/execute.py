import asyncio
from aioconsole import aexec


async def aeval(input_string: str, local_namespace: dict):
    """
    Asynchronously evaluate a Python expression or statement within a given local namespace.

    This function allows you to execute a string of Python code asynchronously, capturing and returning the result.
    It supports execution of both expressions and statements, including handling asynchronous functions.

    Parameters:
    -----------
    input_string : str
        The Python code to be executed, provided as a string. This can be an expression, a statement, or a series of statements.
    local_namespace : dict
        A dictionary of key-value pairs representing the local namespace where the code will be executed.
        The provided namespace is used to store and retrieve variables and results from the executed code.

    Returns:
    --------
    Any
        The result of the evaluated expression or statement. If the input was an asynchronous function, it will be awaited,
        and the result of that function will be returned. If the input was a statement without a return value,
        the function returns None.

    Example Usage:
    --------------
    result = await aeval("x + y", x=2, y=3)
    print(result)  # Output: 5

    Notes:
    ------
    - The function attempts to modify the user's input by assigning its result to a special variable '__result__'.
    - If the modified input results in a syntax error (e.g., because it's a statement like 'print()'), the original input
      is executed without modification.
    - The function handles asynchronous functions by awaiting them if they are not assigned to a variable.
    """
    # Ensure asyncio is always part of the namespace
    local_namespace["asyncio"] = asyncio

    # Save the state of the local namespace before executing the code
    previous = {k: v for k, v in local_namespace.items()}

    # Split the input string by lines to handle multiline input
    lines = input_string.splitlines()

    for i, line in enumerate(lines):
        # Capture the result of the expression in a special variable '__result__'
        if i == len(lines) - 1:
            # Only modify the last line to capture the final result
            modified_input = f"__result__ = {line}"
        else:
            modified_input = line

        try:
            # Try to execute the modified input to capture the result in '__result__'
            await aexec(modified_input, local_namespace)
        except SyntaxError:
            # This might be a statement rather than an expression.
            # In this case, execute the original input without modification.
            await aexec(line, local_namespace)

    # Attempt to retrieve the result of the expression from the local namespace
    result = local_namespace.pop("__result__", None)

    # Capture the state of the local namespace after execution
    post = {k: v for k, v in local_namespace.items()}

    # Check if the local namespace has changed.
    # If not, the code might have been a statement rather than an expression
    if previous == post:
        # The result is a coroutine and wasn't assigned to a variable, await its result
        if asyncio.iscoroutine(result) and result not in local_namespace.values():
            result = await result

    return result
