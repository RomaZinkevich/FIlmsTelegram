import telebot
from telebot import types
import sqlite3
import datetime


# токен необходимый для работы бота
TOKEN = '1820942989:AAFl17YwrZAo7vbubZqsViIIXsnpbAWnjow'
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
item7 = types.KeyboardButton("Удалить и выдать предупреждение автору 😡")
admin_markup.add(item1, item2, item3, item4, item5, item6, item7)

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


@bot.message_handler(commands=['warn'])
def warn(message):
    if message.from_user.id in ADMINS_ID:
        try:
            text = message.text[6:]

            con = sqlite3.connect("db.db")
            cur = con.cursor()

            users_to_text = []
            users = cur.execute("SELECT * FROM users").fetchall()
            for i in users:  # +1 к warn
                if text in str(i[1]).split(";"):
                    users_to_text.append(i[0])
                    if int(i[2]) < 3:
                        if str(i[2]) == '2':
                            banned = 1
                        else:
                            banned = int(i[3])
                        warns = int(i[2]) + 1
                        cur.execute(
                            "UPDATE users SET warns=?,banned=? WHERE id=?", (warns, banned, i[0]))
            con.commit()
            con.close()

            for i in users_to_text:
                bot.send_message(
                    i, "Вам было выдано предупреждение за заказ несуществующего фильма. Три таких предупреждения приводят к невозможности больше заказать фильм")

            # удаление фильма из базы данных
            delete(f'/delete {text}', from_another_func=True, message_id=message.chat.id)
        except:
            bot.send_message(
                message.chat.id, "Где-то возникла ошибка", reply_markup=admin_markup)


@bot.message_handler(commands=['delete'])
def delete(message, from_another_func=False, message_id=0):
    if from_another_func:  # проверка на то откуда запущена функция
        id_from_user = message_id
        film_id = message[8:]
    else:
        id_from_user = message.chat.id
        film_id = message.text[8:]

    if id_from_user in ADMINS_ID:
        try:
            con = sqlite3.connect("db.db")
            cur = con.cursor()

            last_film = cur.execute(
                "SELECT * FROM films ORDER BY id").fetchall()
            last_film = last_film[-1]
            last_id, name, votes, dates = last_film

            con.close()

            is_deletable = del_from_films(
                film_id, cur, last_id, name, votes, dates, id_from_user)
            if not is_deletable:  # проверка на успешность удаления
                return 0
            last_id = str(last_id)
            del_from_users(film_id, cur, last_id)

            bot.send_message(
                id_from_user, "Успешно удалено", reply_markup=admin_markup)
        except:
            bot.send_message(
                id_from_user, "Где-то возникла ошибка", reply_markup=admin_markup)


@bot.message_handler(commands=['tech_works'])
def tech_works(message):
    if message.from_user.id in ADMINS_ID:
        try:
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            text = message.text[12:]
            flag = cur.execute("SELECT flag FROM works").fetchone()[0]

            if text == "start":  # проверка что именно делать
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
                    message.chat.id, msg)

            con.commit()
            con.close()
        except:
            bot.send_message(
                message.chat.id, "Где-то возникла ошибка", reply_markup=admin_markup)


@bot.message_handler(commands=['text'])  # красивое оформление текста
def text(message):
    if message.from_user.id in ADMINS_ID:
        try:
            text = message.text[5:]
            text = text[1:]
            text = text.split(';')
            name, year, rate, time, voiceover, genre, age, rezh, roles, desc = text
            bot.send_message(
                message.chat.id, f'🎥 {name} 🎥\n📆 Год: {year} 📆\n📊 Кинопоиск: {rate} 📊\n⏰ Продолжительность: {time} ⏰\n🎤 Озвучка: {voiceover} 🎤\n💾 Жанр: {genre} 💾\n👨‍👩‍👦 Возраст: {age} 👨‍👩‍👦\n🙍‍♂️Режиссёр: {rezh} 🙍‍♂️\n👨‍👨‍👦‍👦 В ролях: {roles} 👨‍👨‍👦‍👦\n\n✉️ Описание: {desc}', reply_markup=admin_markup)
        except:
            bot.send_message(
                message.chat.id, "Где-то возникла ошибка", reply_markup=admin_markup)


@bot.message_handler(commands=['offers'])
def offers(message):
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
                    if i in str(j[2]) and str(j[0]) not in results:
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
            else:  # если список фильмов в БД пуст
                bot.send_message(
                    message.chat.id, "Заказов пока нет", reply_markup=admin_markup)
        except:
            bot.send_message(
                message.chat.id, "Где-то возникла ошибка", reply_markup=admin_markup)


@bot.message_handler(content_types=['text'])
def write(message):
    try:
        # подготовка основных переменных
        text = message.text
        is_admin = message.chat.id in ADMINS_ID

        con = sqlite3.connect("db.db")
        cur = con.cursor()
        is_works = cur.execute("SELECT flag FROM works").fetchone()[0]
        is_banned = cur.execute(
            "SELECT banned FROM users WHERE id=?", (message.chat.id,)).fetchone()

        try:  # проверка на существование banned у пользователя
            is_banned = is_banned[0]
        except:
            pass

        # проверка на включение технических работа
        if not is_admin:
            if is_works:
                bot.send_message(
                    message.chat.id, 'Идут технические работы 👷🏻‍♂️. Напишите позже')
                return 0
            elif is_banned:
                bot.send_message(
                    message.chat.id, 'Извините, но вы были заблокированы за заказ несуществующих фильмов 😮')
                return 0
        con.close()

        cur_markup = markup  # По умолчанию клавиатура обычная

        if is_admin:  # Выбор правильной клавиатуры (админская/обычная)
            cur_markup = admin_markup

            # функции админа для управления каналом
            if text == 'Посмотреть заказы 💾':
                bot.send_message(
                    message.chat.id, 'Формат сообщения должен быть: {/offers day/week/month}')
                return 0
            elif text == "Создать текст ✉️":
                bot.send_message(
                    message.chat.id, 'Формат сообщения должен быть: /text {Название};{Год};{Рейтинг кинопоиска};{Продолжительность};{Озвучка};{Жанр};{Возраст};{Режиссёр};{В ролях};{Описание}\n')
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
            elif text == "Удалить и выдать предупреждение автору 😡":
                bot.send_message(
                    message.chat.id, 'Формат сообщения должен быть: /warn {id фильма}\n')
                return 0
        # недопустимые значения в названии фильма
        if len(text) > 123 or "\n" in text or ';' in text or "/" in text:
            bot.send_message(
                message.chat.id, "Не очень похоже на название фильма 👀")
            return 0
        # Вывод формата для заказа фильма
        if text == "Заказать фильм 🎥":
            bot.send_message(
                message.chat.id, 'Формат заказа: {Название фильма (точное название с афиши)}',
                reply_markup=types.ReplyKeyboardRemove())
        else:  # Обработка названия фильма
            make_offer(text, message, cur_markup)

    except:
        bot.send_message(
            message.chat.id, f'Что-то пошло не так',
            reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(
            322846366, f'Что-то пошло не так, ты дурач3к',
            reply_markup=types.ReplyKeyboardRemove())  # Отправка сообщения создателю бота о поломке бота


def add_film(current_id, film_title, date, films_names, cur, film_id):  # добавление фильма в БД films
    if not films_names:  # Если БД films пустая
        cur.execute("INSERT INTO films VALUES (?, ?, ?, ?)",
                    (film_id, film_title, 1, date))
    elif (film_title,) not in films_names:  # Если БД films не пустая, но заказанного фильма там нет
        cur.execute("INSERT INTO films VALUES (?, ?, ?, ?)",
                    (film_id, film_title, 1, date))
    else:  # Если заказанный фильм есть в БД - обновить даты и голоса за этот фильм
        dates = cur.execute("SELECT dates,votes FROM films WHERE name=?", (film_title,)).fetchone(
        )
        new_dates, votes = dates

        new_dates += ';' + date
        votes = int(votes) + 1

        cur.execute("UPDATE films SET votes=?,dates=? WHERE name=?",
                    (votes, new_dates, film_title))


def make_offer(text, message, cur_markup):  # добавление фильма во все БД
    # подготовка основных переменных
    current_id = message.from_user.id
    film_title = text.lower()

    # получение нынешней даты и оформление её для БД
    now = datetime.datetime.now()
    now_month = now.month
    now_day = now.day
    date = str(now_month) + '-' + str(now_day)

    con = sqlite3.connect("db.db")
    cur = con.cursor()

    users_films = cur.execute(
        "SELECT films FROM users WHERE id=?", (current_id,)).fetchone()  # список желаемого, того кто заказал фильм
    films_names = cur.execute(
        "SELECT name FROM films").fetchall()  # имена всех фильмов за которые когда-либо голосовали
    film_id = cur.execute(
        "SELECT id FROM films WHERE name=?", (str(film_title),)).fetchone()  # ID фильма за который проголосовал пользователь
    last_id = cur.execute(
        "SELECT id FROM films ORDER BY id").fetchall()  # ID последнего фильма в БД

    if last_id:  # если фильмы в БД есть, то записываем ID последнего
        last_id = last_id[-1][0]
    else:
        last_id = 0  # иначе ID последнего по сути равно 0

    if not film_id:  # если фильма за который проголосовали нет в БД, дать ему ID последнего+1
        film_id = last_id + 1
    else:  # иначе оставить ему свой ID
        film_id = film_id[0]

    if not users_films:  # если пользователь еще ни за что не голосовал, нужно добавить его в БД
        cur.execute("INSERT INTO users VALUES (?, ?,?,?)",
                    (current_id, film_id, 0, 0))

        add_film(current_id, film_title, date, films_names,
                 cur, film_id)  # Добавление фильма в БД films

        bot.send_message(
            message.chat.id, "Ваш фильм добавлен в очередь❗️", reply_markup=cur_markup)
        bot.send_message(
            message.chat.id, 'Если вы хотите помочь нашему каналу в развитии можете отправить произвольную сумму на карту ➡️ \n4274 3200 7290 8869')
    else:  # если пользователь уже голосовал за что-то
        users_films = str(users_films[0])

        # если выбранный фильм уже есть в его списке желаемого
        if str(film_id) in users_films.split(';'):
            bot.send_message(
                message.chat.id, 'Извините, вы уже голосовали за этот фильм, но вы можете добавить другой', reply_markup=cur_markup)
        else:  # если выбранного фильма нет в списке желаемого, то добавить
            result_films = ''  # фильмы которые надо добавить в БД

            # переделка в нужный для БД формат
            for i in users_films.split(';'):
                result_films += i + ';'
            if result_films in ["None;", ";"]:
                result_films = ""
            result_films += str(film_id)

            cur.execute("UPDATE users SET films=? WHERE id=?",
                        (result_films, current_id))  # обновление пользователя в БД (новый список фильмов)

            add_film(current_id, film_title,
                     date, films_names, cur, film_id)  # Добавление фильма в БД films

            bot.send_message(
                message.chat.id, "Ваш фильм добавлен в очередь❗️", reply_markup=cur_markup)
            bot.send_message(
                message.chat.id, 'Если вы хотите помочь нашему каналу в развитии можете отправить произвольную сумму на карту ➡️ \n4274 3200 7290 8869')

    con.commit()
    con.close()


def del_from_films(film_id, cur, last_id, name, votes, dates, id_from_user):
    con = sqlite3.connect("db.db")
    cur = con.cursor()

    # если ID который нужен удалить меньше последнего из БД значит удалить ID невозможно
    if last_id < int(film_id):
        bot.send_message(id_from_user.chat.id, "Такого id не существует")
        return False

    cur.execute("DELETE FROM films WHERE id=?", (str(film_id),))
    # если последний ID больше чем выбранный, надо поставить фильм с последним ID на место удаленного
    if last_id > int(film_id):
        cur.execute("DELETE FROM films WHERE id=?", (last_id,))
        cur.execute("INSERT INTO films VALUES (?,?,?,?)",
                    (film_id, name, votes, dates))

    con.commit()
    con.close()
    return True


def del_from_users(film_id, cur, last_id):
    con = sqlite3.connect("db.db")
    cur = con.cursor()

    res = cur.execute(
        "SELECT * FROM users").fetchall()
    for i in res:
        deletable = film_id  # удаляемый ID
        films = str(i[1])
        if films and films != "None":  # Если список желаний пуст, то и нечего удалять
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

            cur.execute(
                "UPDATE users SET films=? WHERE id=?", (";".join(films_list), i[0]))

        con.commit()

    con.close()


def send_bd(message):
    f = open("db.db", "rb")
    bot.send_document(message.chat.id, f)  # отправка базы данных админу


bot.polling(none_stop=True)  # работа бота, пока тот не сломается
