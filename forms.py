from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, URL, EqualTo, Email, Length, Regexp
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
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp(r'(?=.*[0-9])', message='Password must contain at least one number.'),
        Regexp(r'(?=.*[!@#$%^&*(),.?":{}|<>])', message='Password must contain at least one special character.')
    ])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


# Form to log in as an existing user
class LogInForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp(r'(?=.*[0-9])', message='Password must contain at least one number.'),
        Regexp(r'(?=.*[!@#$%^&*(),.?":{}|<>])', message='Password must contain at least one special character.')
    ])
    submit = SubmitField("Let Me In")


# The comment form
class CommentForm(FlaskForm):
    comment = StringField("Comment", validators=[DataRequired()])
    submit = SubmitField("Let's discuss this!")

# Form to request a password reset
class ForgotPasswordForm(FlaskForm):
    email = EmailField("Enter your registered email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Link")

# Form to reset the password
class ResetPasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp(r'(?=.*[0-9])', message='Password must contain at least one number.'),
        Regexp(r'(?=.*[!@#$%^&*(),.?":{}|<>])', message='Password must contain at least one special character.')
    ])

    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo('new_password', message="Passwords must match")])
    submit = SubmitField("Reset Password")
