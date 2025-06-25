import yaml
from yte.context import Context
from yte.code_handler import CodeHandler
from yte.process import FEATURES, SKIP, _process_yaml_value
from yte.document import Document
from yte.value_handler import ValueHandler


DEFAULT_CODE_HANDLER = CodeHandler()
DEFAULT_VALUE_HANDLER = ValueHandler()


def process_yaml(
    file_or_str,
    outfile=None,
    variables=None,
    require_use_yte=False,
    disable_features=None,
    code_handler: CodeHandler = DEFAULT_CODE_HANDLER,
    value_handler: ValueHandler = DEFAULT_VALUE_HANDLER,
):
    """Process a YAML file or string with YTE,
    returning the processed version.

    # Arguments
    * file_or_str - file object or string to render
    * outfile - output file to write to, if None output is returned as string
    * variables - variables to be available in the template
    * require_use_yte - skip templating if there is no `__use_yte__ = True`
      statement in the top level of the document
    * disable_features - list of features that should be disabled during rendering.
      Possible values to choose from are ["definitions", "variables"]
    * code_handler - instance of CodeHandler to use during rendering for evaluating expressions
    * value_handler - instance of ValueHandler to use during rendering for postprocessing values
    """
    if variables is None:
        variables = dict()
    variables["_process_yaml_value"] = _process_yaml_value
    doc = Document()
    variables["doc"] = doc
    variables["this"] = doc
    variables["SKIP"] = SKIP

    try:
        yaml_doc = yaml.load(file_or_str, Loader=yaml.FullLoader)
    except yaml.scanner.ScannerError as e:
        raise yaml.scanner.ScannerError(
            f"{e}\nNote that certain characters like colons have a special "
            "meaning in YAML and hence keys or values containing them have "
            "to be quoted."
        )

    is_use_yte = yaml_doc.get("__use_yte__") if isinstance(yaml_doc, dict) else None
    if is_use_yte is not None:
        # remove __use_yte__ key
        yaml_doc.pop("__use_yte__")

    if not require_use_yte or is_use_yte:
        if disable_features is not None:

            disable_features = frozenset(disable_features)
            if not FEATURES.issuperset(disable_features):
                raise ValueError("Invalid features given to `disable_features`.")
        else:
            disable_features = frozenset([])

        result = _process_yaml_value(
            yaml_doc,
            variables,
            context=Context(),
            disable_features=disable_features,
            code_handler=code_handler,
        )

        result = value_handler.postprocess(result)
    else:
        # do not process document since use_yte is required but not found in document
        result = yaml_doc

    if outfile is not None:
        yaml.dump(result, outfile, sort_keys=False)
    else:
        return result
