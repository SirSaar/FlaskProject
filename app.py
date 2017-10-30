 # #!/usr/bin/env python3

from flask import Flask, render_template, url_for,flash,redirect,session,logging,request
# from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
#config MySQL
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= 'Virtu123456'
app.config['MYSQL_DB']= 'flaskapp'
app.config['MYSQL_CURSORCLASS']= 'DictCursor'
#init MYSQL_DB
mysql = MySQL(app)

#check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized, Please login','danger')
            return redirect(url_for('login'))
    return wrapper

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    cur=mysql.connection.cursor()
    result=cur.execute("SELECT * FROM articles")
    articles=cur.fetchall()
    cur.close()
    if result:
        return render_template('articles.html',articles=articles)
    else:
        return render_template('articles.html',articles=None)

@app.route('/profile')
@is_logged_in
def profile():
    cur=mysql.connection.cursor()
    result=cur.execute("SELECT * FROM articles WHERE author = %s",[session['username']])
    articles=cur.fetchall()
    cur.close()
    if result:
        return render_template('profile.html',articles=articles)
    else:
        return render_template('profile.html',articles=None)


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('login'))

@app.route('/article/<int:id>/')
def article(id):
    cur=mysql.connection.cursor()
    result=cur.execute("SELECT * FROM articles WHERE id = {}".format(id))
    article=cur.fetchone()
    cur.close()
    if result:
        return render_template('article.html', article=article)
    else:
        return render_template('article.html', article=None)


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
        validators.Length(min=4,max=13)
    ])

class ArticleForm(Form):
    title = StringField('Name',[validators.Length(min=1,max=200)])
    body = TextAreaField('Body',[validators.Length(min=30)])

@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        #Create cursor
        cur= mysql.connection.cursor()
        cur.execute("INSERT INTO articles(title,body,author) VALUES(%s,%s,%s)",(title,body,session['username']))
        mysql.connection.commit()
        cur.close()
        flash('Article Created','success')

        return redirect(url_for('profile'))
    return render_template('add_article.html',form=form)

@app.route('/edit_article/<int:id>/',methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    cur= mysql.connection.cursor()
    result=cur.execute("SELECT * FROM articles WHERE id = {}".format(id))
    article=cur.fetchone()
    cur.close()
    form = ArticleForm(request.form)
    form.title.data=article['title']
    form.body.data=article['body']
    if request.method == 'POST' and form.validate():
        cur= mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        #Create cursor
        cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%r",(title,body,id))
        mysql.connection.commit()
        cur.close()
        flash('Article Updated','success')
        return redirect(url_for('profile'))
    return render_template('edit_article.html',form=form)

@app.route('/delete_article/<int:id>',methods=['POST'])
@is_logged_in
def delete_article(id):
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM articles WHERE id=%r",[id])
    mysql.connection.commit()
    cur.close()
    flash('Article Deleted','success')
    return redirect(url_for('profile'))

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
        password_candidate = str(form.password.data)

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #if any user found
            #get the stored hash
            data = cur.fetchone() #fetch the first one accepted
            #get the value from the key('password') thanks to DictCursor
            #compare the passwords
            if sha256_crypt.verify(password_candidate,data['password']):   #1st argument is the str password and the second is the hash password
                session['logged_in'] = True
                session['username'] = username
                app.logger.info('Password matched')
                flash('You are now logged in','success')
                return redirect(url_for('profile'))
            else:
                app.logger.info('password does not match')
                flash('Username/password are not correct','danger')
                return redirect(url_for('login'))
            cur.close()
        else:
            app.logger.info('Username is not found')
            flash('Username/password are not correct','danger')
            return redirect(url_for('login'))
        cur.close()

    return render_template('login.html',form=form)


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
