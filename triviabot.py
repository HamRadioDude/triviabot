import os
import json
import time
import html
import random
import requests
from datetime import datetime, timedelta
from meshtastic.tcp_interface import TCPInterface
from pubsub import pub

# === CONFIG ===
ALLOWED_CHANNEL_INDEX = 1
DATA_DIR = "data"
QUESTION_LOG = os.path.join(DATA_DIR, 'questions.json')
LEADERBOARD_FILE = os.path.join(DATA_DIR, 'leaderboard.json')
CHAR_LIMIT = 180
ROUND_DURATION = 300  # 5 minutes

# === STATE ===
interface = None
current_question = None
current_correct = None
current_answers = {}  # node_id -> answer
round_start_time = None

# === FILE SETUP ===
def init_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(QUESTION_LOG):
        with open(QUESTION_LOG, 'w') as f:
            json.dump([], f)
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump({}, f)

# === UTILITIES ===
def send_message(text):
    print(f"[TriviaBot] ➤ {text}")
    interface.sendText(text, channelIndex=ALLOWED_CHANNEL_INDEX)

# === TRIVIA ===
def fetch_trivia():
    url = 'https://opentdb.com/api.php?amount=1&type=multiple'
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data['response_code'] != 0:
            return None
    except:
        return None

    q = data['results'][0]
    question = html.unescape(q['question'])
    correct = html.unescape(q['correct_answer'])
    incorrect = [html.unescape(ans) for ans in q['incorrect_answers']]
    all_answers = incorrect + [correct]
    random.shuffle(all_answers)

    choices = dict(zip(['A', 'B', 'C', 'D'], all_answers))
    correct_letter = [k for k, v in choices.items() if v == correct][0]
    full_text = f"🤔 TRIVIA TIME!\n{question}\n"
    full_text += "\n".join([f"{k}) {v}" for k, v in choices.items()])
    full_text += "\n➡️ Reply with !answer and the letter (A, B, C, or D)"

    if len(full_text) > CHAR_LIMIT:
        return None

    return {
        "text": full_text,
        "question": question,
        "choices": choices,
        "correct": correct_letter,
        "timestamp": datetime.utcnow().isoformat()
    }

def store_question(q):
    with open(QUESTION_LOG, 'r') as f:
        questions = json.load(f)
    questions.append(q)
    with open(QUESTION_LOG, 'w') as f:
        json.dump(questions, f, indent=2)

# === ROUND HANDLING ===
def record_answer(node_id, answer):
    if node_id in current_answers:
        return
    current_answers[node_id] = answer.upper()
    send_message(f"{node_id}: ✅ Your answer was recorded!")

def end_round():
    global current_question, current_correct, current_answers
    total = len(current_answers)
    correct = sum(1 for a in current_answers.values() if a == current_correct)
    incorrect = total - correct
    pct_correct = int((correct / total) * 100) if total else 0
    pct_wrong = 100 - pct_correct if total else 0

    send_message(f"⏱ Round over! {pct_correct}% got it right, {pct_wrong}% wrong.")
    send_message(f"✅ The correct answer was: {current_correct}) {current_question['choices'][current_correct]}")
    
    update_leaderboard()
    show_leaderboard()

    current_question = None
    current_correct = None
    current_answers = {}

def update_leaderboard():
    key = datetime.utcnow().strftime("%Y-%m-%d")
    with open(LEADERBOARD_FILE, 'r') as f:
        leaderboard = json.load(f)

    if key not in leaderboard:
        leaderboard[key] = {}

    for node_id, answer in current_answers.items():
        # only score if correct
        if answer.upper() == current_correct:
            leaderboard[key][node_id] = leaderboard[key].get(node_id, 0) + 1
        else:
            leaderboard[key].setdefault(node_id, 0)  # ensure they appear

    leaderboard["latest_day"] = key
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard, f, indent=2)

def show_leaderboard():
    with open(LEADERBOARD_FILE, 'r') as f:
        board = json.load(f)

    today = board.get("latest_day", "")
    daily = board.get(today, {})
    sorted_daily = sorted(daily.items(), key=lambda x: x[1], reverse=True)[:5]

    if not sorted_daily:
        send_message("📋 No participants yet today.")
        return

    message = "🏆 TOP 5 TODAY:\n"
    for i, (user, score) in enumerate(sorted_daily, 1):
        message += f"{i}) {user} - {score} pts\n"

    send_message(message.strip())

# === COMMAND HANDLERS ===
def handle_answer(user, msg, iface, channel):
    if not current_question:
        return
    try:
        answer = msg.split(" ")[1].strip().upper()
        if answer in ['A', 'B', 'C', 'D']:
            record_answer(user, answer)
    except IndexError:
        pass

def handle_debugstatus(user, msg, iface, channel):
    if not current_question:
        send_message("ℹ️ No active trivia question.")
        return
    now = datetime.utcnow()
    elapsed = (now - round_start_time).total_seconds()
    remaining = max(0, ROUND_DURATION - int(elapsed))
    send_message(
        f"📊 Debug Status:\n"
        f"Answers received: {len(current_answers)}\n"
        f"Time left: {remaining // 60}m {remaining % 60}s"
    )

# === RECEIVE ===
def on_receive(packet=None, interface=None):
    if not packet or "decoded" not in packet:
        return
    msg = packet['decoded'].get('text', '').strip()
    user = packet.get("fromId", "unknown")
    channel = packet.get("channel", 0)

    print(f"📡 Received from {user} on CH{channel}: {msg}")  # DEBUG

    if channel != ALLOWED_CHANNEL_INDEX:
        return
    if msg.lower().startswith("!answer"):
        handle_answer(user, msg, interface, channel)
    elif msg.lower().startswith("!debugstatus"):
        handle_debugstatus(user, msg, interface, channel)

# === MAIN ===
def main():
    global interface, current_question, current_correct, round_start_time
    print("📡 TriviaBot is live!")
    init_files()
    interface = TCPInterface(hostname="127.0.0.1")
    pub.subscribe(on_receive, "meshtastic.receive")  #  Compatibility fix

    while True:
        q = None
        while not q:
            q = fetch_trivia()
        current_question = q
        current_correct = q["correct"]
        round_start_time = datetime.utcnow()
        store_question(q)
        send_message(q["text"])

        for _ in range(ROUND_DURATION):
            time.sleep(1)

        end_round()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("👋 TriviaBot shutting down.")
