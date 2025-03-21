BUILD INSTRUCTIONS
==================

(Note this file is called "DENODO-README.md" instead of the more standard "README-DENODO.md" in order for it not to
be picked up by the standard "license files" filter in setuptools during build and included in the distribution wheel.)

This project is meant to be built into a "wheel" (standard pythong binary distribution) plus a .tar.gz for sources.
The build system used is `setuptools`, and the configuration for the build lives in the standard `pyproject.toml` file.
The tool used for deploying the distribution packages into pypi is `twine`.

This project uses the "flat" package source structure, so the `denodo` module is directly at the project's root, as
opposed to the "src" package source structure that would see `denodo` included as a subfolder inside an `src` folder.
The reason for this was that this setup allows dynamic addition of the project as a dependency in other projects
with `pip -e` ("Editable Install"), but this reason might be outdated nowadays.


**Before building**

* Make sure `pip`, `setuptools`, `build` and `twine` are installed updated to the latest version. Build needs to be
done from outside the project's virtual environment (it will create one automatically during build)

```
$ python -m pip install --upgrade pip setuptools build twine
```

**Versioning**

The version of the project is kept at the `denodo.sqlalchemy.__version__` property, and `pyproject.toml` reads it from
there. This seems to be the best way, in python projects, to keep project version accessible from the metadata at the
same time it is made accessible from code at runtime.

During build, the `testpypi` repository can be used, but note this repository **does not allow replacing artifacts**,
so once a version is uploaded, a new artifact cannot be uploaded anymore for that same version. There is no equivalent
to the `-SNAPSHOT` mechanism in Maven.

So versions to be adopted during build are of the form `2.0.0.dev1`, `2.0.0.dev2`, etc. An increase on the final `dev`
index will be needed each time it is needed to upload it to testpypi.


**Creating the build artifacts**

* Make sure the `README.md` file (which will be displayed in pypi) contains accurate and up-to-date information about
the dependencies of the project and its versions.
* Make sure no `denodo_sqlalchemy.egginfo` or `dist` folders exist at the project's root. If they exist from a 
previous build, remove them.
* Run `python -m build` in order to build the project. This will create `denodo_sqlalchemy.egg-info` and a `dist` folders.
* Verify the sources `.tar.gz` and the `.whl` packages created inside `dist`. These are both `.zip` files.


**Uploading the artifacts to testpypi**

Once the distribution has been built and verified, it can be uploaded to testpypi with:

```
python -m twine upload --repository testpypi dist/*
```

This will make it available via `pip` like:

```
pip install --index-url https://test.pypi.org/simple/ denodo-sqlalchemy
```
Or:
```
pip install --index-url https://test.pypi.org/simple/ denodo-sqlalchemy[flightsql]
```
But note that `pip` will try to use testpypi for every dependency too, which is inconvenient. So if you install
the package from testpypi this way, make sure all dependencies have been first separately installed from "normal" pypi.


**Uploading and publishing the artifacts**

Once the distribution has been build, verified, and tested in testpypi, it can be uploaded to pypi.

First, make sure that the version in `denodo.sqlalchemy.__version__` is not a `dev*` one any more, and instead it
shows the real, definitive value to be assigned to it.

Then upload with:

```
python -m twine upload dist/*
```

After this, the distribution should be also uploaded to the Support Site and the User Manual should be updated.




