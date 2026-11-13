
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import pyttsx3
import requests
import webbrowser
import datetime
import threading
import queue


# =========================
# CONFIGURATION
# =========================

BG = "#080D18"
PANEL = "#111B2D"
CYAN = "#00D9FF"
WHITE = "#FFFFFF"
GRAY = "#8A9BB5"
GREEN = "#00E59B"

MODEL = "qwen2.5:3b"

messages = queue.Queue()
stop_event = threading.Event()
listening = False


# =========================
# VOICE ENGINE
# =========================

# VOICE ENGINE

engine = pyttsx3.init()

voices = engine.getProperty("voices")

# Microsoft David - English male voice
engine.setProperty("voice", voices[0].id)

# Speaking speed
engine.setProperty("rate", 155)

# Volume
engine.setProperty("volume", 1.0)

for voice in voices:
    if "english" in voice.name.lower() or "en_" in voice.id.lower():
        engine.setProperty("voice", voice.id)
        break


def speak(text):
    messages.put(("assistant", text))

    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("Voice error:", e)


# =========================
# AI CONNECTION
# =========================

def ask_ai(question):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": (
                    "You are JARVIS, an intelligent and helpful "
                    "English-speaking AI assistant. "
                    "Answer clearly and naturally in English. "
                    "Keep answers concise. "
                    f"User: {question}"
                ),
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()

        return response.json()["response"]

    except Exception as e:
        print("AI error:", e)
        return "I cannot connect to my AI system right now."


# =========================
# VOICE RECOGNITION
# =========================

def listen():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            messages.put(("status", "Listening..."))

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=7
            )

        text = recognizer.recognize_google(
            audio,
            language="en-US"
        )

        return text.lower()

    except sr.WaitTimeoutError:
        return ""

    except sr.UnknownValueError:
        messages.put(("status", "Could not understand. Try again."))
        return ""

    except sr.RequestError as e:
        messages.put(("status", "Speech recognition error"))
        print(e)
        return ""

    except Exception as e:
        messages.put(("status", "Microphone error"))
        print(e)
        return ""


# =========================
# COMMAND SYSTEM
# =========================

def process_command(command):

    messages.put(("user", command))

    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")

    elif "open google" in command:
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")

    elif "open camera" in command or "open the camera" in command:
        speak("Opening camera.")
        import subprocess
        subprocess.Popen("start microsoft.windows.camera:", shell=True)

    elif "what time" in command or "current time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}.")

    elif "what date" in command or "today's date" in command:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today is {current_date}.")

    elif "stop listening" in command or "goodbye jarvis" in command:
        stop_listening()
        speak("Goodbye. I am shutting down voice listening.")

    else:
        answer = ask_ai(command)
        speak(answer)


# =========================
# LISTENING THREAD
# =========================

def listening_loop():
    global listening

    while not stop_event.is_set():

        command = listen()

        if stop_event.is_set():
            break

        if command:
            process_command(command)

    listening = False
    messages.put(("status", "Offline"))
    messages.put(("button", "START LISTENING"))


def start_listening():
    global listening

    if listening:
        return

    listening = True
    stop_event.clear()

    status_label.config(text="● ONLINE", fg=GREEN)
    start_button.config(text="LISTENING...", state="disabled")

    thread = threading.Thread(
        target=listening_loop,
        daemon=True
    )
    thread.start()


def stop_listening():
    global listening

    stop_event.set()
    listening = False

    status_label.config(text="● OFFLINE", fg=GRAY)
    start_button.config(text="START LISTENING", state="normal")


# =========================
# GUI DESIGN
# =========================

root = tk.Tk()

root.title("JARVIS AI Assistant")
root.geometry("950x650")
root.minsize(750, 550)
root.configure(bg=BG)


# HEADER

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=35, pady=25)

title = tk.Label(
    header,
    text="J.A.R.V.I.S",
    font=("Segoe UI", 27, "bold"),
    fg=CYAN,
    bg=BG
)
title.pack(side="left")

subtitle = tk.Label(
    header,
    text="PERSONAL AI ASSISTANT",
    font=("Segoe UI", 9),
    fg=GRAY,
    bg=BG
)
subtitle.pack(side="left", padx=18, pady=12)

status_label = tk.Label(
    header,
    text="● OFFLINE",
    font=("Segoe UI", 10, "bold"),
    fg=GRAY,
    bg=BG
)
status_label.pack(side="right")


# MAIN PANEL

main_panel = tk.Frame(
    root,
    bg=PANEL,
    highlightbackground="#1D3650",
    highlightthickness=1
)
main_panel.pack(
    fill="both",
    expand=True,
    padx=35,
    pady=5
)


# CENTER CIRCLE

circle = tk.Canvas(
    main_panel,
    width=180,
    height=180,
    bg=PANEL,
    highlightthickness=0
)
circle.pack(pady=(25, 5))

circle.create_oval(
    15, 15, 165, 165,
    outline=CYAN,
    width=2
)

circle.create_oval(
    30, 30, 150, 150,
    outline="#176B91",
    width=2
)

circle.create_text(
    90, 90,
    text="J",
    fill=CYAN,
    font=("Segoe UI", 65, "bold")
)


# WELCOME TEXT

welcome = tk.Label(
    main_panel,
    text="How can I help you today?",
    font=("Segoe UI", 17, "bold"),
    fg=WHITE,
    bg=PANEL
)
welcome.pack(pady=8)

info = tk.Label(
    main_panel,
    text="Your personal AI assistant is ready.",
    font=("Segoe UI", 10),
    fg=GRAY,
    bg=PANEL
)
info.pack(pady=(0, 15))


# CHAT AREA

chat = scrolledtext.ScrolledText(
    main_panel,
    height=8,
    bg="#0A1220",
    fg=WHITE,
    insertbackground=WHITE,
    font=("Segoe UI", 10),
    relief="flat",
    wrap=tk.WORD,
    padx=12,
    pady=12
)
chat.pack(fill="both", expand=True, padx=25, pady=10)

chat.tag_config("user", foreground=CYAN)
chat.tag_config("assistant", foreground=GREEN)

chat.insert(tk.END, "JARVIS: Hello! I am ready to assist you.\n\n")
chat.config(state="disabled")


def add_message(sender, text):
    chat.config(state="normal")

    if sender == "user":
        chat.insert(tk.END, "YOU: ", "user")
    else:
        chat.insert(tk.END, "JARVIS: ", "assistant")

    chat.insert(tk.END, text + "\n\n")

    chat.see(tk.END)
    chat.config(state="disabled")


# BUTTONS

button_panel = tk.Frame(main_panel, bg=PANEL)
button_panel.pack(pady=18)

start_button = tk.Button(
    button_panel,
    text="START LISTENING",
    command=start_listening,
    bg=CYAN,
    fg="#06111C",
    activebackground="#00AFCB",
    font=("Segoe UI", 11, "bold"),
    relief="flat",
    padx=25,
    pady=12,
    cursor="hand2"
)
start_button.pack(side="left", padx=10)

stop_button = tk.Button(
    button_panel,
    text="STOP",
    command=stop_listening,
    bg="#24334A",
    fg=WHITE,
    activebackground="#344B69",
    font=("Segoe UI", 11, "bold"),
    relief="flat",
    padx=25,
    pady=12,
    cursor="hand2"
)
stop_button.pack(side="left", padx=10)


# FOOTER

footer = tk.Label(
    root,
    text="JARVIS AI  |  POWERED BY OLLAMA",
    font=("Segoe UI", 8),
    fg=GRAY,
    bg=BG
)
footer.pack(pady=12)


# =========================
# UPDATE GUI SAFELY
# =========================

def update_gui():
    try:
        while True:
            item = messages.get_nowait()

            kind, value = item

            if kind == "user":
                add_message("user", value)

            elif kind == "assistant":
                add_message("assistant", value)

            elif kind == "status":
                if value == "Listening...":
                    status_label.config(text="● ONLINE", fg=GREEN)
                else:
                    status_label.config(text=value, fg=GRAY)

            elif kind == "button":
                start_button.config(text=value, state="normal")

    except queue.Empty:
        pass

    root.after(100, update_gui)


def close_app():
    stop_listening()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)

update_gui()

root.mainloop()


import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera could not be opened!")
    exit()

print("Camera is working! Press Q to close.")

while True:
    success, frame = camera.read()

    if not success:
        break

    cv2.imshow("JARVIS Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()