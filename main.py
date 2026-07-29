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

user_states = {}

# ═══════════════════════════════════════════
#  داده‌های بازی
# ═══════════════════════════════════════════
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
    cursor.execute("SELECT COUNT(*) FROM equipment_prices")
    if cursor.fetchone()[0] == 0:
        for eq_key, eq_data in EQUIPMENT.items():
            cursor.execute("INSERT INTO equipment_prices (eq_key, price) VALUES (?, ?)", (eq_key, eq_data['price']))

    cursor.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('war_enabled', 'true')")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forced_chats (
            chat_id TEXT PRIMARY KEY, title TEXT, type TEXT, invite_link TEXT
        )
    ''')
    cursor.execute("PRAGMA table_info(forced_chats)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'invite_link' not in columns:
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
            "last_daily": row[8], "alliance": row[9], "inventory": json.loads(row[10]) if row[10] else {},
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
    return row[0] if (row := cursor.fetchone()) else None

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

def add_forced_chat(chat_id, title, chat_type):
    invite_link = None
    try:
        res = requests.post(f"{BASE_URL}exportChatInviteLink", json={'chat_id': str(chat_id)}, timeout=10).json()
        if res.get('ok'): invite_link = res['result']
    except Exception: pass
    
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO forced_chats (chat_id, title, type, invite_link) VALUES (?, ?, ?, ?)', (str(chat_id), title, chat_type, invite_link))
    conn.commit()

def remove_forced_chat(chat_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM forced_chats WHERE chat_id = ?", (str(chat_id),))
    conn.commit()

def get_forced_chats():
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, title, type, invite_link FROM forced_chats")
    return cursor.fetchall()

def check_user_membership(user_id):
    chats = get_forced_chats()
    if not chats: return True, []
    not_member = []
    for ch_id, ch_title, ch_type, invite_link in chats:
        try:
            response = requests.post(f"{BASE_URL}getChatMember", json={'chat_id': ch_id, 'user_id': user_id}, timeout=10).json()
            if not response.get('ok') or response['result'].get('status') in ['left', 'kicked']:
                not_member.append((ch_id, ch_title, ch_type, invite_link))
        except Exception:
            not_member.append((ch_id, ch_title, ch_type, invite_link))
    return len(not_member) == 0, not_member

# ═══════════════════════════════════════════
#  توابع کمکی جدید
# ═══════════════════════════════════════════
def announce_to_group(text):
    """ارسال پیام اعلامیه به گروه همگانی"""
    send_message(GROUP_CHAT_ID, text)

def check_bankruptcy(chat_id):
    """بررسی ورشکستگی کاربر و اخراج خودکار"""
    user = get_user(chat_id)
    if user and user['country'] and user['budget'] <= 0:
        c_info = COUNTRIES[user['country']]
        reset_user_full(chat_id)
        announce_to_group(f"📉 *سقوط اقتصادی!*\n\nکشور {c_info['flag']} *{c_info['name']}* به دلیل ورشکستگی (بودجه صفر یا منفی) از دست رفت!\nفرمانده این کشور اخراج شد و کشور برای انتخاب مجدد آزاد گردید.")
        send_message(chat_id, "💀 *ورشکستگی!*\n\nبودجه شما به صفر یا کمتر رسید. کشور شما از دست رفت و باید دوباره شروع کنید.", reply_markup=main_menu_kb())
        return True
    return False

# ═══════════════════════════════════════════
#  توابع ارتباطی و کیبوردها
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

def main_menu_kb(is_admin_user=False):
    if is_admin_user:
        return {"inline_keyboard": [
            [{"text": "🔧 پنل مدیریت", "callback_data": "menu_admin"}],
            [{"text": "📩 ارسال پیام", "callback_data": "admin_prompt_msg"}],
            [{"text": "💰 مدیریت بودجه", "callback_data": "admin_manage_budget"}],
            [{"text": "💎 مدیریت قیمت", "callback_data": "admin_manage_prices"}],
            [{"text": "📢 لینک‌های اجباری", "callback_data": "admin_manage_chats"}],
            [{"text": "👥 لیست کاربران", "callback_data": "admin_list_users"}]
        ]}
    return {"inline_keyboard": [
        [{"text": "🌍 انتخاب کشور", "callback_data": "menu_country"}],
        [{"text": "🏪 فروشگاه", "callback_data": "menu_shop"}, {"text": "📦 انبار", "callback_data": "menu_inventory"}],
        [{"text": "⚔️ اتاق جنگ", "callback_data": "menu_war"}, {"text": "🤝 اتحادیه", "callback_data": "menu_alliance"}],
        [{"text": "🎰 لاتاری", "callback_data": "menu_lottery"}, {"text": "👤 پروفایل", "callback_data": "menu_profile"}],
        [{"text": "💰 حقوق روزانه", "callback_data": "action_daily"}, {"text": "💎 خرید سکه", "callback_data": "buy_coins"}],
        [{"text": "🚪 انصراف", "callback_data": "resign_confirm"}]
    ]}

def admin_menu_kb():
    war_status = "✅ فعال" if get_setting('war_enabled') == 'true' else "❌ غیرفعال"
    return {"inline_keyboard": [
        [{"text": f"⚙️ وضعیت جنگ: {war_status}", "callback_data": "admin_toggle_war"}],
        [{"text": "📩 ارسال پیام", "callback_data": "admin_prompt_msg"}],
        [{"text": "💰 مدیریت بودجه", "callback_data": "admin_manage_budget"}],
        [{"text": "💎 مدیریت قیمت", "callback_data": "admin_manage_prices"}],
        [{"text": "📢 لینک‌های اجباری", "callback_data": "admin_manage_chats"}],
        [{"text": "👥 لیست کاربران", "callback_data": "admin_list_users"}],
        [{"text": "🔙 بازگشت", "callback_data": "menu_main"}]
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
    
    # ✨ بررسی بن بودن کاربر
    if user and user.get('is_banned'):
        send_message(chat_id, "🚫 *شما توسط پشتیبان از بازی مسدود (Ban) شده‌اید.*\nدر صورت اعتراض با پشتیبان تماس بگیرید.")
        return

    if admin_user and data in ["menu_country", "menu_shop", "menu_inventory", "menu_war", "menu_alliance", "menu_lottery", "menu_profile", "action_daily", "buy_coins", "resign_confirm"]:
        send_message(chat_id, "🚫 *شما به عنوان پشتیبان، امکان بازی ندارید!*", reply_markup=main_menu_kb(is_admin_user=True))
        return
    
    if not admin_user and data not in ["menu_main", "check_membership"] and data.startswith(("menu_", "action_", "buy_", "trade_", "attack_", "select_country", "lottery_", "buy_coins", "resign_")):
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
        send_message(chat_id, "🌍 *به بازی جنگ جهانی خوش آمدید!*", reply_markup=main_menu_kb(is_admin_user=admin_user))

    elif data == "buy_coins":
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        user_states[chat_id] = "waiting_for_coins"
        send_message(chat_id, f"💎 *درخواست خرید سکه*\n\nمقدار سکه را به صورت عدد وارد کنید (مثال: `1000`)\n💰 بودجه فعلی: {user['budget']}", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_buy_coins"}]]})

    elif data == "cancel_buy_coins":
        user_states.pop(chat_id, None)
        send_message(chat_id, "❌ درخواست لغو شد.", reply_markup=main_menu_kb())

    elif data == "resign_confirm":
        if not user or not user['country']: return send_message(chat_id, "❌ کشوری ندارید!", reply_markup=main_menu_kb())
        c_info = COUNTRIES[user['country']]
        send_message(chat_id, f"🚨 *تایید انصراف*\n\nآیا از {c_info['flag']} {c_info['name']} انصراف می‌دهید؟\n⚠️ *تمام اطلاعات پاک می‌شود!*", reply_markup={"inline_keyboard": [[{"text": "✅ بله", "callback_data": "resign_confirm_yes"}], [{"text": "❌ خیر", "callback_data": "menu_main"}]]})

    elif data == "resign_confirm_yes":
        if not user or not user['country']: return
        c_info = COUNTRIES[user['country']]
        reset_user_full(chat_id)
        announce_to_group(f"🚪 *انصراف فرمانده*\n\nفرمانده کشور {c_info['flag']} *{c_info['name']}* از سمت خود انصراف داد.\nاین کشور اکنون برای انتخاب مجدد آزاد است.")
        send_message(chat_id, f"✅ انصراف ثبت شد. شما از {c_info['flag']} {c_info['name']} خارج شدید.", reply_markup=main_menu_kb())

    elif data == "menu_profile":
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        c_info = COUNTRIES[user['country']]
        inv = "\n".join([f"• {RESOURCES[k]['emoji']} {RESOURCES[k]['name']}: {v}" for k, v in user['inventory'].items() if v > 0]) or "_(خالی)_"
        send_message(chat_id, f"👤 *پروفایل*\n\n🏳️ {c_info['flag']} {c_info['name']}\n🤝 اتحادیه: {user['alliance']}\n🎖️ سطح: {user['level']} | 💰 {user['budget']}\n🏆 برد: {user['wins']} | 💀 باخت: {user['losses']}\n\n📦 انبار: {inv}", reply_markup={"inline_keyboard": [[{"text": "💎 خرید سکه", "callback_data": "buy_coins"}], [{"text": "🚪 انصراف", "callback_data": "resign_confirm"}], [{"text": "🔙 بازگشت", "callback_data": "menu_main"}]]})

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
        announce_to_group(f"🎉 *فرمانده جدید*\n\nکشور {c_info['flag']} *{c_info['name']}* توسط یک فرمانده جدید انتخاب شد!\nآغاز به کار با بودجه {c_info['budget']} سکه.")
        send_message(chat_id, f"✅ {c_info['flag']} {c_info['name']} انتخاب شد!\n💰 بودجه: {c_info['budget']}", reply_markup=main_menu_kb())

    elif data == "menu_shop":
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        prices = get_equipment_prices()
        c_info = COUNTRIES[user['country']]
        text = f"🏪 *فروشگاه*\n{c_info['flag']} {c_info['name']} | 💰 {user['budget']}\n\n"
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
            check_bankruptcy(chat_id) # ✨ بررسی ورشکستگی
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
            check_bankruptcy(chat_id) # ✨ بررسی ورشکستگی
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

    # ✨ ✨ ✨ منطق نبرد اصلاح‌شده و دقیق ✨ ✨ ✨
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
        
        dmg1 = max(0, p1_atk - int(p2_def * 0.4)) # آسیب به دشمن
        dmg2 = max(0, p2_atk - int(p1_def * 0.4)) # آسیب به خودی
        
        c1 = COUNTRIES[user['country']]      # مهاجم
        c2 = COUNTRIES[target_user['country']] # مدافع
        
        attacker_won = dmg1 > dmg2
        defender_won = dmg2 > dmg1

        # --- گزارش برای مهاجم (کاربر فعلی) ---
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
            f"🔴 شما ({c1['flag']} {c1['name']}): ⚔️{p1_atk} 🛡️{p1_def}\n"
            f"🔵 دشمن ({c2['flag']} {c2['name']}): ⚔️{p2_atk} 🛡️{p2_def}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💥 آسیب وارد شده به دشمن: {dmg1}\n"
            f"💥 آسیب دریافت شده از دشمن: {dmg2}\n\n"
            f"{attacker_result}"
        )

        # --- گزارش برای مدافع (هدف حمله) ---
        if defender_won:
            defender_result = f"🏆 *شما پیروز شدید (دفاع موفق)!*\n📈 تجربه: +50\n💰 پاداش دفاعی: +{penalty}"
        elif attacker_won:
            defender_result = f"💀 *شما شکست خوردید (دفاع ناموفق)!*\n💸 غنیمت از دست رفته: -{int(target_user['budget'] * 0.15)}"
        else:
            defender_result = "🤝 *نبرد مساوی!*"

        defender_report = (
            f"⚠️ *گزارش حمله دشمن*\n\n"
            f"🔵 شما ({c2['flag']} {c2['name']}): ⚔️{p2_atk} 🛡️{p2_def}\n"
            f"🔴 مهاجم ({c1['flag']} {c1['name']}): ⚔️{p1_atk} 🛡️{p1_def}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💥 آسیب وارد شده به مهاجم: {dmg2}\n"
            f"💥 آسیب دریافت شده از مهاجم: {dmg1}\n\n"
            f"{defender_result}"
        )

        # اعلام در گروه همگانی
        war_announcement = (
            f"🚨 *خبر فوری: آغاز نبرد!* 🚨\n\n"
            f"⚔️ نیروهای {c1['flag']} *{c1['name']}* به {c2['flag']} *{c2['name']}* حمله کردند!\n\n"
            f"📊 *نتیجه:* {'پیروزی ' + c1['name'] if attacker_won else 'پیروزی ' + c2['name'] if defender_won else 'مساوی'}"
        )
        announce_to_group(war_announcement)

        save_user(user); save_user(target_user)
        send_message(chat_id, attacker_report, reply_markup=main_menu_kb())
        send_message(target_id, defender_report, reply_markup=main_menu_kb())
        
        # ✨ بررسی ورشکستگی برای هر دو طرف پس از نبرد
        check_bankruptcy(chat_id)
        check_bankruptcy(target_id)

    elif data == "menu_alliance":
        if not user or not user['country']: return send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
        send_message(chat_id, f"🤝 *اتحادیه*\n\nاتحادیه فعلی: *{user['alliance']}*\n\nبرای تغییر، پیام متنی بفرستید:\n`اتحادیه نام_جدید`", reply_markup={"inline_keyboard": [[{"text": "🔙 بازگشت", "callback_data": "menu_main"}]]})

    elif data == "menu_lottery":
        send_message(chat_id, "🎰 *لاتاری*\n\nهزینه: 💰 100\n🥇 10%: 1,000 سکه\n🏆 1%: 5,000 سکه", reply_markup={"inline_keyboard": [[{"text": "🎟️ خرید بلیط", "callback_data": "lottery_play"}], [{"text": "🔙 بازگشت", "callback_data": "menu_main"}]]})

    elif data == "lottery_play":
        if user['budget'] < 100: return send_message(chat_id, "❌ بودجه کافی ندارید!", reply_markup=main_menu_kb())
        user['budget'] -= 100
        roll = random.randint(1, 100)
        if roll == 1: user['budget'] += 5000; msg = "🎉 *جکپات!* 5,000 سکه!"
        elif roll <= 10: user['budget'] += 1000; msg = "✅ *تبریک!* 1,000 سکه!"
        else: msg = "❌ *برنده نشدید.*"
        save_user(user)
        check_bankruptcy(chat_id) # ✨ بررسی ورشکستگی
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

    elif data == "menu_admin":
        if not is_admin(chat_id): return send_message(chat_id, "❌ دسترسی محدود!", reply_markup=main_menu_kb())
        send_message(chat_id, "🔧 *پنل مدیریت*", reply_markup=admin_menu_kb())

    elif data == "admin_toggle_war":
        new_val = 'false' if get_setting('war_enabled') == 'true' else 'true'
        set_setting('war_enabled', new_val)
        send_message(chat_id, f"✅ وضعیت جنگ: {'فعال' if new_val == 'true' else 'غیرفعال'}", reply_markup=admin_menu_kb())

    elif data == "admin_prompt_msg":
        if not is_admin(chat_id): return
        send_message(chat_id, "📩 *ارسال پیام*\n\nفرمت: `send_msg 123456789 متن`", reply_markup=admin_menu_kb())

    elif data == "admin_list_users":
        if not is_admin(chat_id): return
        rows = conn.cursor().execute("SELECT chat_id, country, budget, wins, is_banned FROM users").fetchall()
        msg = "👥 *لیست کاربران*\n\n"
        for r in rows:
            c_name = COUNTRIES.get(r[1], {"name": "بدون کشور", "flag": "🏳️"})
            ban_icon = "🚫" if r[4] else ""
            msg += f"{ban_icon} 🆔 `{r[0]}` | {c_name['flag']} {c_name['name']} | 💰{r[2]} | 🏆{r[3]}\n"
        send_message(chat_id, msg, reply_markup=admin_menu_kb())

    elif data == "admin_manage_budget":
        if not is_admin(chat_id): return
        send_message(chat_id, "💰 *مدیریت بودجه*\n\n`add_money ID مبلغ`\n`remove_money ID مبلغ`", reply_markup=admin_menu_kb())

    elif data == "admin_manage_prices":
        if not is_admin(chat_id): return
        prices = get_equipment_prices()
        text = "💎 *قیمت تجهیزات*\n\n" + "\n".join([f"{v['emoji']} {v['name']}: 💰{prices[k]}" for k, v in EQUIPMENT.items()])
        text += "\n\nتغییر قیمت: `set_price tank 150`"
        send_message(chat_id, text, reply_markup={"inline_keyboard": [[{"text": "🔙 بازگشت", "callback_data": "menu_admin"}]]})

    elif data == "admin_manage_chats":
        if not is_admin(chat_id): return
        chats = get_forced_chats()
        text = "📢 *لینک‌های اجباری*\n\n" + ("\n".join([f"{'📢' if c[2]=='channel' else '👥'} {c[1]} (`{c[0]}`)" for c in chats]) if chats else "_(تنظیم نشده)_")
        text += "\n\n`add_chat @username`\n`remove_chat @username`"
        send_message(chat_id, text, reply_markup={"inline_keyboard": [[{"text": "🔙 بازگشت", "callback_data": "menu_admin"}]]})


# ═══════════════════════════════════════════
#  حلقه اصلی ربات
# ═══════════════════════════════════════════
def main():
    print("🎮 ربات جنگ جهانی (نسخه نهایی با رفع باگ نبرد و ورشکستگی) در حال اجراست...")
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
                            handle_callback(update['callback_query']['message']['chat']['id'], update['callback_query']['data'], update['callback_query']['id'])
                        
                        elif 'message' in update:
                            chat_id = update['message']['chat']['id']
                            text = update['message'].get('text', '').strip()
                            user = get_user(chat_id)
                            admin_user = is_admin(chat_id)
                            
                            # ✨ بررسی بن بودن کاربر در پیام‌های متنی
                            if user and user.get('is_banned'):
                                send_message(chat_id, "🚫 *شما توسط پشتیبان مسدود (Ban) شده‌اید.*")
                                continue

                            if chat_id in user_states and user_states[chat_id] == "waiting_for_coins":
                                try:
                                    amount = int(text)
                                    if amount <= 0: raise ValueError
                                    del user_states[chat_id]
                                    for admin_id in ADMIN_IDS:
                                        send_message(admin_id, f"🔔 *درخواست خرید سکه*\n👤 ID: `{chat_id}`\n💎 مقدار: {amount}\n💰 بودجه فعلی: {user['budget']}\n\nدستور تایید:\n`add_money {chat_id} {amount}`")
                                    send_message(chat_id, f"✅ درخواست {amount} سکه ثبت شد. پشتیبان به زودی بررسی می‌کند.", reply_markup=main_menu_kb())
                                except ValueError:
                                    send_message(chat_id, "❌ لطفاً فقط یک عدد مثبت وارد کنید.", reply_markup={"inline_keyboard": [[{"text": "❌ لغو", "callback_data": "cancel_buy_coins"}]]})
                                continue
                            
                            if text.startswith("اتحادیه ") and user and user['country']:
                                user['alliance'] = text.replace("اتحادیه ", "").strip()
                                save_user(user)
                                send_message(chat_id, f"✅ عضو اتحادیه «*{user['alliance']}*» شدید.", reply_markup=main_menu_kb(is_admin_user=admin_user))
                            
                            elif text.startswith("send_msg ") and admin_user and len(text.split(maxsplit=2)) >= 3:
                                parts = text.split(maxsplit=2)
                                try:
                                    res = send_message(int(parts[1]), f"📩 *پیام پشتیبانی:*\n\n{parts[2]}")
                                    send_message(chat_id, "✅ ارسال شد." if res and res.get('ok') else f"❌ خطا: {res}")
                                except ValueError: send_message(chat_id, "❌ ID باید عدد باشد.")
                            
                            elif text.startswith("add_money ") and admin_user and len(text.split()) == 3:
                                t_user = get_user(int(text.split()[1]))
                                if t_user:
                                    t_user['budget'] += int(text.split()[2])
                                    save_user(t_user)
                                    send_message(chat_id, f"✅ {text.split()[2]} سکه به {text.split()[1]} اضافه شد.")
                                    send_message(int(text.split()[1]), f"🎁 ادمین {text.split()[2]} سکه به شما اضافه کرد!")
                            
                            elif text.startswith("remove_money ") and admin_user and len(text.split()) == 3:
                                t_user = get_user(int(text.split()[1]))
                                if t_user:
                                    t_user['budget'] = max(0, t_user['budget'] - int(text.split()[2]))
                                    save_user(t_user)
                                    send_message(chat_id, f"✅ {text.split()[2]} سکه از {text.split()[1]} کسر شد.")
                            
                            elif text.startswith("set_price ") and admin_user and len(text.split()) == 3 and text.split()[1] in EQUIPMENT:
                                try:
                                    set_equipment_price(text.split()[1], int(text.split()[2]))
                                    send_message(chat_id, f"✅ قیمت {EQUIPMENT[text.split()[1]]['emoji']} به 💰{text.split()[2]} تغییر کرد.", reply_markup=admin_menu_kb())
                                except ValueError: send_message(chat_id, "❌ قیمت باید عدد باشد!")
                            
                            # ✨ ✨ ✨ دستورات بن و آنبن کاربر ✨ ✨ ✨
                            elif text.startswith("ban_user ") and admin_user and len(text.split()) == 2:
                                try:
                                    target_id = int(text.split()[1])
                                    t_user = get_user(target_id)
                                    if t_user:
                                        c_info = COUNTRIES.get(t_user['country'], {"name": "نامشخص", "flag": "🏳️"})
                                        cursor = conn.cursor()
                                        cursor.execute("UPDATE users SET is_banned = 1 WHERE chat_id = ?", (target_id,))
                                        conn.commit()
                                        announce_to_group(f"🚫 *مسدودیت کاربر*\n\nفرمانده کشور {c_info['flag']} *{c_info['name']}* (ID: `{target_id}`) توسط پشتیبان از بازی مسدود (Ban) شد.")
                                        send_message(chat_id, f"✅ کاربر `{target_id}` بن شد.")
                                        send_message(target_id, "🚫 *شما توسط پشتیبان از بازی مسدود (Ban) شدید.*\nدر صورت اعتراض با پشتیبان تماس بگیرید.", reply_markup={"inline_keyboard": []})
                                except ValueError: send_message(chat_id, "❌ ID باید عدد باشد.")
                            
                            elif text.startswith("unban_user ") and admin_user and len(text.split()) == 2:
                                try:
                                    target_id = int(text.split()[1])
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE users SET is_banned = 0 WHERE chat_id = ?", (target_id,))
                                    conn.commit()
                                    send_message(chat_id, f"✅ کاربر `{target_id}` از حالت بن خارج (Unban) شد.")
                                    send_message(target_id, "✅ *حساب شما توسط پشتیبان آزاد (Unban) شد.*\nمی‌توانید به بازی ادامه دهید.", reply_markup=main_menu_kb())
                                except ValueError: send_message(chat_id, "❌ ID باید عدد باشد.")
                            
                            elif text.startswith("add_chat ") and admin_user and len(text.split(maxsplit=1)) == 2:
                                try:
                                    res = requests.post(f"{BASE_URL}getChat", json={'chat_id': text.split(maxsplit=1)[1].strip()}, timeout=10).json()
                                    if res.get('ok'):
                                        add_forced_chat(res['result']['id'], res['result'].get('title') or res['result'].get('username') or text.split(maxsplit=1)[1].strip(), res['result'].get('type', 'unknown'))
                                        send_message(chat_id, f"✅ به لیست اجباری اضافه شد.\n⚠️ *ربات باید در این چت ادمین باشد!*", reply_markup=admin_menu_kb())
                                except Exception as e: send_message(chat_id, f"❌ خطا: {e}")
                            
                            elif text.startswith("remove_chat ") and admin_user and len(text.split(maxsplit=1)) == 2:
                                for ch_id, ch_title, _, _ in get_forced_chats():
                                    if text.split(maxsplit=1)[1].strip() in [ch_title, str(ch_id), f"@{ch_title.lstrip('@')}"]:
                                        remove_forced_chat(ch_id)
                                        send_message(chat_id, f"✅ {ch_title} حذف شد.", reply_markup=admin_menu_kb())
                                        break
                            
                            elif admin_user:
                                send_message(chat_id, "🔧 *پنل مدیریت*", reply_markup=main_menu_kb(is_admin_user=True))
                            
                            elif not user or not user['country']:
                                send_message(chat_id, "👋 به بازی جنگ جهانی خوش آمدید!\nلطفاً کشور خود را انتخاب کنید:", reply_markup=main_menu_kb())
                            
                            elif not text.startswith('/') and not text.startswith("اتحادیه ") and not text.startswith("send_msg ") and not text.startswith("add_money ") and not text.startswith("remove_money ") and not text.startswith("set_price ") and not text.startswith("add_chat ") and not text.startswith("remove_chat ") and not text.startswith("ban_user ") and not text.startswith("unban_user "):
                                msg = f"🇺🇳 *سازمان ملل متحد*\n\n{text}" if admin_user else f"{COUNTRIES[user['country']]['flag']} *{COUNTRIES[user['country']]['name']}*\n\n{text}"
                                res = send_message(GROUP_CHAT_ID, msg)
                                send_message(chat_id, "✅ در گروه ارسال شد." if res and res.get('ok') else "❌ خطا در ارسال به گروه.", reply_markup=main_menu_kb(is_admin_user=admin_user))
            
            elif response.status_code == 401:
                print("❌ توکن اشتباه!"); time.sleep(10)
        except Exception as e:
            print(f"❌ خطا: {e}"); time.sleep(3)
        time.sleep(1)

if __name__ == '__main__':
    main()