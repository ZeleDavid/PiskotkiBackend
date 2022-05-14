if [ ! -f v_env\Scripts\activate ]
then
    pip install --user virtualenv
    python -m virtualenv v_env

bash v_env\Scripts\activate

pip install -r requirements.txt

#bash /WAIT /B "Flask backend"
sleep 2m

FLASK_APP=server.py
FLASK_ENV=development
flask run

fi
