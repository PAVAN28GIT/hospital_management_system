from flask import Flask,render_template,request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask import flash

app = Flask(__name__)


# db connection
local_server = True
app.secret_key = 'pavandbms'

# configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@host/database'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:zoro1234@localhost/dbms_mp'
db = SQLAlchemy(app)

# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader  
def load_user(user_id):
    return User.query.get(int(user_id))

# Table 1
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key =True, autoincrement=True)
    uname = db.Column(db.String(50))
    email = db.Column(db.String(50),unique = True)
    password =db.Column(db.String(100))

    def get_id(self):
        return str(self.id)
    def is_active(self):
        return True
    def is_authenticated(self):
        return True
    

# Table 2
class Patient(db.Model):
    __tablename__ = 'patient'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pemail = db.Column(db.String(20), db.ForeignKey('user.email'), nullable=False)
    dname = db.Column(db.String(50))
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    user = db.relationship('User', foreign_keys=[pemail])

    def get_id(self):
        return str(self.id)
    def is_active(self):
        return True
    def is_authenticated(self):
        return True



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login',  methods=['POST','GET'])
def login():
    if request.method == "POST" :
        email = request.form.get('email')
        password = request.form.get('password')

        cur_user = User.query.filter_by(email=email).first()
        if cur_user and check_password_hash(cur_user.password , password):
            login_user(cur_user)    
            return render_template('index.html',username = cur_user.uname)
        else:
            return render_template('login.html')
    return render_template('login.html')

@app.route("/register", methods=['POST','GET'])
def register():
    if request.method == "POST" :
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        epass=generate_password_hash(password)
        
        user = User.query.filter_by(email=email).first()
        if user:
            print("user already exits")
            return render_template('login.html')
        # Creating a new user using SQLAlchemy ORM
        new_user = User(uname=name, email=email, password=epass)

        # Adding the user to the database session and committing the changes
        db.session.add(new_user)
        db.session.commit()

        return render_template('login.html')

    return render_template('register.html')



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/doctor")
def doctor():
    return render_template('doctors.html')


@app.route("/submit_appointment", methods=['POST', 'GET'])
def submit_appointment():
    if request.method == "POST" :
        email = request.form.get('email')
        doctor = request.form.get('doctor')
        date = request.form.get('date')
        time = request.form.get('time')
        user = User.query.filter_by(email=email).first()
        
        # Creating a new user using SQLAlchemy ORM
        new_user = Patient(pemail=email, dname=doctor, date=date,time=time)
        # Adding the user to the database session and committing the changes
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('list_appointments')) # Redirect to '/appointments' after form submission
    if current_user.is_authenticated:
        print("Hello")
        return render_template('appointments.html')
    else:
        return render_template('login.html')


@app.route('/list_appointments')
@login_required
def list_appointments():
    if current_user.is_authenticated:
        appointments_data = Patient.query.filter_by(pemail=current_user.email).all()
        return render_template('appointments.html', appointments=appointments_data)
    else:
        flash('You need to log in first.', 'info')
        return redirect(url_for('login'))


@app.route('/edit/<int:pid>', methods=['GET', 'POST'])
def edit_appointment(pid):
    appointment = Patient.query.get(pid)
    if request.method == 'POST':
        # Update the appointment details based on the form data
        appointment.dname = request.form['doctor']
        appointment.date = request.form['date']
        appointment.time = request.form['time']
        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('list_appointments'))
    return render_template('edit_appointment.html', appointment=appointment)


@app.route('/delete/<int:pid>', methods=['GET', 'POST'])
def delete_appointment(pid):
    appointment = Patient.query.get(pid)
    if request.method == 'POST':
        # Delete the appointment from the database
        db.session.delete(appointment)
        db.session.commit()
        return redirect(url_for('list_appointments'))
    return render_template('delete_appointment.html', appointment=appointment)    

if __name__ == '__main__':
    app.run(debug=True)