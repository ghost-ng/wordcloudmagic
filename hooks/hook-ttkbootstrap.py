# Custom PyInstaller hook for ttkbootstrap to include only necessary themes
from PyInstaller.utils.hooks import collect_data_files

# Collect theme files but exclude any test files
datas = []
for data in collect_data_files('ttkbootstrap'):
    if 'test' not in data[0].lower():
        datas.append(data)

# Only import the standard themes module
hiddenimports = ['ttkbootstrap.themes.standard']