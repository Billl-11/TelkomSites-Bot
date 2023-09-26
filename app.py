from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import mysql.connector
import requests
import os
import random
import string
import datetime

app = Flask(__name__)

app.secret_key = os.urandom(24)

load_dotenv()


# MySQL database configuration (deploy)
database_host = os.environ.get("DATABASE_HOST")
database_user = os.environ.get("DATABASE_USER")
database_password = os.environ.get("DATABASE_PASSWORD")
database_name = os.environ.get("DATABASE_NAME")

# # MySQL database deploy
db_config = {
    'host': database_host,      # Replace with your database host
    'user': database_user,       # Replace with your database username
    'password': database_password,  # Replace with your database password
    'database': database_name   # Replace with your database name
}

# Function to connect to the MySQL database
def connect_to_database():
    return mysql.connector.connect(**db_config)

query_insert_messages = "INSERT INTO messages (user_msg, bot_msg, timestamp_user, timestamp_bot, user_id, topic_id, message_id) VALUES (%s,%s,%s,%s,%s,%s,%s)"

def generate_random_topic_id(length=8):
    characters = string.ascii_letters + string.digits
    random_id = ''.join(random.choice(characters) for _ in range(length))
    return random_id  

# function to query to topic_per_users
def count_msg_id(topic_id):

    connection = connect_to_database()
    cursor = connection.cursor()

    query_1 = """
    SELECT COUNT(DISTINCT message_id) AS message_count
    FROM messages
    WHERE topic_id = %s;
    """
    cursor.execute(query_1, (topic_id,))
    result = cursor.fetchone()

    count_msg = result[0]

    cursor.close()
    connection.close()

    return count_msg

def input_title(count_msg, user_id):

    connection = connect_to_database()
    cursor = connection.cursor(buffered=True)

    if count_msg == 1:
        query_2 = """
        SELECT user_msg
        FROM messages
        WHERE topic_id = %s
        """
        cursor.execute(query_2, (topic_id,))
        result = cursor.fetchone()
        title_topic = result[0][:190]

        query_insert_topic = "INSERT INTO topic_per_user (user_id, topic_id, title) VALUES (%s, %s, %s)"
        values = (user_id, topic_id, title_topic)
        cursor.execute(query_insert_topic, values)
        connection.commit()

    elif count_msg == 2:
        query_2 = """
        SELECT user_msg
        FROM messages
        WHERE topic_id = %s
        ORDER BY timestamp_user ASC
        LIMIT 2
        """
        cursor.execute(query_2, (topic_id,))
        results = cursor.fetchall()

        title_topic = " - ".join(result[0] for result in results)[:190]
        
        query_update_title = """
        UPDATE topic_per_user
        SET title = %s
        WHERE user_id = %s AND topic_id = %s
        """
        values = (title_topic, user_id, topic_id)
        cursor.execute(query_update_title, values)
        connection.commit()

    cursor.close()
    connection.close()

def input_new_user(username, password,timestamp):
    connection = connect_to_database()
    cursor = connection.cursor()
    query = "INSERT INTO users (user_id, username, password, created_at) VALUES (%s, %s, %s, %s)"
    user_id = generate_random_topic_id(4)
    values = (user_id, username, password, timestamp)
    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

# User authentication function (replace this with your actual authentication logic)
def is_valid_credentials(username, password):
    connection = connect_to_database()
    cursor = connection.cursor()
    # username = "user1"
    # password = "12345678"
    query = "SELECT COUNT(*) FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    count = cursor.fetchone()[0]
    connection.close()
    return count > 0


topic_id = generate_random_topic_id()

# Route to render the HTML chat interface
# @app.route('/')
# def home():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     current_user_id = session['user_id']

#     connection = connect_to_database()
#     cursor = connection.cursor()

#      # Fetch topic_id values
#     cursor.execute("SELECT title FROM topic_per_user WHERE user_id = %s", (current_user_id,))
#     topic_ids = [row[0] for row in cursor.fetchall()]

#     # Fetch username
#     cursor.execute("SELECT username FROM users WHERE user_id = %s", (current_user_id,)) 
#     username = cursor.fetchone()[0]

#     connection.close()
    
#     return render_template('chatbot.html', topic_ids=topic_ids, username=username)
#     # return render_template('chatbot.html')

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user_id = session['user_id']

    connection = connect_to_database()
    cursor = connection.cursor()

    # Fetch topic_id values and corresponding titles
    cursor.execute("SELECT topic_id, title FROM topic_per_user WHERE user_id = %s", (current_user_id,))
    topics = [{'topic_id': row[0], 'title': row[1]} for row in cursor.fetchall()]

    # Fetch username
    cursor.execute("SELECT username FROM users WHERE user_id = %s", (current_user_id,)) 
    username = cursor.fetchone()[0]

    connection.close()
    
    return render_template('chatbot.html', topics=topics, username=username)


# # User login route
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')


        if is_valid_credentials(username, password):
            # Fetch the user_id associated with the authenticated user from the database
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            user_id = cursor.fetchone()[0]  # Fetch the first column (user_id)
            connection.close()

            # Set user_id in session
            session['user_id'] = user_id

            return redirect(url_for('home'))  # Redirect to home or authorized route
        else:
            # Redirect to login page after sending "Invalid credentials" response
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    success_message = None
    if request.method == 'POST':
        # Retrieve registration data from the form
        data = request.form
        username = data.get('username')
        password = data.get('password')

        print(username, password)
        timestamp = datetime.datetime.now()
        input_new_user(username, password, timestamp)
        success_message = "Registration successful. You can now log in."
        
        return redirect(url_for('login'))

    return render_template('register.html', success_message=success_message)


@app.route('/get_conversation/<topic_id>', methods=['GET'])
def get_conversation(topic_id):
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT user_msg, bot_msg FROM messages WHERE topic_id = %s ORDER BY timestamp_user ASC"
    # query = "SELECT user_msg, bot_msg FROM messages WHERE topic_id = %s ORDER BY id ASC"
    cursor.execute(query, (topic_id,))
    conversation = cursor.fetchall()
    connection.close()
    return jsonify(conversation)


# # # Protected route
# @app.route('/protected', methods=['GET'])
# def protected():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     user_id = session['user_id']

#     # Fetch user data from the database using current_user_id
#     connection = connect_to_database()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
#     user_data = cursor.fetchone()
#     connection.close()

#     return jsonify({'user_id': user_id, 'username': user_data['username']})

# Chatbot interaction route
@app.route('/gpt', methods=['POST'])
def gpt():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json

    global topic_id # global variable"
    user_id = session['user_id']

    if 'refresh' in data and data['refresh']:
        topic_id = generate_random_topic_id()
        

    if 'clicked_topic_id' in data:
        topic_id = data['clicked_topic_id']

    if 'text' in data:
        # input prompt
        if data['text'] != '':
            prompt = data['text']
            timestamp_user = datetime.datetime.now()
            data = {'input': prompt}
        

            url = f'https://telkomsite-engine-2uittvl6zq-as.a.run.app/telkom-bot/topic_id={topic_id}'
            headers = {os.environ.get("ENGINE_HEADER"):os.environ.get("ENGINE_PASS")}

            message_id = generate_random_topic_id(10)

            try:
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()

                response_dict = response.json()
                model_response = response_dict['output']

                timestamp_bot = datetime.datetime.now()
                con = connect_to_database()
                cursor_to_msg = con.cursor()
                data_to_insert_msg = (prompt, model_response, timestamp_user, timestamp_bot, user_id, topic_id, message_id)
                cursor_to_msg.execute(query_insert_messages, data_to_insert_msg)
                con.commit(); con.close()
                
                msg_id_count = count_msg_id(topic_id)
                input_title(msg_id_count, user_id)

                return jsonify({'model_response': model_response})

            except Exception as req_err:
                error_message = "Ada kegagalan di server kami nih, silakan kirim ulang pertanyaan anda"
                print(f"{req_err}")
                return jsonify({'model_response': error_message})

    else:
        return jsonify({'error': 'Text not provided.'})

@app.route('/logout')
def logout():
    session.clear()  # Clear the user's session
    return redirect(url_for('login'))  # Redirect to the login page

# @app.before_request
# def check_login():
#     no_session_required = ['login', 'static', 'logout']  # Add 'logout' to the list
#     if request.endpoint not in no_session_required and 'user_id' not in session:
#         return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port = 8080)
