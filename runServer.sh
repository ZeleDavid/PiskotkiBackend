if [ ! -f v_env\Scripts\activate ]
then
    pip install --user virtualenv
    python -m virtualenv v_env

sleep 1m

bash v_env\Scripts\activate

pip install -r requirements.txt

sleep 1m

set FLASK_APP=server.py
set FLASK_ENV=development
flask run

fi
