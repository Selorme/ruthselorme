from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, EqualTo
from flask_ckeditor import CKEditorField


# Form to submit a post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired()])
    submit = SubmitField("Send In Your Post!")

# Form to register to leave a comment as a user
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


# Form to log in as an existing user
class LogInForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In")


# The comment form
class CommentForm(FlaskForm):
    comment = StringField("Comment", validators=[DataRequired()])
    submit = SubmitField("Let's discuss this!")

# Form to request a password reset
class ForgotPasswordForm(FlaskForm):
    email = StringField("Enter your registered email", validators=[DataRequired()])
    submit = SubmitField("Send Reset Link")

# Form to reset the password
class ResetPasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    submit = SubmitField("Reset Password")