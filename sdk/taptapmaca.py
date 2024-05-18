import telebot
import random
import json
import sqlite3
import threading
import time
from telebot import types

token = '6692988014:AAHl7O0r_4RtDJeeMHer4kzTI5xqja8wQDg'
bot = telebot.TeleBot(token)

jsonfile = 'tapmaca.json'
with open(jsonfile, 'r') as file:
    data = json.load(file)

def get_random_tapmaca():
    return random.choice(data['tapmacalar'])

current_tapmaca = get_random_tapmaca()

def create_connection():
    return sqlite3.connect('database.db', check_same_thread=False)

def create_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS istifadeciler(username TEXT PRIMARY KEY, xal INTEGER)''')
    conn.commit()
    conn.close()

def add_or_update_user(username, points):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT xal FROM istifadeciler WHERE username=?", (username,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE istifadeciler SET xal=xal+? WHERE username=?", (points, username))
        c.execute("SELECT xal FROM istifadeciler WHERE username=?", (username,))
        new_points = c.fetchone()[0]
    else:
        c.execute("INSERT INTO istifadeciler (username, xal) VALUES (?, ?)", (username, points))
        new_points = points
    conn.commit()
    conn.close()
    return new_points

def get_top_users():
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT username, xal FROM istifadeciler ORDER BY xal DESC LIMIT 5")
    top_users = c.fetchall()
    conn.close()
    return top_users

create_table()

game_running = True

@bot.message_handler(chat_types=['private'], commands=['start'])
def start_private(message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    elaveet = types.InlineKeyboardButton(text='Meni Qurupuna Elave et', url='https://t.me/taptapmaca_bot?startgroup=true')
    reytinq = types.InlineKeyboardButton(text='Reytinq', callback_data='reytinq')
    kb.add(elaveet, reytinq)
    bot.send_message(message.chat.id, 'Salam! Məni qrupunuza əlavə edərək oyuna başlaya bilərsiniz 🫡🤖 \n\n Oyunu başlatmaq üçün | /start | yazın 🎮🕹️👾 \n reytinq baxmaq üçün | /reytinq | yazın 📊⭐ \n\n Cavabı Tapa Bilmesez | /cavab | yazaraq cavabı oyrene bilersiz 📬 \n\n Oyunu dayandırmaq üçün | /stop | yazın💢 \n\nReklam və əməkdaşlıq üçün |  @Rauffj  |', reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data == "reytinq")
def handle_callback_query(call):
    top_users = get_top_users()
    if top_users:
        reytinq_message = "🏆 Reytinq 🏆\n\n╰┈➤"
        for i, (username, xal) in enumerate(top_users, start=1):
            reytinq_message += f"{i}. @{username}: {xal} xal\n"
    else:
        reytinq_message = "Hələ heç kim xal toplamayıb."
    bot.send_message(call.message.chat.id, reytinq_message)

@bot.message_handler(commands=['stop'], chat_types=['supergroup'])
def stop_supergroup(message):
    global game_running
    if message.from_user.id in [admin.user.id for admin in bot.get_chat_administrators(message.chat.id)] or message.from_user.id == message.chat.id:
      game_running = False
      bot.send_message(message.chat.id, 'Oyun Dayandırıldı✋🏻🛑⛔️ \n\n Yenidən başlamaq üçün /start yazın 🚀')
    else:
      bot.send_message(message.chat.id, 'Siz admin deyilsiniz! ❌ Botu dayandırmaq üçün admin olmalısınız 🚫')

@bot.message_handler(commands=['cavab'], chat_types=['supergroup'])
def reveal_answer_and_penalty(message):
    global current_tapmaca
    username = message.from_user.username
    if not username:  
        username = f"user_{message.from_user.id}"
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT xal FROM istifadeciler WHERE username=?", (username,))
    row = c.fetchone()
    if row:
        user_points = row[0]
        if user_points >= 10:
            bot.send_message(message.chat.id, f"Tapmacanın Cavabı: {current_tapmaca['answer']}")
            c.execute("UPDATE istifadeciler SET xal=xal-10 WHERE username=?", (username,))
            conn.commit()
            bot.send_message(message.chat.id, "Cavabi Tapa Bilmediniz 😔? Olsun Daha Cox Tapmacalarimiz var😁 ")
            bot.send_message(message.chat.id, f"@{username} Sizin Umumi Xaliniz: {user_points - 10}")
            bot.send_message(message.chat.id, "Yeni Tapmaca Gelirrr⏰📦")
            time.sleep(4)
            bot.send_message(message.chat.id, f"Tapmaca: {current_tapmaca['question']}❓\n\n\nCAVABINIZI YAZIN🤔🧠")
        else:
            bot.send_message(message.chat.id, "Xaliniz 10-dan az olduğu üçün cavabı deye bilmerem 😶")
    else:
        bot.send_message(message.chat.id, "Teesufki, belə bir istifadəçi tapılmadı.")
    conn.close()

@bot.message_handler(chat_types=['supergroup'], commands=['start'])
def start_supergroup(message):
    global game_running, current_tapmaca
    if message.from_user.id in [admin.user.id for admin in bot.get_chat_administrators(message.chat.id)] or message.from_user.id == message.chat.id:
        game_running = True
        current_tapmaca = get_random_tapmaca()
        bot.send_message(message.chat.id, 'Oyun Başladı! 🎮✨ \n\n Cavabı Tapa Bilmesez | /cavab | yazaraq cavabı oyrene bilersiz 📬')
        bot.send_message(message.chat.id, f"Tapmaca: {current_tapmaca['question']}❓❓❓\n\n\nCAVABINIZI YAZIN🤔🧠")
    else:
        bot.send_message(message.chat.id, 'Siz admin deyilsiniz! ❌ Botu başlatmaq üçün admin olmalısınız 🚫')

@bot.message_handler(func=lambda message: True, chat_types=['supergroup'])
def handle_group_messages(message):
    global current_tapmaca, game_running
    if game_running:
        print(f"Received message: {message.text.lower()}")  # Debugging line
        print(f"Expected answer: {current_tapmaca['answer'].lower()}")  # Debugging line
        if message.text.lower() == current_tapmaca['answer'].lower():
            username = message.from_user.username
            if not username:  
                username = f"user_{message.from_user.id}"
            user_points = add_or_update_user(username, 3)
            bot.send_message(message.chat.id, f"DÜZGÜN CAVAB! {current_tapmaca['answer']}-idi Tebrikler 「 ✦ @{username} ✦ 」 🎉\n\n HESABINIZA +3 XAL ELAVE EDiLDi💰 \n\nSenin Umumi Xalin: {user_points}")
            current_tapmaca = get_random_tapmaca()
            bot.send_message(message.chat.id, f"Yeni Tapmaca Gelirrr⏰📦")
            time.sleep(5)
            bot.send_message(message.chat.id, f"Tapmaca: {current_tapmaca['question']}❓\n\n\nCAVABINIZI YAZIN🤔🧠")
        elif message.text.lower() == '/reytinq':
            top_users = get_top_users()
            if top_users:
                reytinq_message = "🏆 Reytinq 🏆\n\n╰┈➤"
                for i, (username, xal) in enumerate(top_users, start=1):
                    reytinq_message += f"{i}. @{username}: {xal} xal\n\n\n 1-xal ≈ 0,00009azn teskil edir."
            else:
                reytinq_message = "Hələ heç kim xal toplamayıb."
            bot.send_message(message.chat.id, reytinq_message)

bot.polling()
