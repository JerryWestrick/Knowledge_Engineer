# Devlopement

The local installation is used for development and testing.  It is also used to run the example projects.  The local installation is done using the following steps:

    pip install --editable .

The --editable option is used to install the package in "editable" mode.  This means that the package is installed in such a way that changes to the source code are immediately available to the installed package.  This is useful for development and testing.  Unfortunately, the --editable option is not 100% accurate, in that it will expose some things that are not exposed in the release.

You can uninstall the package using the following command:

    pip uninstall knowledge-engineer



# Release A Version
In order to release a version of the knowledge-engineer package, you need to do the following:


1. uninstall the Knowledge Engineer package from your local environment.
2. Increment the version no in the setup.cfg file.
3. Build the distribution files.
4. Upload the distribution files to the test.pypi repository.
5. Test the test release.
6. uninstall the test release.
7. Upload the distribution files to the pypi repository.
8. Install the release.
9. Test the release.

### 1. Uninstall the Knowledge Engineer package from your local environment

    pip uninstall knowledge-engineer

### 2. Increment the version no in the setup.cfg file.
    
    The version number is in the setup.cfg file.  Increment the version number by one.  The version number is in the following format:

    ```
    [metadata]
    name = knowledge_engineer
    version = 0.1.2
    ```

3. Build the distribution files.     


    rm -r dist
    python -m build

4. Upload the distribution files to the test.pypi repository.
    
        twine upload --repository testpypi dist/*

5. Test the test release.


    pip install --index-url https://test.pypi.org/simple/ --no-deps knowledge-engineer

6. uninstall the test release.\


    pip uninstall knowledge-engineer

7. Upload the distribution files to the pypi repository.


    twine upload  --repository pypi dist/*

8. Install the release.


    pip install knowledge-engineer

9. Test the release.

    Good luck