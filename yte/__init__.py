import sys
import yaml
import plac
import os.path
from pathlib import Path
from yte.context import Context
from yte.process import FEATURES, _process_yaml_value, _process_inherit, Format, Include
from yte.document import Document
from yte.exceptions import YteError


def process_yaml(
    file_or_str,
    outfile=None,
    variables=None,
    require_use_yte=False,
    disable_features=None,
    base_folder=None,
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
      Possible values to choose from are ["variables", "definitions", "templates", "format", "include"]
    * base_folder - when performing !include or __inherit__, this is the scope limit of target file
      For process_yaml(file), the default value is the folder of the file;
      For process_yaml(str/sys.stdin), the default value is None, and in this case, the include and inherit features are disabled
    """
    result, _ = _process_yaml(
        file_or_str=file_or_str,
        variables=variables,
        require_use_yte=require_use_yte,
        disable_features=disable_features,
        base_folder=base_folder,
    )

    if outfile is not None:
        yaml.dump(result, outfile, sort_keys=False)
    else:
        return result


def _process_yaml(
    file_or_str,
    variables: dict,
    require_use_yte=False,
    disable_features=None,
    base_folder=None,
):
    file_path = None
    try:
        file_name = file_or_str.name
        if os.path.isfile(file_name):
            file_path = Path(os.path.abspath(file_name))
    except AttributeError:
        pass
    if base_folder is None:
        if file_path is not None:
            base_folder = file_path.parent.absolute().as_posix()

    def _load_file(file: str, variables, context: Context):
        if base_folder is None:
            raise YteError(
                f"Cannot perform include or inherit without base_folder been set",
                context,
            )
        base_path = Path(base_folder).absolute()
        if os.path.isabs(file) or file_path is None:
            # load from base_folder param
            file = file.lstrip("/")
            path = base_path / file
        else:
            # load from file
            if file.startswith("../"):
                path = file_path.parent.parent / file.lstrip(".").lstrip("/")
            elif file.startswith("./"):
                path = file_path.parent / file.lstrip(".").lstrip("/")
            else:
                path = file_path.parent / file

        if not base_path in path.parents:
            raise YteError(
                f"Cannot include or inherit file outside of base_folder ({base_folder}), got {path.as_posix()}",
                context,
            )

        new_variables = dict()
        for key in variables:
            if key.startswith("_"):
                continue
            new_variables[key] = variables[key]
        with open(path.as_posix()) as f:
            yaml_value, updated_variables = _process_yaml(
                file_or_str=f,
                variables=new_variables,
                require_use_yte=require_use_yte,
                disable_features=disable_features,
                base_folder=base_folder,
            )

        return yaml_value, updated_variables

    if variables is None:
        variables = dict()
    variables["_process_yaml_value"] = _process_yaml_value
    doc = Document()
    variables["doc"] = doc
    variables["this"] = doc
    variables["_load_file"] = _load_file

    loader = yaml.FullLoader
    loader.add_constructor("!format", lambda loader, node: Format(loader, node))
    loader.add_constructor("!f", lambda loader, node: Format(loader, node))
    loader.add_constructor("!include", lambda loader, node: Include(loader, node))

    try:
        yaml_doc = yaml.load(file_or_str, Loader=loader)
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

        yaml_doc, variables = _process_inherit(
            yaml_doc, variables, Context(), disable_features
        )

        result = _process_yaml_value(
            yaml_doc,
            variables,
            context=Context(),
            disable_features=disable_features,
        )
    else:
        # do not process document since use_yte is required but not found in document
        result = yaml_doc

    return result, variables


@plac.flg(
    "require_use_yte",
    "Require that the document contains a `__use_yte__: true` statement at the top level. "
    "If the statement is not present or false, return document unprocessed "
    "(except removing the `__use_yte__: false` statement if present)",
)
def cli(
    require_use_yte=False,
):
    """Process a YAML file given at STDIN with YTE,
    and print the result to STDOUT.

    Note: if nothing is provided at STDIN,
    this will wait forever.
    """
    process_yaml(sys.stdin, outfile=sys.stdout, require_use_yte=require_use_yte)


def main():
    plac.call(cli)
