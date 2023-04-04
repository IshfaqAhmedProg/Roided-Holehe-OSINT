call jupyter nbconvert app.ipynb --to script  --output RoidedHolehe
call RD /s /q "C:\WorkHolder\python work\RoidedHolehe\dist" 
call RD /s /q "C:\WorkHolder\python work\RoidedHolehe\build" 
call pyinstaller RoidedHolehe.py --collect-all pyfiglet --collect-data grapheme --paths "C:\WorkHolder\python work\RoidedHolehe\.venv\Lib\site-packages"
exit