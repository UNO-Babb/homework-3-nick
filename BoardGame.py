from flask import Flask, render_template, session, request, redirect, url_for, jsonify
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

ROWS = 6
COLS = 7

def initialize_game():
    session['board'] = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    session['turn'] = 1
    session['winner'] = 0
    session['wins'] = {'1': 0, '2': 0, 'draws': 0}

def check_winner(board, player):
    for row in range(ROWS):
        for col in range(COLS - 3):
            if all(board[row][col + i] == player for i in range(4)):
                return True
    for col in range(COLS):
        for row in range(ROWS - 3):
            if all(board[row + i][col] == player for i in range(4)):
                return True
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if all(board[row + i][col + i] == player for i in range(4)):
                return True
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if all(board[row - i][col + i] == player for i in range(4)):
                return True
    return False

def check_draw(board):
    return all(cell != 0 for row in board for cell in row)

@app.route('/')
def index():
    if 'board' not in session:
        initialize_game()
    return render_template('index.html', 
                           board=session['board'], 
                           turn=session['turn'], 
                           winner=session['winner'], 
                           wins=session['wins'])

@app.route('/click', methods=['POST'])
def click():
    if session.get('winner', 0):
        return jsonify(success=False)

    data = request.get_json()
    row, col = data.get('row'), data.get('col')

    board = session['board']
    turn = session['turn']

    if 0 <= row < ROWS and 0 <= col < COLS and board[row][col] == 0:
        board[row][col] = turn

        if check_winner(board, turn):
            session['winner'] = turn
            session['wins'][str(turn)] += 1
        elif check_draw(board):
            session['winner'] = -1
            session['wins']['draws'] += 1
        else:
            session['turn'] = 2 if turn == 1 else 1

        session['board'] = board
        return jsonify(success=True, board=board, turn=session['turn'], winner=session['winner'], wins=session['wins'])

    return jsonify(success=False)

@app.route('/reset')
def reset():
    session['board'] = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    session['turn'] = 1
    session['winner'] = 0
    return redirect(url_for('index'))

@app.route('/reset_counter')
def reset_counter():
    session['wins'] = {'1': 0, '2': 0, 'draws': 0}
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
