
#!/bin/bash

# Usage: source dist-test.sh your-package-name

# Stop if anything fails
set -e

PACKAGE_NAME="$1"
VENV_DIR=".venv-testpypi"

if [ -z "$PACKAGE_NAME" ]; then
  echo "Usage: source $0 <your-package-name>"
  return 1
fi

# Create a new virtual environment
python3 -m venv "$VENV_DIR"

# Activate it
source "$VENV_DIR/bin/activate"

# Upgrade pip and setuptools
pip install --upgrade pip setuptools

# Install your package from TestPyPI, but pull dependencies from real PyPI
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple \
            "$PACKAGE_NAME"

# Show installed packages
echo
echo "Installed packages in the virtualenv:"
pip list

# Drop you into the activated virtualenv
echo
echo "Virtualenv is active. Type 'deactivate' to exit."
$SHELL
rm -rfv "$VENV_DIR"
