import telebot
from telebot import types
import sqlite3
import datetime


TOKEN = '1820942989:AAFyDaAORsTc7Hy2gYT1mscO1vbZlB4KcH4'
bot = telebot.TeleBot(TOKEN)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item = types.KeyboardButton("Заказать фильм 🎥")
markup.add(item)

admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("Заказать фильм 🎥")
item2 = types.KeyboardButton("Посмотреть заказы 💾")
item3 = types.KeyboardButton("Создать текст ✉️")
item4 = types.KeyboardButton("Отправить БД 📝")
item5 = types.KeyboardButton("Удалить фильм из базы данных ❌")
item6 = types.KeyboardButton("Начать технические работы 👷🏻‍♂️")
item7 = types.KeyboardButton("Закончить технические работы 👷🏻‍♂️")
admin_markup.add(item1, item2, item3, item4, item5, item6, item7)

date_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("День")
item2 = types.KeyboardButton("Неделя")
item3 = types.KeyboardButton("Месяц")
date_markup.add(item1, item2, item3)

OFFER = 'Если вы хотите помочь нашему каналу в развитии можете отправить произвольную сумму на карту ➡️ \n4274 3200 7290 8869'


@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id in [322846366, 1042144066]:
        bot.send_message(
            message.chat.id, 'Выберите одно из действий ниже ⬇️', reply_markup=admin_markup)
    else:
        bot.send_message(
            message.chat.id, 'Привет, чтобы заказать фильм нажми кнопку ниже ⬇️', reply_markup=markup)


@bot.message_handler(commands=['delete'])
def welcome(message):
    if message.from_user.id in [322846366, 1042144066]:
        try:
            film_id = message.text[8:]

            con = sqlite3.connect("db.db")
            cur = con.cursor()

            last_film = cur.execute(
                "SELECT * FROM films ORDER BY id").fetchall()
            last_film = last_film[-1]
            last_id, name, votes, dates = last_film
            if last_id < int(film_id):
                bot.send_message(message.chat.id, "Такого id не существует")
                return 0
            cur.execute("DELETE FROM films WHERE id=?", (film_id,))
            if last_id > int(film_id):
                cur.execute("DELETE FROM films WHERE id=?", (last_id,))
                cur.execute("INSERT INTO films VALUES (?,?,?,?)",
                            (film_id, name, votes, dates))

            res = cur.execute(
                "SELECT * FROM users").fetchall()
            last_id = str(last_id)
            deletable = film_id
            for i in res:
                if deletable in str(i[1]).split(";"):
                    films = str(i[1])
                    last_id_check = str(i[1]).split(";")[-1]
                    first_id_check = str(i[1]).split(";")[0]
                    if last_id not in str(i[1]).split(";"):
                        last_id = deletable
                    if last_id != last_id_check:
                        films = films.replace(f'{last_id};', '')
                    elif last_id_check == first_id_check:
                        films = films.replace(f'{last_id}', '')
                    else:
                        films = films.replace(f';{last_id}', '')

                elif last_id in str(i[1]).split(";"):
                    films = str(i[1])
                    films = films.replace(f'{last_id}', '')
                if films:
                    cur.execute(
                        "UPDATE users SET films=? WHERE id=?", (films, i[0]))
                else:
                    cur.execute(
                        "DELETE FROM users WHERE id=?", (i[0],))
            con.commit()
            con.close()
            bot.send_message(
                message.chat.id, "Успешно удалено", reply_markup=admin_markup)
        except:
            bot.send_message(
                message.chat.id, "Ты дурак?", reply_markup=admin_markup)


@bot.message_handler(content_types=['text'])
def write(message):
    text = message.text
    try:
        is_admin = message.from_user.id in [322846366, 1042144066]
        cur_markup = markup

        con = sqlite3.connect("db.db")
        cur = con.cursor()
        is_works = cur.execute("SELECT flag FROM works").fetchone()[0]
        if is_works and not is_admin:
            bot.send_message(
                message.chat.id, 'Идут технические работы 👷🏻‍♂️. Напишите позже')
            return 0
        con.close()

        if is_admin:
            cur_markup = admin_markup
            if text == 'Посмотреть заказы 💾':
                bot.send_message(
                    message.chat.id, 'За какой период посмотреть заказы?',
                    reply_markup=date_markup)
                return 0
            elif text == "Создать текст ✉️":
                bot.send_message(
                    message.chat.id, 'Формат сообщения должен быть: ✉️{Название};{Год};{Рейтинг кинопоиска};{Продолжительность};{Перевод};{Жанр};{Возраст};{Режиссёр};{В ролях};{Описание}\n')
                return 0
            elif text[0] == '✉':
                text = text[1:]
                text = text.split(';')
                name, year, rate, time, translate, genre, age, rezh, roles, desc = text
                bot.send_message(
                    message.chat.id, f'''🎥 {name} 🎥
📆 Год: {year} 📆
📊 Кинопоиск: {rate} 📊
⏰ Продолжительность: {time} ⏰
🎤 Перевод: {translate} 🎤
💾 Жанр: {genre} 💾
👨‍👩‍👦 Возраст: {age} 👨‍👩‍👦
🙍‍♂️Режиссёр: {rezh} 🙍‍♂️
👨‍👨‍👦‍👦 В ролях: {roles} 👨‍👨‍👦‍👦

✉️ Описание: {desc}''', reply_markup=cur_markup)
                return 0
            elif text == 'Отправить БД 📝':
                f = open("db.db", "rb")
                bot.send_document(message.chat.id, f)
                return 0
            elif text in ["День", "Неделя", "Месяц"]:
                now = datetime.datetime.now()
                month = now.month
                day = now.day
                delta = datetime.timedelta(days=0)
                if text == 'День':
                    delta = datetime.timedelta(days=1)
                elif text == 'Неделя':
                    delta = datetime.timedelta(weeks=1)
                then = now - delta
                then_day, then_month, then_year = then.day, then.month, then.year
                if text == 'Месяц':
                    then_month = month - 1
                    if then_month <= 0:
                        then_month = 12
                        then_year = then.year - 1
                d1 = datetime.date(now.year, now.month, now.day)
                d2 = datetime.date(then_year, then_month, then_day)
                d3 = d1 - d2
                prev_dates = []
                for i in range(d3.days + 1):
                    dt = d2 + datetime.timedelta(i)
                    prev_dates.append(str(dt.month) + '-' + str(dt.day))
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                res = cur.execute(
                    "SELECT name,votes,dates,id FROM films").fetchall()
                con.close()
                results = {}
                names = []
                ids = []
                for i in prev_dates:
                    for j in res:
                        if i in j[2] and j[0] not in results:
                            results[j[0], j[3]] = j[1]
                text = ''
                if results:
                    results = sorted(results.items(), key=lambda x: x[1])
                    for i in results:
                        text += str(i[0][1]) + " " * (6 - len(str(i[0][1]))) + "|  " + str(i[1]) + " " * (6 - len(str(i[1]))) + \
                            "| " + i[0][0] + " " * \
                            (13 - len(i[0][0])) + '\n'
                    bot.send_message(
                        message.chat.id, "<pre><b>ID" + " " * 4 + "| " "Голоса" + " " + "| " + "Название\n" + "-" * 6 + "+" + "-" * 8 + "+" + "-" * 15 + "\n" + text + "</b></pre>", reply_markup=cur_markup, parse_mode='HTML')
                else:
                    bot.send_message(
                        message.chat.id, "Заказов пока нет", reply_markup=cur_markup)
                return 0
            elif text == "Начать технические работы 👷🏻‍♂️":
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                flag = cur.execute("SELECT flag FROM works").fetchone()[0]
                if not flag:
                    cur.execute("UPDATE works SET flag=1")
                    bot.send_message(
                        message.chat.id, "Технические работы начаты")
                else:
                    bot.send_message(
                        message.chat.id, "Технические работы уже начаты")
                con.commit()
                con.close()
                return 0
            elif text == "Закончить технические работы 👷🏻‍♂️":
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                flag = cur.execute("SELECT flag FROM works").fetchone()[0]
                if flag:
                    cur.execute("UPDATE works SET flag=0")
                    bot.send_message(
                        message.chat.id, "Технические работы закончены")
                else:
                    bot.send_message(
                        message.chat.id, "Технические работы не начаты")
                con.commit()
                con.close()
                return 0
            elif text == "Удалить фильм из базы данных ❌":
                bot.send_message(
                    message.chat.id, 'Формат сообщения должен быть: /delete {id фильма}\n')
                return 0
        elif len(text) > 123:
            bot.send_message(
                message.chat.id, "Не очень похоже на название фильма 👀")
            return 0
        if "\n" in text or ';' in text:
            bot.send_message(
                message.chat.id, "Не очень похоже на название фильма 👀")
            return 0
        if text == "Заказать фильм 🎥":
            bot.send_message(
                message.chat.id, 'Формат заказа: {Название фильма (точное название с афиши)}',
                reply_markup=types.ReplyKeyboardRemove())
        else:
            current_id = message.from_user.id
            film_title = text.lower()
            now = datetime.datetime.now()
            month = now.month
            day = now.day
            date = str(month) + '-' + str(day)
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            films = cur.execute(
                "SELECT films FROM users WHERE id=?", (current_id,)).fetchone()
            bdfilms = cur.execute(
                "SELECT name FROM films").fetchall()
            film_id = cur.execute(
                "SELECT id FROM films WHERE name=?", (str(film_title),)).fetchone()
            last_id = cur.execute(
                "SELECT id FROM films").fetchall()
            if last_id:
                last_id = last_id[-1][0]
            else:
                last_id = 0
            if not film_id:
                film_id = last_id + 1
            else:
                film_id = film_id[0]
            if not films:
                cur.execute("INSERT INTO users VALUES (?, ?)",
                            (current_id, film_id))
                add_film(current_id, film_title, date, bdfilms, cur, film_id)
                bot.send_message(
                    message.chat.id, "Ваш фильм добавлен в очередь❗️", reply_markup=cur_markup)
                bot.send_message(
                    message.chat.id, OFFER)
            else:
                films = str(films[0])
                if str(film_id) in films.split(';'):
                    bot.send_message(
                        message.chat.id, 'Извините, вы уже голосовали за этот фильм, но вы можете добавить другой', reply_markup=cur_markup)
                else:
                    mass_films = ''
                    for i in films.split(';'):
                        mass_films += i + ';'
                    mass_films += str(film_id)
                    cur.execute("UPDATE users SET films=? WHERE id=?",
                                (mass_films, current_id))
                    add_film(current_id, film_title,
                             date, bdfilms, cur, film_id)
                    bot.send_message(
                        message.chat.id, "Ваш фильм добавлен в очередь❗️", reply_markup=cur_markup)
                    bot.send_message(
                        message.chat.id, OFFER)
            con.commit()
            con.close()
    except exception as e:
        bot.send_message(
            message.chat.id, f'Что-то пошло не так',
            reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(
            322846366, f'Что-то пошло не так, ты дурач3к',
            reply_markup=types.ReplyKeyboardRemove())


def add_film(current_id, film_title, date, bdfilms, cur, film_id):
    if not bdfilms:
        cur.execute("INSERT INTO films VALUES (?, ?, ?, ?)",
                    (film_id, film_title, 1, date))
    elif (film_title,) not in bdfilms:
        cur.execute("INSERT INTO films VALUES (?, ?, ?, ?)",
                    (film_id, film_title, 1, date))
    else:
        dates = cur.execute("SELECT dates,votes FROM films WHERE name=?", (film_title,)).fetchone(
        )
        new_dates, votes = dates
        new_dates = new_dates + ';' + date
        votes = int(votes) + 1
        cur.execute("UPDATE films SET votes=?,dates=? WHERE name=?",
                    (votes, new_dates, film_title))


bot.polling(none_stop=True)

# {'content_type': 'text', 'id': 442, 'message_id': 442, 'from_user': {'id': 1042144066, 'is_bot': False, 'first_name': 'Max', 'username': None, 'last_name': 'Old', 'language_code': 'ru', 'can_join_groups': None, 'can_read_all_group_messages': None, 'supports_inline_queries': None}, 'date': 1626471987, 'chat': {'id': 1042144066, 'type': 'private', 'title': None, 'username': None, 'first_name': 'Max', 'last_name': 'Old', 'photo': None, 'bio': None, 'description': None, 'invite_link': None, 'pinned_message': None, 'permissions': None, 'slow_mode_delay': None, 'sticker_set_name': None, 'can_set_sticker_set': None, 'linked_chat_id': None, 'location': None}, 'forward_from': None, 'forward_from_chat': None, 'forward_from_message_id': None, 'forward_signature': None, 'forward_sender_name': None, 'forward_date': None, 'reply_to_message': None, 'edit_date': None, 'media_group_id': None, 'author_signature': None, 'text': '/start', 'entities': [<telebot.types.MessageEntity object at 0x035A2C40>], 'caption_entities': None, 'audio': None, 'document': None, 'photo': None, 'sticker': None, 'video': None, 'video_note': None, 'voice': None, 'caption': None, 'contact': None, 'location': None, 'venue': None, 'animation': None, 'dice': None, 'new_chat_member': None, 'new_chat_members': None, 'left_chat_member': None, 'new_chat_title': None, 'new_chat_photo': None, 'delete_chat_photo': None, 'group_chat_created': None, 'supergroup_chat_created': None, 'channel_chat_created': None, 'migrate_to_chat_id': None, 'migrate_from_chat_id': None, 'pinned_message': None, 'invoice': None, 'successful_payment': None, 'connected_website': None, 'reply_markup': None, 'json': {'message_id': 442, 'from': {'id': 1042144066, 'is_bot': False, 'first_name': 'Max', 'last_name': 'Old', 'language_code': 'ru'}, 'chat': {'id': 1042144066, 'first_name': 'Max', 'last_name': 'Old', 'type': 'private'}, 'date': 1626471987, 'text': '/start', 'entities': [{'offset': 0, 'length': 6, 'type': 'bot_command'}]}}


# markup_clothes = types.ReplyKeyboardMarkup(resize_keyboard=True)
# item1 = types.KeyboardButton("Низ")
# item2 = types.KeyboardButton("Верх")
# item3 = types.KeyboardButton("Обувь")
# item4 = types.KeyboardButton("Аксессуары")
# item5 = types.KeyboardButton("Главное меню")
# markup_clothes.add(item1, item2, item3, item4, item5)


# 1042144066 Максимка Шамин
# 322846366 Ромка Зинкевич
