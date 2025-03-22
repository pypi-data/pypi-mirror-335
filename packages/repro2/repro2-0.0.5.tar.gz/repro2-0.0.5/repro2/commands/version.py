import argparse

from overrides import overrides

from repro2 import VERSION
from repro2.commands.subcommand import RootSubcommand


@RootSubcommand.register("version")
class VersionSubcommand(RootSubcommand):
    @overrides
    def add_subparser(self, model: str, parser: argparse._SubParsersAction):
        description = "Display the version"
        self.parser = parser.add_parser("version", description=description, help=description)
        self.parser.set_defaults(func=self.run)

    @overrides
    def run(self, args):
        print(VERSION)
