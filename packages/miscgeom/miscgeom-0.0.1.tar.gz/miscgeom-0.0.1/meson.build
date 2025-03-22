# meson.build

project('miscgeom', 'c', version: '0.0.1', meson_version: '>=1.2.0')

py = import('python').find_installation(pure: false)

# find numpy include directory
numpy_include = run_command(py, '-c', 'import numpy; print(numpy.get_include())', check: true).stdout().strip()

subdir('miscgeom')
