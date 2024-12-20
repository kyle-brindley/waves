import os
import shlex
import string
import typing
import inspect
import pathlib
import tempfile
import subprocess
from importlib.metadata import version, PackageNotFoundError

import pytest

from waves import _settings
from common import platform_check


testing_windows, root_fs, testing_macos = platform_check()

tutorial_directory = _settings._tutorials_directory
env = os.environ.copy()
waves_command = "waves"
odb_extract_command = "odb_extract"

# If executing in repository, add package to PYTHONPATH
try:
    version("waves")
    installed = True
except PackageNotFoundError:
    installed = False

if not installed:
    waves_command = "python -m waves._main"
    odb_extract_command = "python -m waves._abaqus.odb_extract"
    package_parent_path = _settings._project_root_abspath.parent
    key = "PYTHONPATH"
    if key in env:
        env[key] = f"{package_parent_path}:{env[key]}"
    else:
        env[key] = f"{package_parent_path}"

fetch_template = string.Template("${waves_command} fetch ${fetch_options} --destination ${temp_directory}")
system_tests = [
    # CLI sign-of-life and help/usage
    ([string.Template("${waves_command} --help")], None),
    ([string.Template("${waves_command} docs --help")], None),
    ([string.Template("${waves_command} fetch --help")], None),
    ([string.Template("${waves_command} visualize --help")], None),
    ([string.Template("${waves_command} build --help")], None),
    ([string.Template("${waves_command} cartesian_product --help")], None),
    ([string.Template("${waves_command} custom_study --help")], None),
    ([string.Template("${waves_command} latin_hypercube --help")], None),
    ([string.Template("${waves_command} sobol_sequence --help")], None),
    ([string.Template("${waves_command} print_study --help")], None),
    ([string.Template("${odb_extract_command} --help")], None),
    # Real fetch operations (on tutorials directory)
    ([fetch_template], "tutorials"),
    # Real visualize operations (on modsim template)
    # TODO: Fix the Windows execution of this system test
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/796
    pytest.param(
        [
            fetch_template,
            "scons -h",
            string.Template("${waves_command} visualize rectangle_compression-nominal --output-file nominal.png"),
        ],
        "modsim_template",
        marks=pytest.mark.skipif(
            testing_windows, reason="System test fails on Windows when run with pytest, but succeeds when run manually."
        ),
    ),
]
if installed:
    system_tests.append(
        # The HTML docs path doesn't exist in the repository. Can only system test from an installed package.
        ([string.Template("${waves_command} docs --print-local-path")], None),
    )

require_third_party_tests = [
    # Tutorials
    ([fetch_template, string.Template("scons rectangle ${unconditional_build}")], "tutorials/scons_quickstart"),
    pytest.param(
        [fetch_template, string.Template("scons rectangle ${unconditional_build}")],
        "tutorials/multi_action_task",
        marks=pytest.mark.skipif(
            testing_windows and not installed, reason="Windows handles symlinks in repository poorly"
        ),
    ),
    (
        [
            fetch_template,
            string.Template("scons nominal mesh_convergence ${unconditional_build}"),
            string.Template("${waves_command} print_study build/parameter_studies/mesh_convergence.h5"),
        ],
        "tutorials/waves_quickstart",
    ),
    ([fetch_template, string.Template("scons rectangle ${unconditional_build}")], "tutorials/tutorial_gmsh"),
    (
        [fetch_template, string.Template("scons submit_beam_cae ${unconditional_build}")],
        "tutorials/tutorial_abaqus_cae",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons . --sconstruct=tutorial_00_SConstruct ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 0",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_01_geometry --sconstruct=tutorial_01_geometry_SConstruct ${unconditional_build} --print-build-failures"  # noqa: E501
            ),
        ],
        "--tutorial 1",
    ),
    pytest.param(
        [fetch_template, "scons tutorial_matlab --sconstruct=tutorial_matlab_SConstruct"],
        "tutorials",
        marks=pytest.mark.skip("Too few licenses to reliably pass"),
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_02_partition_mesh --sconstruct=tutorial_02_partition_mesh_SConstruct ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 2",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_argparse_types --sconstruct=tutorial_argparse_types_SConstruct ${unconditional_build} --print-build-failures"
            ),
        ],
        "tutorials",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_03_solverprep --sconstruct=tutorial_03_solverprep_SConstruct ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 3",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_04_simulation --sconstruct=tutorial_04_simulation_SConstruct ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 4",
    ),
    pytest.param(
        [fetch_template, string.Template("scons . ${unconditional_build} --print-build-failures")],
        "tutorials/tutorial_cubit",
        marks=pytest.mark.skipif(
            testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Cubit"
        ),
    ),
    pytest.param(
        [fetch_template, string.Template("scons . ${unconditional_build} --print-build-failures")],
        "tutorials/tutorial_cubit_alternate",
        marks=pytest.mark.skipif(
            testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Cubit"
        ),
    ),
    (
        [fetch_template, string.Template("scons quinoa-local ${unconditional_build} --print-build-failures")],
        "tutorials/tutorial_quinoa",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_escape_sequences --sconstruct=tutorial_escape_sequences_SConstruct --solve-cpus=1 ${unconditional_build} --print-build-failures"
            ),
        ],
        "tutorials",
    ),
    # TODO: Figure out how to authenticate the institutional account without expanding the user credential exposure to
    # AEA Gitlab group members. Until then, the SSH remote execution can't be integration/regression tested.
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_remote_execution --sconstruct=tutorial_remote_execution_SConstruct ${unconditional_build} --print-build-failures"
            ),
        ],
        "tutorials",
        marks=pytest.mark.skip("Can't reliably authenticate to the remote server"),
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_sbatch --sconstruct=tutorial_sbatch_SConstruct ${unconditional_build} --print-build-failures"
            ),
        ],
        "tutorials",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_05_parameter_substitution --sconstruct=tutorial_05_parameter_substitution_SConstruct ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 5",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_06_include_files --sconstruct=tutorial_06_include_files_SConstruct ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 6",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_07_cartesian_product --sconstruct=tutorial_07_cartesian_product_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 7",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_07_latin_hypercube --sconstruct=tutorial_07_latin_hypercube_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "tutorials",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_07_sobol_sequence --sconstruct=tutorial_07_sobol_sequence_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "tutorials",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_08_data_extraction --sconstruct=tutorial_08_data_extraction_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 8",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_09_post_processing --sconstruct=tutorial_09_post_processing_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 9",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons unit_testing --sconstruct=tutorial_10_unit_testing_SConstruct ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 10",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_sensitivity_study --sconstruct=tutorial_sensitivity_study_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "tutorials",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons datacheck --sconstruct=tutorial_11_regression_testing_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 11",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_12_archival --sconstruct=tutorial_12_archival_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "--tutorial 12",
    ),
    # TODO: Windows compatible writing builders tutorial
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/803
    pytest.param(
        [fetch_template, "chmod +x solver.py", "scons ."],
        "tutorials/tutorial_writing_builders",
        marks=pytest.mark.skipif(testing_windows, reason="Tutorial not yet Windows compatible"),
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_task_reuse --sconstruct=tutorial_task_reuse_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "tutorials",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_mesh_convergence --sconstruct=tutorial_mesh_convergence_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "tutorials",
    ),
    (
        [
            fetch_template,
            string.Template(
                "${waves_command} build tutorial_extend_study --max-iterations=4 --sconstruct=tutorial_extend_study_SConstruct --jobs=4"
            ),
        ],
        "tutorials",
    ),
    (
        [
            fetch_template,
            string.Template(
                "scons tutorial_part_image --sconstruct=tutorial_part_image_SConstruct --jobs=4 ${unconditional_build} --print-build-failures"
            ),
        ],
        "tutorials",
    ),
    # TODO: Write a Windows friendly "cat" like command
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/802
    pytest.param(
        [fetch_template, "scons . --jobs=4"],
        "tutorials/tutorial_ParameterStudySConscript",
        marks=pytest.mark.skipif(testing_windows, reason="Windows CI server doesn't like the cat command"),
    ),
    # ModSim templates
    pytest.param(
        [
            fetch_template,
            string.Template("scons . ${unconditional_build} --jobs=4"),
            string.Template("${waves_command} visualize rectangle_compression-nominal --output-file nominal.png"),
            string.Template(
                "${waves_command} print_study build/rectangle_compression-mesh_convergence/mesh_convergence.h5"
            ),
        ],
        "modsim_template",
        marks=pytest.mark.skipif(
            testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Abaqus"
        ),
    ),
    pytest.param(
        [
            fetch_template,
            string.Template("scons . ${unconditional_build} --jobs=4"),
            string.Template("${waves_command} visualize rectangle_compression-nominal --output-file nominal.png"),
            string.Template(
                "${waves_command} print_study build/parameter_studies/rectangle_compression-mesh_convergence.h5"
            ),
        ],
        "modsim_template_2",
        marks=pytest.mark.skipif(
            testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Abaqus"
        ),
    ),
]


@pytest.mark.systemtest
@pytest.mark.parametrize("commands, fetch_options", system_tests)
def test_system(
    system_test_directory,
    unconditional_build,
    commands: typing.Iterable[str],
    fetch_options: typing.Optional[str],
) -> None:
    """Run shell commands as system tests in a temporary directory

    Iterates on the command strings in the commands list. Performs string template substitution using keys:

    * ``waves_command``: module namespace variable selected to match installation status
    * ``odb_extract_command``: module namespace variable selected to match installation status
    * ``fetch_options``: test API variable
    * ``temp_directory``: temporary directory created one per test with ``tempfile``

    Accepts a custom pytest CLI option to re-direct the temporary system test root directory away from ``$TMPDIR`` as

    .. code-block::

       pytest --system-test-dir=/my/systemtest/output

    :param commands: list of command strings for the system test
    :param fetch_options: the fetch arguments for replacement in string templates
    """
    if system_test_directory is not None:
        system_test_directory.mkdir(parents=True, exist_ok=True)

    kwargs = {}
    temporary_directory_arguments = inspect.getfullargspec(tempfile.TemporaryDirectory).args
    if "ignore_cleanup_errors" in temporary_directory_arguments and system_test_directory is not None:
        kwargs.update({"ignore_cleanup_errors": True})
    with tempfile.TemporaryDirectory(dir=system_test_directory, **kwargs) as temp_directory:
        template_substitution = {
            "waves_command": waves_command,
            "odb_extract_command": odb_extract_command,
            "fetch_options": fetch_options,
            "temp_directory": temp_directory,
            "unconditional_build": "--unconditional-build" if unconditional_build else "",
        }
        for command in commands:
            if isinstance(command, string.Template):
                command = command.substitute(template_substitution)
            command = shlex.split(command, posix=not testing_windows)
            subprocess.check_output(command, env=env, cwd=temp_directory, text=True)


@pytest.mark.systemtest
@pytest.mark.require_third_party
@pytest.mark.parametrize("commands, fetch_options", require_third_party_tests)
def test_system_requiring_third_party_software(
    system_test_directory,
    unconditional_build,
    commands: typing.Iterable[str],
    fetch_options: typing.Optional[str],
) -> None:
    """Pass through wrapper of :meth:`test_system` to allow variations in bulk pytest markers"""
    test_system(system_test_directory, unconditional_build, commands, fetch_options)
