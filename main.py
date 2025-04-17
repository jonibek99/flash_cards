from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update, ReplyKeyboardMarkup
import sqlite3
import wikipediaapi
from googletrans import Translator
from tinydb import TinyDB,Query
chat = TinyDB('id.json')
wiki_wiki = wikipediaapi.Wikipedia(
    user_agent="MyTelegramBot/1.0 (contact: example@email.com)", 
    language="en"
)

conn = sqlite3.connect("students.db") 
cursor = conn.cursor()

def words(update, context):
    reply_key = [[ '➕ Add Words ✍️'],
                 ['📜 Show All Words 📚', '🌍 Show All Translations 🌐'],
                 ['❌ Exit 🚪']
                 ]
    key = ReplyKeyboardMarkup(reply_key, resize_keyboard=True)
    update.message.reply_text("Please choose one of the options below ⬇️:", reply_markup=key)

def test(update, context):
    reply_key = [['🏁 Begin 🏃‍♂️', '📊 Show Result 📈'],     
                 ['❌ Exit 🚪']]
    key = ReplyKeyboardMarkup(reply_key, resize_keyboard=True)
    update.message.reply_text("Please choose one of the options below ⬇️:", reply_markup=key)

def add_data(update, context):
    update.message.reply_text("Please send the topic name and word in the following format: topic_name*word ✍️")

def start(update, context):
    Student = Query()
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    existing_user = chat.search(Student.chat_id == chat_id)
   
    if not existing_user:
        chat.insert({'chat_id': chat_id})
    relpy_key =[['📚 Words 🏫', '👨‍🏫 TEST 🎓']]
    key = ReplyKeyboardMarkup(relpy_key)
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)
    user_username = update.message.from_user.username
    if user_username:
        update.message.reply_text(f"Hello, @{user_username}! 👋 To start using this bot, please choose one of the buttons below. 📲", reply_markup=key)
    else:
        user_first_name = update.message.from_user.first_name
        update.message.reply_text(f"Hello, {user_first_name}! 👋 To start using this bot, please choose one of the buttons below. 📲", reply_markup=key)

    conn = sqlite3.connect("students.db") 
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY,
        topic TEXT,
        word TEXT,
        definition TEXT,
        uzbek TEXT
        )
    """)

def add_word(update, context, text):
    try:
        user_id = update.message.from_user.id
        table_name = 'a' + str(user_id)
        matn = text.split('*')
        topic_name = matn[0]
        word = matn[1]
        translator = Translator()
        result = translator.translate(word, src='en', dest='uz')
        page = wiki_wiki.page(word)
        if not page.exists():
            update.message.reply_text(f"❌ Sorry, no definition found for '{word}'.")
            return
        summary = page.summary
        sentences = summary.split('. ')
        short_definition = '. '.join(sentences[:1])
        clean_definition = short_definition.replace(word, "This term").replace(word.capitalize(), "This term")
        conn = sqlite3.connect("students.db") 
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO {table_name} (topic, word, definition, uzbek)
            VALUES (?, ?, ?, ?)
        """, (topic_name, word, clean_definition, result.text))
        conn.commit() 
        update.message.reply_text(f'{topic_name} is created topc and add this word {word}')
    except Exception as e:
        update.message.reply_text(f"❌ Error occurred: {e}")

def show_words(update, context):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)

    cursor.execute(f"SELECT topic, word, definition FROM {table_name}")  
    rows = cursor.fetchall()

    topics = {}
    for topic, word, definition in rows:
        if topic not in topics:
            topics[topic] = []
        topics[topic].append((word, definition))

    if not topics:
        update.message.reply_text("❌ You don't have any words saved yet.")
        return

    message = ""
    for i, (topic, words) in enumerate(topics.items(), 1):
        message += f"\n📚 {i}. **Topic Name:** _{topic}_ ({len(words)} words):\n"
        for j, (word, definition) in enumerate(words, 1):
            message += f"    {j}) {word} — {definition}\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"

    update.message.reply_text(message, parse_mode='Markdown')

def show_uzbek(update, context):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)

    cursor.execute(f"SELECT topic, word, uzbek FROM {table_name}")  
    rows = cursor.fetchall()

    topics = {}
    for topic, word, uzbek in rows:
        if topic not in topics:
            topics[topic] = []
        topics[topic].append((word, uzbek))

    if not topics:
        update.message.reply_text("❌ You don't have any words saved yet.")
        return

    message = ""
    for i, (topic, words) in enumerate(topics.items(), 1):
        message += f"\n📚 {i}. **Topic Name:** _{topic}_ ({len(words)} words):\n"
        for j, (word, uzbek) in enumerate(words, 1):
            message += f"    {j}) {word} — {uzbek}\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"

    update.message.reply_text(message, parse_mode='Markdown')

def check(update, context):
    global chat
    text = update.message.text.lower().strip()
    if text.startswith('*123'):
        message_to_send = text[4:].strip()
        if not message_to_send:
            update.message.reply_text("⚠️ Message cannot be empty! 📢")
            return
        for user in chat.all():
            try:
                context.bot.send_message(chat_id=user['chat_id'], text=f"📢 Message from Admin: {message_to_send}")
            except Exception as e:
                print(f"Error: {e}")
        update.message.reply_text("✅ Message sent to all users! 🚀")
        return
    if '*' in text:
        add_word(update, context, text)

    

updater = Updater('7981798770:AAGbSqQmu-Z4JJ5kD8P-wFwIIWaUvWmCOV4', use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text('📚 Words 🏫'), words))
dispatcher.add_handler(MessageHandler(Filters.text('👨‍🏫 TEST 🎓'), test))

dispatcher.add_handler(MessageHandler(Filters.text('🌍 Show All Translations 🌐'), show_uzbek))
dispatcher.add_handler(MessageHandler(Filters.text('➕ Add Words ✍️'), add_data))
dispatcher.add_handler(MessageHandler(Filters.text('❌ Exit 🚪'), start))
dispatcher.add_handler(MessageHandler(Filters.text('📜 Show All Words 📚'), show_words))
dispatcher.add_handler(MessageHandler(Filters.text, check))

updater.start_polling()
updater.idle()
