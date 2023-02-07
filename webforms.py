from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

#Create a search form
class SearchForm(FlaskForm):
    searched=StringField('Aranan', validators=[DataRequired()])
    submit=SubmitField('Yolla')

#Create login form
class LoginForm(FlaskForm):
    username=StringField('Kullanıcı Adı', validators=[DataRequired()])
    password=PasswordField('Şifre', validators=[DataRequired()])
    submit=SubmitField('Yolla')

#Create a posts form
class PostForm(FlaskForm):
    title=StringField("Başlık",validators=[DataRequired()])
    #content=StringField("İçerik",validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('İçerik', validators=[DataRequired()])
    #author=StringField("Yazar")
    slug=StringField("Slug",validators=[DataRequired()])
    submit=SubmitField("Yolla")

# Create a Form class for db
class PersonelForm(FlaskForm):
    name = StringField("Adı, Soyadı", validators=[DataRequired()])
    username = StringField("Kullanıcı Adı", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favourite_color=StringField("En sevdiği renk")
    about_author = TextAreaField("Yazar hakkında")
    password_hash = PasswordField("Şifre", validators=[DataRequired(), EqualTo("password_hash2", message='Şifreler aynı olmalı!')])
    password_hash2 = PasswordField("Şifreyi tekrarla", validators=[DataRequired()])
    profile_pic=FileField("Profil Resmi")
    submit = SubmitField("Yolla!")

# Create a  Password Test class
class PasswordForm(FlaskForm):
    email = StringField("E-postanız nedir?", validators=[DataRequired()])
    password_hash = PasswordField("Şifreniz nedir?", validators=[DataRequired()])
    submit = SubmitField("Yolla!")

