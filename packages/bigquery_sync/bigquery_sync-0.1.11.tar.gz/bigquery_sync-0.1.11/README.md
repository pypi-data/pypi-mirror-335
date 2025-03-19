# BigQuery Sync

This repository contains the `bigquery_sync` package, which helps to sync between git and Bigquery in your Python projects. This guide provides instructions for configuring, building, and publishing the package to PyPI using `poetry`.

## Prerequisites

Before getting started, ensure that you have the following installed on your machine:

- [Python](https://www.python.org/downloads/) (version 3.8 or higher)
- Poetry (latest version)

If you're new to Poetry, it’s a dependency management and packaging tool that simplifies the Python project workflow.

## Setup Instructions

### 1. Configure Your PyPI Credentials

Before you can publish a package to PyPI, you'll need to authenticate. If you haven’t already, configure your Poetry installation with your PyPI API token.

To do this, run the following command, replacing `your-api-token` with your actual PyPI token:

```bash
bash
poetry config pypi-token.pypi your-api-token

```

If you don’t have an API token yet, you can generate one by logging into your [PyPI account](https://pypi.org/manage/account/token/) and following the instructions for creating a new token.

### 2. Update the Version Number

Before publishing a new version of your package, you need to update the version number in the `pyproject.toml` file. This is important for tracking releases and ensuring that your package’s version is unique on PyPI.

Open the `pyproject.toml` file and locate the `[tool.poetry]` section. Update the `version` field to reflect the new version you're about to publish:

```toml
[tool.poetry]
name = "bigquery_sync"
version = "0.1.0"  # Update this version number
description = "A Python package for syncing with BigQuery."

```

### 3. Build the Package

Once you've updated the version number, it's time to build the package. This will create distributable files that can be uploaded to PyPI.

Run the following command to build the package:

```bash
poetry build

```

This command will generate two types of files inside the `dist/` directory:

- A source distribution (`.tar.gz` file)
- A wheel distribution (`.whl` file)

### 4. Publish the Package to PyPI

After successfully building the package, you can now publish it to PyPI.

Use the following command to publish your package:

```bash
poetry publish
```

If you’ve correctly configured your PyPI token, Poetry will authenticate and publish the package.

### 5. Verifying the Package

Once the package has been published, you can verify it by visiting the PyPI website:

- Go to https://pypi.org/project/bigquery_sync/
- Confirm that the new version is listed and that all the information is correct.

You can also install and test your package locally by running:

```bash
pip install bigquery_sync
```

## Additional Resources

For more detailed instructions on publishing Python packages to PyPI using Poetry, you can refer to the following tutorial:

- [How To Publish Python Packages to PyPI Using Poetry](https://www.digitalocean.com/community/tutorials/how-to-publish-python-packages-to-pypi-using-poetry-on-ubuntu-22-04)

This guide provides further insights and troubleshooting tips if you run into any issues.

## Conclusion

By following the steps above, you can easily configure, build, and publish your Python package to PyPI using Poetry. Happy coding!