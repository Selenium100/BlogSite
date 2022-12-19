from datetime import datetime

from flask import Flask, render_template, request, session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import requests
import json

with open("config.json", "r") as c:
    params = json.load(c)["params"]

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = "Your_secret_string"
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL='True',
    MAIL_USERNAME=params["MAIL_USERNAME"],
    MAIL_PASSWORD=params["MAIL_PASSWORD"]
)

mail = Mail(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/theCodingninja"
db.init_app(app)


class Contacts(db.Model):
    ''' sno,name,email,phoneno,message,date'''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phoneno = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)


@app.route('/')
def home():
    posts = Posts.query.filter_by().all()[0:params["no_of_posts"]]
    return render_template("index.html" , posts=posts)


@app.route('/dictionary')
def dictionary_route():
    return render_template("dic.html")


@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/post')
def postroute():
    return render_template("post.html" , post=post)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        '''Fetch entry from contact.html'''
        name = request.form.get("name")
        email = request.form.get("email")
        phoneno = request.form.get("phoneno")
        message = request.form.get("message")

        entry = Contacts(name=name, email=email, phoneno=phoneno, message=message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from Blog', sender=email, recipients=[params["MAIL_USERNAME"]],
                          body=message + "\n" + phoneno)

        '''Add entry in database'''


    return render_template("contact.html")


@app.route('/post/<string:post_slug>', methods=['GET'])
def post(post_slug):
    post = Posts.query.filter_by(slug = post_slug).first()
    return render_template("post.html" ,params =params, post=post)


@app.route('/login' , methods=['GET','POST'])
def login():

    if ('user' in session and session["user"] == params['admin_user']):
        posts = Posts.query.all()
        return render_template("dashboard.html" , params =params, posts=posts)


    if request.method == "POST":
        username = request.form.get('uname');
        password = request.form.get('pass');

        if (username == params['admin_user'] and password == params['admin_password']):
            session["user"] = username
            posts = Posts.query.all()
            return render_template("dashboard.html" , params=params, posts=posts)



    return render_template("login.html", params=params)


@app.route('/edit/<string:sno>' , methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method =='POST'):
            name = request.form.get('name')
            title = request.form.get('title')
            content = request.form.get('content')
            slug = request.form.get('slug')
            date = datetime.now()

            if sno == "0":
                post = Posts(name=name,title=title,content=content,slug=slug,date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.name=name
                post.title=title
                post.content=content
                post.slug=slug
                post.date=date
                db.session.commit()
                return redirect("/edit/"+sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',sno=sno,params=params,post=post)









app.run(debug=True)
