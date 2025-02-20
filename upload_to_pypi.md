# PyPI Upload Guide

## Cleaning Previous Builds

```bash
rm -rf build/ dist/ *.egg-info/
```

## Building the Package

```bash
python setup.py bdist_wheel
```

## Uploading to PyPI

### Test PyPI Upload
```bash
twine upload --repository testpypi dist/*.whl
```

### Production PyPI Upload
```bash
twine upload --repository pypi dist/*.whl
```

## Installation Instructions

### Installing from Production PyPI
```bash
pip install docgen-cli==1.0.5
```

### Installing from Test PyPI
```bash
pip install --index-url https://test.pypi.org/simple/ docgen-cli==1.0.5
```
