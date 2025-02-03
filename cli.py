#!/usr/bin/env python3
import glob
import os
import sys

import click

sys.path.insert(0, ".")

plugin_folder = os.path.join(os.path.dirname(__file__), "commands")


class MyCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith(".py") and filename.find("_") != 0:
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        # only looks in plugins dir ;
        ns = {}
        fn = os.path.join(plugin_folder, name + ".py")
        if not os.path.exists(fn):
            files = glob.glob(os.path.join(plugin_folder, name + "*.py"))

            if len(files) == 1:
                fn = files[0]
            elif len(files) > 1:
                print("Possible commands: ")
                print(files)
                exit(0)
        try:
            with open(fn) as f:
                code = compile(f.read(), fn, "exec")
                eval(code, ns, ns)
            return ns["cli"]
        except Exception as e:
            print(f"Error on {name=}", e)
            # raise


@click.group()
def cli1():
    pass


cli2 = MyCLI(
    help="This tool's subcommands are loaded from a " "plugin folder dynamically.",
)


cli = click.CommandCollection(
    sources=[cli1, cli2],
)
if __name__ == "__main__":
    cli()
