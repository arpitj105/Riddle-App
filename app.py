from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Global variables to track game state
riddles = []
current_riddle_index = 0
correct_answers = 0
total_questions = 10

# Function to fetch a riddle
def fetch_riddle():
    try:
        response = requests.get("https://riddles-api.vercel.app/random")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print("Error fetching riddle:", e)
        return None

# Fetch a list of riddles at the beginning of the game
def initialize_riddles():
    global riddles
    riddles = []
    for _ in range(total_questions):
        riddle = fetch_riddle()
        if riddle:
            riddles.append(riddle)

# Route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    global current_riddle_index, correct_answers
    if request.method == 'POST':
        user_answer = request.form['answer']
        correct_answer = riddles[current_riddle_index]['answer'].strip().lower()
        # Check if the answer is correct
        if user_answer.strip().lower() == correct_answer:
            correct_answers += 1
        
        # Move to the next riddle
        current_riddle_index += 1
        # Check if the game is finished
        if current_riddle_index >= total_questions:
            if correct_answers >= 7:
                return redirect(url_for('win'))
            else:
                return redirect(url_for('lose'))
    # Render the next riddle
    if current_riddle_index < len(riddles):
        current_riddle = riddles[current_riddle_index]['riddle']
        correct_answer = riddles[current_riddle_index]['answer']
        return render_template('index.html', riddle=current_riddle, answer=correct_answer, question_number=current_riddle_index + 1, total_questions=total_questions)
    else:
        return render_template('index.html', riddle="An error occurred while fetching riddles.", question_number=current_riddle_index + 1, total_questions=total_questions)

# Route for the win page
@app.route('/win')
def win():
    return render_template('win.html')

# Route for the lose page
@app.route('/lose')
def lose():
    return render_template('lose.html')

# Initialize the game with 10 riddles before the first request
@app.before_first_request
def setup_game():
    initialize_riddles()

# Route for starting a new game
@app.route('/play-again')
def play_again():
    global current_riddle_index, correct_answers
    current_riddle_index = 0
    correct_answers = 0
    initialize_riddles()  # Reinitialize riddles for a new game
    return redirect(url_for('index'))  # Redirect to the main page

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
