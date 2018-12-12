import sys
from cx_freeze import setup, Executable


base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable('cm_sales.py',base=base,icon = "cashbox.ico"),
    Executable('setup_gui.py',base=base,icon= "Setup.ico"),
    Executable('backoffice_window.py', base=base,icon= "BuildingManagement.ico"),
    Executable('display_secundar.py', base=base,icon= "display.ico")

]
Packages = ["config_parser","config_read","datecs_print",
            "sys","os","time","threading","mysql.connector","uuid","multiprocessing","psutil","logging","webbrowser","threading","platform","base64"]

Include = ["resources","ui","setup","module","ca-cert.pem","client-cert.pem","client-key.pem","mysql.exe","mysql_config.pl","mysqldump.exe","mysqldump.pdb"]

setup(name='OptimPos',
      version='1.0',
      description='Point of Sale',
      options={"build_exe": {"packages": Packages, "include_files": Include}},
      executables=executables, requires=["mysql", 'psutil', 'PyQt4', 'Crypto', 'pyjasper']
      )