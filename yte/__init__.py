import sys
import yaml
import plac
from yte.utils import _process_yaml_value


def process_yaml(file_or_str, outfile=None, variables=None):
    """Process a YAML file or string with YTE,
    returning the processed version.
    """
    if variables is None:
        variables = dict()
    variables["_process_yaml_value"] = _process_yaml_value
    result = _process_yaml_value(
        yaml.load(file_or_str, Loader=yaml.FullLoader), variables
    )

    if outfile is not None:
        yaml.dump(result, outfile)
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
