# Custom PyInstaller hook for matplotlib to reduce size
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Only include the TkAgg backend
hiddenimports = ['matplotlib.backends.backend_tkagg']

# Exclude all other backends and test modules
excludedimports = [
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_qt4agg',
    'matplotlib.backends.backend_gtk3agg',
    'matplotlib.backends.backend_wxagg',
    'matplotlib.backends.backend_pdf',
    'matplotlib.backends.backend_ps',
    'matplotlib.backends.backend_svg',
    'matplotlib.backends.backend_pgf',
    'matplotlib.backends.backend_cairo',
    'matplotlib.backends.backend_macosx',
    'matplotlib.backends.backend_webagg',
    'matplotlib.backends.backend_nbagg',
    'matplotlib.testing',
    'matplotlib.tests',
    'matplotlib.sphinxext',
    'matplotlib.backends.qt_editor',
    'matplotlib.backends.backend_qt5',
    'matplotlib.backends.backend_qt4',
]

# Only collect essential data files
datas = []
for data in collect_data_files('matplotlib'):
    # Skip test data, sample data, and unnecessary backends
    if not any(skip in data[0] for skip in ['tests', 'testing', 'backends/web_backend', 
                                             'mpl-data/sample_data', 'mpl-data/fonts/afm',
                                             'mpl-data/fonts/pdfcorefonts']):
        datas.append(data)