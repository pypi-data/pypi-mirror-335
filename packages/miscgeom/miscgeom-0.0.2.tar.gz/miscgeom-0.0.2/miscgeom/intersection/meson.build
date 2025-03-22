# miscgeom/intersection/meson.build

# Define the include directory for _c_core
c_core_include = include_directories('../_c_core')

fast_intersection = py.extension_module(
    'fast_intersection',
    'fast_intersection.c',
    include_directories: [
        numpy_include,
        c_core_include  # Include the _c_core directory
    ],
    install: true,
    subdir: 'miscgeom/intersection'
)

py.install_sources(
    [
        '__init__.py',
        '_intersection.py'
    ],
    subdir: 'miscgeom/intersection'
)

py.install_sources(
    [
        'tests/test_intersection.py'
    ],
    subdir: 'miscgeom/intersection/tests',
    install_tag: 'tests'
)
