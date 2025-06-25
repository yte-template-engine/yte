from dataclasses import dataclass, field
import importlib.metadata
from pathlib import Path
import sys
import textwrap
from typing import Any, List, Optional, Tuple
import json
import yaml
import argparse_dataclass
from yte import process_yaml


@argparse_dataclass.dataclass
class Options:
    template: str = field(
        default="-",
        metadata={
            "help": "Path to the template file. If '-' is given, read from STDIN."
        },
    )

    output: str = field(
        default="-",
        metadata={"help": "Path to the output file. If '-' is given, write to STDOUT."},
    )

    require_use_yte: bool = field(
        default=False,
        metadata={
            "help": "Require that the document contains a `__use_yte__: true` "
            "statement at the top level. If the statement is not present or false, "
            "return document unprocessed (except removing the `__use_yte__: false` "
            "statement if present)."
        },
    )

    variable_file: Optional[Path] = field(
        default=None,
        metadata={
            "help": "Path to a file containing map of variables for the template "
            "(.json or .yaml format). Values given here are overwritten by values "
            "with the same names in the --variables option."
        },
    )

    # Variables to use in the template, given as space separated name=value pairs.
    variables: List[str] = field(
        default_factory=list,
        metadata={
            "nargs": "*",
            "help": "Space separated list of variables to use in the template, "
            "given as name=value pairs.",
        },
    )

    version: bool = field(default=False, metadata={"help": "Print version and exit."})


def get_argument_parser():
    return argparse_dataclass.ArgumentParser(
        Options,
        description=textwrap.dedent(
            """
            Process a YAML file given at STDIN with YTE,
            and print the result to STDOUT.

            Note: if nothing is provided at STDIN,
            this will wait forever.
            """
        ),
    )


@dataclass
class Cli:
    args: argparse_dataclass.OptionsType

    def handle_args(self):
        if not self.handle_version():
            self.handle_process()

    def handle_version(self) -> bool:
        if self.args.version:
            print(importlib.metadata.version("yte"))
            return True
        return False

    def handle_process(self):
        variables = {}

        if self.args.variable_file is not None:

            def handle_mapping(loaded: Any):
                if not isinstance(loaded, dict):
                    raise ValueError(
                        "Variables file must contain a YAML mapping (dictionary)."
                    )
                variables.update(loaded)

            if self.args.variable_file.suffix in [".yaml", ".yml"]:
                with open(self.args.variable_file, "r") as f:
                    handle_mapping(yaml.load(f, Loader=yaml.SafeLoader))
            elif self.args.variable_file.suffix == ".json":
                with open(self.args.variable_file, "r") as f:
                    handle_mapping(json.load(f))
            else:
                raise ValueError(
                    "Unsupported file format for variables file. Use .yaml or .json."
                )
        if self.args.variables:

            def parse_item(item: str) -> Tuple[str, Any]:
                key, value = item.split("=", 1)
                value = yaml.load(value, Loader=yaml.SafeLoader)
                return key, value

            variables.update(parse_item(item) for item in self.args.variables)

        use_stdin = self.args.template == "-"
        use_stdout = self.args.output == "-"

        infile = sys.stdin if use_stdin else open(self.args.template, "r")
        outfile = sys.stdout if use_stdout else open(self.args.output, "w")

        process_yaml(infile, outfile=outfile, variables=variables)

        if not use_stdin:
            infile.close()
        if not use_stdout:
            outfile.close()


def main():
    parser = get_argument_parser()
    args = parser.parse_args()
    Cli(args).handle_args()
