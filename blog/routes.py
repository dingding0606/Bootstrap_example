from flask import render_template, url_for, flash, redirect, request
from blog.models import User, Post
from blog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from blog import app, bcrypt, db
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))  #url_for(name of the function of the route)
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Welcome, {}! You are now able to log in".format(form.username.data), 'success') #f string: python 3.6 and above; 'success' is the Bootstrap class
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')  # args is a dict; using get is better: value of None; if use ['next'] to get the value, it will be value/ERROR.
            flash("Login successful.", 'success')
            print(next_page)
            return redirect(next_page) if next_page else redirect(url_for('home'))
        flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_profile_pic(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_file_name)

    # crop to square and resize the picutre

    i = Image.open(form_picture)

    width, height = i.size
    new_size = min(width, height)

    left = (width - new_size)/2
    top = (height - new_size)/2
    right = (width + new_size)/2
    bottom = (height + new_size)/2

    i = i.crop((left, top, right, bottom))
    i.thumbnail([100, 100])

    # save it to static folder
    i.save(picture_path)

    return picture_file_name


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():

        if form.picture.data:
            file_name = save_profile_pic(form.picture.data)
            current_user.image_file = file_name
            db.session.commit()

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    if current_user.image_file:
        profile_pic = url_for('static', filename='profile_pics/' + current_user.image_file)
    else:
        profile_pic = url_for('static', filename='profile_pics/default.jpg')

    return render_template('account.html', title="Account", profile_pic=profile_pic, form=form)


# TODO
def save_post_pic(form_picture):
    pass

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    picture = url_for('static', filename='post_pics/default2.jpg')
    return render_template("home.html", title="Home", posts=posts, picture=picture)

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.route("/organize/new", methods=['GET', 'POST'])
@login_required
def create_activity():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Successfully submitted to Activity Office', 'success')
        return redirect(url_for('home'))
    return render_template("create_activity.html", title="New Activity", form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="Not Found"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html', title="500"), 500
