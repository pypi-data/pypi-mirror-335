from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote_plus
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Secure your secret key with an environment variable

# MongoDB Configuration with properly escaped credentials
username = quote_plus("betrand1999") # add username and pst
password = quote_plus("Cameroon@10K")
client = MongoClient(f"mongodb+srv://{username}:{password}@cluster.7plpy.mongodb.net/my-database?retryWrites=true&w=majority")
db = client['my-database']  # Specify your database as shown in the MongoDB Atlas interface
users_collection = db['inventory_collection']  # Collection for storing user data

@app.route('/')
def home():
    video_url = None
    if 'username' in session:
        video_url = None  # Removed S3 video URL
    return render_template('index.html', video_url=video_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the user already exists
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('register'))
        
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        user_data = {'username': username, 'password': hashed_password}
        users_collection.insert_one(user_data)
        flash('Successfully registered! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact-form', methods=['GET', 'POST'])
def contact_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        category = request.form['category']
        appointment = request.form.get('appointment')
        message = request.form['message']
        
        # Store the contact data in the database
        contact_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'category': category,
            'appointment': appointment,
            'message': message
        }
        db.contacts.insert_one(contact_data)

        # Remove the email or SMS notification logic here
        # Simply flash a success message
        flash('Your message has been submitted successfully!', 'success')

        return redirect(url_for('home'))
    return render_template('contact-form.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
