from flask import Flask, render_template, redirect, url_for, request, flash, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import uuid  # For generating unique IDs

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session and flash messages

# Database configuration for MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',      # Replace with your MySQL username
    'password': '123456',  # Replace with your MySQL password
    'database': 'loan_approval_data'
}

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            try:
                # Connect to MySQL and insert user credentials
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255))")
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                connection.commit()
                flash("Registration successful! Please log in.")
                return redirect(url_for('login'))
            except Error as e:
                flash("Username already exists. Please try a different one.")
            finally:
                if cursor: cursor.close()
                if connection: connection.close()
        else:
            flash("Please enter both username and password to register.")
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # Connect to MySQL and fetch stored password hash
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            # Check if user exists and password is correct
            if user and check_password_hash(user[0], password):
                session['username'] = username
                flash("Login successful!")
                return redirect(url_for('predict'))
            else:
                flash("Invalid username or password. Please try again.")
        
        except Error as e:
            flash("Error connecting to the database.")
        
        finally:
            if cursor: cursor.close()
            if connection: connection.close()
    
    return render_template('login.html')

# Predict route
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))
    
    unique_loan_id = str(uuid.uuid4())  # Generate a unique loan ID
    
    if request.method == 'POST':
        # Collect form data
        gender = request.form.get('gender')
        married = request.form.get('married')
        dependents = request.form.get('dependents')
        education = request.form.get('education')
        self_employed = request.form.get('self_employed')
        applicant_income = request.form.get('applicant_income')
        coapplicant_income = request.form.get('coapplicant_income')
        loan_amount = request.form.get('loan_amount')
        loan_amount_term = request.form.get('loan_amount_term')
        credit_history = request.form.get('credit_history')
        property_area = request.form.get('property_area')

        # Simple eligibility check
        eligibility = "Eligible" if int(applicant_income) > 30000 and int(loan_amount) < 200000 else "Not Eligible"
        
        # Render result page with eligibility outcome
        return render_template('result.html', result=eligibility)
    
    # Pass the unique loan ID to the predict page
    return render_template('predict.html', loan_id=unique_loan_id)

# Result route
@app.route('/result')
def result():
    result = request.args.get('result', 'Unknown')
    return render_template('result.html', result=result)

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
