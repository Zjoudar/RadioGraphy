from email.mime import image
import os
import uuid
import flask
import urllib
from PIL import Image
from tensorflow.keras.models import load_model
from flask import Flask , render_template  , request , send_file
from tensorflow.keras.preprocessing.image import load_img , img_to_array
import numpy as np


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(BASE_DIR , 'finnalproject_Apps.h5'))
#model = load_model(r'C:\Users\user\Downloads\Dataset\Python-Flask-Authentication-Tutorial-main\finnalproject_Apps.h5')
ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png' , 'jfif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT


classes = ['Degenerative Infectious Disease','Encapsulated Lesions','Higher Density','Lower Density','Mediastinal Alterations',
          'Normal Anatomy','Obstructive Pulmonary Diseases','Pneumonia','Tuberculosis', 'Cavity', 'Fillings', 'Periodontitis', 'bone loss', 'decay', 'fractured', 'glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']

def predict(filename , model):
    img = load_img(filename , target_size = (224 , 224))
    img = img_to_array(img)
    img = img.reshape(1 , 224 ,224 ,3)

    img = img.astype('float32')
    img = img/255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(len(result[0])):
        dict_result[round(result[0][i], 4)] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]

    class_result = []
    for i in range(1):
        class_result.append(dict_result[round(prob[i], 4)]) 

    return class_result





from flask import Flask, request,render_template, redirect,session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

from flask import Flask, send_from_directory, request, redirect, session, jsonify


@app.route('/')
def index():
    return render_template('edit.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/success')
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/success')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')
  
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def aout():
    return render_template('About.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/working')
def working():
    return render_template('working.html')

@app.route('/questions')
def questions():
    return render_template('FAQ.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/term')
def term():
    return render_template('term.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/success' , methods = ['GET' , 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd() , 'static/images')
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try :
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img , filename)
                output = open(img_path , "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result  = predict(img_path , model)

                predictions = {
                    class_result[0]
                       
                }

            except Exception as e : 
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
            else:
                return render_template('index0.html' , error = error) 

            
        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img , file.filename))
                img_path = os.path.join(target_img , file.filename)
                img = file.filename

                class_result  = predict(img_path , model)

                predictions = {
                    class_result[0],
                }

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
            else:
                return render_template('index0.html' , error = error)

    else:
        return render_template('index0.html')


@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)








