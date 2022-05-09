import sys
import yaml
import plac
from yte.context import Context
from yte.process import _process_yaml_value
from yte.document import Document


def process_yaml(file_or_str, outfile=None, variables=None, disable_features=None):
    """Process a YAML file or string with YTE,
    returning the processed version.

    # Arguments
    * file_or_str - file object or string to render
    * outfile - output file to write to, if None output is returned as string
    * variables - variables to be available in the template
    * disable_features - list of features that should be disabled during rendering.
      Possible values to choose from are ["definitions", "variables"]
    """
    if variables is None:
        variables = dict()
    variables["_process_yaml_value"] = _process_yaml_value
    variables["doc"] = Document()

    try:
        yaml_doc = yaml.load(file_or_str, Loader=yaml.FullLoader)
    except yaml.scanner.ScannerError as e:
        raise yaml.scanner.ScannerError(
            f"{e}\nNote that certain characters like colons have a special "
            "meaning in YAML and hence keys or values containing them have "
            "to be quoted."
        )

    if disable_features is not None:
        disable_features = frozenset(disable_features)
    else:
        disable_features = frozenset([])

    result = _process_yaml_value(
        yaml_doc, variables, context=Context(), disable_features=disable_features
    )

    if outfile is not None:
        yaml.dump(result, outfile, sort_keys=False)
    else:
        return result


def cli():
    """Process a YAML file given at STDIN with YTE,
    and print the result to STDOUT.

    Note: if nothing is provided at STDIN,
    this will wait forever.
    """
    process_yaml(sys.stdin, outfile=sys.stdout)


def main():
    plac.call(cli)
