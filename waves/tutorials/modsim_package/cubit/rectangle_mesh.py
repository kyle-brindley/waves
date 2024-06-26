import sys
import argparse
import pathlib
import shutil

import cubit


def main(input_file, output_file, global_seed, element_type="QUAD", solver="abaqus"):
    """Mesh the simple rectangle geometry partitioned by ``rectangle_partition.py``

    This script meshes a simple Cubit model with a single rectangle part.

    **Node sets:**

    * ``bottom_left`` - bottom left node
    * ``bottom_right`` - bottom right node
    * ``top_right`` - top right node
    * ``top_left`` - top left node
    * ``top`` - top edge nodes
    * ``bottom`` - bottom edge nodes
    * ``left`` - left edge nodes
    * ``right`` - right edge nodes

    **Element sets:**

    * ``ELEMENTS`` - all part elements

    :param str input_file: The Cubit model file created by ``rectangle_geometry.py`` without extension. Will be
        appended with the required extension, e.g. ``input_file``.cub
    :param str output_file: The output file for the Cubit model without extension. Will be appended with the required
        extension, e.g. ``output_file``.cub
    :param float global_seed: The global mesh seed size
    :param str element_type: The model element type. Must be a supported Cubit 4 node element type.
    :param str solver: The solver type to use when exporting the mesh

    :returns: writes ``output_file``.cub and ``output_file``.inp

    :raises RuntimeError: If the solver is not supported
    """

    input_with_extension = f"{input_file}.cub"
    output_with_extension = f"{output_file}.cub"

    # Avoid modifying the contents or timestamp on the input file.
    # Required to get conditional re-builds with a build system such as GNU Make, CMake, or SCons
    if input_file != output_file:
        shutil.copyfile(input_with_extension, output_with_extension)

    cubit.init(['cubit', '-noecho', '-nojournal', '-nographics', '-batch'])
    cubit.cmd('new')
    cubit.cmd('reset')

    cubit.cmd(f"open '{output_with_extension}'")

    cubit.cmd(f"surface 1 size {global_seed}")
    cubit.cmd("mesh surface 1")
    cubit.cmd("set duplicate block elements off")

    cubit.cmd("nodeset 1 add vertex 1")
    cubit.cmd("nodeset 1 name 'bottom_left'")
    cubit.cmd("nodeset 2 add vertex 2")
    cubit.cmd("nodeset 2 name 'bottom_right'")
    cubit.cmd("nodeset 3 add vertex 3")
    cubit.cmd("nodeset 3 name 'top_right'")
    cubit.cmd("nodeset 4 add vertex 4")
    cubit.cmd("nodeset 4 name 'top_left'")

    cubit.cmd("nodeset 5 add curve 3")
    cubit.cmd("nodeset 5 name 'top'")
    cubit.cmd("nodeset 6 add curve 1")
    cubit.cmd("nodeset 6 name 'bottom'")
    cubit.cmd("nodeset 7 add curve 4")
    cubit.cmd("nodeset 7 name 'left'")
    cubit.cmd("nodeset 8 add curve 2")
    cubit.cmd("nodeset 8 name 'right'")

    cubit.cmd("block 1 add surface 1")

    cubit.cmd(f"block 1 name 'ELEMENTS' Element type {element_type}")

    cubit.cmd(f"save as '{output_with_extension}' overwrite")

    if solver.lower() == "abaqus":
        # Export Abaqus orphan mesh for Abaqus workflow
        cubit.cmd(f"export abaqus '{output_file}.inp' partial dimension 2 block 1 overwrite everything")
    elif solver.lower() in ["sierra", "adagio"]:
        # Export Genesis file for Sierra workflow
        cubit.cmd(f"export mesh '{output_file}.g' overwrite")
    else:
        raise RuntimeError(f"Uknown solver '{solver}'")


def get_parser():
    script_name = pathlib.Path(__file__)
    # Set default parameter values
    default_input_file = script_name.stem.replace('_mesh', '_partition')
    default_output_file = script_name.stem
    default_global_seed = 1.0
    default_element_type = "QUAD"
    default_solver = "abaqus"

    prog = f"python {script_name.name} "
    cli_description = "Mesh the simple rectangle geometry partitioned by ``rectangle_partition.py`` " \
                      "and write an ``output_file``.cub Cubit model file and ``output_file``.inp orphan mesh file."
    parser = argparse.ArgumentParser(description=cli_description,
                                     prog=prog)
    parser.add_argument('--input-file', type=str, default=default_input_file,
                        help="The Cubit model file created by ``rectangle_geometry.py`` without extension. " \
                             "Will be appended with the required extension, e.g. ``input_file``.cub " \
                             "(default: %(default)s)")
    parser.add_argument('--output-file', type=str, default=default_output_file,
                        help="The output file for the Cubit model without extension. Will be appended with the " \
                             "required extension, e.g. ``output_file``.cub (default: %(default)s)")
    parser.add_argument('--global-seed', type=float, default=default_global_seed,
                        help="The global mesh seed size (default: %(default)s)")
    parser.add_argument('--element-type', type=str, default=default_element_type,
                        help="The model element type. Must be a supported Cubit 4 node element type. " \
                             "(default: %(default)s)")
    parser.add_argument('--solver', type=str, default=default_solver, choices=["abaqus", "sierra", "adagio"],
                        help="The target solver for the mesh file. (default: %(default)s)")

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    sys.exit(main(
        input_file=args.input_file,
        output_file=args.output_file,
        global_seed=args.global_seed,
        element_type=args.element_type,
        solver=args.solver
    ))
