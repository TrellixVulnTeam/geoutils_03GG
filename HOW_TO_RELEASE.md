# How to issue a GeoUtils release

## The easy way

1. Change the version number in setup.py. It can be easily done from GitHub directly without a PR. The version number is important for PyPI as it will determine the file name of the wheel. A name can [never be reused](https://pypi.org/help/#file-name-reuse), even if a file or project have been deleted.

2. Follow the steps to [create a new release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository) on GitHub.
Use the same release number and tag as in setup.py.

An automatic GitHub action will start to push and publish the new release to PyPI.

**Note**: A tag and a release can easily be deleted if doing a mistake, but if the release is pushed to PyPI with a new version number, it will not be possible to re-use the same version number anymore.

**In short, if you mess up a release by forgetting to change the version number**:

- PyPI will block the upload, so the GitHub action failed. All is fine.
- You can now edit the version number on the main branch.
- Before releasing, you need to delete **both** the tag and the release of the previous release. If you release with the same tag without deletion, it will ignore your commit changing the version number, and PyPI will block the upload again. You're stuck in a circle.


## The hard way

 1. Go to your local main repository (not the fork) and ensure your master branch is synced:
       git checkout master
       git pull
 2. Look over whats-new.rst and the docs. Make sure "What's New" is complete
    (check the date!) and add a brief summary note describing the release at the
    top.
 3. If you have any doubts, run the full test suite one final time!
      pytest --run-slow --mpl .
 4. Increment the version number "FULLVERSION" in setup.py for PyPI and conda.
 5. On the master branch, commit the release in git:
      git commit -a -m 'Release v1.X.Y'
 6. Tag the release:
      git tag -a v1.X.Y -m 'v1.X.Y'
 7. Build source and binary wheels for pypi:
      git clean -xdf  # this deletes all uncommited changes!
      python setup.py bdist_wheel sdist
 8. Use twine to register and upload the release on pypi. Be careful, you can't
    take this back!
      twine upload dist/geoutils-1.X.Y*
    You will need to be listed as a package owner at
    https://pypi.python.org/pypi/geoutils for this to work.
 9. Push your changes to master:
      git push origin master
      git push origin --tags
 10. Update the stable branch (used by ReadTheDocs) and switch back to master:
       git checkout stable
       git rebase master
       git push origin stable
       git checkout master
     It's OK to force push to 'stable' if necessary.
     We also update the stable branch with `git cherrypick` for documentation
     only fixes that apply the current released version.
 11. Add a section for the next release (v.X.(Y+1)) to doc/whats-new.rst.
 12. Commit your changes and push to master again:
       git commit -a -m 'Revert to dev version'
       git push origin master
     You're done pushing to master!
 13. Issue the release on GitHub. Click on "Draft a new release" at
     https://github.com/geoutils/geoutils/releases. Type in the version number, but
     don't bother to describe it -- we maintain that on the docs instead.
 14. Update the docs. Login to https://readthedocs.org/projects/geoutils/versions/
     and switch your new release tag (at the bottom) from "Inactive" to "Active".
     It should now build automatically.
 15. Issue the release announcement!


## conda-forge
To update the conda-forge distribution of geoutils, a few steps have to be performed manually.
The process **should** be automatic, but at the moment (September 2022), the automatic process does not function!
conda-forge distributions work by having a "feedstock" version of the package, containing instructions on how to bundle it for conda.
The geoutils feedstock is available at [https://github.com/conda-forge/geoutils-feedstock](https://github.com/conda-forge/geoutils-feedstock).

Assuming the dependencies have not changed, only two lines have to be changed in the `meta.yaml` file of the feedstock.
The new version number has to be specified, as well as the new sha256 checksum for the package.
The most straightforward way to obtain the new sha256 checksum is to run `conda-build` (see below) with the old checksum which will fail, and then copying the new hash of the "SHA256 mismatch: ..." error that arises!

First, the geoutils-feedstock repo has to be forked on GitHub.
Then, follow these steps for `NEW_VERSION` (substitute with the actual version name):
```bash

>>> conda install conda-build

>>> git clone https://github.com/your_username/geoutils-feedstock  # or git pull (and make sure the fork is up to date with the upstream repo) if the repo is already cloned

>>> cd geoutils-feedstock/recipe

# Update meta.yaml:
# {% set version = "NEW_VERSION" %}
# sha256: NEW_SHA256

>>> conda-build .  # This is to validate that the build process works, but is technically optional.

>>> git add -u && git commit -m "Updated version to NEW_VERSION"  #  Or whatever you want to tell us :)

>>> git push -u origin master
```
Now, a PR can be made from your personal fork to the upstream geoutils-feedstock.
An automatic linter will say whether the updates conform to the syntax and a CI action will build the package to validate it.
Note that you have to be a maintainer or have the PR be okayed by a maintainer for the CI action to run.
If this works, the PR can be merged, and the conda-forge version will be updated within a few hours!
