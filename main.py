import requests
import random
import json
import time
import sqlite3
import os

# ═══════════════════════════════════════════
#  تنظیمات اولیه (خوانده شده از متغیرهای محیطی)
# ═══════════════════════════════════════════
TOKEN = os.getenv("TOKEN")
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "123456789")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip().isdigit()]
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "5752220430"))
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}/"

# ═══════════════════════════════════════════
#  داده‌های بازی
# ═══════════════════════════════════════════
COUNTRIES = {
    "usa": {"name": "آمریکا 🇺🇸", "budget": 1000, "bonus": "air", "bonus_val": 1.3, "flag": "🇺🇸"},
    "russia": {"name": "روسیه 🇷🇺", "budget": 950, "bonus": "tank", "bonus_val": 1.35, "flag": "🇷🇺"},
    "china": {"name": "چین 🇨", "budget": 900, "bonus": "soldier", "bonus_val": 1.3, "flag": "🇨🇳"},
    "india": {"name": "هند 🇮🇳", "budget": 750, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇮🇳"},
    "uk": {"name": "انگلستان 🇬🇧", "budget": 800, "bonus": "ship", "bonus_val": 1.3, "flag": "🇧"},
    "france": {"name": "فرانسه 🇷", "budget": 780, "bonus": "air", "bonus_val": 1.25, "flag": "🇫🇷"},
    "japan": {"name": "ژاپن 🇯🇵", "budget": 720, "bonus": "ship", "bonus_val": 1.3, "flag": "🇯🇵"},
    "turkey": {"name": "ترکیه 🇹🇷", "budget": 680, "bonus": "drone", "bonus_val": 1.35, "flag": "🇹🇷"},
    "iran": {"name": "ایران 🇮🇷", "budget": 700, "bonus": "missile", "bonus_val": 1.35, "flag": "🇮🇷"},
    "germany": {"name": "آلمان 🇩🇪", "budget": 760, "bonus": "tank", "bonus_val": 1.25, "flag": "🇩🇪"},
}

DEFAULT_EQUIPMENT = {
    "tank": {"name": "تانک 🛡️", "price": 80, "attack": 15, "defense": 20},
    "jet": {"name": "جنگنده ✈️", "price": 120, "attack": 25, "defense": 10},
    "ship": {"name": "ناو جنگی 🚢", "price": 150, "attack": 20, "defense": 25},
    "soldier": {"name": "سرباز ", "price": 50, "attack": 10, "defense": 10},
    "missile": {"name": "موشک 🚀", "price": 200, "attack": 35, "defense": 0},
    "defense": {"name": "پدافند 🛡️", "price": 130, "attack": 0, "defense": 30},
    "drone": {"name": "پهپاد 🤖", "price": 90, "attack": 18, "defense": 5},
}

# ═══════════════════════════════════════════
#  مدیریت پایگاه داده
# ═══════════════════════════════════════════
def init_db():
    conn = sqlite3.connect('war_game.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY, country TEXT, budget INTEGER,
            equipment TEXT, wins INTEGER DEFAULT 0, losses INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1, last_daily INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment_prices (eq_key TEXT PRIMARY KEY, price INTEGER)
    ''')
    cursor.execute("SELECT COUNT(*) FROM equipment_prices")
    if cursor.fetchone()[0] == 0:
        for eq_key, eq_data in DEFAULT_EQUIPMENT.items():
            cursor.execute("INSERT INTO equipment_prices (eq_key, price) VALUES (?, ?)", 
                         (eq_key, eq_data['price']))
    conn.commit()
    return conn

conn = init_db()
waiting_queue = []

def get_user(chat_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    if row:
        return {
            "chat_id": row[0], "country": row[1], "budget": row[2],
            "equipment": json.loads(row[3]) if row[3] else {},
            "wins": row[4], "losses": row[5], "xp": row[6],
            "level": row[7], "last_daily": row[8]
        }
    return None

def save_user(user):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (chat_id, country, budget, equipment, wins, losses, xp, level, last_daily)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user['chat_id'], user['country'], user['budget'], json.dumps(user['equipment']),
        user['wins'], user['losses'], user['xp'], user['level'], user['last_daily']
    ))
    conn.commit()

def reset_user_country(chat_id):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET country = NULL, budget = 0, equipment = '{}', wins = 0, losses = 0, xp = 0, level = 1, last_daily = 0
        WHERE chat_id = ?
    ''', (chat_id,))
    conn.commit()

def delete_user(chat_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE chat_id = ?", (chat_id,))
    conn.commit()

def get_selected_countries():
    cursor = conn.cursor()
    cursor.execute("SELECT country FROM users WHERE country IS NOT NULL")
    return [row[0] for row in cursor.fetchall()]

def get_equipment():
    cursor = conn.cursor()
    cursor.execute("SELECT eq_key, price FROM equipment_prices")
    prices = {row[0]: row[1] for row in cursor.fetchall()}
    equipment = {}
    for eq_key, eq_data in DEFAULT_EQUIPMENT.items():
        equipment[eq_key] = eq_data.copy()
        equipment[eq_key]['price'] = prices.get(eq_key, eq_data['price'])
    return equipment

def set_equipment_price(eq_key, new_price):
    cursor = conn.cursor()
    cursor.execute("UPDATE equipment_prices SET price = ? WHERE eq_key = ?", (new_price, eq_key))
    conn.commit()

# ═══════════════════════════════════════════
#  توابع ارتباطی با API
# ═══════════════════════════════════════════
def send_request(method, payload):
    try:
        response = requests.post(BASE_URL + method, json=payload, timeout=10)
        result = response.json()
        if not result.get('ok'):
            print(f"❌ خطای API در {method}: {result.get('description', 'خطای نامشخص')}")
        return result
    except Exception as e:
        print(f"❌ خطای شبکه: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = reply_markup
    return send_request('sendMessage', payload)

def answer_callback(callback_query_id, text=""):
    return send_request('answerCallbackQuery', {'callback_query_id': callback_query_id, 'text': text, 'show_alert': False})

def is_admin(chat_id):
    return chat_id in ADMIN_IDS

# ═══════════════════════════════════════════
#  منطق بازی
# ═══════════════════════════════════════════
def show_country_selection(chat_id):
    user = get_user(chat_id)
    if user and user['country']:
        send_message(chat_id, f"⚠️ شما قبلاً کشور {COUNTRIES[user['country']]['name']} را انتخاب کرده‌اید.\nبرای تغییر کشور، ابتدا «استعفا» را بزنید.")
        return
    selected_countries = get_selected_countries()
    available_countries = {k: v for k, v in COUNTRIES.items() if k not in selected_countries}
    if not available_countries:
        send_message(chat_id, "⚠️ تمام کشورها انتخاب شده‌اند!")
        return
    keyboard_rows = []
    countries_list = list(available_countries.items())
    for i in range(0, len(countries_list), 2):
        row = [{"text": countries_list[i][1]["name"], "callback_data": f"country_{countries_list[i][0]}"}]
        if i + 1 < len(countries_list):
            row.append({"text": countries_list[i+1][1]["name"], "callback_data": f"country_{countries_list[i+1][0]}"})
        keyboard_rows.append(row)
    send_message(chat_id, "🌍 *انتخاب کشور*\n\nکشور خود را انتخاب کنید:\n_(هر کشور فقط توسط یک فرمانده قابل انتخاب است)_", reply_markup={"inline_keyboard": keyboard_rows})

def show_shop(chat_id):
    user = get_user(chat_id)
    if not user or not user['country']:
        send_message(chat_id, "❌ ابتدا کشور خود را انتخاب کنید.")
        return
    EQUIPMENT = get_equipment()
    country_info = COUNTRIES[user['country']]
    text = f" *فروشگاه تجهیزات نظامی*\n\n️ کشور: {country_info['name']} | 🎖️ سطح: {user['level']}\n💰 بودجه: {user['budget']} واحد\n\n📦 *تجهیزات شما:*\n"
    has_item = False
    for eq_key, count in user['equipment'].items():
        if count > 0:
            text += f"  • {EQUIPMENT[eq_key]['name']} × {count}\n"
            has_item = True
    if not has_item:
        text += "  _(هنوز چیزی نخریده‌اید)_\n"
    keyboard_rows = []
    for eq_key, eq_info in EQUIPMENT.items():
        keyboard_rows.append([{"text": f"{eq_info['name']} | 💰{eq_info['price']} | ⚔️{eq_info['attack']} 🛡️{eq_info['defense']}", "callback_data": f"buy_{eq_key}"}])
    keyboard_rows.append([{"text": "️ فروش همه", "callback_data": "sell_all"}, {"text": "✅ آماده نبرد!", "callback_data": "ready_fight"}])
    send_message(chat_id, text, reply_markup={"inline_keyboard": keyboard_rows})

def buy_equipment(chat_id, eq_key):
    user = get_user(chat_id)
    EQUIPMENT = get_equipment()
    eq = EQUIPMENT[eq_key]
    if user['budget'] >= eq['price']:
        user['budget'] -= eq['price']
        user['equipment'][eq_key] = user['equipment'].get(eq_key, 0) + 1
        save_user(user)
        send_message(chat_id, f"✅ {eq['name']} خریداری شد!\n💰 بودجه: {user['budget']}")
    else:
        send_message(chat_id, f"❌ بودجه کافی نیست!\nنیاز: {eq['price']} | موجودی: {user['budget']}")
    show_shop(chat_id)

def calculate_power(user_data):
    total_attack, total_defense = 0, 0
    country_info = COUNTRIES[user_data['country']]
    for eq_key, count in user_data['equipment'].items():
        if count > 0:
            eq = DEFAULT_EQUIPMENT[eq_key]
            attack, defense = eq['attack'] * count, eq['defense'] * count
            if eq_key == country_info['bonus']:
                attack, defense = int(attack * country_info['bonus_val']), int(defense * country_info['bonus_val'])
            total_attack += attack
            total_defense += defense
    return int(total_attack * random.uniform(0.9, 1.1)), total_defense

def start_battle(player1_id, player2_id):
    p1, p2 = get_user(player1_id), get_user(player2_id)
    p1_atk, p1_def = calculate_power(p1)
    p2_atk, p2_def = calculate_power(p2)
    p1_dmg, p2_dmg = max(0, p1_atk - int(p2_def * 0.4)), max(0, p2_atk - int(p1_def * 0.4))
    c1_name, c2_name = COUNTRIES[p1['country']]['name'], COUNTRIES[p2['country']]['name']
    report = f"⚔️ *═══════ گزارش نبرد ═══════* ⚔️\n\n🔴 {c1_name} (سطح {p1['level']})\n   ⚔️ حمله: {p1_atk} | 🛡️ دفاع: {p1_def}\n\n🔵 {c2_name} (سطح {p2['level']})\n   ⚔️ حمله: {p2_atk} | 🛡️ دفاع: {p2_def}\n\n━━━━━━━━━━━━━━━━━━━━\n💥 آسیب به {c2_name}: {p1_dmg}\n💥 آسیب به {c1_name}: {p2_dmg}\n\n"
    if p1_dmg > p2_dmg:
        p1['wins'], p1['xp'], p2['losses'] = p1['wins'] + 1, p1['xp'] + 50, p2['losses'] + 1
        report += f"🏆 *برنده: {c1_name}!* 🎉"
        if p1['xp'] >= p1['level'] * 100: p1['level'], p1['budget'], p1['xp'] = p1['level'] + 1, p1['budget'] + 500, 0; report += f"\n\n🎉 *به سطح {p1['level']} رسیدید!*"
    elif p2_dmg > p1_dmg:
        p2['wins'], p2['xp'], p1['losses'] = p2['wins'] + 1, p2['xp'] + 50, p1['losses'] + 1
        report += f" *برنده: {c2_name}!* 🎉"
        if p2['xp'] >= p2['level'] * 100: p2['level'], p2['budget'], p2['xp'] = p2['level'] + 1, p2['budget'] + 500, 0; report += f"\n\n🎉 *به سطح {p2['level']} رسیدید!*"
    else:
        report += "🤝 *مساوی!*"
    save_user(p1); save_user(p2)
    send_message(player1_id, report)
    if player1_id != player2_id: send_message(player2_id, report)

def find_opponent(chat_id):
    if chat_id in waiting_queue:
        waiting_queue.remove(chat_id)
        send_message(chat_id, "❌ از صف خارج شدید.")
        return
    for waiting_id in waiting_queue:
        if waiting_id != chat_id and get_user(waiting_id):
            waiting_queue.remove(waiting_id)
            send_message(chat_id, "⚔️ حریف پیدا شد!")
            send_message(waiting_id, "⚔️ حریف پیدا شد!")
            time.sleep(2)
            start_battle(chat_id, waiting_id)
            return
    waiting_queue.append(chat_id)
    send_message(chat_id, "⏳ در صف انتظار...")

def send_to_group_with_flag(chat_id, text):
    user = get_user(chat_id)
    if not user or not user['country']:
        send_message(chat_id, "❌ ابتدا کشور خود را انتخاب کنید.")
        return
    country_info = COUNTRIES[user['country']]
    message = f"{country_info['flag']} *{country_info['name']}*\n\n{text}"
    result = send_message(GROUP_CHAT_ID, message)
    if result and result.get('ok'):
        send_message(chat_id, "✅ پیام در گروه ارسال شد.")
    else:
        send_message(chat_id, "❌ خطا در ارسال به گروه.")

# ═══════════════════════════════════════════
#  دستورات ادمین
# ══════════════════════════════════════════
def admin_set_price(chat_id, text):
    if not is_admin(chat_id):
        send_message(chat_id, "❌ دسترسی ادمین ندارید!")
        return
    parts = text.split()
    if len(parts) != 3:
        send_message(chat_id, "❌ فرمت اشتباه!\n\n*مثال:* `تنظیم_قیمت tank 100`\n\n*تجهیزات:*\n" + "\n".join([f"• `{k}`" for k in DEFAULT_EQUIPMENT.keys()]))
        return
    eq_key, new_price = parts[1], parts[2]
    if eq_key not in DEFAULT_EQUIPMENT:
        send_message(chat_id, f"❌ تجهیز '{eq_key}' وجود ندارد!")
        return
    try:
        new_price = int(new_price)
        set_equipment_price(eq_key, new_price)
        send_message(chat_id, f"✅ قیمت {DEFAULT_EQUIPMENT[eq_key]['name']} به {new_price} تغییر کرد.")
    except ValueError:
        send_message(chat_id, "❌ قیمت باید عدد باشد!")

def admin_give_equipment(chat_id, text):
    if not is_admin(chat_id):
        send_message(chat_id, "❌ دسترسی ادمین ندارید!")
        return
    parts = text.split()
    if len(parts) != 4:
        send_message(chat_id, "❌ فرمت اشتباه!\n\n*مثال:* `دادن_تجهیزات 123456789 tank 5`")
        return
    target_id, eq_key, count = parts[1], parts[2], parts[3]
    try:
        target_id = int(target_id)
        count = int(count)
    except ValueError:
        send_message(chat_id, "❌ شناسه و تعداد باید عدد باشند!")
        return
    if eq_key not in DEFAULT_EQUIPMENT:
        send_message(chat_id, f"❌ تجهیز '{eq_key}' وجود ندارد!")
        return
    user = get_user(target_id)
    if not user:
        send_message(chat_id, "❌ کاربر وجود ندارد!")
        return
    user['equipment'][eq_key] = user['equipment'].get(eq_key, 0) + count
    save_user(user)
    send_message(chat_id, f"✅ {count} عدد {DEFAULT_EQUIPMENT[eq_key]['name']} به کاربر داده شد.")

def admin_set_budget(chat_id, text):
    if not is_admin(chat_id):
        send_message(chat_id, " دسترسی ادمین ندارید!")
        return
    parts = text.split()
    if len(parts) != 3:
        send_message(chat_id, "❌ فرمت اشتباه!\n\n*مثال:* `تنظیم_بودجه 123456789 5000`")
        return
    target_id, new_budget = parts[1], parts[2]
    try:
        target_id = int(target_id)
        new_budget = int(new_budget)
    except ValueError:
        send_message(chat_id, "❌ مقادیر باید عدد باشند!")
        return
    user = get_user(target_id)
    if not user:
        send_message(chat_id, "❌ کاربر وجود ندارد!")
        return
    user['budget'] = new_budget
    save_user(user)
    send_message(chat_id, f"✅ بودجه کاربر به {new_budget} تغییر کرد.")

def admin_delete_user(chat_id, text):
    if not is_admin(chat_id):
        send_message(chat_id, "❌ دسترسی ادمین ندارید!")
        return
    parts = text.split()
    if len(parts) != 2:
        send_message(chat_id, "❌ فرمت اشتباه!\n\n*مثال:* `حذف_کاربر 123456789`")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        send_message(chat_id, "❌ شناسه باید عدد باشد!")
        return
    user = get_user(target_id)
    if not user:
        send_message(chat_id, "❌ کاربر وجود ندارد!")
        return
    delete_user(target_id)
    send_message(chat_id, f"✅ کاربر {target_id} حذف شد.")

def admin_show_users(chat_id):
    if not is_admin(chat_id):
        send_message(chat_id, "❌ دسترسی ادمین ندارید!")
        return
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, country, budget, wins FROM users")
    rows = cursor.fetchall()
    if not rows:
        send_message(chat_id, "📊 هیچ کاربری ثبت نام نکرده!")
        return
    msg = "👥 *لیست کاربران*\n\n"
    for row in rows:
        c_name = COUNTRIES.get(row[1], {"name": "نامشخص"})["name"] if row[1] else "بدون کشور"
        msg += f"🆔 `{row[0]}` | {c_name} | 💰{row[2]} | 🏆{row[3]}\n"
    send_message(chat_id, msg)

def is_admin_command(text):
    admin_commands = ['تنظیم_قیمت', 'دادن_تجهیزات', 'تنظیم_بودجه', 'حذف_کاربر', 'لیست_کاربران',
                      '/setprice', '/giveequipment', '/setbudget', '/deleteuser', '/users']
    for cmd in admin_commands:
        if text.startswith(cmd):
            return True
    return False

# ═══════════════════════════════════════════
#  حلقه اصلی ربات
# ═══════════════════════════════════════════
def main():
    print("🎮 ربات جنگ جهانی در حال اجراست...")
    print(f"🔑 ادمین‌ها: {ADMIN_IDS}")
    print(f" گروه: {GROUP_CHAT_ID}")
    last_update_id = None
    
    while True:
        try:
            payload = {'timeout': 30, 'offset': last_update_id}
            response = requests.get(f"{BASE_URL}getUpdates", params=payload, timeout=35)
            
            if response.status_code == 200:
                updates = response.json()
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        last_update_id = update['update_id'] + 1
                        
                        if 'message' in update:
                            chat_id = update['message']['chat']['id']
                            text = update['message'].get('text', '').strip()
                            user = get_user(chat_id)
                            
                            if text in ['/start', 'شروع', 'استارت']:
                                msg = "🌍 *به بازی جنگ جهانی خوش آمدید!*\n\n *دستورات:*\n"
                                msg += "🎮 `شروع` : انتخاب کشور\n🏪 `فروشگاه` : خرید\n⚔️ `حمله` : نبرد\n"
                                msg += "💰 `روزانه` : بودجه رایگان\n `پروفایل` : آمار\n `رتبه‌بندی` : برترین‌ها\n"
                                msg += "📚 `آموزش` : راهنما\n🚨 `استعفا` : حذف کشور\n\n"
                                if is_admin(chat_id):
                                    msg += "🔧 *دستورات ادمین:*\n"
                                    msg += "`تنظیم_قیمت tank 100`\n`دادن_تجهیزات ID tank 5`\n"
                                    msg += "`تنظیم_بودجه ID 5000`\n`حذف_کاربر ID`\n`لیست_کاربران`\n\n"
                                msg += "💬 هر پیام عادی در گروه با پرچم ارسال می‌شود!"
                                send_message(chat_id, msg)
                            
                            elif text in ['/play', 'شروع بازی', 'انتخاب کشور']:
                                show_country_selection(chat_id)
                            
                            elif text in ['/shop', 'فروشگاه', 'خرید']:
                                show_shop(chat_id)
                            
                            elif text in ['/fight', 'حمله', 'نبرد', 'جنگ']:
                                if user and user['country']:
                                    if any(v > 0 for v in user['equipment'].values()): find_opponent(chat_id)
                                    else: send_message(chat_id, "❌ اول تجهیزات بخرید!")
                                else: send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.")
                            
                            elif text in ['/daily', 'روزانه', 'حقوق']:
                                if not user or not user['country']:
                                    send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.")
                                    continue
                                current_time = int(time.time())
                                if current_time - user['last_daily'] >= 86400:
                                    user['budget'] += 300; user['last_daily'] = current_time; save_user(user)
                                    send_message(chat_id, "✅ *بودجه روزانه!*\n💰 ۳۰۰ واحد اضافه شد.")
                                else:
                                    remaining = 86400 - (current_time - user['last_daily'])
                                    send_message(chat_id, f"⏳ {remaining // 3600} ساعت و {(remaining % 3600) // 60} دقیقه")
                            
                            elif text in ['/profile', 'پروفایل', 'آمار']:
                                if not user or not user['country']:
                                    send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.")
                                    continue
                                c_name = COUNTRIES[user['country']]['name']
                                send_message(chat_id, f" *پروفایل*\n\n🏳️ {c_name}\n🎖️ سطح: {user['level']} (XP: {user['xp']}/{user['level'] * 100})\n💰 {user['budget']}\n {user['wins']} | 💀 {user['losses']}")
                            
                            elif text in ['/leaderboard', 'رتبه‌بندی', 'جدول']:
                                cursor = conn.cursor()
                                cursor.execute("SELECT country, level, wins FROM users ORDER BY wins DESC, level DESC LIMIT 10")
                                rows = cursor.fetchall()
                                if not rows: send_message(chat_id, "📊 هنوز کاربری نیست!")
                                else:
                                    msg = "🏆 *جدول برترین‌ها*\n\n"
                                    for i, row in enumerate(rows, 1):
                                        c_name = COUNTRIES.get(row[0], {"name": "نامشخص"})["name"]
                                        medal = "" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
                                        msg += f"{medal} {c_name} | 🎖️{row[1]} | 🏆{row[2]}\n"
                                    send_message(chat_id, msg)
                            
                            elif text in ['/help', 'آموزش', 'راهنما']:
                                send_message(chat_id, "📚 *راهنما*\n\n. «شروع» → انتخاب کشور\n۲. «فروشگاه» → خرید\n۳. «حمله» → نبرد\n۴. «روزانه» → بودجه\n۵. پیام عادی → ارسال به گروه\n\n🚨 «استعفا» → پاک شدن همه‌چیز!")
                            
                            elif text in ['/resign', 'استعفا', 'حذف کشور', 'ترک کشور']:
                                if not user or not user['country']:
                                    send_message(chat_id, "❌ کشوری ندارید!")
                                    continue
                                old_country = COUNTRIES[user['country']]['name']
                                reset_user_country(chat_id)
                                send_message(chat_id, f" *استعفا ثبت شد!*\n\nکشور {old_country} ترک شد.\n⚠️ همه‌چیز پاک شد.\n\n«شروع» را بزنید.")
                            
                            elif text in ['/testgroup', 'تست گروه']:
                                result = send_message(GROUP_CHAT_ID, "✅ *تست*\nربات متصل است!")
                                if result and result.get('ok'): send_message(chat_id, "✅ متصل است.")
                                else: send_message(chat_id, "❌ خطا. ربات را ادمین کنید.")
                            
                            elif is_admin_command(text):
                                if text.startswith('تنظیم_قیمت') or text.startswith('/setprice'):
                                    admin_set_price(chat_id, text)
                                elif text.startswith('دادن_تجهیزات') or text.startswith('/giveequipment'):
                                    admin_give_equipment(chat_id, text)
                                elif text.startswith('تنظیم_بودجه') or text.startswith('/setbudget'):
                                    admin_set_budget(chat_id, text)
                                elif text.startswith('حذف_کاربر') or text.startswith('/deleteuser'):
                                    admin_delete_user(chat_id, text)
                                elif text in ['لیست_کاربران', '/users']:
                                    admin_show_users(chat_id)
                            
                            elif not text.startswith('/') and not is_admin_command(text) and user and user['country']:
                                send_to_group_with_flag(chat_id, text)
                        
                        elif 'callback_query' in update:
                            cb = update['callback_query']
                            chat_id = cb['message']['chat']['id']
                            data = cb['data']
                            answer_callback(cb['id'])
                            user = get_user(chat_id)
                            
                            if data.startswith("country_"):
                                country_key = data.replace("country_", "")
                                if country_key in COUNTRIES:
                                    if country_key in get_selected_countries():
                                        send_message(chat_id, "⚠️ این کشور انتخاب شده!")
                                        show_country_selection(chat_id)
                                        continue
                                    c_info = COUNTRIES[country_key]
                                    new_user = {"chat_id": chat_id, "country": country_key, "budget": c_info['budget'], "equipment": {}, "wins": 0, "losses": 0, "xp": 0, "level": 1, "last_daily": 0}
                                    save_user(new_user)
                                    send_message(chat_id, f"✅ {c_info['name']} انتخاب شد!\n💰 {c_info['budget']}")
                                    show_shop(chat_id)
                            elif data.startswith("buy_") and user: buy_equipment(chat_id, data.replace("buy_", ""))
                            elif data == "sell_all" and user:
                                EQUIPMENT = get_equipment()
                                total_refund = sum(EQUIPMENT[k]['price'] * v for k, v in user['equipment'].items())
                                for k in user['equipment']: user['equipment'][k] = 0
                                user['budget'] += int(total_refund * 0.7)
                                save_user(user)
                                send_message(chat_id, f"️ فروخته شد. بازگشت: {int(total_refund * 0.7)}")
                                show_shop(chat_id)
                            elif data == "ready_fight" and user:
                                if any(v > 0 for v in user['equipment'].values()): send_message(chat_id, "✅ آماده! «حمله» را بزنید.")
                                else: send_message(chat_id, "❌ حداقل یک تجهیز بخرید!")
            
            elif response.status_code == 401:
                print("❌ توکن اشتباه!")
                time.sleep(10)
        except Exception as e:
            print(f"❌ خطا: {e}")
            time.sleep(3)
        time.sleep(1)

if __name__ == '__main__':
    main()