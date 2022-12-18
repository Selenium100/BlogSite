from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import requests
import json

with open("config.json", "r") as c:
    params = json.load(c)["params"]

db = SQLAlchemy()
app = Flask(__name__)
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


app.run(debug=True)
