from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'software_engineering'

# Update the SQL Server connection string for Azure SQL Server
connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=time-manager-24.database.windows.net;DATABASE=time-manager-database;UID=CloudSAe3d0c2d0;PWD=Suarez89!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=120;'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc:///?odbc_connect={connection_string}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True)
    password_hash = db.Column(db.String(1500), nullable=False)  # Ensure password_hash is not nullable

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)  # Hash the password

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class New_Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<New_Event {self.title}>'

@app.route('/')
def splash_page():
    return render_template('splash.html')

@app.route('/calendar')
def calendar():
    user_id = session.get('user_id')
    if user_id:
        new_events = New_Event.query.filter_by(user_id=user_id).all()
        return render_template('calendar.html', events=new_events)
    else:
        return "Unauthorized", 401

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')

        # Create new event associated with the current user
        new_event = New_Event(title=title, start_time=start_time, end_time=end_time, user_id=session.get('user_id'))
        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for('calendar'))

    return render_template('add_event.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        return redirect(url_for('calendar'))
    else:
        return "Invalid username or password", 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('splash_page'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validate input if necessary
        new_user = User(username=username)
        new_user.set_password(password)  # Set the password using set_password method
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('splash_page'))  # Redirect to the calendar after registering
        except Exception as e:
            return f"An error occurred: {e}", 500  # Return an error message and HTTP status code
    return render_template('register.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables based on models
    app.run(debug=True)