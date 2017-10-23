# FlaskProject
commands need to be run before:
  git config --global user.name ""
  git config --global user.email ""

  git remote add origin https://github.com/SirSaar/FlaskProject

  in new dir:
    install python3 and python3-pip
    pip install virtualenv
    pip install flask
    . bin/activate

to start the flask server:
  export FLASK_APP=app.py
  flask run --host=0.0.0.0
