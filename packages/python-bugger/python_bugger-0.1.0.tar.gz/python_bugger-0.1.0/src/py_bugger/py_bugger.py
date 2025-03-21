import libcst as cst
import os
import random
from pathlib import Path

import py_bugger.cli as cli
import py_bugger.cli_messages as cli_messages


class ImportModifier(cst.CSTTransformer):
    """Modify imports in the user's project."""

    def leave_Import(self, original_node, updated_node):
        """Modify a direct `import <package>` statement."""
        names = updated_node.names
        if names:
            original_name = names[0].name.value

            # Remove one letter from the package name.
            chars = list(original_name)
            char_remove = random.choice(chars)
            chars.remove(char_remove)
            new_name = "".join(chars)

            # Modify the node name.
            new_names = [cst.ImportAlias(name=cst.Name(new_name))]

            return updated_node.with_changes(names=new_names)

        return updated_node


def main():

    args = cli.parse_cli_args()

    # Show message about bare `py-bugger` calls.
    if not any([a for a in vars(args).values()]):
        print(cli_messages.msg_bare_call)

    if args.exception_type == "ModuleNotFoundError":
        print("Introducing a ModuleNotFoundError...")

        # Get the first .py file in the project's root dir.
        if args.target_dir:
            path_project = Path(args.target_dir)
            assert path_project.exists()
        else:
            path_project = Path(os.getcwd())

        py_files = path_project.glob("*.py")
        path = next(py_files)

        # Read user's code.
        source = path.read_text()
        tree = cst.parse_module(source)

        # Modify user's code.
        modified_tree = tree.visit(ImportModifier())

        # Rewrite user's code.
        path.write_text(modified_tree.code)

        print("  Modified file.")


if __name__ == "__main__":
    main()