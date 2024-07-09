# Devlopement

The local installation is used for development and testing.  It is also used to run the example projects.  The local installation is done using the following steps:

    pip install --editable .

The --editable option is used to install the package in "editable" mode.  This means that the package is installed in such a way that changes to the source code are immediately available to the installed package.  This is useful for development and testing.  Unfortunately, the --editable option is not 100% accurate, in that it will expose some things that are not exposed in the release.

You can uninstall the package using the following command:

    ```
    pip uninstall knowledge-engineer
    ```


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

    ```
    pip uninstall knowledge-engineer
    ```
    
### 2. Increment the version no in the pyproject.toml file.
    
    **This has been changed...** 
    We used to use the setup.cfg, but now are following this doc: https://www.freecodecamp.org/news/how-to-create-and-upload-your-first-python-package-to-pypi/ 
    

    The version number is in the pyproject.toml file.  Increment the version.  The version number is in the following format:

    ```
[project]
name = "knowledge_engineer"
version = "0.5.0"
    ```

3. Build the distribution files.     

    ```
    rm -r dist
    python -m build
    ```

    To Install
    ```
    python3 -m pip install --upgrade build
    ```

5. Upload the distribution files to the test.pypi repository.
    
   ```
   twine upload --repository testpypi dist/*
   ```

6. Test the test release.

    ```
    pip install --index-url https://test.pypi.org/simple/ --no-deps knowledge-engineer
    ```
    
7. uninstall the test release.\

    ```
    pip uninstall knowledge-engineer
    ```
    
8. Upload the distribution files to the pypi repository.

    ```
    twine upload  --repository pypi dist/*
    ```
    
9. Install the release.

    ```
    pip install knowledge-engineer
    ```
    
10. Test the release.

    Good luck
