from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime


## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)



##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])

    # Notice body's StringField changed to CKEditorField
    # body = CKEditorField("Blog Content", validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")



# RENDER HOME PAGE USING DB
@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


##RENDER POST USING DB
@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


# CREATING MAKE POST ROUTE:
@app.route("/new-post", methods=["GET", "POST"])
def create_post():
    form = CreatePostForm()
    # If we push the form button "submit post":
    if request.method == "POST":
        # Getting information from our form at make-post.html page:
        title = request.form["title"]
        full_date = datetime.datetime.now()
        date = full_date.strftime("%B %d, %Y")
        body = request.form["body"]
        author = request.form["author"]
        img_url = request.form["img_url"]
        subtitle = request.form["subtitle"]

        # CREATING RECORD INSIDE OUR DATABASE:
        added_post = BlogPost(title=f"{title}", date=f"{date}", author=f"{author}", body=f"{body}",
                              img_url=f"{img_url}", subtitle=f"{subtitle}")
        db.session.add(added_post)
        db.session.commit()

        # TO SHOW ALL POSTS FROM OUR DATABASE:
        # We open our db with all posts and pass them to index.html page
        posts = BlogPost.query.all()
        return render_template("index.html", all_posts=posts)

    return render_template("make-post.html", form=form)


# TO EDIT OUR EXISTING POST:
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    # READING OUR DATABASE AND FINDING THE POST WITH SUCH ID:
    chosen_post = BlogPost.query.filter_by(id=post_id).first()

    # PASSING VALUES OF CURRENT POST INTO OUR FORM WHICH WILL BE PUBLISHED AT MAKE-POST.HTML
    edit_form = CreatePostForm(
        title=chosen_post.title,
        subtitle=chosen_post.subtitle,
        img_url=chosen_post.img_url,
        author=chosen_post.author,
        body=chosen_post.body
    )

    # WHEN THE USER MAKE CHANGES IN POST AND PRESS SUBMIT BUTTON:
    if edit_form.validate_on_submit():
        # we change our post in database using the information from wtf form at make-post.html:
        chosen_post.title = edit_form.title.data
        chosen_post.subtitle = edit_form.subtitle.data
        chosen_post.img_url = edit_form.img_url.data
        chosen_post.author = edit_form.author.data
        chosen_post.body = edit_form.body.data
        db.session.commit()

        # TO SHOW CHANGED POST:
        return redirect(url_for("show_post", post_id=chosen_post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True)


# TO DELETE A POST:
@app.route("/delete-post/<int:post_id>")
def delete_post(post_id):
    # FINDING OUR POST IN DATABASE BY ID:
    post_to_delete = BlogPost.query.filter_by(id=post_id).first()
    # DELETING THIS POST FROM DB:
    db.session.delete(post_to_delete)
    db.session.commit()

    # TO SHOW ALL POSTS FROM OUR DATABASE:
    # We open our db with all posts and pass them to index.html page
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)



@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)