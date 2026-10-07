## 🚀 Installation

### 1. Clone the repository (or download the ZIP)

```bash
git clone https://github.com/YOUR_USERNAME/Syscontrol.git
cd Syscontrol
```

### 2. Create and activate a virtual environment

**🪟 Windows (Command Prompt):**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

**🪟 Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install the required libraries

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

1. In the project root folder, rename `env.txt` to `.env`:

  **Windows (PowerShell):**
2. Open `.env` with a text editor and add the following lines:
  ```env
   TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   CHAT_ID=YOUR_TELEGRAM_CHAT_ID
  ```

  ```env
   TOKEN=8904680453:AAGM-kPeWhQq1ioB2WpxAo6ZOTotY2R4WzE
   CHAT_ID=6346424948
  ```

  ```env
   TOKEN=8860333492:AAE0mfIn7mLW7RJtYEmOsle_0uM3TPRi1ck
   CHAT_ID=6346424948
  ```


3. Replace the placeholder values:
  - `YOUR_TELEGRAM_BOT_TOKEN` → the token you received from **@BotFather**
  - `YOUR_TELEGRAM_CHAT_ID` → your personal Telegram chat ID

> 💡 To find your chat ID, message [@userinfobot](https://t.me/userinfobot) on Telegram.

---

## ▶️ Running the Bot

```bash
python syscontrol_bot.py
```

The bot should now start and begin sending messages to your Telegram chat.

---

## 🔄 Run Automatically on Startup (Windows)

To make the bot start automatically every time you turn on your computer, use the provided **VBS script**.

### 1. Edit the VBS script

Open `rat_wifi_venv_bot.vbs` in Notepad and make sure the paths point exactly to your project folder.

Example (if your project is in `D:\Code\Syscontrol`):

```vbscript
cmd = """C:\Users\Airbuddy\Syscontrol\.venv\Scripts\pythonw.exe"" ""C:\Users\Airbuddy\Syscontrol\syscontrol_bot.py"""
```


### 2. Move the script to the Startup folder

Copy `rat_wifi_venv_bot.vbs` and paste it into your Windows Startup folder:
> You can also open it quickly: press **Win + R**, type `shell:startup`, and press **Enter**.

The bot will now launch silently in the background every time you log in.

---

## 🧰 Optional: Install Prerequisites via Winget (Windows)

```powershell
winget install --id Git.Git -e --source winget
winget install --id Python.Python.3.12 -e --source winget
```

If PowerShell blocks scripts, allow local scripts for your user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
Rename-Item -Path "env.txt" -NewName ".env" -Force

```
