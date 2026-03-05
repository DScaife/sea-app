import re
from datetime import date
from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, DateField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError


ALLOWED_ASSET_STATUSES = ["Pending Approval", "Active", "Rejected", "Inactive"]


def validate_password_strength(form, field):
    password = field.data or ""
    if len(password) < 10:
        raise ValidationError("Password must be at least 10 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must include at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must include at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must include at least one number.")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValidationError("Password must include at least one special character.")


def validate_not_future_date(form, field):
    if field.data and field.data > date.today():
        raise ValidationError("Purchase date cannot be in the future.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField(
        "Password", validators=[DataRequired(), validate_password_strength]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Register")


class AssetForm(FlaskForm):
    name = StringField("Asset Name", validators=[DataRequired(), Length(min=2, max=100)])
    category = StringField("Category", validators=[DataRequired(), Length(min=2, max=50)])
    purchase_date = DateField(
        "Purchase Date",
        format="%Y-%m-%d",
        validators=[DataRequired(), validate_not_future_date],
    )
    status = SelectField(
        "Status",
        choices=[(status, status) for status in ALLOWED_ASSET_STATUSES],
        validate_choice=False,
    )
    submit = SubmitField("Save")
