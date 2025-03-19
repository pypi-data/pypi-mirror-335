# degel-python-utils

Shared Python utilities from Degel Software Ltd.

## Using degel-python-utils

### Initial setup on a new machine

To get started with `degel-python-utils` on a new machine, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/degel-python-utils.git
   cd degel-python-utils
   ```

2. **Install dependencies:**

   Make sure you have `pipenv` installed. If not, install it using `pip`:

   ```bash
   pip install pipenv
   ```

   Then, install the project dependencies and pre-commit hooks:

   ```bash
   make install
   ```


### Using degel-python-utils in other projects

To use `degel-python-utils` in other projects, you need to install it via PyPI:

1. **Install the library:**

   Add `degel-python-utils` to your `Pipfile` or install it directly using `pipenv`:

   ```bash
   pipenv install degel-python-utils
   ```

2. **Import and use:**

   You can now import and use the utility functions provided by `degel-python-utils` in
   your project:

   ```python
   from degel_python_utils import some_function

   some_function()
   ```

### Developing degel-python-utils

If you want to contribute to the development of `degel-python-utils` or make local
modifications, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/degel-python-utils.git
   cd degel-python-utils
   ```

2. **Install dependencies and pre-commit hooks:**

   ```bash
   make install
   ```

4. **Run tests:**

   Ensure all tests pass before making changes:

   ```bash
   make test
   ```

5. **Make your changes:**

   Edit the code as needed. Ensure that your code follows the project's coding standards.

6. **Lint and test:**

   Before committing your changes, run linting and tests:

   ```bash
   make lint
   make test
   ```

7. **Commit and push:**

   Commit your changes and push to your fork or branch:

   ```bash
   git add .
   git commit -m "Describe your changes"
   git push origin your-branch
   ```

### Distributing degel-python-utils

To distribute a new version of `degel-python-utils`, follow these steps:

1. **Update version:**

   Update the version number in `setup.cfg`.

2. **Build the package:**

   Use `build` to create the distribution package:

   ```bash
   make build
   ```

3. **Upload to PyPI:**

   Upload the package to PyPI using `twine`:

   ```bash
   make publish
   ```

4. **Tag the release:**

   Tag the new release in your git repository:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

By following these instructions, you can effectively use, develop, and distribute the
`degel-python-utils` library. If you encounter any issues or have questions, feel free
to open an issue on the GitHub repository.


### License and copyright

This project is licensed under the [MIT License](LICENSE).

Copyright &copy; 2024, Degel Software Ltd.
