# python-embed

**Install Embedded Python from pip**

## Usage

```cmd
pip install python-embed==3.13 --target install_location
```

support 3.8 to 3.13

## Build Package
```cmd
python -m build --sdist
```

## Test Installation
```cmd
pip install -v --target embed .\dist\python_embed-3.13.0.tar.gz
```

## Publish to PyPI
```cmd
python -m twine upload dist/*
```
