from flask import Flask, request, jsonify
import markovify
import sqlite3

app = Flask(__name__)

# Create a database connection
def get_db():
    conn = sqlite3.connect('content.db')
    return conn

# Create the database schema if not exists
def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS content
                        (id INTEGER PRIMARY KEY, user_input TEXT, generated_content TEXT)''')

init_db()

# Generate content using Markovify
def generate_content(text):
    if not text:
        text = "Default text to initialize the Markov model."
    text_model = markovify.Text(text)
    return text_model.make_sentence()

# API endpoint to generate blog content
@app.route('/generate', methods=['POST'])
def generate_blog_content():
    data = request.json
    user_input = data.get('user_input')
    
    # Generate content using Markovify
    generated_content = generate_content(user_input)

    # Store the input and generated content in the database
    with get_db() as conn:
        conn.execute('INSERT INTO content (user_input, generated_content) VALUES (?, ?)',
                     (user_input, generated_content))
        conn.commit()

    return jsonify({'user_input': user_input, 'generated_content': generated_content})

# API endpoint to retrieve content
@app.route('/content/<int:content_id>', methods=['GET'])
def get_content(content_id):
    with get_db() as conn:
        cursor = conn.execute('SELECT * FROM content WHERE id = ?', (content_id,))
        row = cursor.fetchone()
        if row:
            return jsonify({'id': row[0], 'user_input': row[1], 'generated_content': row[2]})
        else:
            return jsonify({'error': 'Content not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)