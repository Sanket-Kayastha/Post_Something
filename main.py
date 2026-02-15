from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

ckeditor = CKEditor(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class MyPostForm(FlaskForm):
    title = StringField('Blog Post Title')
    subtitle = StringField('Subtitle')
    author_name = StringField('Your Name')
    blog_url = StringField('Blog Image URL')
    blog_content = CKEditorField('Blog Content')
    submit = SubmitField("Submit Post")

# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    posts = []
    all_data = db.session.execute(db.select(BlogPost))
    post = all_data.scalars().all()
    for p in post:
        posts.append(p)
    
    return render_template("index.html", all_posts=posts)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route("/new-post", methods=["POST","GET"])
def add():
    My_form = MyPostForm()

    if My_form.validate_on_submit():
        blog = BlogPost(
            title = My_form.title.data,
            subtitle= My_form.subtitle.data,
            author = My_form.author_name.data,
            body = My_form.blog_content.data,
            img_url = My_form.blog_url.data,
            date = datetime.now().strftime("%B %d,%Y")
        )
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form=My_form, post="New Post")

# TODO: edit_post() to change an existing blog post
@app.route("/edit-post/<int:post_id>", methods=["POST","GET"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_post = MyPostForm(
        title = post.title,
        subtitle = post.subtitle,
        author_name = post.author,
        blog_url = post.img_url,
        blog_content = post.body
    )
    if edit_post.validate_on_submit():
            post.title=edit_post.title.data
            post.subtitle = edit_post.subtitle.data
            post.author = edit_post.author_name.data
            post.img_url = edit_post.blog_url.data
            post.body = edit_post.blog_content.data
            db.session.commit()
            return redirect(url_for('show_post', post_id=post.id))

    return render_template("make-post.html", form=edit_post, post="Edit Post")

# TODO: delete_post() to remove a blog post from the database
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    blog_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(blog_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
