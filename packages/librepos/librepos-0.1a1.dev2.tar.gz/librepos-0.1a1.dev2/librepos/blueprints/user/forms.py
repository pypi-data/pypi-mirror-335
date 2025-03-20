from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email

kw = {"placeholder": " "}


class UserForm(FlaskForm):
    def __init__(self, **kwargs):
        super(UserForm, self).__init__(**kwargs)

        from librepos.models import Role

        active_roles = Role.query.filter_by(is_active=True).all()
        self.role_id.choices = [(r.id, r.name.title()) for r in active_roles]

    role_id = SelectField("Role", coerce=int, render_kw=kw)
    username = StringField("Username", validators=[DataRequired()], render_kw=kw)
    first_name = StringField("First Name", validators=[DataRequired()], render_kw=kw)
    last_name = StringField("Last Name", validators=[DataRequired()], render_kw=kw)
    email = StringField("Email", validators=[DataRequired(), Email()], render_kw=kw)
    phone = StringField("Phone", render_kw=kw)
    hourly_rate = FloatField("Hourly Rate", validators=[DataRequired()], render_kw=kw)
    submit = SubmitField("Submit")


class NewUserForm(FlaskForm):
    # Auth
    role_id = SelectField("Role", coerce=int, render_kw=kw)
    username = StringField("Username", validators=[DataRequired()], render_kw=kw)

    submit = SubmitField("Submit")

    def __init__(self, **kwargs):
        super(NewUserForm, self).__init__(**kwargs)

        from librepos.models import Role

        active_roles = Role.query.filter_by(is_active=True).all()
        self.role_id.choices = [(r.id, r.name.title()) for r in active_roles]


class UserProfileForm(FlaskForm):
    # TODO 2/6/25 : implement the language and timezone selectors

    first_name = StringField("First Name", validators=[DataRequired()], render_kw=kw)
    middle_name = StringField("Middle Name", render_kw=kw)
    last_name = StringField("Last Name", validators=[DataRequired()], render_kw=kw)
    email = EmailField("Email", validators=[DataRequired(), Email()], render_kw=kw)
    phone = StringField("Phone", render_kw=kw)
    gender = SelectField("Gender", coerce=str, render_kw=kw)
    profile_picture = StringField("Profile Picture", render_kw=kw)
    submit = SubmitField("Submit")

    def __init__(self, **kwargs):
        super(UserProfileForm, self).__init__(**kwargs)

        from librepos.models.user_profile import Gender

        self.gender.choices = [(g.value, g.name.title()) for g in Gender]


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()], render_kw=kw)
    password = PasswordField("Password", validators=[DataRequired()], render_kw=kw)
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")
