# Import necessary libraries
import os
import sqlite3
from flask import Flask, g


# Initialize Flask app
app = Flask(__name__)


# Define the path to the database file
DATABASE = '/tmp/hello.db'


# Define a function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# Define a function to close the database connection when the app context ends
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Define the route for the homepage
@app.route('/')
def hello():
    # Get the database connection
    conn = get_db()

    # Create a cursor to execute SQL commands
    c = conn.cursor()

    # Create the visits table if it doesn't exist
    c.execute("CREATE TABLE IF NOT EXISTS visits (timestamp TEXT)")

    # Insert a new visit into the visits table
    c.execute("INSERT INTO visits VALUES (datetime('now'))")

    # Commit the changes to the database
    conn.commit()

    # Count the total number of visits
    c.execute("SELECT COUNT(*) FROM visits")
    count = c.fetchone()[0]

    # Return a response with the total number of visits
    return 'Hello Awesome World! I have been visited {} times.'.format(count)


# Switch to the non-root user
if __name__ == '__main__':
    # Get the UID and GID of the non-root user
    uid = os.getuid()
    gid = os.getgid()

    # Change the UID and GID of the app process
    os.setuid(uid)
    os.setgid(gid)

    # Run the app
    app.run(debug=True, host='0.0.0.0')
