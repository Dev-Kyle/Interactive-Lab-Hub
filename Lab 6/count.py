"""
Distributed Student Guessing Game Server
Bridged Architecture:
- Listens to Web UI via Flask-SocketIO
- Communicates with Pi clients via MQTT
"""

# --- EVENTLET PATCHING ---
try:
    import eventlet
    eventlet.monkey_patch()
    print("Running in eventlet async_mode.")
except ImportError:
    eventlet = None
    print("Running in threading async_mode (eventlet not found).")
# -------------------------

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import json
from collections import OrderedDict
from datetime import datetime
import random
import time

# --- Flask & Socket.IO Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'guess-the-students-2025'

if eventlet:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
else:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- MQTT Configuration (from your example) ---
MQTT_BROKER = 'farlab.infosci.cornell.edu'
MQTT_PORT = 1883
MQTT_USERNAME = 'idd'
MQTT_PASSWORD = 'device@theFarm'

# Define our new game topics
MQTT_TOPIC_PREFIX = 'IDD/studentgame'
MQTT_TOPIC_REGISTER = f'{MQTT_TOPIC_PREFIX}/client/register'
MQTT_TOPIC_SUBMIT_GUESS = f'{MQTT_TOPIC_PREFIX}/client/submit_guess'

MQTT_TOPIC_NEW_ROUND = f'{MQTT_TOPIC_PREFIX}/broadcast/new_round'
MQTT_TOPIC_TIMES_UP = f'{MQTT_TOPIC_PREFIX}/broadcast/times_up'
MQTT_TOPIC_ROUND_IDLE = f'{MQTT_TOPIC_PREFIX}/broadcast/round_idle'

# --- Flask Routes ---
@app.route('/')
def index():
    """Serve the main game screen UI"""
    return render_template('index.html')

# --- Global Game State ---
# Store player data: {mac_address: {'guess': int}}
# We no longer need 'sid' since Pis are identified by MAC via MQTT
players = OrderedDict()

GAME_STATE = 'IDLE'  # States: IDLE, GUESSING, RESULTS
CORRECT_ANSWER = 0
GAME_COUNTDOWN = 10
RESULTS_DURATION = 8
SUBMIT_GRACE_PERIOD = 3


# --- MQTT Bridge Callbacks ---

def handle_pi_registration(mac):
    """A Pi client has registered via MQTT."""
    if not mac:
        return
    
    if mac not in players:
        print(f'MQTT: Pi registered: {mac}')
        players[mac] = {'guess': None}
        
        # --- FIX: Yield to eventlet hub before emitting from MQTT thread ---
        socketio.sleep(0) 
        
        # Notify WEB UI (via Socket.IO) of the new player
        socketio.emit('player_joined', {
            'mac': mac,
            'count': len(players)
        })
    else:
        print(f'MQTT: Pi re-registered: {mac}')

def handle_pi_guess(mac, guess):
    """A Pi client has submitted a guess via MQTT."""
    if mac in players:
        # Only accept guesses during the GUESSING or RESULTS (grace period) state
        if GAME_STATE == 'GUESSING' or GAME_STATE == 'RESULTS':
            try:
                int_guess = int(guess)
                players[mac]['guess'] = int_guess
                print(f'MQTT: Guess received from {mac}: {int_guess}')
                
                # --- NEW FEATURE: Notify web UI of the live guess ---
                socketio.sleep(0) # Yield to eventlet hub
                socketio.emit('live_guess', {'mac': mac, 'guess': int_guess})
                
            except ValueError:
                print(f'MQTT: Invalid guess from {mac}: {guess}')
        else:
            print(f'MQTT: Guess from {mac} rejected (game not active)')
    else:
        print(f'MQTT: Guess from unknown MAC {mac} rejected')

def on_mqtt_connect(client, userdata, flags, rc):
    """Callback when the server connects to the MQTT broker."""
    if rc == 0:
        print(f"[OK] Connected to MQTT broker: {MQTT_BROKER}")
        # Subscribe to topics where Pis will send data
        client.subscribe(MQTT_TOPIC_REGISTER)
        client.subscribe(MQTT_TOPIC_SUBMIT_GUESS)
        print(f"Subscribed to: {MQTT_TOPIC_REGISTER}")
        print(f"Subscribed to: {MQTT_TOPIC_SUBMIT_GUESS}")
    else:
        print(f"[ERROR] MQTT Connection failed with code {rc}")

def on_mqtt_message(client, userdata, msg):
    """Callback for ANY message received from the MQTT broker."""
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        
        print(f"MQTT RX on {msg.topic}: {payload}")

        if msg.topic == MQTT_TOPIC_REGISTER:
            handle_pi_registration(data.get('mac'))
            
        elif msg.topic == MQTT_TOPIC_SUBMIT_GUESS:
            handle_pi_guess(data.get('mac'), data.get('guess'))
            
    except Exception as e:
        print(f"Error processing MQTT message on topic {msg.topic}: {e}")

# --- Background Game Loop ---
def game_loop(mqtt_client):
    """
    Manages the game state transitions.
    Now publishes game state to MQTT instead of Socket.IO for Pis.
    """
    global GAME_STATE, CORRECT_ANSWER
    
    while True:
        if GAME_STATE == 'IDLE':
            socketio.sleep(1)
            
        elif GAME_STATE == 'GUESSING':
            # --- START NEW ROUND ---
            for mac in players:
                players[mac]['guess'] = None
            
            CORRECT_ANSWER = random.randint(10, 30)
            print("\n--- NEW ROUND ---")
            print(f"Correct answer is: {CORRECT_ANSWER}")
            
            # --- MQTT PUBLISH ---
            # Notify Pis (via MQTT) of the new round
            payload = json.dumps({
                'student_count': CORRECT_ANSWER,
                'countdown': GAME_COUNTDOWN
            })
            mqtt_client.publish(MQTT_TOPIC_NEW_ROUND, payload)
            print(f"MQTT TX to {MQTT_TOPIC_NEW_ROUND}: {payload}")
            
            # Notify Web UI (via Socket.IO)
            socketio.emit('new_round', {
                'student_count': CORRECT_ANSWER,
                'countdown': GAME_COUNTDOWN
            })
            
            socketio.sleep(GAME_COUNTDOWN)
            
            # --- TIMES UP, MOVE TO RESULTS ---
            print("Time's up!")
            GAME_STATE = 'RESULTS'
            
            # --- MQTT PUBLISH ---
            # Tell Pis (via MQTT) to submit their final guess
            mqtt_client.publish(MQTT_TOPIC_TIMES_UP, "{}")
            print(f"MQTT TX to {MQTT_TOPIC_TIMES_UP}: {{}}")
            
            socketio.sleep(SUBMIT_GRACE_PERIOD)
            
        elif GAME_STATE == 'RESULTS':
            # --- CALCULATE WINNERS ---
            all_guesses = []
            min_diff = float('inf')
            winners = []
            
            for mac, data in players.items():
                guess = data['guess']
                all_guesses.append({'mac': mac, 'guess': guess})
                
                if guess is not None:
                    diff = abs(guess - CORRECT_ANSWER)
                    if diff < min_diff:
                        min_diff = diff
                        winners = [mac]
                    elif diff == min_diff:
                        winners.append(mac)
            
            print(f"Winners: {winners} (Difference: {min_diff})")
            
            # --- SOCKET.IO EMIT ---
            # Broadcast results ONLY to web UI
            socketio.emit('show_results', {
                'correct_answer': CORRECT_ANSWER,
                'guesses': all_guesses,
                'winners': winners
            })
            
            socketio.sleep(RESULTS_DURATION)
            
            # --- BACK TO IDLE ---
            print("Round over, returning to IDLE.")
            GAME_STATE = 'IDLE'

            # --- MQTT PUBLISH ---
            # Tell Pis (via MQTT) to go idle
            mqtt_client.publish(MQTT_TOPIC_ROUND_IDLE, "{}")
            print(f"MQTT TX to {MQTT_TOPIC_ROUND_IDLE}: {{}}")

            # --- SOCKET.IO EMIT ---
            # Tell Web UI (via Socket.IO) to go idle
            socketio.emit('round_idle')

# --- SocketIO Handlers (for Web UI only) ---

@socketio.on('connect')
def handle_web_connect():
    """A new web UI client connected."""
    print(f'Web UI Client connected: {request.sid}')
    # Send current state
    socketio.emit('game_state', {
        'state': GAME_STATE,
        'answer': CORRECT_ANSWER
    }, to=request.sid)
    # Send current players
    socketio.emit('current_players', {
        'players': list(players.keys())
    }, to=request.sid)

@socketio.on('disconnect')
def handle_web_disconnect():
    """A web UI client disconnected."""
    print(f'Web UI Client disconnected: {request.sid}')
    # We don't remove players here, as Pis are persistent

@socketio.on('start_game')
def handle_start_game():
    """Triggered by the 'Start Game' button on the web UI."""
    global GAME_STATE
    if GAME_STATE == 'IDLE':
        print("Start Game signal received! -> Moving to GUESSING")
        GAME_STATE = 'GUESSING'
    else:
        print("Start Game signal ignored (game already in progress)")


if __name__ == '__main__':
    # --- Setup MQTT Client ---
    mqtt_client = mqtt.Client(f"student-game-server-{random.randint(100,999)}")
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message
    
    try:
        mqtt_client.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()  # Starts a background thread
    except Exception as e:
        print(f"CRITICAL: Could not connect to MQTT broker: {e}")
        print("Please check MQTT settings and network connection.")
        exit(1)
    
    # --- Start Game Loop ---
    # Pass the mqtt_client instance to the game loop
    socketio.start_background_task(game_loop, mqtt_client)
    
    # --- Start Flask Server ---
    print("=" * 60)
    print("  Distributed Student Guessing Game Server (MQTT Bridged)")
    print("=" * 60)
    print(f"  MQTT Broker: {MQTT_BROKER}")
    print(f"  Web UI Screen: http://0.0.0.0:5001")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
