if not exist v_env\Scripts\activate call create_virtualenv.bat
call v_env\Scripts\activate
call pip install -r requirements.txt
start /WAIT /B "Flask backend" run_DEV.bat