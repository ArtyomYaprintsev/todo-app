set -xe
flake8 server
mypy server
isort server --check-only
pylint server
