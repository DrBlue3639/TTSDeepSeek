from flask import Flask, request, jsonify, render_template
import subprocess
import pyttsx3
import threading

speak_lock = threading.Lock()

# Predefined keyword-based responses
predefined_talks = {
    "who are you": "My name is MEI, your favorite AI.",
    "your name": "My name is MEI, your favorite AI.",
    "what time is it": "Let me check the time for you.",
    "good morning": "Good morning! Hope your day starts with a smile.",
    "bye": "Goodbye! Talk to you later.",
    "who is mandeep": "Mandip is the gayest person I have met, and he treats his girl so badly that she was crying in insta Notes once.",
    "who is mandir": "Mandip is the definition of someone who treats his girl so badly that she would cry in insta Notes someday.",
    "who is mandip": "Mandip is Sudip's best friend, honestly speaking... he's gay though.",
}

app = Flask(__name__)
app.secret_key = "any-secret-key"

def speak_text(text):
    try:
        local_engine = pyttsx3.init()
        local_engine.setProperty('rate', 160)
        voices = local_engine.getProperty('voices')
        local_engine.setProperty('voice', voices[1].id)
        with speak_lock:
            local_engine.say(text)
            local_engine.runAndWait()
        local_engine.stop()
    except Exception as e:
        print("Speech error:", e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    transcript = data.get("text", "").strip()

    if not transcript:
        return jsonify({"reply": ""})

    # Check predefined replies first
    for keyword, reply in predefined_talks.items():
        if keyword in transcript.lower():
            print(f"[Custom keyword triggered]: {reply}")
            threading.Thread(target=speak_text, args=(reply,)).start()
            return jsonify({"reply": reply})

    print(f"[+] Heard: {transcript}")

    try:
        result = subprocess.run(
            ["ollama", "run", "deepseek-coder-v2:16b"],
            input=transcript,
            text=True,
            capture_output=True,
            timeout=10
        )

        deepseek_reply = result.stdout.strip() if result.stdout else "Hmm, I couldn't understand that."

    except Exception as e:
        print("[!] DeepSeek error:", e)
        deepseek_reply = "There was an error processing your request."

    threading.Thread(target=speak_text, args=(deepseek_reply,)).start()

    return jsonify({"reply": deepseek_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
