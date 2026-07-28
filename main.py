import requests
import random
import json
import time
import sqlite3
import os

# ═══════════════════════════════════════════
#  تنظیمات اولیه
# ═══════════════════════════════════════════
TOKEN = os.getenv("TOKEN", "توکن_خود_را_اینجا_بگذارید")
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "123456789")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip().isdigit()]
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "5752220430"))
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}/"

# ═══════════════════════════════════════════
#  داده‌های بازی
# ═══════════════════════════════════════════
COUNTRIES = {
    "iran": {"name": "ایران", "budget": 900, "bonus": "missile", "bonus_val": 1.4, "flag": "🇮🇷"},
    "turkey": {"name": "ترکیه", "budget": 880, "bonus": "drone", "bonus_val": 1.35, "flag": "🇹🇷"},
    "israel": {"name": "اسرائیل", "budget": 900, "bonus": "defense", "bonus_val": 1.4, "flag": "🇮🇱"},
    "palestine": {"name": "فلسطین", "budget": 350, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇵🇸"},
    "usa": {"name": "آمریکا", "budget": 1000, "bonus": "air", "bonus_val": 1.4, "flag": "🇺🇸"},
    "russia": {"name": "روسیه", "budget": 980, "bonus": "tank", "bonus_val": 1.4, "flag": "🇷🇺"},
    "china": {"name": "چین", "budget": 970, "bonus": "soldier", "bonus_val": 1.35, "flag": "🇨🇳"},
    "uk": {"name": "انگلستان", "budget": 940, "bonus": "ship", "bonus_val": 1.35, "flag": "🇬🇧"},
    "france": {"name": "فرانسه", "budget": 930, "bonus": "air", "bonus_val": 1.35, "flag": "🇫🇷"},
    "germany": {"name": "آلمان", "budget": 890, "bonus": "tank", "bonus_val": 1.3, "flag": "🇩🇪"},
}

EQUIPMENT = {
    "tank": {"name": "تانک", "price": 80, "attack": 15, "defense": 20, "emoji": "🛡️"},
    "jet": {"name": "جنگنده", "price": 120, "attack": 25, "defense": 10, "emoji": "✈️"},
    "ship": {"name": "ناو جنگی", "price": 150, "attack": 20, "defense": 25, "emoji": "🚢"},
    "soldier": {"name": "سرباز", "price": 50, "attack": 10, "defense": 10, "emoji": "🪖"},
    "missile": {"name": "موشک", "price": 200, "attack": 35, "defense": 0, "emoji": "🚀"},
    "defense": {"name": "پدافند", "price": 130, "attack": 0, "defense": 30, "emoji": "🛡️"},
    "drone": {"name": "پهپاد", "price": 90, "attack": 18, "defense": 5, "emoji": "🤖"},
}

RESOURCES = {
    "oil": {"name": "نفت", "buy_price": 50, "sell_price": 70, "emoji": "🛢️"},
    "goods": {"name": "کالای غیرنفتی", "buy_price": 30, "sell_price": 45, "emoji": "📦"}
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
            xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1, last_daily INTEGER DEFAULT 0,
            alliance TEXT DEFAULT 'بدون اتحادیه', inventory TEXT DEFAULT '{}'
        )
    ''')
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'alliance' not in columns: cursor.execute("ALTER TABLE users ADD COLUMN alliance TEXT DEFAULT 'بدون اتحادیه'")
    if 'inventory' not in columns: cursor.execute("ALTER TABLE users ADD COLUMN inventory TEXT DEFAULT '{}'")

    cursor.execute('CREATE TABLE IF NOT EXISTS equipment_prices (eq_key TEXT PRIMARY KEY, price INTEGER)')
    cursor.execute("SELECT COUNT(*) FROM equipment_prices")
    if cursor.fetchone()[0] == 0:
        for eq_key, eq_data in EQUIPMENT.items():
            cursor.execute("INSERT INTO equipment_prices (eq_key, price) VALUES (?, ?)", (eq_key, eq_data['price']))

    cursor.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('war_enabled', 'true')")
    cursor.execute('CREATE TABLE IF NOT EXISTS forced_channels (chat_id INTEGER PRIMARY KEY, title TEXT)')
    
    conn.commit()
    return conn

conn = init_db()

def get_user(chat_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    if row:
        return {
            "chat_id": row[0], "country": row[1], "budget": row[2],
            "equipment": json.loads(row[3]) if row[3] else {},
            "wins": row[4], "losses": row[5], "xp": row[6], "level": row[7],
            "last_daily": row[8], "alliance": row[9], "inventory": json.loads(row[10]) if row[10] else {}
        }
    return None

def save_user(user):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (chat_id, country, budget, equipment, wins, losses, xp, level, last_daily, alliance, inventory)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user['chat_id'], user['country'], user['budget'], json.dumps(user['equipment']),
        user['wins'], user['losses'], user['xp'], user['level'], user['last_daily'],
        user['alliance'], json.dumps(user['inventory'])
    ))
    conn.commit()

def reset_user_full(chat_id):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET country = NULL, budget = 0, equipment = '{}', wins = 0, losses = 0, 
            xp = 0, level = 1, last_daily = 0, alliance = 'بدون اتحادیه', inventory = '{}'
        WHERE chat_id = ?
    ''', (chat_id,))
    conn.commit()

def get_setting(key):
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    return row[0] if row else None

def set_setting(key, value):
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()

def get_equipment_prices():
    cursor = conn.cursor()
    cursor.execute("SELECT eq_key, price FROM equipment_prices")
    return {row[0]: row[1] for row in cursor.fetchall()}

def set_equipment_price(eq_key, new_price):
    cursor = conn.cursor()
    cursor.execute("UPDATE equipment_prices SET price = ? WHERE eq_key = ?", (new_price, eq_key))
    conn.commit()

def add_forced_channel(chat_id, title):
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO forced_channels (chat_id, title) VALUES (?, ?)", (chat_id, title))
    conn.commit()

def remove_forced_channel(chat_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM forced_channels WHERE chat_id = ?", (chat_id,))
    conn.commit()

def get_forced_channels():
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, title FROM forced_channels")
    return cursor.fetchall()

def check_user_membership(user_id):
    channels = get_forced_channels()
    if not channels:
        return True, []
    
    not_member = []
    for ch_id, ch_title in channels:
        try:
            payload = {'chat_id': ch_id, 'user_id': user_id}
            response = requests.post(f"{BASE_URL}getChatMember", json=payload, timeout=10)
            result = response.json()
            if not result.get('ok'):
                not_member.append((ch_id, ch_title))
                continue
            status = result['result'].get('status', '')
            if status in ['left', 'kicked']:
                not_member.append((ch_id, ch_title))
        except Exception as e:
            print(f"❌ خطا در بررسی عضویت کانال {ch_id}: {e}")
            not_member.append((ch_id, ch_title))
    
    return len(not_member) == 0, not_member

# ═══════════════════════════════════════════
#  توابع ارتباطی و کیبوردها
# ═══════════════════════════════════════════
def send_request(method, payload):
    try:
        response = requests.post(BASE_URL + method, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ خطای شبکه: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = reply_markup
    return send_request('sendMessage', payload)

def answer_callback(callback_query_id, text=""):
    send_request('answerCallbackQuery', {'callback_query_id': callback_query_id, 'text': text, 'show_alert': False})

def is_admin(chat_id):
    return chat_id in ADMIN_IDS

def main_menu_kb(is_admin_user=False):
    kb = {"inline_keyboard": []}
    if is_admin_user:
        kb["inline_keyboard"] = [
            [{"text": "🔧 پنل مدیریت", "callback_data": "menu_admin"}],
            [{"text": "📩 ارسال پیام به کاربر", "callback_data": "admin_prompt_msg"}],
            [{"text": "💰 مدیریت بودجه", "callback_data": "admin_manage_budget"}],
            [{"text": "💎 مدیریت قیمت تجهیزات", "callback_data": "admin_manage_prices"}],
            [{"text": "📢 مدیریت کانال‌های اجباری", "callback_data": "admin_manage_channels"}],
            [{"text": "👥 لیست کاربران", "callback_data": "admin_list_users"}]
        ]
        return kb
    
    # ✨ منوی اصلی با دکمه‌های خرید سکه و انصراف
    kb["inline_keyboard"] = [
        [{"text": "🌍 انتخاب کشور", "callback_data": "menu_country"}],
        [{"text": "🏪 فروشگاه", "callback_data": "menu_shop"}, {"text": "📦 انبار و تجارت", "callback_data": "menu_inventory"}],
        [{"text": "⚔️ اتاق جنگ", "callback_data": "menu_war"}, {"text": "🤝 اتحادیه‌ها", "callback_data": "menu_alliance"}],
        [{"text": "🎰 لاتاری", "callback_data": "menu_lottery"}, {"text": "👤 پروفایل من", "callback_data": "menu_profile"}],
        [{"text": "💰 دریافت حقوق روزانه", "callback_data": "action_daily"}, {"text": "💎 خرید سکه", "callback_data": "buy_coins"}],
        [{"text": "🚪 انصراف از بازی", "callback_data": "resign_confirm"}]
    ]
    return kb

def admin_menu_kb():
    war_status = "✅ فعال" if get_setting('war_enabled') == 'true' else "❌ غیرفعال"
    return {"inline_keyboard": [
        [{"text": f"⚙️ وضعیت جنگ: {war_status}", "callback_data": "admin_toggle_war"}],
        [{"text": "📩 ارسال پیام به کاربر", "callback_data": "admin_prompt_msg"}],
        [{"text": "💰 مدیریت بودجه", "callback_data": "admin_manage_budget"}],
        [{"text": "💎 مدیریت قیمت تجهیزات", "callback_data": "admin_manage_prices"}],
        [{"text": "📢 مدیریت کانال‌های اجباری", "callback_data": "admin_manage_channels"}],
        [{"text": "👥 لیست کاربران", "callback_data": "admin_list_users"}],
        [{"text": "🔙 بازگشت", "callback_data": "menu_main"}]
    ]}

def show_join_required(chat_id, not_member_channels):
    text = "🔒 *عضویت اجباری*\n\n"
    text += "برای استفاده از ربات، ابتدا باید در کانال‌های زیر عضو شوید:\n\n"
    kb = {"inline_keyboard": []}
    for ch_id, ch_title in not_member_channels:
        if ch_title and ch_title.startswith('@'):
            username = ch_title
        else:
            username = f"کانال {ch_id}"
        kb["inline_keyboard"].append([{"text": f"📢 عضویت در {ch_title}", "url": f"https://ble.ir/{username.lstrip('@')}"}])
    kb["inline_keyboard"].append([{"text": "✅ بررسی مجدد عضویت", "callback_data": "check_membership"}])
    send_message(chat_id, text, reply_markup=kb)

# ═══════════════════════════════════════════
#  منطق بازی و منوها
# ═══════════════════════════════════════════
def handle_callback(chat_id, data, cb_id):
    answer_callback(cb_id)
    user = get_user(chat_id)
    admin_user = is_admin(chat_id)
    
    if admin_user and data in ["menu_country", "menu_shop", "menu_inventory", "menu_war", "menu_alliance", "menu_lottery", "menu_profile", "action_daily", "buy_coins", "resign_confirm"]:
        send_message(chat_id, "🚫 *شما به عنوان پشتیبان، امکان بازی ندارید!*", reply_markup=main_menu_kb(is_admin_user=True))
        return
    
    if not admin_user and data not in ["menu_main", "check_membership"] and data.startswith(("menu_", "action_", "buy_", "trade_", "attack_", "select_country", "lottery_", "buy_coins", "resign_")):
        is_member, not_member_channels = check_user_membership(chat_id)
        if not is_member:
            show_join_required(chat_id, not_member_channels)
            return
    
    if data == "check_membership":
        is_member, not_member_channels = check_user_membership(chat_id)
        if is_member:
            send_message(chat_id, "✅ *عضویت شما تایید شد!*\nحالا می‌توانید از تمام امکانات ربات استفاده کنید.", reply_markup=main_menu_kb())
        else:
            show_join_required(chat_id, not_member_channels)
            send_message(chat_id, "❌ شما هنوز در تمام کانال‌های اجباری عضو نشده‌اید.")

    if data == "menu_main":
        msg = "🌍 *به بازی جنگ جهانی خوش آمدید!*\n\nاز منوی زیر بخش مورد نظر را انتخاب کنید:"
        kb = main_menu_kb(is_admin_user=admin_user)
        send_message(chat_id, msg, reply_markup=kb)

    # ✨ دکمه خرید سکه
    elif data == "buy_coins":
        if not user or not user['country']:
            send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
            return
        
        msg = "💎 *خرید سکه از پشتیبان*\n\n"
        msg += "برای خرید سکه، لطفاً به پشتیبان پیام دهید و مقدار مورد نظر را درخواست کنید.\n\n"
        msg += "📩 *روش درخواست:*\n"
        msg += "1. به پشتیبان پیام دهید\n"
        msg += "2. مقدار سکه مورد نظر را بگویید\n"
        msg += "3. پشتیبان پس از بررسی، سکه را به حساب شما اضافه می‌کند\n\n"
        msg += "💡 *نکته:* پشتیبان می‌تواند با دستور `add_money [شناسه_شما] [مقدار]` سکه اضافه کند.\n\n"
        msg += f"🆔 *شناسه شما:* `{chat_id}`\n"
        msg += f"💰 *بودجه فعلی:* {user['budget']} سکه"
        
        kb = {"inline_keyboard": [
            [{"text": "📩 ارسال درخواست به پشتیبان", "url": "https://ble.ir/"}],
            [{"text": "🔙 بازگشت به منو", "callback_data": "menu_main"}]
        ]}
        send_message(chat_id, msg, reply_markup=kb)

    # ✨ دکمه انصراف از بازی
    elif data == "resign_confirm":
        if not user or not user['country']:
            send_message(chat_id, "❌ شما کشوری ندارید!", reply_markup=main_menu_kb())
            return
        
        c_info = COUNTRIES[user['country']]
        msg = f"🚨 *تایید انصراف از بازی*\n\n"
        msg += f"آیا مطمئن هستید که می‌خواهید از {c_info['flag']} {c_info['name']} انصراف دهید؟\n\n"
        msg += "⚠️ *هشدار:*\n"
        msg += "• تمام بودجه شما پاک می‌شود\n"
        msg += "• تمام تجهیزات شما از بین می‌رود\n"
        msg += "• آمار برد و باخت شما صفر می‌شود\n"
        msg += "• کشور شما برای دیگران آزاد می‌شود\n\n"
        msg += "این عملیات غیرقابل بازگشت است!"
        
        kb = {"inline_keyboard": [
            [{"text": "✅ بله، انصراف می‌دهم", "callback_data": "resign_confirm_yes"}],
            [{"text": "❌ خیر، منصرف شدم", "callback_data": "menu_main"}]
        ]}
        send_message(chat_id, msg, reply_markup=kb)

    elif data == "resign_confirm_yes":
        if not user or not user['country']:
            send_message(chat_id, "❌ شما کشوری ندارید!", reply_markup=main_menu_kb())
            return
        
        c_info = COUNTRIES[user['country']]
        reset_user_full(chat_id)
        
        msg = f"✅ *انصراف شما ثبت شد!*\n\n"
        msg += f"شما از {c_info['flag']} {c_info['name']} خارج شدید.\n"
        msg += "تمام اطلاعات شما پاک شد.\n\n"
        msg += "حالا می‌توانید کشور جدیدی انتخاب کنید."
        
        send_message(chat_id, msg, reply_markup=main_menu_kb())

    elif data == "menu_profile":
        if not user or not user['country']:
            send_message(chat_id, "❌ شما هنوز کشوری انتخاب نکرده‌اید!", reply_markup=main_menu_kb())
            return
        c_info = COUNTRIES[user['country']]
        inv_text = "\n".join([f"• {RESOURCES[k]['emoji']} {RESOURCES[k]['name']}: {v}" for k, v in user['inventory'].items() if v > 0]) or "_(خالی)_"
        msg = f"👤 *پروفایل فرمانده*\n\n"
        msg += f"🏳️ کشور: {c_info['flag']} {c_info['name']}\n"
        msg += f"🤝 اتحادیه: {user['alliance']}\n"
        msg += f"🎖️ سطح: {user['level']} (XP: {user['xp']}/{user['level']*100})\n"
        msg += f"💰 بودجه: {user['budget']}\n"
        msg += f"🏆 برد: {user['wins']} | 💀 باخت: {user['losses']}\n\n"
        msg += f"📦 *انبار منابع:*\n{inv_text}\n\n"
        msg += "⚠️ *توجه:* با انصراف، تمام اطلاعات شما پاک می‌شود!"
        
        kb = {"inline_keyboard": [
            [{"text": "💎 خرید سکه", "callback_data": "buy_coins"}],
            [{"text": "🚪 انصراف از بازی", "callback_data": "resign_confirm"}],
            [{"text": "🔙 بازگشت به منو", "callback_data": "menu_main"}]
        ]}
        send_message(chat_id, msg, reply_markup=kb)

    elif data == "menu_country":
        if user and user['country']:
            c_info = COUNTRIES[user['country']]
            send_message(chat_id, f"⚠️ شما متعلق به {c_info['flag']} {c_info['name']} هستید.\nبرای تغییر، ابتدا انصراف دهید.", reply_markup=main_menu_kb())
            return
        cursor = conn.cursor()
        cursor.execute("SELECT country FROM users WHERE country IS NOT NULL")
        taken = [row[0] for row in cursor.fetchall()]
        available = {k: v for k, v in COUNTRIES.items() if k not in taken}
        if not available:
            send_message(chat_id, "⚠️ تمام کشورها اشباع شده‌اند!", reply_markup=main_menu_kb())
            return
        kb = {"inline_keyboard": []}
        items = list(available.items())
        for i in range(0, len(items), 2):
            row = [{"text": f"{items[i][1]['flag']} {items[i][1]['name']}", "callback_data": f"select_country:{items[i][0]}"}]
            if i + 1 < len(items):
                row.append({"text": f"{items[i+1][1]['flag']} {items[i+1][1]['name']}", "callback_data": f"select_country:{items[i+1][0]}"})
            kb["inline_keyboard"].append(row)
        send_message(chat_id, "🌍 *کشور خود را انتخاب کنید:*", reply_markup=kb)

    elif data.startswith("select_country:"):
        country_key = data.split(":")[1]
        new_user = {"chat_id": chat_id, "country": country_key, "budget": COUNTRIES[country_key]['budget'], 
                    "equipment": {}, "wins": 0, "losses": 0, "xp": 0, "level": 1, "last_daily": 0, 
                    "alliance": "بدون اتحادیه", "inventory": {}}
        save_user(new_user)
        c_info = COUNTRIES[country_key]
        send_message(chat_id, f"✅ {c_info['flag']} {c_info['name']} انتخاب شد!\n💰 بودجه: {COUNTRIES[country_key]['budget']}", reply_markup=main_menu_kb())

    elif data == "menu_shop":
        if not user or not user['country']:
            send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
            return
        prices = get_equipment_prices()
        c_info = COUNTRIES[user['country']]
        text = f"🏪 *فروشگاه تجهیزات*\n"
        text += f"🏳️ کشور: {c_info['flag']} {c_info['name']}\n"
        text += f"💰 بودجه شما: {user['budget']}\n\n"
        kb = {"inline_keyboard": []}
        for k, v in EQUIPMENT.items():
            text += f"{v['emoji']} {v['name']} | ⚔️{v['attack']} 🛡️{v['defense']} | 💰{prices[k]}\n"
            kb["inline_keyboard"].append([{"text": f"خرید {v['emoji']} {v['name']} ({prices[k]})", "callback_data": f"buy_eq:{k}"}])
        kb["inline_keyboard"].append([{"text": "🔙 بازگشت", "callback_data": "menu_main"}])
        send_message(chat_id, text, reply_markup=kb)

    elif data.startswith("buy_eq:"):
        eq_key = data.split(":")[1]
        prices = get_equipment_prices()
        price = prices[eq_key]
        if user['budget'] >= price:
            user['budget'] -= price
            user['equipment'][eq_key] = user['equipment'].get(eq_key, 0) + 1
            save_user(user)
            send_message(chat_id, f"✅ {EQUIPMENT[eq_key]['emoji']} {EQUIPMENT[eq_key]['name']} خریداری شد!", reply_markup=main_menu_kb())
        else:
            send_message(chat_id, "❌ بودجه کافی نیست!", reply_markup=main_menu_kb())

    elif data == "menu_inventory":
        if not user or not user['country']:
            send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
            return
        text = "📦 *انبار و تجارت منابع*\n\n"
        kb = {"inline_keyboard": []}
        for res_key, res_info in RESOURCES.items():
            amount = user['inventory'].get(res_key, 0)
            text += f"{res_info['emoji']} {res_info['name']}: {amount}\n"
            text += f"   (خرید: 💰{res_info['buy_price']} | فروش: 💰{res_info['sell_price']})\n"
            kb["inline_keyboard"].append([
                {"text": f"خرید {res_info['emoji']} {res_info['name']}", "callback_data": f"trade_buy:{res_key}"},
                {"text": f"فروش {res_info['emoji']} {res_info['name']}", "callback_data": f"trade_sell:{res_key}"}
            ])
        kb["inline_keyboard"].append([{"text": "🔙 بازگشت", "callback_data": "menu_main"}])
        send_message(chat_id, text, reply_markup=kb)

    elif data.startswith("trade_buy:"):
        res_key = data.split(":")[1]
        price = RESOURCES[res_key]['buy_price']
        if user['budget'] >= price:
            user['budget'] -= price
            user['inventory'][res_key] = user['inventory'].get(res_key, 0) + 1
            save_user(user)
            send_message(chat_id, f"✅ {RESOURCES[res_key]['emoji']} {RESOURCES[res_key]['name']} خریداری شد.", reply_markup=main_menu_kb())
        else:
            send_message(chat_id, "❌ بودجه کافی نیست!", reply_markup=main_menu_kb())

    elif data.startswith("trade_sell:"):
        res_key = data.split(":")[1]
        if user['inventory'].get(res_key, 0) > 0:
            user['inventory'][res_key] -= 1
            user['budget'] += RESOURCES[res_key]['sell_price']
            save_user(user)
            send_message(chat_id, f"✅ {RESOURCES[res_key]['emoji']} {RESOURCES[res_key]['name']} فروخته شد.", reply_markup=main_menu_kb())
        else:
            send_message(chat_id, "❌ این کالا را در انبار ندارید!", reply_markup=main_menu_kb())

    elif data == "menu_war":
        if get_setting('war_enabled') != 'true':
            send_message(chat_id, "🚫 *جنگ جهانی متوقف شده است!*", reply_markup=main_menu_kb())
            return
        if not user or not user['country']:
            send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
            return
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, country, level FROM users WHERE country IS NOT NULL AND chat_id != ?", (chat_id,))
        targets = cursor.fetchall()
        if not targets:
            send_message(chat_id, "🌍 کشور دیگری برای حمله وجود ندارد!", reply_markup=main_menu_kb())
            return
        text = "⚔️ *انتخاب هدف برای حمله*"
        kb = {"inline_keyboard": []}
        for t in targets:
            t_country = COUNTRIES[t[1]]
            kb["inline_keyboard"].append([{"text": f"⚔️ حمله به {t_country['flag']} {t_country['name']} (سطح {t[2]})", "callback_data": f"attack_confirm:{t[0]}"}])
        kb["inline_keyboard"].append([{"text": "🔙 بازگشت", "callback_data": "menu_main"}])
        send_message(chat_id, text, reply_markup=kb)

    elif data.startswith("attack_confirm:"):
        target_id = int(data.split(":")[1])
        target_user = get_user(target_id)
        if not target_user or not target_user['country']:
            send_message(chat_id, "❌ این هدف دیگر معتبر نیست!", reply_markup=main_menu_kb())
            return
        p1_atk, p1_def = 0, 0
        for eq, count in user['equipment'].items():
            if count > 0:
                mult = COUNTRIES[user['country']]['bonus_val'] if eq == COUNTRIES[user['country']]['bonus'] else 1
                p1_atk += EQUIPMENT[eq]['attack'] * count * mult
                p1_def += EQUIPMENT[eq]['defense'] * count * mult
        p1_atk = int(p1_atk * random.uniform(0.9, 1.1))
        p2_atk, p2_def = 0, 0
        for eq, count in target_user['equipment'].items():
            if count > 0:
                mult = COUNTRIES[target_user['country']]['bonus_val'] if eq == COUNTRIES[target_user['country']]['bonus'] else 1
                p2_atk += EQUIPMENT[eq]['attack'] * count * mult
                p2_def += EQUIPMENT[eq]['defense'] * count * mult
        p2_atk = int(p2_atk * random.uniform(0.9, 1.1))
        dmg1 = max(0, p1_atk - int(p2_def * 0.4))
        dmg2 = max(0, p2_atk - int(p1_def * 0.4))
        
        c1 = COUNTRIES[user['country']]
        c2 = COUNTRIES[target_user['country']]
        
        report = f"⚔️ *گزارش نبرد*\n\n"
        report += f"🔴 {c1['flag']} شما: ⚔️{p1_atk} 🛡️{p1_def}\n"
        report += f"🔵 {c2['flag']} دشمن: ⚔️{p2_atk} 🛡️{p2_def}\n"
        report += "━━━━━━━━━━━━━━\n"
        
        if dmg1 > dmg2:
            loot = int(target_user['budget'] * 0.15)
            target_loss = int(target_user['budget'] * 0.15)
            user['wins'] += 1; user['xp'] += 50; user['budget'] += loot
            target_user['losses'] += 1; target_user['budget'] -= target_loss
            if target_user['equipment'] and random.random() < 0.3:
                lost_eq = random.choice(list(target_user['equipment'].keys()))
                target_user['equipment'][lost_eq] -= 1
                if target_user['equipment'][lost_eq] <= 0: del target_user['equipment'][lost_eq]
                report += f"💥 شما یک عدد {EQUIPMENT[lost_eq]['emoji']} {EQUIPMENT[lost_eq]['name']} از دشمن نابود کردید!\n"
            report += f"🏆 *شما پیروز شدید!*\n💰 غنیمت: +{loot}\n📈 تجربه: +50"
            if user['xp'] >= user['level'] * 100:
                user['level'] += 1; user['budget'] += 500; user['xp'] = 0
                report += f"\n\n🎉 *به سطح {user['level']} رسیدید (+500 بودجه)*"
        elif dmg2 > dmg1:
            penalty = int(user['budget'] * 0.10)
            user['losses'] += 1; user['budget'] -= penalty
            target_user['wins'] += 1; target_user['xp'] += 50; target_user['budget'] += penalty
            report += f"💀 *شما شکست خوردید!*\n💸 هزینه تعمیرات: -{penalty}"
            if user['equipment'] and random.random() < 0.2:
                lost_eq = random.choice(list(user['equipment'].keys()))
                user['equipment'][lost_eq] -= 1
                if user['equipment'][lost_eq] <= 0: del user['equipment'][lost_eq]
                report += f"\n💥 یک عدد {EQUIPMENT[lost_eq]['emoji']} {EQUIPMENT[lost_eq]['name']} شما نابود شد!"
        else:
            report += "🤝 *نبرد مساوی!*"
        save_user(user); save_user(target_user)
        send_message(chat_id, report, reply_markup=main_menu_kb())
        send_message(target_id, f"⚠️ *شما مورد حمله قرار گرفتید!*\n\n{report}", reply_markup=main_menu_kb())

    elif data == "menu_alliance":
        if not user or not user['country']:
            send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
            return
        text = f"🤝 *مدیریت اتحادیه*\n\n"
        text += f"اتحادیه فعلی: *{user['alliance']}*\n\n"
        text += "برای تغییر، پیام متنی بفرستید:\n`اتحادیه نام_جدید`"
        kb = {"inline_keyboard": [[{"text": "🔙 بازگشت", "callback_data": "menu_main"}]]}
        send_message(chat_id, text, reply_markup=kb)

    elif data == "menu_lottery":
        text = "🎰 *لاتاری شانس*\n\n"
        text += "هزینه بلیط: 💰 100\n"
        text += "🥇 شانس 10%: برنده 1,000 سکه\n"
        text += "🏆 شانس 1%: برنده 5,000 سکه"
        kb = {"inline_keyboard": [
            [{"text": "🎟️ خرید بلیط (100 سکه)", "callback_data": "lottery_play"}],
            [{"text": "🔙 بازگشت", "callback_data": "menu_main"}]
        ]}
        send_message(chat_id, text, reply_markup=kb)

    elif data == "lottery_play":
        if user['budget'] < 100:
            send_message(chat_id, "❌ بودجه کافی ندارید!", reply_markup=main_menu_kb())
            return
        user['budget'] -= 100
        roll = random.randint(1, 100)
        if roll == 1:
            prize = 5000; user['budget'] += prize; msg = f"🎉 *جکپات!* برنده {prize} سکه شدید!"
        elif roll <= 10:
            prize = 1000; user['budget'] += prize; msg = f"✅ *تبریک!* برنده {prize} سکه شدید!"
        else:
            msg = "❌ *برنده نشدید.*"
        save_user(user)
        send_message(chat_id, msg, reply_markup=main_menu_kb())

    elif data == "action_daily":
        if not user or not user['country']:
            send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
            return
        now = int(time.time())
        if now - user['last_daily'] >= 86400:
            user['budget'] += 300; user['last_daily'] = now
            save_user(user)
            send_message(chat_id, "✅ *حقوق روزانه!* (+300 سکه)", reply_markup=main_menu_kb())
        else:
            rem = 86400 - (now - user['last_daily'])
            send_message(chat_id, f"⏳ {rem // 3600} ساعت و {(rem % 3600) // 60} دقیقه", reply_markup=main_menu_kb())

    elif data == "menu_admin":
        if not is_admin(chat_id):
            send_message(chat_id, "❌ دسترسی محدود!", reply_markup=main_menu_kb())
            return
        send_message(chat_id, "🔧 *پنل مدیریت*", reply_markup=admin_menu_kb())

    elif data == "admin_toggle_war":
        current = get_setting('war_enabled')
        new_val = 'false' if current == 'true' else 'true'
        set_setting('war_enabled', new_val)
        send_message(chat_id, f"✅ وضعیت جنگ: {'فعال' if new_val == 'true' else 'غیرفعال'}", reply_markup=admin_menu_kb())

    elif data == "admin_prompt_msg":
        if not is_admin(chat_id): return
        send_message(chat_id, "📩 *ارسال پیام*\n\nفرمت: `send_msg 123456789 متن پیام`", reply_markup=admin_menu_kb())

    elif data == "admin_list_users":
        if not is_admin(chat_id): return
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, country, budget, wins FROM users")
        rows = cursor.fetchall()
        msg = "👥 *لیست کاربران*\n\n"
        for r in rows:
            if r[1]:
                c_name = COUNTRIES.get(r[1], {"name": "نامشخص", "flag": "🏳️"})
                msg += f"🆔 `{r[0]}` | {c_name['flag']} {c_name['name']} | 💰{r[2]} | 🏆{r[3]}\n"
            else:
                msg += f"🆔 `{r[0]}` | بدون کشور | 💰{r[2]} | 🏆{r[3]}\n"
        send_message(chat_id, msg, reply_markup=admin_menu_kb())

    elif data == "admin_manage_budget":
        if not is_admin(chat_id): return
        send_message(chat_id, "💰 *مدیریت بودجه*\n\n`add_money ID مبلغ` (افزایش)\n`remove_money ID مبلغ` (کاهش)", reply_markup=admin_menu_kb())

    elif data == "admin_manage_prices":
        if not is_admin(chat_id): return
        prices = get_equipment_prices()
        text = "💎 *مدیریت قیمت تجهیزات*\n\n"
        for k, v in EQUIPMENT.items():
            text += f"{v['emoji']} {v['name']}: 💰{prices[k]}\n"
        text += "\nبرای تغییر قیمت، پیام متنی بفرستید:\n`set_price tank 150`"
        kb = {"inline_keyboard": [[{"text": "🔙 بازگشت", "callback_data": "menu_admin"}]]}
        send_message(chat_id, text, reply_markup=kb)

    elif data == "admin_manage_channels":
        if not is_admin(chat_id): return
        channels = get_forced_channels()
        text = "📢 *مدیریت کانال‌های اجباری*\n\n"
        if channels:
            text += "*کانال‌های فعلی:*\n"
            for ch_id, ch_title in channels:
                text += f"• {ch_title} (`{ch_id}`)\n"
        else:
            text += "_(هیچ کانالی تنظیم نشده)_\n"
        text += "\n*دستورات:*\n"
        text += "`add_channel @username` - افزودن کانال\n"
        text += "`remove_channel @username` - حذف کانال\n"
        text += "`remove_channel ID` - حذف با شناسه عددی"
        kb = {"inline_keyboard": [[{"text": "🔙 بازگشت", "callback_data": "menu_admin"}]]}
        send_message(chat_id, text, reply_markup=kb)


# ═══════════════════════════════════════════
#  حلقه اصلی ربات
# ═══════════════════════════════════════════
def main():
    print("🎮 ربات جنگ جهانی (نسخه نهایی) در حال اجراست...")
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
                        
                        if 'callback_query' in update:
                            cb = update['callback_query']
                            handle_callback(cb['message']['chat']['id'], cb['data'], cb['id'])
                        
                        elif 'message' in update:
                            chat_id = update['message']['chat']['id']
                            text = update['message'].get('text', '').strip()
                            user = get_user(chat_id)
                            admin_user = is_admin(chat_id)
                            
                            if text.startswith("اتحادیه "):
                                if not user or not user['country']:
                                    send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.")
                                    continue
                                new_alliance = text.replace("اتحادیه ", "").strip()
                                user['alliance'] = new_alliance
                                save_user(user)
                                send_message(chat_id, f"✅ اتحادیه به «{new_alliance}» تغییر کرد.", reply_markup=main_menu_kb(is_admin_user=admin_user))
                            
                            elif text.startswith("send_msg ") and admin_user:
                                parts = text.split(maxsplit=2)
                                if len(parts) >= 3:
                                    try:
                                        target_id = int(parts[1])
                                        msg_text = parts[2]
                                        res = send_message(target_id, f"📩 *پیام از پشتیبانی:*\n\n{msg_text}")
                                        if res and res.get('ok'):
                                            send_message(chat_id, f"✅ پیام به `{target_id}` ارسال شد.")
                                        else:
                                            send_message(chat_id, f"❌ خطا: {res}")
                                    except ValueError:
                                        send_message(chat_id, "❌ شناسه باید عدد باشد.")
                                else:
                                    send_message(chat_id, "❌ فرمت: `send_msg ID متن`")
                            
                            elif text.startswith("add_money ") and admin_user:
                                parts = text.split()
                                if len(parts) == 3:
                                    t_id, amount = int(parts[1]), int(parts[2])
                                    t_user = get_user(t_id)
                                    if t_user:
                                        t_user['budget'] += amount
                                        save_user(t_user)
                                        send_message(chat_id, f"✅ {amount} سکه به {t_id} اضافه شد.")
                                        send_message(t_id, f"🎁 ادمین {amount} سکه به حساب شما اضافه کرد!")
                                    else:
                                        send_message(chat_id, "❌ کاربر یافت نشد.")
                            
                            elif text.startswith("remove_money ") and admin_user:
                                parts = text.split()
                                if len(parts) == 3:
                                    t_id, amount = int(parts[1]), int(parts[2])
                                    t_user = get_user(t_id)
                                    if t_user:
                                        t_user['budget'] = max(0, t_user['budget'] - amount)
                                        save_user(t_user)
                                        send_message(chat_id, f"✅ {amount} سکه از {t_id} کسر شد.")
                                        send_message(t_id, f"⚠️ ادمین {amount} سکه از حساب شما کسر کرد!")
                                    else:
                                        send_message(chat_id, "❌ کاربر یافت نشد.")
                            
                            elif text.startswith("set_price ") and admin_user:
                                parts = text.split()
                                if len(parts) == 3:
                                    eq_key, new_price = parts[1], parts[2]
                                    if eq_key not in EQUIPMENT:
                                        send_message(chat_id, f"❌ تجهیز '{eq_key}' وجود ندارد!\nموجود: {', '.join(EQUIPMENT.keys())}")
                                        continue
                                    try:
                                        new_price = int(new_price)
                                        set_equipment_price(eq_key, new_price)
                                        send_message(chat_id, f"✅ قیمت {EQUIPMENT[eq_key]['emoji']} {EQUIPMENT[eq_key]['name']} به 💰{new_price} تغییر کرد.", reply_markup=admin_menu_kb())
                                    except ValueError:
                                        send_message(chat_id, "❌ قیمت باید عدد باشد!")
                                else:
                                    send_message(chat_id, "❌ فرمت: `set_price tank 150`")
                            
                            elif text.startswith("add_channel ") and admin_user:
                                parts = text.split(maxsplit=1)
                                if len(parts) == 2:
                                    channel_username = parts[1].strip()
                                    try:
                                        res = requests.post(f"{BASE_URL}getChat", json={'chat_id': channel_username}, timeout=10).json()
                                        if res.get('ok'):
                                            ch_id = res['result']['id']
                                            ch_title = res['result'].get('title') or res['result'].get('username') or channel_username
                                            add_forced_channel(ch_id, ch_title)
                                            send_message(chat_id, f"✅ کانال «{ch_title}» (`{ch_id}`) به لیست اجباری اضافه شد.", reply_markup=admin_menu_kb())
                                        else:
                                            send_message(chat_id, f"❌ کانال یافت نشد. مطمئن شوید ربات در کانال عضو است.\nخطا: {res.get('description', '')}")
                                    except Exception as e:
                                        send_message(chat_id, f"❌ خطا: {e}")
                                else:
                                    send_message(chat_id, "❌ فرمت: `add_channel @username`")
                            
                            elif text.startswith("remove_channel ") and admin_user:
                                parts = text.split(maxsplit=1)
                                if len(parts) == 2:
                                    channel_input = parts[1].strip()
                                    channels = get_forced_channels()
                                    removed = False
                                    for ch_id, ch_title in channels:
                                        if channel_input == ch_title or channel_input == str(ch_id) or channel_input == f"@{ch_title.lstrip('@')}":
                                            remove_forced_channel(ch_id)
                                            send_message(chat_id, f"✅ کانال «{ch_title}» حذف شد.", reply_markup=admin_menu_kb())
                                            removed = True
                                            break
                                    if not removed:
                                        send_message(chat_id, "❌ کانال یافت نشد.")
                                else:
                                    send_message(chat_id, "❌ فرمت: `remove_channel @username` یا `remove_channel ID`")
                            
                            elif admin_user:
                                send_message(chat_id, "🔧 *پنل مدیریت پشتیبان*", reply_markup=main_menu_kb(is_admin_user=True))
                            
                            elif not user or not user['country']:
                                send_message(chat_id, "👋 به بازی جنگ جهانی خوش آمدید!\nلطفاً کشور خود را انتخاب کنید:", reply_markup=main_menu_kb())
                            
                            elif not text.startswith('/') and not text.startswith("اتحادیه ") and not text.startswith("send_msg ") and not text.startswith("add_money ") and not text.startswith("remove_money ") and not text.startswith("set_price ") and not text.startswith("add_channel ") and not text.startswith("remove_channel "):
                                if admin_user:
                                    msg = f"🇺🇳 *سازمان ملل متحد*\n\n{text}"
                                else:
                                    c_info = COUNTRIES[user['country']]
                                    msg = f"{c_info['flag']} *{c_info['name']}*\n\n{text}"
                                res = send_message(GROUP_CHAT_ID, msg)
                                if res and res.get('ok'):
                                    send_message(chat_id, "✅ پیام در گروه ارسال شد.", reply_markup=main_menu_kb(is_admin_user=admin_user))
                                else:
                                    send_message(chat_id, "❌ خطا در ارسال به گروه.", reply_markup=main_menu_kb(is_admin_user=admin_user))
            
            elif response.status_code == 401:
                print("❌ توکن اشتباه!")
                time.sleep(10)
        except Exception as e:
            print(f"❌ خطا: {e}")
            time.sleep(3)
        time.sleep(1)

if __name__ == '__main__':
    main()