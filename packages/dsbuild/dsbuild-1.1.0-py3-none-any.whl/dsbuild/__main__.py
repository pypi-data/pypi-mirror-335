#!/usr/bin/env python
"""
dsbuild – A multi-purpose build and packaging helper for Python projects.

This script provides commands for:
  * Building Python wheel packages.
  * Cleaning build artifacts.
  * Running tests with coverage.
  * Generating version files.
  * Managing namespace- vs. non-namespace-based libraries.

It offers additional options such as checking for newer dsbuild releases on PyPI.
Run `dsbuild --help` or `dsbuild <subcommand> --help` for usage details.
"""

import json
import os
import shutil
import subprocess
import sys
import urllib.request
from argparse import Action, ArgumentParser, Namespace, RawTextHelpFormatter
from configparser import ConfigParser, NoSectionError
from functools import lru_cache
from inspect import signature
from pathlib import Path
from setuptools import find_namespace_packages, find_packages
from typing import Any, TypedDict

from packaging.version import parse

# Local Folder
from . import __version__
from .version import get_version


class DsBuildConfig(TypedDict):
    """Data structure for the dsbuild configuration."""

    package_prefix: str
    """The prefix to add to each package name."""

    namespace_package_topdirs: list[str]
    """The top-level directories to check for namespace packages."""

    test_dir: str
    """The directory containing the unit tests."""

    check_for_a_new_version: bool
    """Whether to check for a new version of dsbuild on PyPI."""


##################################################
# Path-based utilities


@lru_cache
def get_venv_dir() -> Path:
    """
    Get the full path to the directory containing the virtual environment.

    Returns:
        Full path to the existing(!) dir containing the virtual environment.

    Raises:
        FileNotFoundError: In case no virtual environment could be found.
    """
    cwd = Path.cwd()
    for p in (cwd, *cwd.parents):
        if (venv_dir := (p / _VENV_NAME)).is_dir():
            return venv_dir
    raise FileNotFoundError(
        f'Virtual environment directory `{_VENV_NAME}` not found...'
    )


def get_project_root_dir() -> Path:
    """
    Get the root directory for this project or package.

    This dir is determined using the assumption that the venv dir is created at this
    top-level.

    Returns:
        Full path to the root directory of the project.
    """
    return get_venv_dir().parent


def get_venv_executable(executable: str, required: bool = True) -> Path | None:
    """
    Return the full path to an executable inside a given virtual environment.

    Args:
        executable: Name of the executable.
        required: Whether to consider it a fatal error if the executable is not found.

    Returns:
        Full path to an executable inside the virtual environment. In case it cannot be
        found, either an exception is raised or None is returned, depending on whether the
        executable is required or not.

    Raises:
        FileNotFoundError: When the executable is required and could not be found.
    """
    search_path = [get_venv_dir() / p for p in _VENV_BIN_SEARCH_DIRS]
    search_path = os.pathsep.join(p.as_posix() for p in search_path)
    venv_executable = shutil.which(executable, path=search_path)

    if required and not venv_executable:
        raise FileNotFoundError(
            f'The virtual environment executable could not be found: {venv_executable}'
        )

    return None if venv_executable is None else Path(venv_executable)


def get_venv_python(required: bool = True) -> Path | None:
    """
    Return the Python executable inside a given virtual environment.

    Args:
        required: Whether to consider it a fatal error if the executable is not found.

    Returns:
        Full path to the Python executable inside the virtual environment. In case it
        cannot be found, either an exception is raised or None is returned, depending on
        whether the executable is required or not.

    Raises:
        FileNotFoundError: When the executable is required and could not be found.
    """
    return get_venv_executable(
        executable=os.path.basename(sys.executable), required=required
    )


##################################################
# Paths

_VENV_NAME = '.venv'
_WHEELS_DIR_NAME = 'wheels'
_BUILD_DIR_NAME = 'build'  # legacy
_SRC_DIR_NAME = 'src' if (get_project_root_dir() / 'src').exists() else 'lib'
_VENV_BIN_SEARCH_DIRS = ['Scripts', 'bin']

##################################################


def check_for_a_new_version(package_name: str, package_version: str):
    """
    Check if there is a newer version of the package on PyPI.

    The function grabs the list of all the versions of the package from PyPI filtering
    out the pre-releases and checks if the last version is greater than the specified
    one.

    It works best if all the versions are PEP440 compatible. Otherwise, the rules for
    filtering and comparison can be found here:
    - https://packaging.pypa.io/en/latest/version.html

    Args:
        package_name: a name of the package to check.
        package_version: the version of the package to compare to PyPI.
    """
    # Get list of all versions from PyPI
    try:
        pypi_index_url = f'https://pypi.python.org/pypi/{package_name}/json'
        pypi_index = json.load(urllib.request.urlopen(pypi_index_url))
        available_versions = [parse(v) for v in pypi_index['releases']]
        available_versions = [v for v in available_versions if not v.is_prerelease]
    except Exception:
        print(f'Warning: unable to check for a new version of {package_name}')
        return

    if not available_versions:
        return

    latest_version = available_versions[-1]
    current_version = parse(package_version)

    if latest_version > current_version:
        print(
            f'Warning: {package_name} {latest_version} is available, while you are '
            f'still using {current_version}. Please consider updating.'
        )
        if latest_version.major > current_version.major:
            print(
                'Warning: There may be breaking changes compared to the version '
                'you are using. Please review the release notes carefully.'
            )
        else:
            print(
                'Note: There are no breaking changes in a new version compared to '
                'the one you are using, only new features and bugfixes - the update '
                'should be safe!'
            )


def get_lib_version(changelog_path: Path | None = None) -> str:
    """Wrapper around version.get_lib_version to provide a sensible default argument."""
    if changelog_path is None:
        changelog_path = get_project_root_dir() / 'Changelog.md'

    return get_version(changelog_path=changelog_path.as_posix())


##################################################
# Helpers to define the sub commands of this script.


def format_parser_description(subparsers: Action) -> str:
    """
    Format the list of subparsers with their descriptions for the console.

    Formatting is done by aligning the "<subparser name>: <subparser description>" lines
    by a ":" symbol to achieve the following effect:

            short_name: description for the short name
                  name: description for the name
        very_long_name: description for the very long name

    Args:
        subparsers: a name of the package to check.

    Returns:
        A formatted string (containing newline symbols) with the subparser names and
            descriptions.
    """
    subparsers_description = {k: v.description for k, v in subparsers.choices.items()}
    max_command_length = len(max(subparsers_description, key=len))

    formatted_descriptions = [
        f'{k:>{max_command_length}}: {v}' for k, v in subparsers_description.items()
    ]
    return '\n'.join(formatted_descriptions)


def call_command(arguments: Namespace) -> Any:
    """
    Calls a function stored in `command_function` argument.

    It requires the argument to contain a callable object under a `command_function`
    argument as well as the arguments for all the function parameters.

    This implementation is inspired by the trick described in the documentation of the
    argparse subparsers functionality:
    https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers

    Arguments:
        arguments: an argparse namespace with the parsed arguments.

    Returns:
        The result of the function call.

    Raises:
        RuntimeError: When the function call cannot be performed due to missing
            arguments.
    """
    command_function = arguments.command_function

    command_parameters = signature(command_function).parameters.keys()
    arguments_dict = vars(arguments)

    missing_arguments = set(command_parameters) - set(arguments_dict)

    if missing_arguments:
        raise RuntimeError(
            'The following arguments are missing for a function call to '
            f'{command_function}: {list(missing_arguments)}'
        )

    kwargs = {k: arguments_dict[k] for k in command_parameters}

    return command_function(**kwargs)


def read_dsbuild_config(config_path: Path | None = None) -> DsBuildConfig:
    """
    Reads the config file that contains a dsbuild section.

    If the file does not exist, the default config is returned, which
    would look like this in the configuration file:

    [dsbuild]
    package_prefix =
    test_dir = tests  # Relative to top-level
    check_for_a_new_version = True
    namespace_package_topdirs = [<_SRC_DIR_NAME>]
    """
    # default config
    dsbuild_conf = {
        'package_prefix': '',
        'namespace_package_topdirs': f'["{_SRC_DIR_NAME}"]',
        'test_dir': 'tests',
        'check_for_a_new_version': True,
    }
    # Note that `namespace_package_topdirs` is always set, but is only actually used
    # when the project root dir does not contain a `setup.py` file.

    # default config path
    if config_path is None:
        config_path = get_project_root_dir() / 'setup.cfg'

    # try to read the configuration file
    try:
        config = ConfigParser()
        config.read(config_path)
        dsbuild_conf.update(dict(config.items('dsbuild')))
    except FileNotFoundError:
        # if the file does not exist, we just return defaults
        pass
    except NoSectionError:
        # if the [dsbuild] section does not exist, we just return defaults
        pass

    # Ensure boolean values
    for k in ['check_for_a_new_version']:
        dsbuild_conf[k] = dsbuild_conf[k] in {True, 'True', 'true', 'Yes', 'yes'}

    # Convert string representing list to an actual list
    for k in ['namespace_package_topdirs']:
        dsbuild_conf[k] = json.loads(dsbuild_conf[k])

    return DsBuildConfig(**dsbuild_conf)  # type: ignore


def find_library(folder: Path) -> tuple[Path, bool]:
    """
    Locate a Python library and identify if it's normal or part of a namespace package.

    This function takes care of ignoring some special folders that might incorrectly be
    detected as a package. For instance, a `tests` folder, if it contains an
    `__init__.py` file, would be detected as a package, which is not what we want.

    Args:
        folder: the folder containing the setup.py file

    Returns:
        str, bool: path to library, False if normal library, True if namespace package

    Raises:
        ValueError in case the provided path does points to neither a normal library
        nor to a namespace package.
    """
    # In case a `_SRC_DIR_NAME` subdir exists (i.e., `src`, or `lib` for older project
    # structures), we should search for packages inside this subdir.
    src_dir = folder / _SRC_DIR_NAME
    if src_dir.is_dir():
        folder = src_dir

    # First, try to find a normal library; then a namespace package.
    for finder in [find_packages, find_namespace_packages]:
        try:
            # To find the main package name, we find all packages and exclude matches that
            # (1) should explicitly be excluded (i.c., 'tests', 'scripts' and 'build'); or
            # (2) contain a literal dot.
            #
            packages = finder(
                where=folder, exclude=['tests', 'scripts', 'build', '*.*']
            )

            if len(packages) > 1:
                raise ValueError(
                    'dsbuild supports only repos with a exactly a single library or '
                    'multiple namespace packages in the same namespace. Found packages: '
                    f'{packages}.'
                )

            return (folder / packages[0], finder == find_namespace_packages)
        except IndexError:
            # In case no package is found, we continue to search for a namespace package.
            # If also no namespace packages are found, a ValueError will be raised
            # below.
            pass

    raise ValueError(
        f'The provided folder `{folder}` does not point to a valid "normal" library '
        'nor does it point to a namespace package.'
    )


def get_library_dirs(toplevel_dirs_to_check: list[str]) -> list[Path]:
    """
    Get the paths to the Python library-containing folders.

    A folder contains a library if it contains a `setup.py` file. There are two
    options:
    1. Simple library: A single `setup.py` file is present in the top-level.
    2. Namespace packages: Possibly multiple `setup.py` files can be found
                           underneath the `./<_SRC_DIR_NAME>` directory.

    Args:
        toplevel_dirs_to_check: List of folders (subfolders of project_root_dir) where
            Python library-containing folders will be searched.

    Returns:
        a list of folders that contain the python library (the folder containing the
            setup.py file)
    """
    project_root_dir = get_project_root_dir()

    # Option 1: Simple library, `setup.py` in top-level.
    if (project_root_dir / 'setup.py').exists():
        return [project_root_dir]

    # Option 2: Namespace packages.
    setup_files = []
    for toplevel in toplevel_dirs_to_check:
        setup_files += sorted((project_root_dir / toplevel).rglob('setup.py'))

    return [f.parent for f in setup_files]


def _clean_setuptools_intermediate_artifacts(pkg_folder: Path, src_subfolder: str):
    """
    Cleans up the intermediate build artifacts created by setuptools.

    This should be called once per actual (sub-)package being built, i.e. for
    namespace packages it must be called for each subpackage.

    The setuptools backend has hardcoded paths for these artefacts and doesn't give us
    the option to clean them.

    There are 2 types of intermediate artifacts:
    1. The `build` directory.
    2. The `<pkg_name>.egg-info` directory.

    More info, see: https://github.com/pypa/setuptools/issues/1871 and
    https://github.com/pypa/setuptools/issues/1347

    To consider, could we switch to the hatchling backend or even the hatch build
    system?

    Args:
        pkg_folder: The full path to the package folder containing the `setup.py` file.
        src_subfolder: A string indicating a subfolder of `pkg_folder`, containing the
            actual source code. For regular packages, this should be 'src' / 'lib',
            for namespace packages, this should be empty. This is directly tied with
            how _we_ (in our team) structure our projects.
    """

    def _safe_del(path: Path):
        try:
            if path.is_dir():
                shutil.rmtree(path)
                print(f'Removed build artifact: {path.as_posix()}')
        except PermissionError as e:
            print(f'!!!Warning!!! Could not delete {path.as_posix()}. Error {e}')

    _safe_del(path=pkg_folder / 'build')

    pkg_name = pkg_folder.name.replace('-', '_')
    _safe_del(path=pkg_folder / src_subfolder / f'{pkg_name}.egg-info')


def cmd_help():
    subprocess.check_call([sys.executable, __file__, '--help'])


def cmd_clean():
    """Clean the root directory of the project to ensure a clean build."""
    dirs_to_clean = [_WHEELS_DIR_NAME, _BUILD_DIR_NAME]

    # Wheels + old-style build cleaning.
    project_root_dir = get_project_root_dir()
    for dirname in dirs_to_clean:
        path = (project_root_dir / dirname).resolve()
        try:
            shutil.rmtree(path)
            print(f'Cleaned directory {path.as_posix()}.')
        except FileNotFoundError:
            pass
        except OSError as e:
            raise OSError(
                f'The folder {path.as_posix()} could not be deleted, '
                'so we are not sure that all build files are fresh.'
            ) from e

    # Clean potential setuptools intermediate artifacts.
    dsbuild_config = read_dsbuild_config()
    library_dirs = get_library_dirs(dsbuild_config['namespace_package_topdirs'])
    if not library_dirs:
        raise ValueError(
            f'No python libraries could be found in {project_root_dir.as_posix()}'
        )

    for library_dir in library_dirs:
        _, is_namespace_pkg = find_library(library_dir)
        src_dir = _SRC_DIR_NAME if not is_namespace_pkg else ''
        _clean_setuptools_intermediate_artifacts(
            pkg_folder=library_dir, src_subfolder=src_dir
        )


def cmd_wheel():
    """Build a wheel of the library."""
    project_root_dir = get_project_root_dir()
    wheels_dir = (project_root_dir / _WHEELS_DIR_NAME).resolve()
    dsbuild_config = read_dsbuild_config()
    venv_python = get_venv_python()
    assert venv_python is not None

    library_dirs = get_library_dirs(dsbuild_config['namespace_package_topdirs'])
    if not library_dirs:
        raise ValueError(
            f'No python libraries could be found in {project_root_dir.as_posix()}'
        )

    for library_dir in library_dirs:
        # Recall our project layout: `library_dir` is the dir containing `setup.py`!!
        #
        # non-namespace package:
        #    <my_lib_root>              <== library_dir
        #    ├── setup.py
        #    └── src/lib
        #        └── my_lib             <== lib_folder
        #
        # namespace package:
        #    <prefix-root>
        #    └── src/lib
        #        ├── prefix-pkg1        <== library_dir
        #        |   ├── setup.py
        #        |   └── prefix         <== lib_folder
        #        |       └── pkg1
        #        ├── prefix-pkg2        <== library_dir
        #        |   ├── setup.py
        #        |   └── prefix         <== lib_folder
        #        |       └── pkg2
        #        ...
        assert os.path.exists(os.path.join(library_dir, 'setup.py'))

        # Determine the package name.
        lib_folder, is_namespace_pkg = find_library(library_dir)

        if is_namespace_pkg:
            lib_name = library_dir.name
        else:
            lib_name = lib_folder.name

        package_name = dsbuild_config['package_prefix'] + lib_name
        this_wheel_dir = wheels_dir / package_name

        # run the wheel creation command
        command = [
            venv_python.as_posix(),
            '-m',
            'build',
            '--wheel',
            '--outdir',
            this_wheel_dir.as_posix(),
        ]
        print(f'Command:{" ".join(command)}')
        subprocess.check_call(command, cwd=library_dir)

        # Clean setuptools cruft.
        src_dir = _SRC_DIR_NAME if not is_namespace_pkg else ''
        _clean_setuptools_intermediate_artifacts(
            pkg_folder=library_dir, src_subfolder=src_dir
        )

    print(f'Wheel(s) created in {wheels_dir.as_posix()}')


def cmd_test():
    """
    Run unittests and coverage report. The tests are being picked up from a directory
    with name matching the pattern `tests`, `*_test` or from `<_SRC_DIR_NAME>/tests`.
    Note that at most a single directory on disk should match. If not, this is considered
    a fatal error.
    Also, note that independently of which directory contained the tests, the output
    directory will always be the top-level `tests_results`.
    """
    project_root_dir = get_project_root_dir()
    dsbuild_config = read_dsbuild_config()

    # check if we can find libraries, otherwise raise exception
    libs = get_library_dirs(dsbuild_config['namespace_package_topdirs'])
    if not libs:
        raise ValueError(
            f'No python libraries could be found in {project_root_dir.as_posix()}'
        )

    # Get a list of (existing) folders that can contain tests.
    test_folders = []
    # 1. Legacy: dirs of the form `*_test`
    test_folders += [f for f in project_root_dir.glob('*_test') if f.is_dir()]

    # 2. Legacy 2: `<_SRC_DIR_NAME>/tests`
    test_dir = project_root_dir / _SRC_DIR_NAME / 'tests'
    if test_dir.is_dir():
        test_folders.append(test_dir)
    # 3. Custom (or new): By default `tests`, but can be configured in `setup.cfg`.
    test_dir = project_root_dir / dsbuild_config['test_dir']
    if test_dir.is_dir():
        test_folders.append(test_dir)

    if len(test_folders) == 0:
        print('Could not find a folder with unittests. No tests will be run.')
        return

    if len(test_folders) > 1:
        raise FileNotFoundError(
            f'Could not find a unique folder with unittests. Found: {test_folders}.'
        )

    test_folder = test_folders[0].as_posix()

    # Define the output dir.
    test_output_dir = (get_project_root_dir() / 'tests_results').as_posix()

    # We only want to report coverage info for the source files in our library (i.e. we
    # need to provide a suitable filter to `--cov=...` when running pytest).
    # For this purpose we use the library directories found in the project. Each of them
    # needs to have its own '--cov' argument.
    cov_args = [f'--cov={os.path.relpath(lib, project_root_dir)}' for lib in libs]

    # run tests
    command = [
        get_venv_python(),
        '-m',
        'pytest',
        test_folder,
        f'--junitxml={test_output_dir}/test-results.xml',
        *cov_args,
        '--cov-branch',
        '--cov-report=term',
        f'--cov-report=xml:{test_output_dir}/coverage.xml',
        f'--cov-report=html:{test_output_dir}/html',
    ]
    subprocess.check_call(command, cwd=project_root_dir)

    print(f'Ran all unittests. Output is written to: {test_output_dir}.')


def cmd_version(changelog: Path):
    """
    Print library version.

    Args:
        changelog: An optional path to the changelog.
    """
    lib_version = get_lib_version(changelog_path=changelog)
    print(lib_version)


def cmd_generate_version_py():
    """Generate a self-sufficient version.py script."""
    src = Path(__file__).parent / 'version.py'
    dst = get_project_root_dir() / 'version.py'

    enc = 'utf-8'

    with open(src, 'r', encoding=enc) as fin, open(dst, 'w', encoding=enc) as fout:
        header = (
            f'#########################################################################'
            f'###############\n'
            f'#\n'
            f'# THIS FILE WAS AUTO-GENERATED BY DSBUILD {__version__}.\n'
            f'#\n'
            f'# IT SHOULD BE COMMITTED TO THE PROJECT ROOT DIRECTORY AND PREFERABLY '
            f'NOT MODIFIED\n'
            f'# MANUALLY.\n'
            f'#\n'
            f'# YOU CAN ALWAYS REGENERATE IT BY RUNNING:\n'
            f'#   $ dsbuild generate-version-py\n'
            f'#\n'
            f'#########################################################################'
            f'###############\n\n\n'
        )

        fout.write(header)
        fout.write(fin.read())

    print(f'Version.py file generated at {dst.as_posix()}')


def cmd_all():
    """Convenience mode that does 'everything' from scratch (build, test, packaging)."""
    cmd_clean()
    cmd_test()
    cmd_wheel()


def cmd_package():
    """Convenience mode that does a clean packaging."""
    cmd_clean()
    cmd_wheel()


def main():
    """Main entry point for the dsbuild script."""
    parser = ArgumentParser(
        prog='dsbuild', formatter_class=RawTextHelpFormatter, description=''
    )
    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=f'%(prog)s {__version__}',
    )

    subparsers = parser.add_subparsers()

    sp = subparsers.add_parser(
        'clean',
        description='Clean the project root directory to ensure a clean build.',
    )
    sp.set_defaults(command_function=cmd_clean)

    sp = subparsers.add_parser('wheel', description='Build wheel.')
    sp.set_defaults(command_function=cmd_wheel)

    sp = subparsers.add_parser('test', description='Run unittests + coverage.')
    sp.set_defaults(command_function=cmd_test)

    sp = subparsers.add_parser(
        'version', description='Determine the version of a library.'
    )
    sp.add_argument(
        '--changelog',
        '-clog',
        default=None,
        type=Path,
        help='Path to the Changelog.md file for version parsing.',
    )
    sp.set_defaults(command_function=cmd_version)

    sp = subparsers.add_parser(
        'generate-version-py',
        description='Generate a self-sufficient version.py at the project root.',
    )
    sp.set_defaults(command_function=cmd_generate_version_py)

    sp = subparsers.add_parser('all', description='clean + test + wheel.')
    sp.set_defaults(command_function=cmd_all)

    sp = subparsers.add_parser('package', description='clean + wheel.')
    sp.set_defaults(command_function=cmd_package)

    parser.description = (
        f'This script helps to build and package python libraries.\n'
        f'{format_parser_description(subparsers)}'
    )

    args = parser.parse_args()

    dsbuild_config = read_dsbuild_config()

    if dsbuild_config['check_for_a_new_version']:
        check_for_a_new_version('dsbuild', __version__)

    call_command(args)


if __name__ == '__main__':
    main()
