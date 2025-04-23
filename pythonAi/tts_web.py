from flask import Flask, request, jsonify, render_template
import subprocess
import pyttsx3
import threading

# engine = pyttsx3.init()
# engine.setProperty('rate', 160)
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[1].id)

speak_lock = threading.Lock()

app = Flask(__name__)
app.secret_key = "any-secret-key"

def speak_text(text):
    try:
        # Create a new TTS engine instance for each response
        local_engine = pyttsx3.init()
        local_engine.setProperty('rate', 160)
        voices = local_engine.getProperty('voices')
        local_engine.setProperty('voice', voices[1].id)
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

    print(f"[+] Heard: {transcript}")

    result = subprocess.run(
        ["ollama", "run", "deepseek-coder-v2:16b"],
        input=transcript,
        text=True,
        capture_output=True
    )

    deepseek_reply = result.stdout.strip()
    print(f"[DeepSeek Reply]: {deepseek_reply}")

    # # Interrupt current speech if any
    # if engine._inLoop:
    #     engine.stop()

    # Speak the reply
    threading.Thread(target=speak_text, args=(deepseek_reply,)).start()

    return jsonify({"reply": deepseek_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
