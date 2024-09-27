import telebot
from telebot import types
import threading
import time
import random
import string
from datetime import datetime, timedelta

API_TOKEN = '7402320205:AAGpLKWxempyGzfWSZDOW2WCPhkmNsJ-0P0'  # Вставьте токен вашего Telegram-бота
YOUR_ADMIN_ID = 714244082  # Вставьте сюда ваш Telegram ID (или ID администратора)
ADMIN_CHAT_ID = 714244082  # ID чата для администраторов (где админы получают уведомления)

bot = telebot.TeleBot(API_TOKEN)

# Временные словари для хранения лицензий и пользователей
licenses = {}  # Здесь будут храниться сгенерированные ключи
users = {}  # Храним здесь пользователей с активными лицензиями и временем окончания подписки




def generate_license_key():
    """Генерация случайного лицензионhsного ключа."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def check_license(user_id):
    """Проверяет, есть ли у пользователя активная лицензия."""
    user_data = users.get(user_id)
    if user_data:
        expiration_date = user_data['expiration_date']
        return datetime.now() < expiration_date
    return False

def add_license(user_id, license_key):
    """Активирует лицензию для пользователя на 30 дней."""
    if licenses.get(license_key):
        expiration_date = datetime.now() + timedelta(days=30)
        users[user_id] = {'license': license_key, 'expiration_date': expiration_date}
        del licenses[license_key]  # Удаляем ключ после использования
        return True
    return False

# Создание тестового лицензионного ключа
TEST_LICENSE_KEY = "TEST1234567890"  # Пример тестового ключа, который активирует подписку на 30 дней

# Основная команда /start

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    enter_key_btn = types.InlineKeyboardButton("🔑 Ввести лицензионный ключ", callback_data="enter_license")
    buy_key_btn = types.InlineKeyboardButton("💳 Купить лицензионный ключ", callback_data="buy_license")
    test_key_btn = types.InlineKeyboardButton("🆓 Активировать тестовый ключ", callback_data="activate_test_key")
    back_btn = types.InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
    markup.add(enter_key_btn, buy_key_btn, test_key_btn, back_btn)

    welcome_message = (
        "*Здравствуйте, {message.from_user.first_name}*\n\n"
        "Добро пожаловать в наш бот. У вас нет активной лицензии. Выберите действие:\n\n"
        "🔑 *Ввести лицензионный ключ* - если у вас уже есть ключ.\n"
        "💳 *Купить лицензионный ключ* - для покупки нового ключа.\n"
        "🆓 *Активировать тестовый ключ* - для активации тестового ключа.\n"
        "🏠 *Главное меню* - вернуться в главное меню."
    )

    if check_license(message.from_user.id):
        show_main_menu(message)
    else:
        bot.send_message(message.chat.id, welcome_message, parse_mode='Markdown', reply_markup=markup)

def collect_support_ticket(message):
    user_id = message.from_user.id
    username = message.from_user.username
    ticket_content = message.text
    ticket_message = f"Новый тикет от @{username} (ID: {user_id}):\n\n{ticket_content}"
    bot.send_message(ADMIN_CHAT_ID, ticket_message)
    bot.send_message(message.chat.id, "Ваш тикет отправлен в техподдержку. Спасибо!")

@bot.callback_query_handler(func=lambda call: True)
def handle_user_callback(call):
    if call.data == "support":
        msg = bot.send_message(call.message.chat.id, "Пожалуйста, опишите вашу проблему:")
        bot.register_next_step_handler(msg, collect_support_ticket)
    elif call.data == "admin_panel":
        if call.from_user.id == YOUR_ADMIN_ID:
            show_admin_panel(call.message)
        else:
            bot.send_message(call.message.chat.id, "Эта команда доступна только администратору.")
    # ... other callbacks ...


    if call.data == "enter_license":
        msg = bot.send_message(call.message.chat.id, "Пожалуйста, введите лицензионный ключ:")
        bot.register_next_step_handler(msg, activate_license)
    elif call.data == "buy_license":
        bot.send_message(call.message.chat.id, "Пожалуйста, свяжитесь с администратором для покупки лицензии.")
        notify_admin_purchase_request(call.from_user)
    elif call.data == "profile":
        send_profile_info(call.message)
    elif call.data == "subscription_status":
        send_subscription_status(call.message)
    elif call.data == "upload_video":
        ask_for_video(call.message)
    elif call.data == "back_to_main":
        show_main_menu(call.message)
    elif call.data == "activate_test_key":
        activate_license_test(call.message)
    elif call.data == "check_status":
        check_bot_status(call.message)


def check_bot_status(message):
    try:
        # Perform a simple check, e.g., checking the bot's uptime or a simple response
        bot.send_message(message.chat.id, "Бот работает нормально.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")
# Меню для пользователей с активной лицензией
def show_main_menu(message):
    markup = types.InlineKeyboardMarkup()
    profile_btn = types.InlineKeyboardButton("👤 Профиль", callback_data="profile")
    active_time_btn = types.InlineKeyboardButton("⏳ Активность подписки", callback_data="subscription_status")
    upload_video_btn = types.InlineKeyboardButton("📹 Загрузить видео в TikTok", callback_data="upload_video")
    check_status_btn = types.InlineKeyboardButton("📊 Проверить статус бота", callback_data="check_status")
    support_btn = types.InlineKeyboardButton("🆘 Тех поддержка", callback_data="support")
    admin_panel_btn = types.InlineKeyboardButton("🔧 Админ панель", callback_data="admin_panel")
    back_btn = types.InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
    markup.add(profile_btn, active_time_btn, upload_video_btn, check_status_btn, support_btn, admin_panel_btn, back_btn)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите действие:", reply_markup=markup)

# Обработка нажатий на inline-кнопки пользователей
@bot.callback_query_handler(func=lambda call: True)
def handle_user_callback(call):
    if call.data == "enter_license":
        msg = bot.send_message(call.message.chat.id, "Пожалуйста, введите лицензионный ключ:")
        bot.register_next_step_handler(msg, activate_license)
    elif call.data == "buy_license":
        bot.send_message(call.message.chat.id, "Пожалуйста, свяжитесь с администратором для покупки лицензии.")
        notify_admin_purchase_request(call.from_user)
    elif call.data == "profile":
        send_profile_info(call.message)
    elif call.data == "subscription_status":
        send_subscription_status(call.message)
    elif call.data == "upload_video":
        ask_for_video(call.message)
    elif call.data == "back_to_main":
        show_main_menu(call.message)
    elif call.data == "activate_test_key":
        activate_license_test(call.message)
    elif call.data == "check_status":
        check_bot_status(call.message)
    elif call.data == "support":
        support_request(call.message)

def support_request(message):
    bot.send_message(message.chat.id, "Пожалуйста, свяжитесь с нашей техподдержкой по email: support@example.com")

# Функция для активации тестового ключа
def activate_license_test(message):
    user_id = message.from_user.id
    expiration_date = datetime.now() + timedelta(days=30)
    users[user_id] = {'license': TEST_LICENSE_KEY, 'expiration_date': expiration_date}
    bot.send_message(message.chat.id, "Тестовый ключ успешно активирован на 30 дней!")
    show_main_menu(message)  # Показать меню после активации лицензии

# Функция для показа информации о профиле
def send_profile_info(message):
    user_data = users.get(message.from_user.id)
    if user_data:
        license_key = user_data['license']
        expiration_date = user_data['expiration_date']
        remaining_time = expiration_date - datetime.now()
        days, seconds = remaining_time.days, remaining_time.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        profile_info = (f"Ваш профиль:\n"
                        f"Лицензионный ключ: {license_key}\n"
                        f"Дата окончания подписки: {expiration_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Оставшееся время подписки: {days} дней, {hours} часов и {minutes} минут.")
        bot.send_message(message.chat.id, profile_info)
    else:
        bot.send_message(message.chat.id, "У вас нет активной подписки.")

# Функция для показа времени активности подписки
def send_subscription_status(message):
    user_data = users.get(message.from_user.id)
    if user_data:
        expiration_date = user_data['expiration_date']
        remaining_time = expiration_date - datetime.now()
        days, seconds = remaining_time.days, remaining_time.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        bot.send_message(message.chat.id, f"Ваша подписка активна ещё {days} дней, {hours} часов и {minutes} минут.")
    else:
        bot.send_message(message.chat.id, "У вас нет активной подписки.")

# Команда для активации лицензии
@bot.message_handler(commands=['license'])
def ask_for_license(message):
    msg = bot.send_message(message.chat.id, "Please enter your license key:")
    bot.register_next_step_handler(msg, activate_license)

def activate_license(message):
    license_key = message.text
    user_id = message.from_user.id

    if add_license(user_id, license_key):
        bot.send_message(message.chat.id, "License successfully activated!")
        show_main_menu(message)  # Show the main menu after activation
    else:
        bot.send_message(message.chat.id, "Invalid license key.")

# Функция загрузки видео
def ask_for_video(message):
    msg = bot.send_message(message.chat.id, "Отправьте видео для загрузки:")
    bot.register_next_step_handler(msg, process_video)

def process_video(message):
    video = message.video
    if video:
        bot.send_message(message.chat.id, "Видео получено. Загрузка на TikTok...")
        threading.Thread(target=upload_to_tiktok, args=(message,)).start()
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте корректное видео.")

def upload_to_tiktok(message):
    """Загрузка видео на TikTok (заглушка)."""
    time.sleep(5)  # Симуляция процесса загрузки
    bot.send_message(message.chat.id, "Ваше видео успешно загружено на TikTok!")

# Уведомление администратора о запросе на покупку лицензии
def notify_admin_purchase_request(user):
    """Отправляет сообщение в чат администраторов о запросе на покупку ключа."""
    message = f"Пользователь @{user.username} (ID: {user.id}) запросил покупку лицензионного ключа."
    bot.send_message(ADMIN_CHAT_ID, message)

# Инлайн-кнопки для администратора
@bot.message_handler(commands=['admin'])

def show_admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    generate_btn = types.InlineKeyboardButton("🆕 Создать лицензионный ключ", callback_data="generate_license")
    broadcast_btn = types.InlineKeyboardButton("📢 Рассылка", callback_data="broadcast")
    markup.add(generate_btn, broadcast_btn)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


def ask_for_broadcast(message):
    pass


@bot.callback_query_handler(func=lambda call: True)
def handle_admin_callback(call):
    if call.data == "generate_license" and call.from_user.id == YOUR_ADMIN_ID:
        license_key = generate_license_key()
        licenses[license_key] = True
        bot.send_message(call.message.chat.id, f"Новый лицензионный ключ: {license_key}")
    elif call.data == "broadcast" and call.from_user.id == YOUR_ADMIN_ID: ask_for_broadcast(call.message)
    # ... other admin callbacks ...
    # ... other admin callbacks ...
    # ... other admin callbacks ...
    def ask_for_broadcast(message):
        msg = bot.send_message(message.chat.id, "Введите сообщение для рассылки:")
        bot.register_next_step_handler(msg, broadcast_message)

    def broadcast_message(message):
        text = message.text
        for user_id in users:
            bot.send_message(user_id, text)
        bot.send_message(message.chat.id, "Сообщение успешно отправлено всем пользователям.")
    
    

# Обработка нажатий на инлайн-кнопки администратора
@bot.callback_query_handler(func=lambda call: True)
def handle_admin_callback(call):
    if call.data == "generate_license" and call.from_user.id == YOUR_ADMIN_ID:
        license_key = generate_license_key()
        licenses[license_key] = True
        bot.send_message(call.message.chat.id, f"Новый лицензионный ключ: {license_key}")
    elif call.data == "broadcast" and call.from_user.id == YOUR_ADMIN_ID:
        ask_for_broadcast(call.message)

# Команда для рассылки сообщения всем пользователям
def ask_for_broadcast(message):
    msg = bot.send_message(message.chat.id, "Введите сообщение для рассылки:")
    bot.register_next_step_handler(msg, broadcast_message)

def broadcast_message(message):
    text = message.text
    for user_id in users:
        bot.send_message(user_id, text)

# Запуск бота

print("Бот успешно запущен!")
bot.polling(none_stop=True)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    enter_key_btn = types.InlineKeyboardButton("🔑 Ввести лицензионный ключ", callback_data="enter_license")
    buy_key_btn = types.InlineKeyboardButton("💳 Купить лицензионный ключ", callback_data="buy_license")
    test_key_btn = types.InlineKeyboardButton("🆓 Активировать тестовый ключ", callback_data="activate_test_key")
    markup.add(enter_key_btn, buy_key_btn, test_key_btn)

    if check_license(message.from_user.id):
        show_main_menu(message)
    else:
        bot.send_message(message.chat.id, "Здравствуйте! У вас нет активной лицензии. Выберите действие:", reply_markup=markup)