import telebot
from telebot import types
import sqlite3

TOKEN = '1722315207:AAHRPALzJ_IFw6D26WgPKKj-ffECfGYIzr0'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id, 'Формат сообщения должен быть: {Название};{Год};{Рейтинг кинопоиска};{Продолжительность};{Жанр};{Возраст};{Режиссёр};{В ролях};{Описание}')


@bot.message_handler(content_types=['text'])
def write(message):
    text = message.text
    try:
        text = text.split(';')
        name, year, rate, time, genre, age, rezh, roles, desc = text
        bot.send_message(
            message.chat.id, f'''🎥 {name} 🎥
📆 Год: {year} 📆
📊 Кинопоиск: {rate} 📊
⏰ Продолжительность: {time} ⏰
💾 Жанр: {genre} 💾
👨‍👩‍👦 Возраст: {age} 👨‍👩‍👦
🙍‍♂️Режиссёр: {rezh} 🙍‍♂️
👨‍👨‍👦‍👦 В ролях: {roles} 👨‍👨‍👦‍👦

✉️ Описание: {desc}''')
    except:
        bot.send_message(
            message.chat.id, f'Где-то ты проебался')


bot.polling(none_stop=True)
