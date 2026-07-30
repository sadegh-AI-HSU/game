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

# ✨ دیکشنری حالت‌های کاربر (برای مدیریت جریان دکمه‌ها)
user_states = {}

# ═══════════════════════════════════════════
#  داده‌های بازی
# ══════════════════════════════════════════
COUNTRIES = {
    # --- خاورمیانه و شمال آفریقا (اصلاح شده و دقیق) ---
    "iran": {"name": "ایران", "budget": 900, "bonus": "missile", "bonus_val": 1.4, "flag": "🇮🇷"},
    "turkey": {"name": "ترکیه", "budget": 880, "bonus": "drone", "bonus_val": 1.35, "flag": "🇹🇷"},
    "israel": {"name": "اسرائیل", "budget": 900, "bonus": "defense", "bonus_val": 1.4, "flag": "🇮🇱"},
    "palestine": {"name": "فلسطین", "budget": 350, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇵🇸"},
    "egypt": {"name": "مصر", "budget": 860, "bonus": "tank", "bonus_val": 1.3, "flag": "🇪🇬"},
    "saudi": {"name": "عربستان", "budget": 810, "bonus": "air", "bonus_val": 1.3, "flag": "🇸🇦"},
    "uae": {"name": "امارات", "budget": 800, "bonus": "drone", "bonus_val": 1.3, "flag": "🇦🇪"},
    "iraq": {"name": "عراق", "budget": 560, "bonus": "soldier", "bonus_val": 1.2, "flag": "🇮🇶"},
    "syria": {"name": "سوریه", "budget": 430, "bonus": "missile", "bonus_val": 1.2, "flag": "🇸🇾"},
    "lebanon": {"name": "لبنان", "budget": 380, "bonus": "missile", "bonus_val": 1.15, "flag": "🇱🇧"},
    "jordan": {"name": "اردن", "budget": 420, "bonus": "air", "bonus_val": 1.2, "flag": "🇯🇴"},
    "yemen": {"name": "یمن", "budget": 370, "bonus": "missile", "bonus_val": 1.15, "flag": "🇾🇪"},
    "oman": {"name": "عمان", "budget": 360, "bonus": "ship", "bonus_val": 1.15, "flag": "🇴🇲"},
    "qatar": {"name": "قطر", "budget": 350, "bonus": "air", "bonus_val": 1.15, "flag": "🇶🇦"},
    "kuwait": {"name": "کویت", "budget": 340, "bonus": "air", "bonus_val": 1.15, "flag": "🇰🇼"},
    "libya": {"name": "لیبی", "budget": 350, "bonus": "tank", "bonus_val": 1.15, "flag": "🇱🇾"},
    "tunisia": {"name": "تونس", "budget": 340, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇹🇳"},
    "algeria": {"name": "الجزایر", "budget": 750, "bonus": "missile", "bonus_val": 1.25, "flag": "🇩🇿"},
    "morocco": {"name": "مراکش", "budget": 630, "bonus": "drone", "bonus_val": 1.25, "flag": "🇲🇦"},
    
    # --- سایر کشورها (پرچم‌ها بررسی و تایید شدند) ---
    "usa": {"name": "آمریکا", "budget": 1000, "bonus": "air", "bonus_val": 1.4, "flag": "🇺🇸"},
    "russia": {"name": "روسیه", "budget": 980, "bonus": "tank", "bonus_val": 1.4, "flag": "🇷🇺"},
    "china": {"name": "چین", "budget": 970, "bonus": "soldier", "bonus_val": 1.35, "flag": "🇨🇳"},
    "india": {"name": "هند", "budget": 950, "bonus": "missile", "bonus_val": 1.35, "flag": "🇮🇳"},
    "uk": {"name": "انگلستان", "budget": 940, "bonus": "ship", "bonus_val": 1.35, "flag": "🇬🇧"},
    "france": {"name": "فرانسه", "budget": 930, "bonus": "air", "bonus_val": 1.35, "flag": "🇫🇷"},
    "japan": {"name": "ژاپن", "budget": 920, "bonus": "ship", "bonus_val": 1.35, "flag": "🇯🇵"},
    "skorea": {"name": "کره جنوبی", "budget": 910, "bonus": "drone", "bonus_val": 1.35, "flag": "🇰🇷"},
    "germany": {"name": "آلمان", "budget": 890, "bonus": "tank", "bonus_val": 1.3, "flag": "🇩🇪"},
    "italy": {"name": "ایتالیا", "budget": 870, "bonus": "ship", "bonus_val": 1.3, "flag": "🇮🇹"},
    "pakistan": {"name": "پاکستان", "budget": 850, "bonus": "missile", "bonus_val": 1.3, "flag": "🇵🇰"},
    "brazil": {"name": "برزیل", "budget": 840, "bonus": "soldier", "bonus_val": 1.3, "flag": "🇧🇷"},
    "australia": {"name": "استرالیا", "budget": 830, "bonus": "air", "bonus_val": 1.3, "flag": "🇦🇺"},
    "canada": {"name": "کانادا", "budget": 820, "bonus": "defense", "bonus_val": 1.3, "flag": "🇨🇦"},
    "spain": {"name": "اسپانیا", "budget": 790, "bonus": "ship", "bonus_val": 1.25, "flag": "🇪🇸"},
    "indonesia": {"name": "اندونزی", "budget": 780, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇮🇩"},
    "poland": {"name": "لهستان", "budget": 770, "bonus": "tank", "bonus_val": 1.25, "flag": "🇵🇱"},
    "ukraine": {"name": "اوکراین", "budget": 760, "bonus": "drone", "bonus_val": 1.3, "flag": "🇺🇦"},
    "argentina": {"name": "آرژانتین", "budget": 740, "bonus": "ship", "bonus_val": 1.25, "flag": "🇦🇷"},
    "mexico": {"name": "مکزیک", "budget": 730, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇲🇽"},
    "southafrica": {"name": "آفریقای جنوبی", "budget": 720, "bonus": "tank", "bonus_val": 1.25, "flag": "🇿🇦"},
    "netherlands": {"name": "هلند", "budget": 710, "bonus": "ship", "bonus_val": 1.25, "flag": "🇳🇱"},
    "greece": {"name": "یونان", "budget": 700, "bonus": "air", "bonus_val": 1.25, "flag": "🇬🇷"},
    "vietnam": {"name": "ویتنام", "budget": 690, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇻🇳"},
    "thailand": {"name": "تایلند", "budget": 680, "bonus": "ship", "bonus_val": 1.25, "flag": "🇹🇭"},
    "malaysia": {"name": "مالزی", "budget": 670, "bonus": "air", "bonus_val": 1.25, "flag": "🇲🇾"},
    "philippines": {"name": "فیلیپین", "budget": 660, "bonus": "ship", "bonus_val": 1.25, "flag": "🇵🇭"},
    "colombia": {"name": "کلمبیا", "budget": 650, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇨🇴"},
    "nigeria": {"name": "نیجریه", "budget": 640, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇳🇬"},
    "sweden": {"name": "سوئد", "budget": 620, "bonus": "air", "bonus_val": 1.25, "flag": "🇸🇪"},
    "switzerland": {"name": "سوئیس", "budget": 610, "bonus": "defense", "bonus_val": 1.3, "flag": "🇨🇭"},
    "singapore": {"name": "سنگاپور", "budget": 600, "bonus": "ship", "bonus_val": 1.25, "flag": "🇸🇬"},
    "romania": {"name": "رومانی", "budget": 590, "bonus": "tank", "bonus_val": 1.2, "flag": "🇷🇴"},
    "chile": {"name": "شیلی", "budget": 580, "bonus": "ship", "bonus_val": 1.2, "flag": "🇨🇱"},
    "finland": {"name": "فنلاند", "budget": 570, "bonus": "air", "bonus_val": 1.2, "flag": "🇫🇮"},
    "newzealand": {"name": "نیوزیلند", "budget": 550, "bonus": "ship", "bonus_val": 1.2, "flag": "🇳🇿"},
    "peru": {"name": "پرو", "budget": 540, "bonus": "soldier", "bonus_val": 1.2, "flag": "🇵🇪"},
    "venezuela": {"name": "ونزوئلا", "budget": 530, "bonus": "missile", "bonus_val": 1.2, "flag": "🇻🇪"},
    "czechia": {"name": "چک", "budget": 520, "bonus": "tank", "bonus_val": 1.2, "flag": "🇨🇿"},
    "bangladesh": {"name": "بنگلادش", "budget": 510, "bonus": "soldier", "bonus_val": 1.2, "flag": "🇧🇩"},
    "hungary": {"name": "مجارستان", "budget": 500, "bonus": "tank", "bonus_val": 1.2, "flag": "🇭🇺"},
    "belgium": {"name": "بلژیک", "budget": 490, "bonus": "air", "bonus_val": 1.2, "flag": "🇧🇪"},
    "austria": {"name": "اتریش", "budget": 480, "bonus": "defense", "bonus_val": 1.2, "flag": "🇦🇹"},
    "norway": {"name": "نروژ", "budget": 470, "bonus": "ship", "bonus_val": 1.2, "flag": "🇳🇴"},
    "denmark": {"name": "دانمارک", "budget": 460, "bonus": "air", "bonus_val": 1.2, "flag": "🇩🇰"},
    "portugal": {"name": "پرتغال", "budget": 440, "bonus": "ship", "bonus_val": 1.2, "flag": "🇵🇹"},
    "serbia": {"name": "صربستان", "budget": 410, "bonus": "tank", "bonus_val": 1.2, "flag": "🇷🇸"},
    "azerbaijan": {"name": "آذربایجان", "budget": 400, "bonus": "drone", "bonus_val": 1.25, "flag": "🇦🇿"},
    "afghanistan": {"name": "افغانستان", "budget": 390, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇦🇫"},
    "georgia": {"name": "گرجستان", "budget": 330, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇬🇪"},
    "armenia": {"name": "ارمنستان", "budget": 320, "bonus": "defense", "bonus_val": 1.15, "flag": "🇦🇲"},
    "kazakhstan": {"name": "قزاقستان", "budget": 310, "bonus": "tank", "bonus_val": 1.15, "flag": "🇰🇿"},
    "uzbekistan": {"name": "ازبکستان", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇺🇿"},
    "mongolia": {"name": "مغولستان", "budget": 300, "bonus": "tank", "bonus_val": 1.15, "flag": "🇲🇳"},
    "cuba": {"name": "کوبا", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇨🇺"},
    "bolivia": {"name": "بولیوی", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇧🇴"},
    "paraguay": {"name": "پاراگوئه", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇵🇾"},
    "uruguay": {"name": "اروگوئه", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇺🇾"},
    "ecuador": {"name": "اکوادور", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇪🇨"},
    "guatemala": {"name": "گواتمالا", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇬🇹"},
    "costarica": {"name": "کاستاریکا", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇨🇷"},
    "panama": {"name": "پاناما", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇵🇦"},
    "jamaica": {"name": "جامائیکا", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇯🇲"},
    "trinidad": {"name": "ترینیداد", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇹🇹"},
    "bahamas": {"name": "باهاما", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇧🇸"},
    "croatia": {"name": "کرواسی", "budget": 350, "bonus": "ship", "bonus_val": 1.15, "flag": "🇭🇷"},
    "bulgaria": {"name": "بلغارستان", "budget": 340, "bonus": "tank", "bonus_val": 1.15, "flag": "🇧🇬"},
    "slovakia": {"name": "اسلواکی", "budget": 330, "bonus": "tank", "bonus_val": 1.15, "flag": "🇸🇰"},
    "lithuania": {"name": "لیتوانی", "budget": 320, "bonus": "air", "bonus_val": 1.15, "flag": "🇱🇹"},
    "latvia": {"name": "لتونی", "budget": 310, "bonus": "air", "bonus_val": 1.15, "flag": "🇱🇻"},
    "estonia": {"name": "استونی", "budget": 300, "bonus": "cyber", "bonus_val": 1.15, "flag": "🇪🇪"},
    "belarus": {"name": "بلاروس", "budget": 350, "bonus": "missile", "bonus_val": 1.15, "flag": "🇧🇾"},
    "moldova": {"name": "مولداوی", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇩"},
    "cyprus": {"name": "قبرس", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇨🇾"},
    "malta": {"name": "مالت", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇲🇹"},
    "iceland": {"name": "ایسلند", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇮🇸"},
    "luxembourg": {"name": "لوکزامبورگ", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇱🇺"},
    "ireland": {"name": "ایرلند", "budget": 350, "bonus": "air", "bonus_val": 1.15, "flag": "🇮🇪"},
    "sudan": {"name": "سودان", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇸🇩"},
    "ethiopia": {"name": "اتیوپی", "budget": 350, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇪🇹"},
    "kenya": {"name": "کنیا", "budget": 320, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇰🇪"},
    "ghana": {"name": "غنا", "budget": 310, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇬🇭"},
    "senegal": {"name": "سنگال", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇸🇳"},
    "tanzania": {"name": "تانزانیا", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇹🇿"},
    "uganda": {"name": "اوگاندا", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇺🇬"},
    "zambia": {"name": "زامبیا", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇿🇲"},
    "zimbabwe": {"name": "زیمبابوه", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇿🇼"},
    "angola": {"name": "آنگولا", "budget": 320, "bonus": "missile", "bonus_val": 1.15, "flag": "🇦🇴"},
    "mozambique": {"name": "موزامبیک", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇿"},
    "madagascar": {"name": "ماداگاسکار", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇬"},
    "cameroon": {"name": "کامرون", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇨🇲"},
    "ivorycoast": {"name": "ساحل عاج", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇨🇮"},
    "mali": {"name": "مالی", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇱"},
    "burkina": {"name": "بورکینافاسو", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇧🇫"},
    "niger": {"name": "نیجر", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇳🇪"},
    "chad": {"name": "چاد", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇹🇩"},
    "somalia": {"name": "سومالی", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇸🇴"},
    "rwanda": {"name": "رواندا", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇷🇼"},
    "nepal": {"name": "نپال", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇳🇵"},
    "srilanka": {"name": "سریلانکا", "budget": 320, "bonus": "ship", "bonus_val": 1.15, "flag": "🇱🇰"},
    "myanmar": {"name": "میانمار", "budget": 330, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇲"},
    "cambodia": {"name": "کامبوج", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇰🇭"},
    "laos": {"name": "لائوس", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇱🇦"},
    "brunei": {"name": "برونئی", "budget": 350, "bonus": "ship", "bonus_val": 1.15, "flag": "🇧🇳"},
    "papua": {"name": "پاپوآ گینه نو", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇵🇬"},
    "fiji": {"name": "فیجی", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇫🇯"},
    "solomon": {"name": "جزایر سلیمان", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇸🇧"},
    "vanuatu": {"name": "وانواتو", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇻🇺"},
    "samoa": {"name": "ساموآ", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇼🇸"},
    "kiribati": {"name": "کیریباتی", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇰🇮"},
    "tonga": {"name": "تونگا", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇹🇴"},
    "seychelles": {"name": "سیشل", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇸🇨"},
    "mauritius": {"name": "موریس", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇲🇺"},
    "maldives": {"name": "مالدیو", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇲🇻"},
    "bhutan": {"name": "بوتان", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇧🇹"},
    "tajikistan": {"name": "تاجیکستان", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇹🇯"},
    "kyrgyzstan": {"name": "قرقیزستان", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇰🇬"},
    "turkmenistan": {"name": "ترکمنستان", "budget": 300, "bonus": "missile", "bonus_val": 1.15, "flag": "🇹🇲"},
    "northkorea": {"name": "کره شمالی", "budget": 400, "bonus": "missile", "bonus_val": 1.3, "flag": "🇰🇵"},
    "haiti": {"name": "هائیتی", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇭🇹"},
    "honduras": {"name": "هندوراس", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇭🇳"},
    "elsalvador": {"name": "السالوادور", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇸🇻"},
    "nicaragua": {"name": "نیکاراگوئه", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇳🇮"},
    "dominican": {"name": "جمهوری دومینیکن", "budget": 320, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇩🇴"},
    "albania": {"name": "آلبانی", "budget": 310, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇦🇱"},
    "macedonia": {"name": "مقدونیه", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇰"},
    "bosnia": {"name": "بوسنی", "budget": 310, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇧🇦"},
    "kosovo": {"name": "کوزوو", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇽🇰"},
    "montenegro": {"name": "مونته‌نگرو", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇲🇪"},
    "andorra": {"name": "آندورا", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇦🇩"},
    "monaco": {"name": "موناکو", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇲🇨"},
    "sanmarino": {"name": "سان مارینو", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇸🇲"},
    "vatican": {"name": "واتیکان", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇻🇦"},
    "mauritania": {"name": "موریتانی", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇷"},
    "gambia": {"name": "گامبیا", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇬🇲"},
    "guinea": {"name": "گینه", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇬🇳"},
    "liberia": {"name": "لیبریا", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇱🇷"},
    "sierraleone": {"name": "سیرالئون", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇸🇱"},
    "togo": {"name": "توگو", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇹🇬"},
    "benin": {"name": "بنین", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇧🇯"},
}

EQUIPMENT = {
    "tank": {"name": "تانک", "price": 80, "attack": 15, "defense": 20, "emoji": "️"},
    "jet": {"name": "جنگنده", "price": 120, "attack": 25, "defense": 10, "emoji": "✈️"},
    "ship": {"name": "ناو جنگی", "price": 150, "attack": 20, "defense": 25, "emoji": "🚢"},
    "soldier": {"name": "سرباز", "price": 50, "attack": 10, "defense": 10, "emoji": ""},
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
            alliance TEXT DEFAULT 'بدون اتحادیه', inventory TEXT DEFAULT '{}',
            is_banned INTEGER DEFAULT 0
        )
    ''')
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'alliance' not in columns: cursor.execute("ALTER TABLE users ADD COLUMN alliance TEXT DEFAULT 'بدون اتحادیه'")
    if 'inventory' not in columns: cursor.execute("ALTER TABLE users ADD COLUMN inventory TEXT DEFAULT '{}'")
    if 'is_banned' not in columns: cursor.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")

    cursor.execute('CREATE TABLE IF NOT EXISTS equipment_prices (eq_key TEXT PRIMARY KEY, price INTEGER)')
    if cursor.execute("SELECT COUNT(*) FROM equipment_prices").fetchone()[0] == 0:
        for eq_key, eq_data in EQUIPMENT.items():
            cursor.execute("INSERT INTO equipment_prices VALUES (?, ?)", (eq_key, eq_data['price']))

    cursor.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    cursor.execute("INSERT OR IGNORE INTO settings VALUES ('war_enabled', 'true')")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forced_chats (
            chat_id TEXT PRIMARY KEY, title TEXT, type TEXT, invite_link TEXT
        )
    ''')
    cursor.execute("PRAGMA table_info(forced_chats)")
    if 'invite_link' not in [col[1] for col in cursor.fetchall()]:
        cursor.execute("ALTER TABLE forced_chats ADD COLUMN invite_link TEXT")
    
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
            "last_daily": row[8], "alliance": row[9], 
            "inventory": json.loads(row[10]) if row[10] else {},
            "is_banned": row[11]
        }
    return None

def save_user(user):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (chat_id, country, budget, equipment, wins, losses, xp, level, last_daily, alliance, inventory, is_banned)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user['chat_id'], user['country'], user['budget'], json.dumps(user['equipment']),
        user['wins'], user['losses'], user['xp'], user['level'], user['last_daily'],
        user['alliance'], json.dumps(user['inventory']), user.get('is_banned', 0)
    ))
    conn.commit()

def reset_user_full(chat_id):
    conn.cursor().execute('''
        UPDATE users SET country = NULL, budget = 0, equipment = '{}', wins = 0, losses = 0, 
            xp = 0, level = 1, last_daily = 0, alliance = 'بدون اتحادیه', inventory = '{}'
        WHERE chat_id = ?
    ''', (chat_id,))
    conn.commit()

def get_setting(key):
    row = conn.cursor().execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row[0] if row else None

def set_setting(key, value):
    conn.cursor().execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (key, value))
    conn.commit()

def get_equipment_prices():
    return {r[0]: r[1] for r in conn.cursor().execute("SELECT eq_key, price FROM equipment_prices").fetchall()}

def set_equipment_price(eq_key, new_price):
    conn.cursor().execute("UPDATE equipment_prices SET price = ? WHERE eq_key = ?", (new_price, eq_key))
    conn.commit()

def add_forced_chat(chat_id, title, chat_type):
    invite_link = None
    try:
        res = requests.post(f"{BASE_URL}exportChatInviteLink", json={'chat_id': str(chat_id)}, timeout=10).json()
        if res.get('ok'): invite_link = res['result']
    except: pass
    conn.cursor().execute('INSERT OR REPLACE INTO forced_chats VALUES (?, ?, ?, ?)', (str(chat_id), title, chat_type, invite_link))
    conn.commit()

def remove_forced_chat(chat_id):
    conn.cursor().execute("DELETE FROM forced_chats WHERE chat_id = ?", (str(chat_id),))
    conn.commit()

def get_forced_chats():
    return conn.cursor().execute("SELECT chat_id, title, type, invite_link FROM forced_chats").fetchall()

def check_user_membership(user_id):
    chats = get_forced_chats()
    if not chats: return True, []
    not_member = []
    for ch_id, ch_title, ch_type, invite_link in chats:
        try:
            response = requests.post(f"{BASE_URL}getChatMember", json={'chat_id': ch_id, 'user_id': user_id}, timeout=10).json()
            if not response.get('ok') or response['result'].get('status') in ['left', 'kicked']:
                not_member.append((ch_id, ch_title, ch_type, invite_link))
        except:
            not_member.append((ch_id, ch_title, ch_type, invite_link))
    return len(not_member) == 0, not_member

# ═══════════════════════════════════════════
#  توابع کمکی
# ═══════════════════════════════════════════
def announce_to_group(text):
    send_message(GROUP_CHAT_ID, text)

def check_bankruptcy(chat_id):
    user = get_user(chat_id)
    if user and user['country'] and user['budget'] <= 0:
        c_info = COUNTRIES[user['country']]
        reset_user_full(chat_id)
        announce_to_group(f"📉 *سقوط اقتصادی!*\n\nکشور {c_info['flag']} *{c_info['name']}* به دلیل ورشکستگی از دست رفت!")
        send_message(chat_id, "💀 *ورشکستگی!*\n\nکشور شما از دست رفت. دوباره شروع کنید.", reply_markup=main_menu_kb())
        return True
    return False

# ═══════════════════════════════════════════
#  توابع ارتباطی
# ═══════════════════════════════════════════
def send_request(method, payload):
    try:
        return requests.post(BASE_URL + method, json=payload, timeout=10).json()
    except Exception as e:
        print(f"خطای شبکه: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup: payload['reply_markup'] = reply_markup
    return send_request('sendMessage', payload)

def answer_callback(callback_query_id, text=""):
    send_request('answerCallbackQuery', {'callback_query_id': callback_query_id, 'text': text, 'show_alert': False})

def is_admin(chat_id):
    return chat_id in ADMIN_IDS

# ═══════════════════════════════════════════
#  کیبوردها
# ═══════════════════════════════════════════
def main_menu_kb(is_admin_user=False):
    if is_admin_user:
        return {"inline_keyboard": [
            [{"text": "🔧 پنل مدیریت", "callback_data": "menu_admin"}]
        ]}
    return {"inline_keyboard": [
        [{"text": "🌍 انتخاب کشور", "callback_data": "menu_country"}],
        [{"text": "🏪 فروشگاه", "callback_data": "menu_shop"}, {"text": "📦 انبار", "callback_data": "menu_inventory"}],
        [{"text": "⚔️ اتاق جنگ", "callback_data": "menu_war"}, {"text": "🤝 اتحادیه", "callback_data": "menu_alliance"}],
        [{"text": "🎰 لاتاری", "callback_data": "menu_lottery"}, {"text": "👤 پروفایل", "callback_data": "menu_profile"}],
        [{"text": "💰 حقوق روزانه", "callback_data": "action_daily"}, {"text": "💎 خرید سکه", "callback_data": "buy_coins"}],
        [{"text": "📢 ارسال به گروه", "callback_data": "user_send_to_group"}, {"text": "🏆 برترین‌ها", "callback_data": "leaderboard"}],
        [{"text": "🚪 انصراف", "callback_data": "resign_confirm"}]
    ]}

def admin_menu_kb():
    war_status = "✅ فعال" if get_setting('war_enabled') == 'true' else "❌ غیرفعال"
    return {"inline_keyboard": [
        [{"text": f"️ وضعیت جنگ: {war_status}", "callback_data": "admin_toggle_war"}],
        [{"text": "📩 ارسال پیام به کاربر", "callback_data": "admin_start_send_msg"}],
        [{"text": "💰 افزایش بودجه کاربر", "callback_data": "admin_start_add_money"}],
        [{"text": "💸 کاهش بودجه کاربر", "callback_data": "admin_start_remove_money"}],
        [{"text": "🚫 مسدود کردن کاربر", "callback_data": "admin_start_ban"}],
        [{"text": "✅ آزاد کردن کاربر", "callback_data": "admin_start_unban"}],
        [{"text": "💎 مدیریت قیمت تجهیزات", "callback_data": "admin_manage_prices"}],
        [{"text": "📢 مدیریت لینک‌های اجباری", "callback_data": "admin_manage_chats"}],
        [{"text": "👥 لیست کاربران", "callback_data": "admin_list_users"}],
        [{"text": "🔙 بازگشت به منوی اصلی", "callback_data": "menu_main"}]
    ]}

def show_join_required(chat_id, not_member_chats):
    text = "🔒 *عضویت اجباری*\n\nبرای استفاده از ربات، ابتدا باید در کانال/گروه‌های زیر عضو شوید:\n\n"
    kb = {"inline_keyboard": []}
    for ch_id, ch_title, ch_type, invite_link in not_member_chats:
        emoji = "📢" if ch_type == "channel" else "👥"
        url = invite_link or (f"https://ble.ir/{ch_title.lstrip('@')}" if not ch_title.lstrip('@').startswith('-100') else None)
        if url:
            kb["inline_keyboard"].append([{"text": f"{emoji} عضویت در {ch_title}", "url": url}])
            text += f"{emoji} *{ch_title}*\n🔗 [کلیک برای عضویت]({url})\n\n"
        else:
            kb["inline_keyboard"].append([{"text": f"{emoji} {ch_title} (بدون لینک)", "callback_data": "no_link"}])
            text += f"{emoji} *{ch_title}*\n⚠️ لینک در دسترس نیست\n\n"
    kb["inline_keyboard"].append([{"text": "✅ بررسی مجدد", "callback_data": "check_membership"}])
    send_message(chat_id, text, reply_markup=kb)

# ═══════════════════════════════════════════
#  منطق بازی و منوها
# ═══════════════════════════════════════════
def handle_callback(chat_id, data, cb_id):
    answer_callback(cb_id)
    user = get_user(chat_id)
    admin_user = is_admin(chat_id)
    
    if user and user.get('is_banned'):
        send_message(chat_id, " *شما توسط پشتیبان مسدود شده‌اید.*")
        return

    if admin_user and data in ["menu_country", "menu_shop", "menu_inventory", "menu_war", "menu_alliance", "menu_lottery", "menu_profile", "action_daily", "buy_coins", "resign_confirm", "user_send_to_group", "leaderboard"]:
        send_message(chat_id, "🚫 *شما به عنوان پشتیبان، امکان بازی ندارید!*", reply_markup=main_menu_kb(is_admin_user=True))
        return
    
    if not admin_user and data not in ["menu_main", "check_membership", "no_link"] and data.startswith(("menu_", "action_", "buy_", "trade_", "attack_", "select_country", "lottery_", "buy_coins", "resign_", "user_send", "leaderboard")):
        is_member, not_member_chats = check_user_membership(chat_id)
        if not is_member:
            show_join_required(chat_id, not_member_chats)
            return
    
    if data == "check_membership":
        is_member, not_member_chats = check_user_membership(chat_id)
        if is_member:
            send_message(chat_id, "✅ *عضویت شما تایید شد!*", reply_markup=main_menu_kb())
        else:
            show_join_required(chat_id, not_member_chats)

    if data == "menu_main":
        send_message(chat_id, " *به بازی جنگ جهانی خوش آمدید!*", reply_markup=main_menu_kb(is_admin_user=admin_user))

    # ═══════════════════════════════════════════
    #  ✨ دکمه‌های جدید کاربر
    # ═══════════════════════════════════════════
    elif data == "user_send_to_group":
        if not user or not user['country']:
            send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
            return
        user_states[chat_id] = "user_group_msg"
        c_info = COUNTRIES[user['country']]
        send_message(chat_id, 
            f" *ارسال پیام به گروه همگانی*\n\n"
            f"پیام شما با پرچم {c_info['flag']} *{c_info['name']}* در گروه همگانی ارسال خواهد شد.\n\n"
            f" *پیام خود را تایپ کنید:*",
            reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})

    elif data == "cancel_action":
        user_states.pop(chat_id, None)
        send_message(chat_id, "❌ عملیات لغو شد.", reply_markup=main_menu_kb())

    elif data == "leaderboard":
        rows = conn.cursor().execute(
            "SELECT country, level, wins, losses FROM users WHERE country IS NOT NULL ORDER BY wins DESC, level DESC LIMIT 10"
        ).fetchall()
        if not rows:
            send_message(chat_id, "📊 هنوز کاربری ثبت نام نکرده است!", reply_markup=main_menu_kb())
            return
        msg = " *۱۰ فرمانده برتر*\n\n"
        for i, (country, level, wins, losses) in enumerate(rows, 1):
            c = COUNTRIES.get(country, {"name": "نامشخص", "flag": "🏳️"})
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"🔹"
            msg += f"{medal} *رتبه {i}:* {c['flag']} {c['name']}\n   🎖️ سطح {level} | 🏆 {wins} برد | 💀 {losses} باخت\n\n"
        send_message(chat_id, msg, reply_markup=main_menu_kb())

    # ═══════════════════════════════════════════
    #  دکمه‌های موجود کاربر
    # ═══════════════════════════════════════════
    elif data == "buy_coins":
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        user_states[chat_id] = "waiting_for_coins"
        send_message(chat_id, f"💎 *درخواست خرید سکه*\n\nمقدار سکه را به صورت عدد وارد کنید (مثال: `1000`)\n💰 بودجه فعلی: {user['budget']}", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})

    elif data == "resign_confirm":
        if not user or not user['country']: return send_message(chat_id, "❌ کشوری ندارید!", reply_markup=main_menu_kb())
        c_info = COUNTRIES[user['country']]
        send_message(chat_id, f"🚨 *تایید انصراف*\n\nآیا از {c_info['flag']} {c_info['name']} انصراف می‌دهید؟\n⚠️ *تمام اطلاعات پاک می‌شود!*", reply_markup={"inline_keyboard": [[{"text": "✅ بله", "callback_data": "resign_confirm_yes"}], [{"text": "❌ خیر", "callback_data": "menu_main"}]]})

    elif data == "resign_confirm_yes":
        if not user or not user['country']: return
        c_info = COUNTRIES[user['country']]
        reset_user_full(chat_id)
        announce_to_group(f"🚪 *انصراف فرمانده*\n\nفرمانده کشور {c_info['flag']} *{c_info['name']}* انصراف داد.")
        send_message(chat_id, f"✅ انصراف ثبت شد.", reply_markup=main_menu_kb())

    elif data == "menu_profile":
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        c_info = COUNTRIES[user['country']]
        inv = "\n".join([f"• {RESOURCES[k]['emoji']} {RESOURCES[k]['name']}: {v}" for k, v in user['inventory'].items() if v > 0]) or "_(خالی)_"
        send_message(chat_id, f"👤 *پروفایل*\n\n🏳️ {c_info['flag']} {c_info['name']}\n🤝 اتحادیه: {user['alliance']}\n🎖️ سطح: {user['level']} | 💰 {user['budget']}\n🏆 برد: {user['wins']} | 💀 باخت: {user['losses']}\n\n📦 انبار: {inv}", reply_markup=main_menu_kb())

    elif data == "menu_country":
        if user and user['country']: return send_message(chat_id, f"⚠️ شما متعلق به {COUNTRIES[user['country']]['flag']} {COUNTRIES[user['country']]['name']} هستید.", reply_markup=main_menu_kb())
        taken = [row[0] for row in conn.cursor().execute("SELECT country FROM users WHERE country IS NOT NULL").fetchall()]
        available = {k: v for k, v in COUNTRIES.items() if k not in taken}
        if not available: return send_message(chat_id, "⚠️ تمام کشورها اشباع شده‌اند!", reply_markup=main_menu_kb())
        kb = {"inline_keyboard": []}
        items = list(available.items())
        for i in range(0, len(items), 2):
            row = [{"text": f"{items[i][1]['flag']} {items[i][1]['name']}", "callback_data": f"select_country:{items[i][0]}"}]
            if i + 1 < len(items): row.append({"text": f"{items[i+1][1]['flag']} {items[i+1][1]['name']}", "callback_data": f"select_country:{items[i+1][0]}"})
            kb["inline_keyboard"].append(row)
        send_message(chat_id, "🌍 *کشور خود را انتخاب کنید:*", reply_markup=kb)

    elif data.startswith("select_country:"):
        country_key = data.split(":")[1]
        new_user = {"chat_id": chat_id, "country": country_key, "budget": COUNTRIES[country_key]['budget'], "equipment": {}, "wins": 0, "losses": 0, "xp": 0, "level": 1, "last_daily": 0, "alliance": "بدون اتحادیه", "inventory": {}, "is_banned": 0}
        save_user(new_user)
        c_info = COUNTRIES[country_key]
        announce_to_group(f"🎉 *فرمانده جدید*\n\nکشور {c_info['flag']} *{c_info['name']}* انتخاب شد!")
        send_message(chat_id, f"✅ {c_info['flag']} {c_info['name']} انتخاب شد!\n💰 بودجه: {c_info['budget']}", reply_markup=main_menu_kb())

    elif data == "menu_shop":
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        prices = get_equipment_prices()
        c_info = COUNTRIES[user['country']]
        text = f" *فروشگاه*\n{c_info['flag']} {c_info['name']} | 💰 {user['budget']}\n\n"
        kb = {"inline_keyboard": [[{"text": f"خرید {v['emoji']} {v['name']} ({prices[k]})", "callback_data": f"buy_eq:{k}"}] for k, v in EQUIPMENT.items()]}
        kb["inline_keyboard"].append([{"text": "🔙 بازگشت", "callback_data": "menu_main"}])
        send_message(chat_id, text + "\n".join([f"{v['emoji']} {v['name']} | ⚔️{v['attack']} 🛡️{v['defense']}" for k, v in EQUIPMENT.items()]), reply_markup=kb)

    elif data.startswith("buy_eq:"):
        eq_key = data.split(":")[1]
        price = get_equipment_prices()[eq_key]
        if user['budget'] >= price:
            user['budget'] -= price
            user['equipment'][eq_key] = user['equipment'].get(eq_key, 0) + 1
            save_user(user)
            check_bankruptcy(chat_id)
            send_message(chat_id, f"✅ {EQUIPMENT[eq_key]['emoji']} {EQUIPMENT[eq_key]['name']} خریداری شد!", reply_markup=main_menu_kb())
        else:
            send_message(chat_id, "❌ بودجه کافی نیست!", reply_markup=main_menu_kb())

    elif data == "menu_inventory":
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        text = "📦 *انبار*\n\n"
        kb = {"inline_keyboard": []}
        for k, v in RESOURCES.items():
            amount = user['inventory'].get(k, 0)
            text += f"{v['emoji']} {v['name']}: {amount} (خرید: {v['buy_price']} | فروش: {v['sell_price']})\n"
            kb["inline_keyboard"].append([{"text": f"خرید {v['emoji']}", "callback_data": f"trade_buy:{k}"}, {"text": f"فروش {v['emoji']}", "callback_data": f"trade_sell:{k}"}])
        kb["inline_keyboard"].append([{"text": "🔙 بازگشت", "callback_data": "menu_main"}])
        send_message(chat_id, text, reply_markup=kb)

    elif data.startswith("trade_buy:"):
        k = data.split(":")[1]
        if user['budget'] >= RESOURCES[k]['buy_price']:
            user['budget'] -= RESOURCES[k]['buy_price']
            user['inventory'][k] = user['inventory'].get(k, 0) + 1
            save_user(user)
            check_bankruptcy(chat_id)
            send_message(chat_id, f"✅ {RESOURCES[k]['emoji']} خریداری شد.", reply_markup=main_menu_kb())
        else:
            send_message(chat_id, "❌ بودجه کافی نیست!", reply_markup=main_menu_kb())

    elif data.startswith("trade_sell:"):
        k = data.split(":")[1]
        if user['inventory'].get(k, 0) > 0:
            user['inventory'][k] -= 1
            user['budget'] += RESOURCES[k]['sell_price']
            save_user(user)
            send_message(chat_id, f"✅ {RESOURCES[k]['emoji']} فروخته شد.", reply_markup=main_menu_kb())
        else:
            send_message(chat_id, "❌ این کالا را ندارید!", reply_markup=main_menu_kb())

    elif data == "menu_war":
        if get_setting('war_enabled') != 'true': return send_message(chat_id, "🚫 *جنگ متوقف شده است!*", reply_markup=main_menu_kb())
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        targets = conn.cursor().execute("SELECT chat_id, country, level FROM users WHERE country IS NOT NULL AND chat_id != ?", (chat_id,)).fetchall()
        if not targets: return send_message(chat_id, "🌍 کشور دیگری برای حمله وجود ندارد!", reply_markup=main_menu_kb())
        kb = {"inline_keyboard": [[{"text": f"⚔️ حمله به {COUNTRIES[t[1]]['flag']} {COUNTRIES[t[1]]['name']} (سطح {t[2]})", "callback_data": f"attack_confirm:{t[0]}"}] for t in targets]}
        kb["inline_keyboard"].append([{"text": "🔙 بازگشت", "callback_data": "menu_main"}])
        send_message(chat_id, "⚔️ *انتخاب هدف*", reply_markup=kb)

    elif data.startswith("attack_confirm:"):
        target_id = int(data.split(":")[1])
        target_user = get_user(target_id)
        if not target_user or not target_user['country']: return send_message(chat_id, "❌ هدف معتبر نیست!", reply_markup=main_menu_kb())
            
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
        
        attacker_won = dmg1 > dmg2
        defender_won = dmg2 > dmg1

        if attacker_won:
            loot = int(target_user['budget'] * 0.15)
            user['wins'] += 1; user['xp'] += 50; user['budget'] += loot
            target_user['losses'] += 1; target_user['budget'] -= int(target_user['budget'] * 0.15)
            attacker_result = f"🏆 *شما پیروز شدید!*\n💰 غنیمت: +{loot}\n📈 تجربه: +50"
            if target_user['equipment'] and random.random() < 0.3:
                lost = random.choice(list(target_user['equipment'].keys()))
                target_user['equipment'][lost] -= 1
                if target_user['equipment'][lost] <= 0: del target_user['equipment'][lost]
                attacker_result += f"\n💥 یک {EQUIPMENT[lost]['emoji']} {EQUIPMENT[lost]['name']} دشمن نابود شد!"
            if user['xp'] >= user['level'] * 100:
                user['level'] += 1; user['budget'] += 500; user['xp'] = 0
                attacker_result += f"\n\n🎉 *به سطح {user['level']} رسیدید (+500 بودجه)*"
        elif defender_won:
            penalty = int(user['budget'] * 0.10)
            user['losses'] += 1; user['budget'] -= penalty
            target_user['wins'] += 1; target_user['xp'] += 50; target_user['budget'] += penalty
            attacker_result = f"💀 *شما شکست خوردید!*\n💸 هزینه تعمیرات: -{penalty}"
            if user['equipment'] and random.random() < 0.2:
                lost = random.choice(list(user['equipment'].keys()))
                user['equipment'][lost] -= 1
                if user['equipment'][lost] <= 0: del user['equipment'][lost]
                attacker_result += f"\n💥 یک {EQUIPMENT[lost]['emoji']} {EQUIPMENT[lost]['name']} شما نابود شد!"
        else:
            attacker_result = "🤝 *نبرد مساوی!*"

        attacker_report = (
            f"⚔️ *گزارش نبرد*\n\n"
            f"🔴 شما ({c1['flag']} {c1['name']}): ⚔️{p1_atk} ️{p1_def}\n"
            f"🔵 دشمن ({c2['flag']} {c2['name']}): ⚔️{p2_atk} 🛡️{p2_def}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💥 آسیب به دشمن: {dmg1}\n💥 آسیب دریافتی: {dmg2}\n\n{attacker_result}"
        )

        if defender_won:
            defender_result = f"🏆 *دفاع موفق!*\n📈 تجربه: +50\n💰 پاداش: +{penalty}"
        elif attacker_won:
            defender_result = f"💀 *دفاع ناموفق!*\n💸 غنیمت از دست رفته: -{int(target_user['budget'] * 0.15)}"
        else:
            defender_result = "🤝 *نبرد مساوی!*"

        defender_report = (
            f"⚠️ *گزارش حمله*\n\n"
            f"🔵 شما ({c2['flag']} {c2['name']}): ⚔️{p2_atk} 🛡️{p2_def}\n"
            f"🔴 مهاجم ({c1['flag']} {c1['name']}): ⚔️{p1_atk} ️{p1_def}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💥 آسیب به مهاجم: {dmg2}\n💥 آسیب دریافتی: {dmg1}\n\n{defender_result}"
        )

        war_announcement = (
            f"🚨 *آغاز نبرد!* 🚨\n\n"
            f"⚔️ {c1['flag']} *{c1['name']}* به {c2['flag']} *{c2['name']}* حمله کرد!\n\n"
            f"📊 *نتیجه:* {'پیروزی ' + c1['name'] if attacker_won else 'پیروزی ' + c2['name'] if defender_won else 'مساوی'}"
        )
        announce_to_group(war_announcement)

        save_user(user); save_user(target_user)
        send_message(chat_id, attacker_report, reply_markup=main_menu_kb())
        send_message(target_id, defender_report, reply_markup=main_menu_kb())
        
        check_bankruptcy(chat_id)
        check_bankruptcy(target_id)

    elif data == "menu_alliance":
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        send_message(chat_id, f" *اتحادیه*\n\nاتحادیه فعلی: *{user['alliance']}*\n\nبرای تغییر، پیام متنی بفرستید:\n`اتحادیه نام_جدید`", reply_markup={"inline_keyboard": [[{"text": "🔙 بازگشت", "callback_data": "menu_main"}]]})

    elif data == "menu_lottery":
        send_message(chat_id, " *لاتاری*\n\nهزینه:  100\n🥇 10%: 1,000 سکه\n 1%: 5,000 سکه", reply_markup={"inline_keyboard": [[{"text": "🎟️ خرید بلیط", "callback_data": "lottery_play"}], [{"text": "🔙 بازگشت", "callback_data": "menu_main"}]]})

    elif data == "lottery_play":
        if user['budget'] < 100: return send_message(chat_id, "❌ بودجه کافی ندارید!", reply_markup=main_menu_kb())
        user['budget'] -= 100
        roll = random.randint(1, 100)
        if roll == 1: user['budget'] += 5000; msg = "🎉 *جکپات!* 5,000 سکه!"
        elif roll <= 10: user['budget'] += 1000; msg = "✅ *تبریک!* 1,000 سکه!"
        else: msg = "❌ *برنده نشدید.*"
        save_user(user)
        check_bankruptcy(chat_id)
        send_message(chat_id, msg, reply_markup=main_menu_kb())

    elif data == "action_daily":
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        now = int(time.time())
        if now - user['last_daily'] >= 86400:
            user['budget'] += 300; user['last_daily'] = now
            save_user(user)
            send_message(chat_id, "✅ *حقوق روزانه!* (+300 سکه)", reply_markup=main_menu_kb())
        else:
            rem = 86400 - (now - user['last_daily'])
            send_message(chat_id, f"⏳ {rem // 3600} ساعت و {(rem % 3600) // 60} دقیقه", reply_markup=main_menu_kb())

    # ═══════════════════════════════════════════
    #  ✨ پنل مدیریت با دکمه‌های شیشه‌ای
    # ═══════════════════════════════════════════
    elif data == "menu_admin":
        if not is_admin(chat_id): return send_message(chat_id, "❌ دسترسی محدود!", reply_markup=main_menu_kb())
        send_message(chat_id, "🔧 *پنل مدیریت*\n\nیکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=admin_menu_kb())

    elif data == "admin_toggle_war":
        new_val = 'false' if get_setting('war_enabled') == 'true' else 'true'
        set_setting('war_enabled', new_val)
        send_message(chat_id, f"✅ وضعیت جنگ: {'فعال' if new_val == 'true' else 'غیرفعال'}", reply_markup=admin_menu_kb())

    # --- ارسال پیام به کاربر ---
    elif data == "admin_start_send_msg":
        if not is_admin(chat_id): return
        user_states[chat_id] = "admin_send_msg_id"
        send_message(chat_id, "📩 *ارسال پیام به کاربر*\n\nشناسه عددی کاربر را وارد کنید:", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})

    # --- افزایش بودجه ---
    elif data == "admin_start_add_money":
        if not is_admin(chat_id): return
        user_states[chat_id] = "admin_add_money_id"
        send_message(chat_id, "💰 *افزایش بودجه کاربر*\n\nشناسه عددی کاربر را وارد کنید:", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})

    # --- کاهش بودجه ---
    elif data == "admin_start_remove_money":
        if not is_admin(chat_id): return
        user_states[chat_id] = "admin_remove_money_id"
        send_message(chat_id, "💸 *کاهش بودجه کاربر*\n\nشناسه عددی کاربر را وارد کنید:", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})

    # --- مسدود کردن ---
    elif data == "admin_start_ban":
        if not is_admin(chat_id): return
        user_states[chat_id] = "admin_ban_id"
        send_message(chat_id, "🚫 *مسدود کردن کاربر*\n\nشناسه عددی کاربر را وارد کنید:", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})

    # --- آزاد کردن ---
    elif data == "admin_start_unban":
        if not is_admin(chat_id): return
        user_states[chat_id] = "admin_unban_id"
        send_message(chat_id, "✅ *آزاد کردن کاربر*\n\nشناسه عددی کاربر را وارد کنید:", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})

    # --- مدیریت قیمت ---
    elif data == "admin_manage_prices":
        if not is_admin(chat_id): return
        prices = get_equipment_prices()
        text = "💎 *مدیریت قیمت تجهیزات*\n\n"
        kb = {"inline_keyboard": []}
        for k, v in EQUIPMENT.items():
            text += f"{v['emoji']} {v['name']}: {prices[k]}\n"
            kb["inline_keyboard"].append([{"text": f"✏️ تغییر قیمت {v['emoji']} {v['name']}", "callback_data": f"admin_set_price:{k}"}])
        kb["inline_keyboard"].append([{"text": "🔙 بازگشت", "callback_data": "menu_admin"}])
        send_message(chat_id, text, reply_markup=kb)

    elif data.startswith("admin_set_price:"):
        eq_key = data.split(":")[1]
        user_states[chat_id] = f"admin_set_price:{eq_key}"
        send_message(chat_id, f"💎 *تغییر قیمت {EQUIPMENT[eq_key]['emoji']} {EQUIPMENT[eq_key]['name']}*\n\nقیمت جدید را وارد کنید:", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})

    # --- مدیریت لینک‌های اجباری ---
    elif data == "admin_manage_chats":
        if not is_admin(chat_id): return
        chats = get_forced_chats()
        text = "📢 *مدیریت لینک‌های اجباری*\n\n"
        kb = {"inline_keyboard": []}
        if chats:
            text += "*لیست فعلی:*\n"
            for ch_id, ch_title, ch_type, _ in chats:
                type_emoji = "📢" if ch_type == "channel" else "👥"
                text += f"{type_emoji} {ch_title} (`{ch_id}`)\n"
                kb["inline_keyboard"].append([{"text": f"❌ حذف {ch_title}", "callback_data": f"admin_remove_chat:{ch_id}"}])
        else:
            text += "_(تنظیم نشده)_\n"
        kb["inline_keyboard"].insert(0, [{"text": "➕ افزودن کانال/گروه جدید", "callback_data": "admin_add_chat"}])
        kb["inline_keyboard"].append([{"text": "🔙 بازگشت", "callback_data": "menu_admin"}])
        send_message(chat_id, text, reply_markup=kb)

    elif data == "admin_add_chat":
        if not is_admin(chat_id): return
        user_states[chat_id] = "admin_add_chat"
        send_message(chat_id, "📢 *افزودن کانال/گروه اجباری*\n\nنام کاربری (با @) یا شناسه عددی را وارد کنید:\n\nمثال: `@MyChannel`", reply_markup={"inline_keyboard": [[{"text": " لغو", "callback_data": "cancel_action"}]]})

    elif data.startswith("admin_remove_chat:"):
        ch_id = data.split(":")[1]
        remove_forced_chat(ch_id)
        send_message(chat_id, "✅ لینک اجباری حذف شد.", reply_markup=admin_menu_kb())

    # --- لیست کاربران ---
    elif data == "admin_list_users":
        if not is_admin(chat_id): return
        rows = conn.cursor().execute("SELECT chat_id, country, budget, wins, is_banned FROM users").fetchall()
        if not rows:
            send_message(chat_id, " هیچ کاربری ثبت نام نکرده است!", reply_markup=admin_menu_kb())
            return
        msg = "👥 *لیست کاربران*\n\n"
        for r in rows:
            c_name = COUNTRIES.get(r[1], {"name": "بدون کشور", "flag": "🏳️"})
            ban_icon = "" if r[4] else ""
            msg += f"{ban_icon} 🆔 `{r[0]}` | {c_name['flag']} {c_name['name']} | 💰{r[2]} | 🏆{r[3]}\n"
        send_message(chat_id, msg, reply_markup=admin_menu_kb())


# ══════════════════════════════════════════
#  حلقه اصلی ربات
# ══════════════════════════════════════════
def main():
    print(" ربات جنگ جهانی (نسخه دکمه‌ای کامل) در حال اجراست...")
    last_update_id = None
    
    while True:
        try:
            response = requests.get(f"{BASE_URL}getUpdates", params={'timeout': 30, 'offset': last_update_id}, timeout=35)
            if response.status_code == 200:
                updates = response.json()
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        last_update_id = update['update_id'] + 1
                        
                        if 'callback_query' in update:
                            chat_type = update['callback_query']['message']['chat'].get('type', 'private')
                            if chat_type != 'private': continue
                            handle_callback(
                                update['callback_query']['message']['chat']['id'], 
                                update['callback_query']['data'], 
                                update['callback_query']['id']
                            )
                        
                        elif 'message' in update:
                            chat_type = update['message']['chat'].get('type', 'private')
                            if chat_type != 'private': continue
                                
                            chat_id = update['message']['chat']['id']
                            text = update['message'].get('text', '').strip()
                            user = get_user(chat_id)
                            admin_user = is_admin(chat_id)
                            
                            if user and user.get('is_banned'):
                                send_message(chat_id, " *شما مسدود شده‌اید.*")
                                continue

                            # ✨ مدیریت حالت‌های کاربر
                            current_state = user_states.get(chat_id)
                            
                            if current_state == "waiting_for_coins":
                                try:
                                    amount = int(text)
                                    if amount <= 0: raise ValueError
                                    del user_states[chat_id]
                                    for admin_id in ADMIN_IDS:
                                        send_message(admin_id, f" *درخواست خرید سکه*\n👤 ID: `{chat_id}`\n💎 مقدار: {amount}\n💰 بودجه فعلی: {user['budget']}\n\nدستور: `add_money {chat_id} {amount}`")
                                    send_message(chat_id, f"✅ درخواست {amount} سکه ثبت شد.", reply_markup=main_menu_kb())
                                except ValueError:
                                    send_message(chat_id, "❌ فقط عدد مثبت وارد کنید.", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                continue
                            
                            elif current_state == "admin_send_msg_id":
                                try:
                                    target_id = int(text)
                                    user_states[chat_id] = f"admin_send_msg:{target_id}"
                                    send_message(chat_id, f"📩 پیام خود را برای کاربر `{target_id}` وارد کنید:", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                except ValueError:
                                    send_message(chat_id, "❌ شناسه باید عدد باشد.", reply_markup={"inline_keyboard": [[{"text": " لغو", "callback_data": "cancel_action"}]]})
                                continue
                            
                            elif current_state and current_state.startswith("admin_send_msg:"):
                                target_id = int(current_state.split(":")[1])
                                del user_states[chat_id]
                                res = send_message(target_id, f"📩 *پیام پشتیبانی:*\n\n{text}")
                                send_message(chat_id, "✅ پیام ارسال شد." if res and res.get('ok') else f"❌ خطا: {res}", reply_markup=admin_menu_kb())
                                continue
                            
                            elif current_state == "admin_add_money_id":
                                try:
                                    target_id = int(text)
                                    user_states[chat_id] = f"admin_add_money:{target_id}"
                                    send_message(chat_id, f" مقدار سکه برای افزودن به کاربر `{target_id}`:", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                except ValueError:
                                    send_message(chat_id, "❌ شناسه باید عدد باشد.", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                continue
                            
                            elif current_state and current_state.startswith("admin_add_money:"):
                                target_id = int(current_state.split(":")[1])
                                try:
                                    amount = int(text)
                                    del user_states[chat_id]
                                    t_user = get_user(target_id)
                                    if t_user:
                                        t_user['budget'] += amount
                                        save_user(t_user)
                                        send_message(chat_id, f"✅ {amount} سکه به `{target_id}` اضافه شد.", reply_markup=admin_menu_kb())
                                        send_message(target_id, f"🎁 پشتیبان {amount} سکه به شما اضافه کرد!")
                                    else:
                                        send_message(chat_id, "❌ کاربر یافت نشد.", reply_markup=admin_menu_kb())
                                except ValueError:
                                    send_message(chat_id, "❌ مقدار باید عدد باشد.", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                continue
                            
                            elif current_state == "admin_remove_money_id":
                                try:
                                    target_id = int(text)
                                    user_states[chat_id] = f"admin_remove_money:{target_id}"
                                    send_message(chat_id, f"💸 مقدار سکه برای کسر از کاربر `{target_id}`:", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                except ValueError:
                                    send_message(chat_id, "❌ شناسه باید عدد باشد.", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                continue
                            
                            elif current_state and current_state.startswith("admin_remove_money:"):
                                target_id = int(current_state.split(":")[1])
                                try:
                                    amount = int(text)
                                    del user_states[chat_id]
                                    t_user = get_user(target_id)
                                    if t_user:
                                        t_user['budget'] = max(0, t_user['budget'] - amount)
                                        save_user(t_user)
                                        send_message(chat_id, f"✅ {amount} سکه از `{target_id}` کسر شد.", reply_markup=admin_menu_kb())
                                        send_message(target_id, f"⚠️ پشتیبان {amount} سکه از شما کسر کرد!")
                                    else:
                                        send_message(chat_id, "❌ کاربر یافت نشد.", reply_markup=admin_menu_kb())
                                except ValueError:
                                    send_message(chat_id, "❌ مقدار باید عدد باشد.", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                continue
                            
                            elif current_state == "admin_ban_id":
                                try:
                                    target_id = int(text)
                                    del user_states[chat_id]
                                    t_user = get_user(target_id)
                                    if t_user:
                                        c_info = COUNTRIES.get(t_user['country'], {"name": "نامشخص", "flag": "🏳️"})
                                        conn.cursor().execute("UPDATE users SET is_banned = 1 WHERE chat_id = ?", (target_id,))
                                        conn.commit()
                                        announce_to_group(f"🚫 *مسدودیت*\n\nفرمانده {c_info['flag']} {c_info['name']} (ID: `{target_id}`) بن شد.")
                                        send_message(chat_id, f"✅ کاربر `{target_id}` بن شد.", reply_markup=admin_menu_kb())
                                        send_message(target_id, "🚫 *شما بن شدید.*", reply_markup={"inline_keyboard": []})
                                    else:
                                        send_message(chat_id, "❌ کاربر یافت نشد.", reply_markup=admin_menu_kb())
                                except ValueError:
                                    send_message(chat_id, "❌ شناسه باید عدد باشد.", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                continue
                            
                            elif current_state == "admin_unban_id":
                                try:
                                    target_id = int(text)
                                    del user_states[chat_id]
                                    conn.cursor().execute("UPDATE users SET is_banned = 0 WHERE chat_id = ?", (target_id,))
                                    conn.commit()
                                    send_message(chat_id, f"✅ کاربر `{target_id}` آنبن شد.", reply_markup=admin_menu_kb())
                                    send_message(target_id, "✅ حساب شما آزاد شد.", reply_markup=main_menu_kb())
                                except ValueError:
                                    send_message(chat_id, "❌ شناسه باید عدد باشد.", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                continue
                            
                            elif current_state and current_state.startswith("admin_set_price:"):
                                eq_key = current_state.split(":")[1]
                                try:
                                    new_price = int(text)
                                    del user_states[chat_id]
                                    set_equipment_price(eq_key, new_price)
                                    send_message(chat_id, f"✅ قیمت {EQUIPMENT[eq_key]['emoji']} {EQUIPMENT[eq_key]['name']} به 💰{new_price} تغییر کرد.", reply_markup=admin_menu_kb())
                                except ValueError:
                                    send_message(chat_id, "❌ قیمت باید عدد باشد.", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_action"}]]})
                                continue
                            
                            elif current_state == "admin_add_chat":
                                del user_states[chat_id]
                                try:
                                    res = requests.post(f"{BASE_URL}getChat", json={'chat_id': text}, timeout=10).json()
                                    if res.get('ok'):
                                        add_forced_chat(res['result']['id'], res['result'].get('title') or res['result'].get('username') or text, res['result'].get('type', 'unknown'))
                                        send_message(chat_id, f"✅ به لیست اجباری اضافه شد.\n️ ربات باید ادمین باشد!", reply_markup=admin_menu_kb())
                                    else:
                                        send_message(chat_id, f"❌ خطا: {res.get('description')}", reply_markup=admin_menu_kb())
                                except Exception as e:
                                    send_message(chat_id, f"❌ خطا: {e}", reply_markup=admin_menu_kb())
                                continue
                            
                            elif current_state == "user_group_msg":
                                # ذخیره پیام موقت و نمایش تایید
                                user_states[chat_id] = f"user_group_confirm:{text}"
                                send_message(chat_id, 
                                    f" *پیش‌نمایش پیام*\n\n{text}\n\nآیا می‌خواهید این پیام ارسال شود؟",
                                    reply_markup={"inline_keyboard": [
                                        [{"text": "✅ ارسال به گروه", "callback_data": "user_group_send"}, {"text": "❌ لغو", "callback_data": "cancel_action"}]
                                    ]})
                                continue
                            
                            # ✨ تایید ارسال به گروه
                            elif current_state and current_state.startswith("user_group_confirm:"):
                                if data == "user_group_send":
                                    msg_text = current_state.split(":", 1)[1]
                                    del user_states[chat_id]
                                    c_info = COUNTRIES[user['country']]
                                    msg = f"{c_info['flag']} *{c_info['name']}*\n\n{msg_text}"
                                    res = send_message(GROUP_CHAT_ID, msg)
                                    send_message(chat_id, "✅ پیام در گروه ارسال شد." if res and res.get('ok') else " خطا در ارسال.", reply_markup=main_menu_kb())
                                continue

                            # پیام‌های عادی (بدون حالت خاص)
                            if text.startswith("اتحادیه ") and user and user['country']:
                                user['alliance'] = text.replace("اتحادیه ", "").strip()
                                save_user(user)
                                send_message(chat_id, f"✅ عضو اتحادیه «*{user['alliance']}*» شدید.", reply_markup=main_menu_kb(is_admin_user=admin_user))
                            
                            elif admin_user:
                                send_message(chat_id, "🔧 *پنل مدیریت*", reply_markup=main_menu_kb(is_admin_user=True))
                            
                            elif not user or not user['country']:
                                send_message(chat_id, "👋 به بازی جنگ جهانی خوش آمدید!\nلطفاً کشور خود را انتخاب کنید:", reply_markup=main_menu_kb())
                            
                            else:
                                send_message(chat_id, "لطفاً از دکمه‌های زیر استفاده کنید:", reply_markup=main_menu_kb())
            
            elif response.status_code == 401:
                print("❌ توکن اشتباه!"); time.sleep(10)
        except Exception as e:
            print(f"❌ خطا: {e}"); time.sleep(3)
        time.sleep(1)

if __name__ == '__main__':
    main()
