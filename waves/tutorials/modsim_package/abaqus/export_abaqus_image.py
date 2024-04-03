import os
import sys
import shutil
import inspect
import argparse
import tempfile

import abaqus
import abaqusConstants

# Import the shared abaqus utilities, trying both tutorial directory structures.
# Most end-users will implement only one of these structures and should replace
# the try/except structure with a single import line, e.g.
#
# import modsim_package.abaqus.abaqus_utilities as abaqus_utilities
try:
    import modsim_package.abaqus.abaqus_utilities as abaqus_utilities
except ImportError:
    import abaqus_utilities


default_x_angle = 0.
default_y_angle = 0.
default_z_angle = 0.
default_image_size = (1920, 1080)
default_model_name = "Model-1"
default_part_name = "Part-1"
cli_description = "Save an assembly view image of an Abaqus model from an input or CAE file"

# One time dump from abaqus.session.viewports['Viewport: 1'].colorMappings.keys()) to stay Python 3 compatible for
# Sphinx documentation
color_map_choices = [
    'Material', 'Section', 'Composite layup', 'Composite ply', 'Part', 'Part instance',
    'Element set', 'Averaging region', 'Element type', 'Default', 'Assembly', 'Part geometry', 'Load', 'Boundary condition',
    'Interaction', 'Constraint', 'Property', 'Meshability', 'Instance type', 'Set', 'Surface', 'Internal set',
    'Internal surface', 'Display group', 'Selection group', 'Skin', 'Stringer', 'Cell', 'Face'
]


def main(input_file, output_file,
         x_angle=default_x_angle,
         y_angle=default_y_angle,
         z_angle=default_z_angle,
         image_size=default_image_size,
         model_name=default_model_name,
         part_name=default_part_name,
         color_map=color_map_choices[0]):
    """Save an assembly view image of an Abaqus model from an input or CAE file.

    Open an Abaqus CAE ``*.cae`` or input ``*.inp`` file and save an assembly view image.
    Abaqus CAE files are copied to a temporary file before opening to avoid file modification, which is necessary for
    compatibility with build systems such as SCons.

    :param str input_file: Abaqus input file. Suports ``*.inp`` and ``*.cae``.
    :param str output_file: Output image file. Supports ``*.png`` and ``*.svg``.
    :param float x_angle: Rotation about X-axis in degrees for ``abaqus.session.viewports[].view.rotate`` Abaqus Python
        method
    :param float y_angle: Rotation about Y-axis in degrees for ``abaqus.session.viewports[].view.rotate`` Abaqus Python
        method
    :param float z_angle: Rotation about Z-axis in degrees for ``abaqus.session.viewports[].view.rotate`` Abaqus Python
        method
    :param tuple image_size: Tuple containing height and width of the output image in pixels
    :param str model_name: model to query in the Abaqus model database
    :param str part_name: part to query in the specified Abaqus model
    :param str color_map: color map key

    :returns: writes image to ``{output_file}``
    """
    input_file_extension = os.path.splitext(input_file)[1]
    if input_file_extension.lower() == ".cae":
        with tempfile.NamedTemporaryFile(suffix=".cae", dir=".") as copy_file:
            shutil.copyfile(input_file, copy_file.name)
            abaqus.openMdb(pathName=copy_file.name)
            image(output_file, x_angle=x_angle, y_angle=y_angle, z_angle=z_angle, image_size=image_size,
                  model_name=model_name, part_name=part_name, color_map=color_map)
    elif input_file_extension.lower() == ".inp":
        abaqus.mdb.ModelFromInputFile(name=model_name, inputFileName=input_file)
        image(output_file, x_angle=x_angle, y_angle=y_angle, z_angle=z_angle, image_size=image_size,
              model_name=model_name, part_name=part_name, color_map=color_map)
    else:
        sys.stderr.write("Unknown file extension {}".format(input_file_extension))
        sys.exit(1)


def image(output_file,
          x_angle=default_x_angle,
          y_angle=default_y_angle,
          z_angle=default_z_angle,
          image_size=default_image_size,
          model_name=default_model_name,
          part_name=default_part_name,
          color_map=color_map_choices[0]):
    """Save an assembly view image of an Abaqus model from an input or CAE file.

    The viewer window is adjusted by the provided x, y, and z angles and the viewport is set to fit the assembly prior
    to saving an image of the viewport screen.

    If the model assembly has no instances, use ``part_name`` to generate one. The ``input_file`` is not modified to
    include this generated instance.

    :param str output_file: Output image file. Supports ``*.png`` and ``*.svg``.
    :param float x_angle: Rotation about X-axis in degrees for ``abaqus.session.viewports[].view.rotate`` Abaqus Python
        method
    :param float y_angle: Rotation about Y-axis in degrees for ``abaqus.session.viewports[].view.rotate`` Abaqus Python
        method
    :param float z_angle: Rotation about Z-axis in degrees for ``abaqus.session.viewports[].view.rotate`` Abaqus Python
        method
    :param tuple image_size: Tuple containing height and width of the output image in pixels
    :param str model_name: model to query in the Abaqus model database
    :param str part_name: part to query in the specified Abaqus model
    :param str color_map: color map key

    :returns: writes image to ``{output_file}``
    """
    output_file_stem, output_file_extension = os.path.splitext(output_file)
    output_file_extension = output_file_extension.lstrip(".")
    assembly = abaqus.mdb.models[model_name].rootAssembly
    if len(assembly.instances.keys()) == 0:
        part = abaqus.mdb.models[model_name].parts[part_name]
        assembly.Instance(name=part_name, part=part, dependent=abaqusConstants.ON)
    viewport = abaqus.session.viewports['Viewport: 1']
    viewport.assemblyDisplay.setValues(
        optimizationTasks=abaqusConstants.OFF, geometricRestrictions=abaqusConstants.OFF,
        stopConditions=abaqusConstants.OFF)
    viewport.setValues(displayedObject=assembly)
    viewport.view.rotate(xAngle=x_angle, yAngle=y_angle, zAngle=z_angle, mode=abaqusConstants.MODEL)
    viewport.view.fitView()
    viewport.enableMultipleColors()
    viewport.setColor(initialColor='#BDBDBD')
    cmap = viewport.colorMappings[color_map]
    viewport.setColor(colorMapping=cmap)
    viewport.disableMultipleColors()
    abaqus.session.printOptions.setValues(vpDecorations=abaqusConstants.OFF)
    abaqus.session.pngOptions.setValues(imageSize=image_size)

    output_format = modsim_package.abaqus_utilities.return_abaqus_constant(output_file_extension)
    abaqus.session.printToFile(fileName=output_file_stem, format=output_format, canvasObjects=(viewport,))


def get_parser():
    file_name = inspect.getfile(lambda: None)
    base_name = os.path.basename(file_name)
    prog = "abaqus cae -noGui {} --".format(base_name)
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument('--input-file', type=str, required=True,
                        help='Abaqus input file. Supports ``*.inp`` and ``*.cae``.')
    parser.add_argument('--output-file', type=str, required=True,
                        help='Output image from the Abaqus viewport. Supports ``*.png``, ``*.svg`` and ``*.eps``.')
    parser.add_argument('--x-angle', type=float, default=default_x_angle,
                        help='Viewer rotation about X-axis in degrees (default: %(default)s)')
    parser.add_argument('--y-angle', type=float, default=default_y_angle,
                        help='Viewer rotation about Y-axis in degrees (default: %(default)s)')
    parser.add_argument('--z-angle', type=float, default=default_z_angle,
                        help='Viewer rotation about Z-axis in degrees (default: %(default)s)')
    parser.add_argument('--image-size', nargs=2, type=int, default=default_image_size,
                        help="Image size in pixels (X, Y) (default: %(default)s)")
    parser.add_argument('--model-name', type=str, default=default_model_name,
                        help="Abaqus model name (default: %(default)s)")
    parser.add_argument('--part-name', type=str, default=default_part_name,
                        help="Abaqus part name (default: %(default)s)")
    parser.add_argument('--color-map', type=str, choices=color_map_choices, default=color_map_choices[0],
                        help="Color map (default: %(default)s)")
    return parser


if __name__ == "__main__":
    parser = get_parser()
    try:
        args, unknown = parser.parse_known_args()
    except SystemExit as err:
        sys.exit(err.code)

    sys.exit(main(
        args.input_file,
        args.output_file,
        x_angle=args.x_angle,
        y_angle=args.y_angle,
        z_angle=args.z_angle,
        image_size=args.image_size,
        model_name=args.model_name,
        part_name=args.part_name,
        color_map=args.color_map
    ))
