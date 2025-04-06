Requirements
-----------------------------
- Python 3.9+
- A Raspberry Pi (tested on Pi 3) with a MeshAdvHat or other Meshtastic-compatible board
- Meshtastic Python API (meshtastic)
- Requests library (requests)
- A running Meshtastic daemon (`meshtasticd`) OR
  a Meshtastic node connected via serial/USB with proper modifications

Notes:
- This script is optimized for use with the MeshAdvHat, which runs `meshtasticd` in the background and allows communication over a local TCP socket (127.0.0.1).
- If you are using a different setup — such as plugging a Meshtastic node directly into the Pi via USB — you will need to:
   - Change the interface in `triviabot.py` from `TCPInterface` to `SerialInterface`
   - Point to the correct serial port (e.g. `/dev/ttyUSB0`)
- TCP interface allows multiple programs (like the web UI and TriviaBot) to share the connection to the device without conflict.
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
