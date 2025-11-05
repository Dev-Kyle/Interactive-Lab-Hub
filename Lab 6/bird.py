"""
Distributed Bird Guessing Game Server
Manages game state for Raspberry Pi clients using Flask-SocketIO.
"""

import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import json
from collections import OrderedDict
from datetime import datetime
import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'guess-the-birds-2025'

# Try eventlet first, fall back to threading if not available
try:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
    print("Running in eventlet async_mode.")
except ImportError:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    print("Running in threading async_mode.")

# Store player data: {mac_address: {'sid': str, 'guess': int, 'last_seen': datetime}}
players = OrderedDict()

# Game State: 'IDLE', 'GUESSING', 'RESULTS'
GAME_STATE = 'IDLE'
CORRECT_ANSWER = 0
game_loop_task = None


@app.route('/')
def index():
    """Serve the main game screen"""
    return render_template('index.html')


def game_loop():
    """
    Manages the game state machine, running as a background task.
    """
    global GAME_STATE, CORRECT_ANSWER

    while True:
        if GAME_STATE == 'IDLE':
            # Wait for a 'start_game' signal
            # This loop just yields control. The actual start is triggered by an event.
            socketio.sleep(1)

        elif GAME_STATE == 'GUESSING':
            # --- START NEW ROUND ---
            print("\n--- NEW ROUND ---")
            CORRECT_ANSWER = random.randint(5, 25)

            # Reset all player guesses
            for mac in players:
                players[mac]['guess'] = None

            print(f"Correct answer is: {CORRECT_ANSWER}")

            # Notify all clients (web UI and Pis)
            socketio.emit('new_round', {
                'bird_count': CORRECT_ANSWER,
                'countdown': 10
            })

            # Wait for 10 seconds
            socketio.sleep(10)

            # --- TIMES UP, MOVE TO RESULTS ---
            print("Time's up!")
            GAME_STATE = 'RESULTS'
            # Tell Pis to submit their final guess
            socketio.emit('times_up')

            # Give clients 3 seconds to send their guesses
            socketio.sleep(3)

        elif GAME_STATE == 'RESULTS':
            # --- CALCULATE WINNERS ---
            print("Calculating results...")
            min_diff = float('inf')
            winners = []
            all_guesses = []

            for mac, data in players.items():
                guess = data['guess']
                all_guesses.append({'mac': mac, 'guess': guess})

                if guess is not None:
                    diff = abs(guess - CORRECT_ANSWER)
                    if diff < min_diff:
                        min_diff = diff
                        winners = [mac]  # New best guess
                    elif diff == min_diff:
                        winners.append(mac) # Tied for best

            print(f"Winners: {winners} (Difference: {min_diff})")

            # Broadcast results to web UI
            socketio.emit('show_results', {
                'correct_answer': CORRECT_ANSWER,
                'guesses': all_guesses,
                'winners': winners
            })

            # Show results for 8 seconds
            socketio.sleep(8)

            # --- BACK TO IDLE ---
            print("Round over, returning to IDLE.")
            GAME_STATE = 'IDLE'
            socketio.emit('round_idle')

# --- SocketIO Event Handlers ---

@socketio.on('connect')
def handle_connect():
    """A new client connected (could be web UI or a Pi)"""
    print(f'Client connected: {request.sid}')
    # Send current state to newly connected client
    emit('current_players', {
        'players': list(players.keys())
    })
    emit('game_state', {
        'state': GAME_STATE,
        'answer': CORRECT_ANSWER
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print(f'Client disconnected: {request.sid}')
    mac_to_remove = None
    for mac, data in players.items():
        if data['sid'] == request.sid:
            mac_to_remove = mac
            break

    if mac_to_remove:
        del players[mac_to_remove]
        # Notify web UI that a player left
        socketio.emit('player_left', {
            'mac': mac_to_remove,
            'count': len(players)
        })
        print(f"Player {mac_to_remove} removed.")


@socketio.on('register')
def handle_register(data):
    """A Raspberry Pi client registers itself"""
    try:
        mac = data.get('mac')
        if not mac:
            return

        print(f'Player Pi registered: {mac} (sid: {request.sid})')
        players[mac] = {
            'sid': request.sid,
            'guess': None,
            'last_seen': datetime.now()
        }
        # Notify web UI of new player
        socketio.emit('player_joined', {
            'mac': mac,
            'count': len(players)
        })

    except Exception as e:
        print(f'Error handling registration: {e}')


@socketio.on('submit_guess')
def handle_submit_guess(data):
    """A Pi client submits its guess"""
    global GAME_STATE
    # Only accept guesses in the short 'RESULTS' window after 'times_up'
    if GAME_STATE != 'RESULTS':
        print(f"Ignoring late/early guess from {data.get('mac')}")
        return

    try:
        mac = data.get('mac')
        guess = int(data.get('guess', 0))

        if mac in players:
            players[mac]['guess'] = guess
            players[mac]['last_seen'] = datetime.now()
            print(f'✓ Guess received from {mac}: {guess}')

            # Optional: Send live guess update to web UI
            socketio.emit('live_guess', {'mac': mac, 'guess': guess})

        else:
            print(f'! Guess from unknown player: {mac}')

    except Exception as e:
        print(f'Error handling guess: {e}')


@socketio.on('start_game')
def handle_start_game():
    """Triggered by web UI button to start a new game"""
    global GAME_STATE
    if GAME_STATE == 'IDLE':
        print("Start game button pressed, moving to GUESSING state.")
        GAME_STATE = 'GUESSING'
        # The game_loop will now pick this up
    else:
        print("Ignoring start_game request, game already in progress.")


if __name__ == '__main__':
    print("=" * 60)
    print("  Distributed Bird Guessing Game Server")
    print("=" * 60)
    print(f"  Main Screen:  http://0.0.0.0:5000")
    print("=" * 60)

    # Start the game loop as a background task
    game_loop_task = socketio.start_background_task(game_loop)
    print("Game loop started in background.")
    print("Waiting for connections and 'Start Game' signal...")
    print("=" * 60)

    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
