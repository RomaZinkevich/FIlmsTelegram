import telebot
from telebot import types
import sqlite3
import datetime


# токен необходимый для работы бота
TOKEN = '1820942989:AAFyDaAORsTc7Hy2gYT1mscO1vbZlB4KcH4'
bot = telebot.TeleBot(TOKEN)

# клавиатура для обычных пользователей
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item = types.KeyboardButton("Заказать фильм 🎥")
markup.add(item)

admin_markup = types.ReplyKeyboardMarkup(
    resize_keyboard=True)  # клавиатура для админов
item1 = types.KeyboardButton("Заказать фильм 🎥")
item2 = types.KeyboardButton("Посмотреть заказы 💾")
item3 = types.KeyboardButton("Создать текст ✉️")
item4 = types.KeyboardButton("Отправить БД 📝")
item5 = types.KeyboardButton("Удалить фильм из базы данных ❌")
item6 = types.KeyboardButton("Технические работы 👷🏻‍♂️")
admin_markup.add(item1, item2, item3, item4, item5, item6)

OFFER = 'Если вы хотите помочь нашему каналу в развитии можете отправить произвольную сумму на карту ➡️ \n4274 3200 7290 8869'

# глобальная переменная с ID админов канала
ADMINS_ID = [322846366, 1042144066]


@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id in ADMINS_ID:  # разные сообщения для пользователей и админов
        bot.send_message(
            message.chat.id, 'Выберите одно из действий ниже ⬇️', reply_markup=admin_markup)
    else:
        bot.send_message(
            message.chat.id, 'Привет, чтобы заказать фильм нажми кнопку ниже ⬇️', reply_markup=markup)


@bot.message_handler(commands=['delete'])
def delete(message):
    if message.from_user.id in ADMINS_ID:
        try:
            con = sqlite3.connect("db.db")
            cur = con.cursor()

            # подготовка переменных
            film_id = message.text[8:]
            last_film = cur.execute(
                "SELECT * FROM films ORDER BY id").fetchall()
            last_film = last_film[-1]
            last_id, name, votes, dates = last_film

            del_from_films(film_id, cur, last_id, name, votes, dates, message)
            last_id = str(last_id)
            del_from_users(film_id, cur, last_id, name, votes, dates, message)

            con.commit()
            con.close()
            bot.send_message(
                message.chat.id, "Успешно удалено", reply_markup=admin_markup)
        except exception as e:
            bot.send_message(
                message.chat.id, "Ты дурак?", reply_markup=admin_markup)


@bot.message_handler(commands=['tech_works'])
def tech_works(message):
    if message.from_user.id in ADMINS_ID:
        try:
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            text = message.text[12:]
            flag = cur.execute("SELECT flag FROM works").fetchone()[0]

            if text == 'start':  # проверка что именно делать
                start = 1
            elif text == "end":
                start = 0

            if flag != start:  # если работы в том же состоянии в которое просят перевести бот ничего не пишет
                flag = abs(flag - 1)
                cur.execute("UPDATE works SET flag=?", (flag,))

                msg = "Технические работы закончены"
                if flag:  # правильное написание админу
                    msg = "Технические работы начаты"
                bot.send_message(
                    message.chat.id, "Технические работы начаты")

            con.commit()
            con.close()
        except exception as e:
            bot.send_message(
                message.chat.id, "Ты дурак?", reply_markup=admin_markup)


@bot.message_handler(commands=['text'])  # красивое оформление текста
def text(message):
    if message.from_user.id in ADMINS_ID:
        try:
            text = text[1:]
            text = text.split(';')
            name, year, rate, time, translate, genre, age, rezh, roles, desc = text
            bot.send_message(
                message.chat.id, f'🎥 {name} 🎥\n📆 Год: {year} 📆\n📊 Кинопоиск: {rate} 📊\n\
                ⏰ Продолжительность: {time} ⏰\n🎤 Перевод: {translate} 🎤\n💾 Жанр: {genre} \
                💾\n👨‍👩‍👦 Возраст: {age} 👨‍👩‍👦\n🙍‍♂️Режиссёр: {rezh} 🙍‍♂️\n👨‍👨‍👦‍👦 В ролях: {roles} 👨‍👨‍👦‍👦\n\
                \n✉️ Описание: {desc}', reply_markup=cur_markup)
        except exception as e:
            bot.send_message(
                message.chat.id, "Ты дурак?", reply_markup=admin_markup)


@bot.message_handler(commands=['offers'])
def day(message):
    if message.from_user.id in ADMINS_ID:
        try:
            text = message.text[8:]
            results, names, ids, prev_dates, text = {}, [], [], [], ''

            # подготовка переменных для будущей работы
            now = datetime.datetime.now()
            month = now.month
            day = now.day

            # подборка нужного количества времени по введенным данным
            delta = datetime.timedelta(days=0)
            if text == 'day':
                delta = datetime.timedelta(days=1)
            elif text == 'week':
                delta = datetime.timedelta(weeks=1)

            prev = now - delta
            prev_day, prev_month, prev_year = prev.day, prev.month, prev.year

            if text == 'month':
                prev_month = month - 1
                if prev_month <= 0:  # цикличность месяцев
                    prev_month = 12
                    prev_year = prev.year - 1

            # перевод настоящего времени в datetime модель
            now_dt = datetime.date(now.year, now.month, now.day)
            # перевод отсчитанного времени в datetime модель
            prev_dt = datetime.date(prev_year, prev_month, prev_day)
            range_dt = now_dt - prev_dt

            # получение всех дат между настойщим и отсчитанным временем
            for i in range(range_dt.days + 1):
                dt = prev_dt + datetime.timedelta(i)
                # преобразование дат в удобное для БД формат
                prev_dates.append(str(dt.month) + '-' + str(dt.day))

            con = sqlite3.connect("db.db")
            cur = con.cursor()
            res = cur.execute(
                "SELECT name,votes,dates,id FROM films").fetchall()
            con.close()

            for i in prev_dates:
                for j in res:
                    # проверка голосовали ли за фильм + проверка на наличие фильм в исходном словаре
                    if i in j[2] and j[0] not in results:
                        # исходный словарь с нужными данными для быстрой работы в телеграме
                        results[j[0], j[3]] = j[1]

            if results:
                # сортировка фильмов по кол-ву голосов за них (возр.)
                results = sorted(results.items(), key=lambda x: x[1])
                for i in results:
                    text += str(i[0][1]) + " " * (6 - len(str(i[0][1]))) + "|  " + str(i[1]) + " " * (6 - len(str(i[1]))) + \
                        "| " + i[0][0] + " " * \
                        (13 - len(i[0][0])) + '\n'
                text = "<pre><b>ID" + " " * 4 + "| " "Голоса" + " " + "| " + "Название\n" + \
                    "-" * 6 + "+" + "-" * 8 + "+" + "-" * 15 + "\n" + text + "</b></pre>"
                # преобразование результатов в удобную для восприятия таблицу

                bot.send_message(
                    message.chat.id, text, reply_markup=admin_markup, parse_mode='HTML')
            else:
                bot.send_message(
                    message.chat.id, "Заказов пока нет", reply_markup=admin_markup)
        except exception as e:
            bot.send_message(
                message.chat.id, "Ты дурак?", reply_markup=admin_markup)


@bot.message_handler(content_types=['text'])
def write(message):
    text = message.text
    try:
        is_admin = message.chat.id in ADMINS_ID
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        is_works = cur.execute("SELECT flag FROM works").fetchone()[0]
        if is_works and not is_admin:
            bot.send_message(
                message.chat.id, 'Идут технические работы 👷🏻‍♂️. Напишите позже')
            return 0
        con.close()
        cur_markup = markup
        if is_admin:  # функции админа для управления каналом
            cur_markup = admin_markup
            if text == 'Посмотреть заказы 💾':
                bot.send_message(
                    message.chat.id, 'Формат сообщения должен быть: \
                    {/offers day/week/month}')
                return 0
            elif text == "Создать текст ✉️":
                bot.send_message(
                    message.chat.id, 'Формат сообщения должен быть: /text{Название}\
                    ;{Год};{Рейтинг кинопоиска};{Продолжительность};{Перевод};\
                    {Жанр};{Возраст};{Режиссёр};{В ролях};{Описание}\n')
                return 0
            elif text == 'Отправить БД 📝':
                send_bd(message)
                return 0
            elif text == "Технические работы 👷🏻‍♂️":
                bot.send_message(
                    message.chat.id, "Формат сообщения должен быть: {/tech_works start/end}")
                return 0
            elif text == "Удалить фильм из базы данных ❌":
                bot.send_message(
                    message.chat.id, 'Формат сообщения должен быть: /delete {id фильма}\n')
                return 0
        # недопустимые значения в названии фильма
        if len(text) > 123 or "\n" in text or ';' in text:
            bot.send_message(
                message.chat.id, "Не очень похоже на название фильма 👀")
            return 0

        if text == "Заказать фильм 🎥":
            bot.send_message(
                message.chat.id, 'Формат заказа: {Название фильма (точное название с афиши)}',
                reply_markup=types.ReplyKeyboardRemove())
        else:
            make_offer()

            # current_id = message.from_user.id
            # film_title = text.lower()
            # now = datetime.datetime.now()
            # month = now.month
            # day = now.day
            # date = str(month) + '-' + str(day)
            # con = sqlite3.connect("db.db")
            # cur = con.cursor()
            # films = cur.execute(
            #     "SELECT films FROM users WHERE id=?", (current_id,)).fetchone()
            # bdfilms = cur.execute(
            #     "SELECT name FROM films").fetchall()
            # film_id = cur.execute(
            #     "SELECT id FROM films WHERE name=?", (str(film_title),)).fetchone()
            # last_id = cur.execute(
            #     "SELECT id FROM films").fetchall()
            # if last_id:
            #     last_id = last_id[-1][0]
            # else:
            #     last_id = 0
            # if not film_id:
            #     film_id = last_id + 1
            # else:
            #     film_id = film_id[0]
            # if not films:
            #     cur.execute("INSERT INTO users VALUES (?, ?)",
            #                 (current_id, film_id))
            #     add_film(current_id, film_title, date, bdfilms, cur, film_id)
            #     bot.send_message(
            #         message.chat.id, "Ваш фильм добавлен в очередь❗️", reply_markup=cur_markup)
            #     bot.send_message(
            #         message.chat.id, OFFER)
            # else:
            #     films = str(films[0])
            #     if str(film_id) in films.split(';'):
            #         bot.send_message(
            #             message.chat.id, 'Извините, вы уже голосовали за этот фильм, но вы можете добавить другой', reply_markup=cur_markup)
            #     else:
            #         mass_films = ''
            #         for i in films.split(';'):
            #             mass_films += i + ';'
            #         mass_films += str(film_id)
            #         cur.execute("UPDATE users SET films=? WHERE id=?",
            #                     (mass_films, current_id))
            #         add_film(current_id, film_title,
            #                  date, bdfilms, cur, film_id)
            #         bot.send_message(
            #             message.chat.id, "Ваш фильм добавлен в очередь❗️", reply_markup=cur_markup)
            #         bot.send_message(
            #             message.chat.id, OFFER)
            # con.commit()
            # con.close()
    except exception as e:
        bot.send_message(
            message.chat.id, f'Что-то пошло не так',
            reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(
            322846366, f'Что-то пошло не так, ты дурач3к',
            reply_markup=types.ReplyKeyboardRemove())  # Отправка сообщения создателю бота о поломке бота


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


def del_from_films(film_id, cur, last_id, name, votes, dates, message):
    # если ID который нужен удалить меньше последнего из БД значит удалить ID невозможно
    if last_id < int(film_id):
        bot.send_message(message.chat.id, "Такого id не существует")
        return 0
    cur.execute("DELETE FROM films WHERE id=?", (film_id,))
    # если последний ID больше чем выбранный, надо поставить фильм с последним ID на место удаленного
    if last_id > int(film_id):
        cur.execute("DELETE FROM films WHERE id=?", (last_id,))
        cur.execute("INSERT INTO films VALUES (?,?,?,?)",
                    (film_id, name, votes, dates))


def del_from_users(film_id, cur, last_id, name, votes, dates, message):
    res = cur.execute(
        "SELECT * FROM users").fetchall()
    for i in res:
        deletable = film_id  # удаляемый ID
        films = str(i[1])
        if films:  # Если список желаний пуст, то и нечего удалять
            films_list = films.split(";")
            last_user_id = 0
            first_user_id = 9999999999

            for j in films_list:  # выбор минимального и максимального ID
                j = int(j)
                if j > last_user_id:
                    last_user_id = j
                if j < first_user_id:
                    first_user_id = j
            last_user_id, first_user_id = str(last_user_id), str(first_user_id)

            # если удаляемый есть в списке желаний пользователя
            if deletable in films_list:
                # если последний ID есть в списке желаний надо удалить его
                if last_id in films_list:
                    deletable = last_id

                films_list.remove(deletable)

            # если последний ID есть в списке, а удаляемого нет, нужно удалить последний
            elif last_id in films_list:
                films_list.remove(last_id)
                films_list.append(deletable)

            # если новый желаемый список не пустой обновить, иначе удалить строку с данным пользователем
            if films_list:
                cur.execute(
                    "UPDATE users SET films=? WHERE id=?", (films, i[0]))
            else:
                cur.execute(
                    "DELETE FROM users WHERE id=?", (i[0],))


def send_bd(message):
    f = open("db.db", "rb")
    bot.send_document(message.chat.id, f)


bot.polling(none_stop=True)


# 1042144066 Максимка Шамин
# 322846366 Ромка Зинкевич
