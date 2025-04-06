README - TriviaBot for Meshtastic
================================

TriviaBot is a lightweight Python bot that sends multiple choice trivia questions over Meshtastic every 5 minutes. 
Users reply with !answer A/B/C/D, and scores are tracked throughout the day.  A top 5 daily leaderboard is displayed.

-----------------------------
Requirements
-----------------------------
- Python 3.9+
- A running Meshtastic daemon (meshtasticd) or device with TCP interface enabled
- Python packages: meshtastic, requests
-----------------------------
Install Instructions
-----------------------------
# (Optional) Set up a virtual environment
python3 -m venv .meshtastic-env
source .meshtastic-env/bin/activate

# Install Meshtastic Python API
pip install meshtastic

# Also install other needed modules
pip install requests

-----------------------------
Setup Directory Structure
-----------------------------
mkdir -p ~/meshscripts/data
cd ~/meshscripts

# Create required data files
echo "[]" > data/questions.json
echo "{}" > data/leaderboard.json

-----------------------------
How to Run
-----------------------------
cd ~/meshscripts
python3 triviabot.py

- Trivia questions will be sent every 5 minutes
- Users can answer using: !answer A
- Each node gets one answer per round
- Leaderboard shows top 5 scores for the day
- Use !debugstatus to check time remaining and how many answered

-----------------------------
Configuration Options (in triviabot.py)
-----------------------------
ALLOWED_CHANNEL_INDEX = 1         # Channel TriviaBot listens/responds on. 					  #Probably best to not have it LongFast
ROUND_DURATION = 300              # Interval between questions (in seconds)
CHAR_LIMIT = 180                  # Max message size allowed by Meshtastic

-----------------------------
Optional Commands
-----------------------------
!answer A         Submit an answer to the current question
!debugstatus      Show how many people answered and time left

-----------------------------
Example Output
-----------------------------
TRIVIA TIME!
Which state of the United States is the smallest?
A) Massachusetts
B) Maine
C) Vermont
D) Rhode Island
Reply with !answer and the letter (A, B, C, or D)
