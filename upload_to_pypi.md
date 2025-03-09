# PyPI Upload Guide

## Cleaning Previous Builds

```bash
rm -rf build/ dist/ *.egg-info/
```

## Building the Package

### Build both wheel and source distribution
```bash
python setup.py sdist bdist_wheel
```

> **Note on Cross-Platform Compatibility**: 
> - When you build a wheel on macOS, it will only work on macOS
> - When you build a wheel on Windows, it will only work on Windows
> - To support all platforms, either:
>   1. Build on each platform separately and upload all wheels, or
>   2. Upload a source distribution (sdist) alongside your wheel
>   3. Use tools like `cibuildwheel` for cross-platform wheels

## Uploading to PyPI

### Test PyPI Upload
```bash
twine upload --repository testpypi dist/*
```

### Production PyPI Upload
```bash
twine upload --repository pypi dist/*
```

## Installation Instructions

### Installing from Production PyPI
```bash
pip install docgen-cli==1.0.6
```

### Installing from Test PyPI
```bash
pip install --index-url https://test.pypi.org/simple/ docgen-cli==1.0.6
```

## Troubleshooting

### Package not found on Windows
If your package works on macOS but not on Windows, it's likely because:
1. You've only uploaded a macOS-specific wheel
2. You need to upload a source distribution (sdist) or Windows wheel

### Missing .pyx files on Windows
If you get errors about missing .pyx files on Windows:
1. Make sure your MANIFEST.in includes the .pyx files (not excludes them)
2. Rebuild your package with `python setup.py sdist bdist_wheel`
3. Upload both the wheel and source distribution with `twine upload dist/*`

### Visual C++ Compiler Error on Windows
If Windows users get a "Microsoft Visual C++ 14.0 or greater is required" error:
1. The package now includes a pure Python fallback implementation
2. Make sure to upload both the wheel and source distribution
3. Windows users should be able to install without needing a C++ compiler

### Building for multiple platforms
For Cython extensions, you'll need to build on each platform or use cross-compilation tools.

### Windows-specific requirements
If your package has Windows-specific dependencies:
1. Make sure they're properly specified in setup.py with platform conditionals
2. Test installation on Windows before publishing
