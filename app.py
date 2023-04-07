from flask import Flask, render_template, flash, request, redirect, url_for, send_file
from datetime import datetime, timedelta, time
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, PersonelForm, PasswordForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from sqlalchemy import create_engine
import pandas as pd

our_users=""
#Create a flask instance
app = Flask(__name__)
ckeditor = CKEditor(app)

# Add database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personel.db'
#app.config['SQLALCHEMY_DATABASE_URI'] ="postgresql://postgres:postgres@localhost:5432/personel"
app.config['SQLALCHEMY_DATABASE_URI'] ="postgresql://postgres:UUkc32LrdZTDntP5K0ZP@containers-us-west-112.railway.app: 6412/railway"
# Secret key
app.config['SECRET_KEY'] = "aH1Crt67x01askR1U"

UPLOAD_FOLDER='static/images/'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

# Initialize the db
db = SQLAlchemy(app)
migrate = Migrate(app,db)

#Flask Login Stuff
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return Personel.query.get(int(user_id))

#Pass stuff to Navbar
@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

#Create an admin page
@app.route('/admin')
@login_required
def admin():
    id=current_user.id
    if id==1:
        return render_template('admin.html')
    else:
        flash('Özür dileriz, Admin sayfasına sadece Admin erişebilir')
        return redirect(url_for('dashboard'))

#Create search function
@app.route('/search', methods=["POST"])
def search():
    form=SearchForm()
    posts=Posts.query
    if form.validate_on_submit():
        #Get data from submitted form
        post.searched=form.searched.data
        #Query the db
        posts=posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts=posts.order_by(Posts.title).all()
        return render_template('search.html', form=form, searched=post.searched, posts=posts)

#Create Login Page
@app.route('/login', methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Personel.query.filter_by(username=form.username.data).first()
        if user:
            #Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Başarıyla Login Oldunuz!')
                return redirect(url_for('dashboard'))
            else:
                flash('Yalnış Şifre, tekrar deneyin!')
        else:
            flash('Bu kullanıcı yoktur, kayıt olun!')

    return render_template('login.html', form=form)

#Create logout function
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('Logout oldunuz, Ziyaretiniz için teşekkürler!')
    return redirect(url_for('login'))

#Create Dashboard Page
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    form = PersonelForm()
    id=current_user.id
    name_to_update = Personel.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        #name_to_update.profile_pic = request.files['profile_pic']

        #Check for profile pic
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']

            #Grab image name
            pic_filename=secure_filename(name_to_update.profile_pic.filename)
            # Set UUID - Kişilerin fotoğraflarına aynı adı vermesi durumuna önlem olarak dosya adına ID atamak
            pic_name=str(uuid.uuid1()) + "_" + pic_filename

            # Save the file in the images
            saver=request.files['profile_pic']

            #Change pic to a string to save it to the db
            name_to_update.profile_pic=pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash("Kullanıcı verileri değiştirildi!")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
            except:
                flash("Oops bir problem var, değişiklik gerçekleşmedi, tekrar deneyin!")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
        else:
            db.session.commit()
            flash("Kullanıcı verileri değiştirildi!")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
    return render_template('dashboard.html')


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete=Posts.query.get_or_404(id)
    id=current_user.id
    if id==post_to_delete.poster.id or id==1:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            #Return a message
            flash('Blog başarıyla silindi!')

            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
        except:
            #return an error message
            flash('Ooops bir problem var, Blog silinemedi!')

    else:
        flash("Bu blog'u silme yetkiniz yoktur!")

        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

@app.route('/posts')
def posts():
    #Grab all the posts from the database
    posts=Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post=Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    post=Posts.query.get_or_404(id)
    form=PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        #post.author=form.author.data
        post.slug=form.slug.data
        post.content=form.content.data
        #Update db
        db.session.add(post)
        db.session.commit()
        flash('Blog başarıyla düzeltildi!')
        return redirect(url_for('post', id=post.id))

    if current_user.id==post.poster_id or current_user.id==1:
        form.title.data=post.title
        #form.author.data=post.author
        form.slug.data=post.slug
        form.content.data=post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("Blog'u değiştirmek için yetkili değilsiniz")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

#Add posts page
@app.route('/add-post',methods=['GET','POST'])
def add_post():
    form=PostForm()
    if form.validate_on_submit():
        poster=current_user.id
        post=Posts(title=form.title.data, content=form.content.data,poster_id=poster, slug=form.slug.data)
        #Clear the form
        form.title.data=''
        form.content.data=''
        #form.author.data=''
        form.slug.data=''
        #Add post to the db
        db.session.add(post)
        db.session.commit()
        #return a message
        flash("İçeriğiniz veritabanına kaydedildi!")
    #Re-direct to the webpage
    return render_template("add_post.html",form=form)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id==current_user.id:

        global our_users
        user_to_delete=Personel.query.get_or_404(id)
        name = None
        form = PersonelForm()
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("Kullanıcı başarıyla silindi!")
            our_users = Personel.query.order_by(Personel.date_added)
            return render_template('add_user.html', form=form, name=name, our_users=our_users)
        except:
            flash("Oops kullanıcı silinemedi, bir daha deneyin!")
            return render_template('add_user.html', form=form, name=name, our_users=our_users)
    else:
        flash("Özür dileriz, ancak bu kullanıcıyı silemezsiniz!")
        return redirect(url_for('dashboard'))
@app.route('/user/add', methods=['GET','POST'])
def add_user():
    ax=0
    name=None
    form=PersonelForm()
    if form.validate_on_submit():
        user=Personel.query.filter_by(email=form.email.data).first()
        if user is not None:
            ax=12
        if user is None:
            #hash the password!
            hashed_pw=generate_password_hash(form.password_hash.data)
            user=Personel(username=form.username.data, name=form.name.data, email=form.email.data, favourite_color=form.favourite_color.data, about_author=form.about_author.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name=form.name.data
        form.name.data=''
        form.username.data=''
        form.email.data=''
        form.favourite_color.data=''
        form.about_author.data = ''
        form.password_hash.data=''

        if ax==12 :
            flash('Veritabanımızda bu email adresine sahip kullanıcı bulunmaktadır!')
        else:
            flash('Kullanıcı başarıyla veritabanımıza kaydedilmiştir!')

    our_users=Personel.query.order_by(Personel.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

#Update a record in the database
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
    form=PersonelForm()
    name_to_update=Personel.query.get_or_404(id)
    if request.method =='POST':
        name_to_update.name=request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author=request.form['about_author']
        try:
            db.session.commit()
            flash("Kullanıcı verileri değiştirildi!")
            return render_template("update.html", form=form, name_to_update=name_to_update,id=id)
        except:
            flash("Oops bir problem var, değişiklik gerçekleşmedi, tekrar deneyin!")
            return render_template("update.html", form=form, name_to_update=name_to_update,id=id)
    else :
        return render_template("update.html", form=form, name_to_update=name_to_update,id=id)

@app.route('/')
def index():
    return render_template('greeting.html')

@app.route('/rapor')
def rapor():
    return render_template('download.html')

#@app.route('/user/<name>')
#def user(name):
@app.route('/download')
def yukle():
    #'postgresql://postgres:UUkc32LrdZTDntP5K0ZP@containers-us-west-112.railway.app: 6412/railway'
    engine = create_engine('postgresql://postgres:yETibMisdEf9aO7l8cCL@containers-us-west-112.railway.app:6412/railway')
    df = pd.read_sql_query('SELECT * from personel', engine)
    df1 = pd.read_sql_query('SELECT * from posts', engine)
    engine.dispose()

    with pd.ExcelWriter('personel_verisi.xlsx') as writer:
        df.to_excel(writer, sheet_name='Pers', index=False)
        df1.to_excel(writer, sheet_name='Posts', index=False)
    #return render_template('hello.html', name=name)
    path='personel_verisi.xlsx'
    return send_file(path,as_attachment=True)

# Create Password Test Page
@app.route('/user/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password=None
    pw_to_check=None
    passed=None
    form = PasswordForm()

    # validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        #Clear the form
        form.email.data = ""
        form.password_hash.data = ""
        #lookup email address from the database
        pw_to_check=Personel.query.filter_by(email=email).first()
        #Check hashed password
        if pw_to_check is None:
            flash('Veritabanında bu e-postaya sahip kullanıcı yoktur, önce kullanıcı ekleme menüsünden kullanıcıyı ekleyiniz!')
        else:
            passed=check_password_hash(pw_to_check.password_hash, password)

    return render_template("passwd_test.html", email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)

#Create a blog post model
class Posts(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(255))
    content=db.Column(db.Text)
    #author=db.Column(db.String(255))
    date_posted=db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours=3))
    slug=db.Column(db.String(255))
    #Foreign key to link users (refer to the primary key of the user)
    poster_id=db.Column(db.Integer, db.ForeignKey('personel.id'))

# Create Model
class Personel(db.Model, UserMixin):
    __tablename__='personel'
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favourite_color=db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True) #Postgres'e geçmek için Text character sayısını (500) kaldırdım!
    date_added = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours=3))
    profile_pic=db.Column(db.String(), nullable=True)
    #Do some password stuff!
    password_hash=db.Column(db.String(128))
    #User can have many posts
    posts=db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError('Şifre okunabilir değil!')
    @password.setter
    def password(self, password):
        self.password_hash=generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a String
    def __repr__(self):
        return '<Personel %r>' % self.name

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))

