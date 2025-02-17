from __future__ import annotations

import os
import warnings

import pytest
import yaml  # type: ignore
from packaging.version import Version

import geoutils
import geoutils.misc


class TestMisc:
    def test_environment_files(self) -> None:
        """Check that environment yml files are properly written: all dependencies of env are also in dev-env"""

        fn_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "environment.yml"))
        fn_devenv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dev-environment.yml"))

        # Load the yml as dictionaries
        yaml_env = yaml.safe_load(open(fn_env))
        yaml_devenv = yaml.safe_load(open(fn_devenv))

        # Extract the dependencies values
        conda_dep_env = yaml_env["dependencies"]
        conda_dep_devenv = yaml_devenv["dependencies"]

        # Check if there is any pip dependency, if yes pop it from the end of the list
        if isinstance(conda_dep_devenv[-1], dict):
            pip_dep_devenv = conda_dep_devenv.pop()

            # Check if there is a pip dependency in the normal env as well, if yes pop it also
            if isinstance(conda_dep_env[-1], dict):
                pip_dep_env = conda_dep_env.pop()

                # The diff below computes the dependencies that are in env but not in dev-env
                # It should be empty, otherwise we raise an error
                diff_pip_check = list(set(pip_dep_env) - set(pip_dep_devenv))
                assert len(diff_pip_check) == 0

        # We do the same for the conda dependency, first a sanity check that everything that is in env is also in dev-ev
        diff_conda_check = list(set(conda_dep_env) - set(conda_dep_devenv))
        assert len(diff_conda_check) == 0

    @pytest.mark.parametrize("deprecation_increment", [-1, 0, 1, None])  # type: ignore
    @pytest.mark.parametrize("details", [None, "It was completely useless!", "dunnowhy"])  # type: ignore
    def test_deprecate(self, deprecation_increment: int | None, details: str | None) -> None:
        """
        Test the deprecation warnings/errors.

        If the removal_version is larger than the current, it should warn.
        If the removal_version is smaller or equal, it should raise an error.

        :param deprecation_increment: The version number relative to the current version.
        :param details: An optional explanation for the description.
        """
        warnings.simplefilter("error")

        current_version = geoutils.version.version

        # Set the removal version to be the current version plus the increment (e.g. 0.0.5 + 1 -> 0.0.6)
        removal_version = (
            current_version[:-1] + str(int(current_version.rsplit(".", 1)[1]) + deprecation_increment)
            if deprecation_increment is not None
            else None
        )

        # Define a function with no use that is marked as deprecated.
        @geoutils.misc.deprecate(removal_version, details=details)  # type: ignore
        def useless_func() -> int:
            return 1

        # Example of why Version needs to be used below
        assert not "0.0.10" > "0.0.8"
        assert Version("0.0.10") > Version("0.0.8")

        # If True, a warning is expected. If False, a ValueError is expected.
        should_warn = removal_version is None or Version(removal_version) > Version(current_version)

        # Add the expected text depending on the parametrization.
        text = (
            "Call to deprecated function 'useless_func'."
            if should_warn
            else f"Deprecated function 'useless_func' was removed in {removal_version}."
        )

        if details is not None:
            text += " " + details.strip().capitalize()

            if not any(text.endswith(c) for c in ".!?"):
                text += "."

        if should_warn and removal_version is not None:
            text += f" This functionality will be removed in version {removal_version}."
        elif not should_warn:
            text += f" Current version: {current_version}."

        # Expect either a warning or an exception with the right text.
        if should_warn:
            with pytest.warns(DeprecationWarning, match="^" + text + "$"):
                useless_func()
        else:
            with pytest.raises(ValueError, match="^" + text + "$"):
                useless_func()
