from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
import math

# from flask_mail import Mail
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = "super-secret-key"

# Set the database URI based on the environment
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


# Model for contact form entries
class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(1000), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    msg = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(20), nullable=False)


# Model for post-entries
class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(31), nullable=False)
    sub_heading = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(12), nullable=False)


@app.route("/")
def home():
    posts = Post.query.filter_by().all()
    post_no = int(params['post_no'])
    posts = posts[0:post_no]
    # last = math.ceil(len(posts) / int(params['post_number']))
    # page = request.args.get('page')
    # if str(page).isnumeric():
    #     page = 1
    # posts = posts[
    # page * int(params['post_number']):page * int(params['post_number']) + page * int(params['post_number'])]
    # if page == '1':
    #     prev = '#'
    #     next1 = "/?page=" + str(page + 1)
    # elif page == last:
    #     prev = "/?page=" + str(page - 1)
    #     next1 = '#'
    # else:
    #     prev = "/?page=" + str(page - 1)
    #     next1 = "/?page=" + str(page + 1)

    return render_template("home.html", params=params, posts=posts)  #prev=prev, next=next1


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Post.query.filter_by().all()
        return render_template("dashboard.html", params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('upass')

        if username == params['admin_user'] and password == params['admin_pass']:
            session['user'] = username
            posts = Post.query.filter_by().all()
            return render_template("dashboard.html", params=params, posts=posts)

    return render_template("login.html", params=params)


@app.route("/post/")
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug=None):
    if post_slug:
        post_item = Post.query.filter_by(slug=post_slug).first()
        if post_item:
            return render_template("post.html", params=params, post=post_item)
        else:
            return "Post not found!", 404
    return "No post specified!", 400


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit_route(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            date = datetime.now()

            if sno == '0':
                post = Post(title=title, slug=slug, sub_heading=tagline, content=content, date=date)
                db.session.add(post)
                db.session.commit()
                return redirect("/dashboard")
            else:
                post = Post.query.filter_by(sno=sno).first()
                if post:
                    post.title = title
                    post.slug = slug
                    post.subheading = tagline
                    post.content = content
                    post.date = date
                    db.session.commit()
                    return redirect("/dashboard/" + sno)
                else:
                    return "post not found error", 404

        post = Post.query.filter_by(sno=sno).first()
        if post or sno == '0':
            return render_template("edit.html", params=params, post=post)
        else:
            return "page not found error", 404


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        date = datetime.now()

        # Create new entry in the database
        entry = Contact(name=name, email=email, number=phone, msg=message, date=date)
        db.session.add(entry)
        db.session.commit()

    return render_template("contact.html")


@app.route("/abou")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)

# Flask-Mail configuration
# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT=587,
#     MAIL_USE_TLS=True,
#     MAIL_USERNAME=params['gmail_username'],
#     MAIL_PASSWORD=params['gmail_password']
# )
# mail = Mail(app)
#
# # Sending the email
# mssg = Message(f'New Message from {name}',
# sender=email,
# recipients=[params['gmail_username']], body=f"Message: {message}\nPhone: {phone}")
# mail.send(mssg)
