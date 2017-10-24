 # #!/usr/bin/env python3

from flask import Flask, render_template, url_for,flash,redirect,session,logging,request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt

app = Flask(__name__)
#config MySQL
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= 'Virtu123456'
app.config['MYSQL_DB']= 'flaskapp'
app.config['MYSQL_CURSORCLASS']= 'DictCursor'
#init MYSQL_DB
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles= Articles())

@app.route('/dashboard')
def dashboard():
    if session.logged_in: #user not logged in
        return render_template('dashboard.html')
    flash('You have to log in first',danger)
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if not session.logged_in : #user not logged in
        flash('You are already logged out',danger)
        return redirect(url_for('login'))
    session.clear()
    flash('You are now logged out',success)
    return redirect(url_for('login'))

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

class RegisterForm(Form):
    name = StringField('Name',[validators.Length(min=1,max=50)])
    username = StringField('Username',[validators.Length(min=4,max=25)])
    email = StringField('Email', [validators.Length(min=6,max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=4,max=13),
        validators.EqualTo('confirm',message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    username = StringField('Username',[validators.Length(min=4,max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=4,max=13),
    ])


@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create cursor
        cur = mysql.connection.cursor()
        #
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name,email,username,password))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        flash('you are now registered and can log in','success')

        return redirect(url_for('login'))
    return render_template('register.html',form=form)

#user logging
@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_candidate = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #if any user found
            #get the stored hash
            data = cur.fetchone() #fetch the first one accepted
            password = data['password']  #get the value from the key('password') thanks to DictCursor

            #compare the passwords
            if sha256_crypt.verify(password_candidate,password):
                session['logged_in'] = True
                session['username'] = username
                app.logger.info('Password matched')
                flash('You are now logged in','success')
                return redirect(url_for('dashboard'))
            else:
                app.logger.info([password_candidate,password])
                app.logger.info('password does not match')
                flash('Username/password are not correct','danger')
                return redirect(url_for('login'))
        else:
            app.logger.info('Username is not found')
            flash('Username/password are not correct','danger')
            return redirect(url_for('login'))

    return render_template('login.html',form=form)


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
