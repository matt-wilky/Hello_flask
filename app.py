from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Update the SQL Server connection string for Azure Active Directory authentication
connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=time-manager-24.database.windows.net;DATABASE=time-manager-database;Authentication=ActiveDirectoryInteractive;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc:///?odbc_connect={connection_string}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable SQLAlchemy track modifications
db = SQLAlchemy(app)

# Database Model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Event {self.title}>'

@app.route('/')
def splash_page():
    return render_template('splash.html')

@app.route('/calendar')
def calendar():
    events = Event.query.all()  # Fetch all events from the database
    return render_template('calendar.html', events=events)

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')  # Adjust format
        end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')  # Adjust format

        # Create new event object
        new_event = Event(title=title, start_time=start_time, end_time=end_time)

        # Add event to the database
        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for('calendar'))  # Redirect to the 'calendar' endpoint

    return render_template('add_event.html')

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    # Find the event by ID
    event_to_delete = Event.query.get_or_404(event_id)

    # Delete the event from the database
    db.session.delete(event_to_delete)
    db.session.commit()

    return redirect(url_for('calendar'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables based on models
    app.run(debug=False)