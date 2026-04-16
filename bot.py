import telebot
import sqlite3
from telebot.types import ReplyKeyboardMarkup

TOKEN = "8772123157:AAGRWDoBIx2S30QHBa0lgtMgJSQEY0TsJRs"
bot = telebot.TeleBot(TOKEN)

# ================= DATABASE (SAFE VERSION) =================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS ustalar (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
phone TEXT,
job TEXT,
about TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS ishlar (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
phone TEXT,
about TEXT
)
""")

conn.commit()

# ================= MENU =================
def menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("🧑‍🔧 Usta ro‘yxatdan o‘tish")
    m.row("📢 Ish joylash")
    m.row("🧑‍🔧 Ustalar ro‘yxati")
    m.row("📋 Ishlar ro‘yxati")
    return m

# ================= START =================
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "👋 Xush kelibsiz!\nUsta-Ish bot", reply_markup=menu())

# ================= FLOW =================
step = {}
data = {}

# ================= USTA START =================
@bot.message_handler(func=lambda m: m.text == "🧑‍🔧 Usta ro‘yxatdan o‘tish")
def usta_start(m):
    data[m.chat.id] = {}
    step[m.chat.id] = "u_name"
    bot.send_message(m.chat.id, "👤 Ismingiz:")

# ================= ISH START =================
@bot.message_handler(func=lambda m: m.text == "📢 Ish joylash")
def ish_start(m):
    data[m.chat.id] = {}
    step[m.chat.id] = "i_name"
    bot.send_message(m.chat.id, "👤 Ismingiz:")

# ================= MAIN FLOW =================
@bot.message_handler(func=lambda m: m.chat.id in step)
def flow(m):
    s = step[m.chat.id]

    # ========== USTA ==========
    if s == "u_name":
        data[m.chat.id]["name"] = m.text
        step[m.chat.id] = "u_phone"
        bot.send_message(m.chat.id, "📞 Telefon:")

    elif s == "u_phone":
        data[m.chat.id]["phone"] = m.text
        step[m.chat.id] = "u_job"
        bot.send_message(m.chat.id, "🛠 Kasb:")

    elif s == "u_job":
        data[m.chat.id]["job"] = m.text
        step[m.chat.id] = "u_about"
        bot.send_message(m.chat.id, "🧑 O‘zingiz haqida:")

    elif s == "u_about":
        d = data[m.chat.id]

        cur.execute("""
        INSERT INTO ustalar (name, phone, job, about)
        VALUES (?, ?, ?, ?)
        """, (d["name"], d["phone"], d["job"], m.text))
        conn.commit()

        bot.send_message(
            m.chat.id,
            f"""✅ Usta qo‘shildi!

👤 {d['name']}
📞 {d['phone']}
🛠 {d['job']}
🧑 {m.text}""",
            reply_markup=menu()
        )

        step.pop(m.chat.id, None)
        data.pop(m.chat.id, None)

    # ========== ISH ==========
    elif s == "i_name":
        data[m.chat.id]["name"] = m.text
        step[m.chat.id] = "i_phone"
        bot.send_message(m.chat.id, "📞 Telefon:")

    elif s == "i_phone":
        data[m.chat.id]["phone"] = m.text
        step[m.chat.id] = "i_about"
        bot.send_message(m.chat.id, "📢 Ish haqida:")

    elif s == "i_about":
        d = data[m.chat.id]

        cur.execute("""
        INSERT INTO ishlar (name, phone, about)
        VALUES (?, ?, ?)
        """, (d["name"], d["phone"], m.text))
        conn.commit()

        bot.send_message(
            m.chat.id,
            f"""📢 Ish joylandi!

👤 {d['name']}
📞 {d['phone']}
📢 {m.text}""",
            reply_markup=menu()
        )

        step.pop(m.chat.id, None)
        data.pop(m.chat.id, None)

# ================= USTALAR LIST =================
@bot.message_handler(func=lambda m: m.text == "🧑‍🔧 Ustalar ro‘yxati")
def ustalar(m):
    cur.execute("SELECT name, phone, job, about FROM ustalar")
    rows = cur.fetchall()

    if not rows:
        bot.send_message(m.chat.id, "❌ Ustalar yo‘q")
        return

    text = "🧑‍🔧 USTALAR:\n\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}. 👤 {r[0]}\n📞 {r[1]}\n🛠 {r[2]}\n🧑 {r[3]}\n\n"

    bot.send_message(m.chat.id, text)

# ================= ISHLAR LIST =================
@bot.message_handler(func=lambda m: m.text == "📋 Ishlar ro‘yxati")
def ishlar(m):
    cur.execute("SELECT name, phone, about FROM ishlar")
    rows = cur.fetchall()

    if not rows:
        bot.send_message(m.chat.id, "❌ Ishlar yo‘q")
        return

    text = "📋 ISHLAR:\n\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}. 👤 {r[0]}\n📞 {r[1]}\n📢 {r[2]}\n\n"

    bot.send_message(m.chat.id, text)

# ================= RUN =================
bot.infinity_polling(skip_pending=True)