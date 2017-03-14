rem cx_Freeze
;xcopy audio dist\audio /I /Y
xcopy images dist\images /I /Y
xcopy packaging\win32\imageformats dist\imageformats /I /Y

rem ***Output to Console for Debugging
rem \Python27\Scripts\cxfreeze bloom-gui.py --compress --target-dir dist --base-name Console --include-modules PySide.QtNetwork,serial.win32,matplotlib.backends.backend_tkagg --icon=images\puzzlebox.ico

rem ***GUI Mode only for Distribution
\Python27\Scripts\cxfreeze bloom-gui.py --compress --target-dir dist --base-name Win32GUI --include-modules PySide.QtNetwork,serial.win32,matplotlib.backends.backend_tkagg --icon=images\puzzlebox.ico
