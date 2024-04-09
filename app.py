from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, DateTime
from flask import jsonify
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.secret_key = 'software_engineering'

# Connection String + database configuration info
connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=time-manager-24.database.windows.net;DATABASE=time-manager-database;UID=CloudSAe3d0c2d0;PWD=Suarez89!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=2000;'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc:///?odbc_connect={connection_string}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Classes
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Create database column
    username = db.Column(db.String(100), index=True, unique=True)
    password_hash = db.Column(db.String(1500), nullable=False)

    # Define the relationship with cascade option
    events = db.relationship('New_Event', backref='user', cascade='all, delete-orphan')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)  # Hash the password

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class New_Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Create database entry
    title = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    color = db.Column(db.String(7), nullable=False, default='#000000')  # Add color attribute with default value
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Connect to other class

    def __repr__(self):
        return f'<New_Event {self.title}>'


# Add Splash Route
@app.route('/')
def splash_page():
    return render_template('splash.html')

# Add Calendar Route
@app.route('/calendar')
def calendar():
    user_id = session.get('user_id')

    if user_id:
        # Pull events from the database for the current user
        all_events = New_Event.query.filter_by(user_id=user_id).all()
        
        # Find today's events for the sidebar
        today = datetime.now().date()
        today_events = [event for event in all_events if event.start_time.date() == today]
        
        # Return Calendar and Sidebar View
        return render_template('calendar.html', events=all_events, today_events=today_events)
    else:
        return "Unauthorized", 401

# Add_Event Route

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        # Ensure user is logged in
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirect to login page or handle appropriately

        # Extract form data
        title = request.form['title']
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')
        color = request.form['color']
        user_id = session['user_id']  # Get user ID from session

        # Save the event to the database
        new_event = New_Event(title=title, start_time=start_time, end_time=end_time, color=color,user_id=user_id)
        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for('calendar'))

    return render_template('add_event.html')


# Login Route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()  # Looks to find user id
    if user and user.check_password(password):  # If found go to calendar view
        session['user_id'] = user.id
        return redirect(url_for('calendar'))
    else:
        return "Invalid username or password", 401  # Else return error message

# Logout Route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)  # Remove id from session
    return redirect(url_for('splash_page'))  # Go to login page

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print('Here')
        print(request.form)
        username = request.form.get('username')  # Get Username
        password = request.form.get('password')  # Get Password
        # If statement
        if not username or not password:
            return "Username and password are required", 400  # Initial stages of error management

        new_user = User(username=username)  # Create new user
        print(f"The new user: {new_user}")
        new_user.set_password(password)  # Set the password
        try:
            db.session.add(new_user)  # Add user to database
            db.session.commit()
            return redirect(url_for('splash_page'))  # Redirect to splash page
        except Exception as e:
            return f"An error occurred: {e}", 500  # Error management
    return render_template('register.html')

# Edit Event Route
@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = New_Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        event.title = request.form['title']
        event.start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')
        event.end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')
        event.color = request.form['color']
        db.session.commit()
        return redirect(url_for('calendar'))
    
    return render_template('edit_event.html', event=event)
    
# Delete Event Route
@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    # Fetch the event from the database
    event = New_Event.query.get_or_404(event_id)
    # Delete the event
    db.session.delete(event)
    db.session.commit()

    # Redirect to calendar page
    return redirect(url_for('calendar'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Update database
    app.run(host='0.0.0.0', port=443, debug=True)