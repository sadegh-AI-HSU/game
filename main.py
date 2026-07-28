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
#  داده‌های بازی (۱۰۰ کشور برتر دنیا)
# ═══════════════════════════════════════════
COUNTRIES = {
    "usa": {"name": "آمریکا 🇺🇸", "budget": 1000, "bonus": "air", "bonus_val": 1.4, "flag": "🇺🇸"},
    "russia": {"name": "روسیه 🇷🇺", "budget": 980, "bonus": "tank", "bonus_val": 1.4, "flag": "🇷🇺"},
    "china": {"name": "چین 🇨🇳", "budget": 970, "bonus": "soldier", "bonus_val": 1.35, "flag": "🇨🇳"},
    "india": {"name": "هند 🇮🇳", "budget": 950, "bonus": "missile", "bonus_val": 1.35, "flag": "🇮🇳"},
    "uk": {"name": "انگلستان 🇬🇧", "budget": 940, "bonus": "ship", "bonus_val": 1.35, "flag": "🇬🇧"},
    "france": {"name": "فرانسه 🇫🇷", "budget": 930, "bonus": "air", "bonus_val": 1.35, "flag": "🇫🇷"},
    "japan": {"name": "ژاپن 🇯🇵", "budget": 920, "bonus": "ship", "bonus_val": 1.35, "flag": "🇯🇵"},
    "skorea": {"name": "کره جنوبی 🇰🇷", "budget": 910, "bonus": "drone", "bonus_val": 1.35, "flag": "🇰🇷"},
    "israel": {"name": "اسرائیل 🇮🇱", "budget": 900, "bonus": "defense", "bonus_val": 1.4, "flag": "🇮🇱"},
    "iran": {"name": "ایران 🇮🇷", "budget": 900, "bonus": "missile", "bonus_val": 1.4, "flag": "🇮🇷"},
    "germany": {"name": "آلمان 🇩🇪", "budget": 890, "bonus": "tank", "bonus_val": 1.3, "flag": "🇩🇪"},
    "turkey": {"name": "ترکیه 🇹🇷", "budget": 880, "bonus": "drone", "bonus_val": 1.35, "flag": "🇹🇷"},
    "italy": {"name": "ایتالیا 🇮🇹", "budget": 870, "bonus": "ship", "bonus_val": 1.3, "flag": "🇮🇹"},
    "egypt": {"name": "مصر 🇪🇬", "budget": 860, "bonus": "tank", "bonus_val": 1.3, "flag": "🇪🇬"},
    "pakistan": {"name": "پاکستان 🇵🇰", "budget": 850, "bonus": "missile", "bonus_val": 1.3, "flag": "🇵🇰"},
    "brazil": {"name": "برزیل 🇧🇷", "budget": 840, "bonus": "soldier", "bonus_val": 1.3, "flag": "🇧🇷"},
    "australia": {"name": "استرالیا 🇦🇺", "budget": 830, "bonus": "air", "bonus_val": 1.3, "flag": "🇦🇺"},
    "canada": {"name": "کانادا 🇨🇦", "budget": 820, "bonus": "defense", "bonus_val": 1.3, "flag": "🇨🇦"},
    "saudi": {"name": "عربستان 🇸🇦", "budget": 810, "bonus": "air", "bonus_val": 1.3, "flag": "🇸🇦"},
    "uae": {"name": "امارات 🇦🇪", "budget": 800, "bonus": "drone", "bonus_val": 1.3, "flag": "🇦🇪"},
    "spain": {"name": "اسپانیا 🇪🇸", "budget": 790, "bonus": "ship", "bonus_val": 1.25, "flag": "🇪🇸"},
    "indonesia": {"name": "اندونزی 🇮🇩", "budget": 780, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇮🇩"},
    "poland": {"name": "لهستان 🇵🇱", "budget": 770, "bonus": "tank", "bonus_val": 1.25, "flag": "🇵🇱"},
    "ukraine": {"name": "اوکراین 🇺🇦", "budget": 760, "bonus": "drone", "bonus_val": 1.3, "flag": "🇺🇦"},
    "algeria": {"name": "الجزایر 🇩🇿", "budget": 750, "bonus": "missile", "bonus_val": 1.25, "flag": "🇩🇿"},
    "argentina": {"name": "آرژانتین 🇦🇷", "budget": 740, "bonus": "ship", "bonus_val": 1.25, "flag": "🇦🇷"},
    "mexico": {"name": "مکزیک 🇲🇽", "budget": 730, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇲🇽"},
    "southafrica": {"name": "آفریقای جنوبی 🇿🇦", "budget": 720, "bonus": "tank", "bonus_val": 1.25, "flag": "🇿🇦"},
    "netherlands": {"name": "هلند 🇳🇱", "budget": 710, "bonus": "ship", "bonus_val": 1.25, "flag": "🇳🇱"},
    "greece": {"name": "یونان 🇬🇷", "budget": 700, "bonus": "air", "bonus_val": 1.25, "flag": "🇬🇷"},
    "vietnam": {"name": "ویتنام 🇻🇳", "budget": 690, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇻🇳"},
    "thailand": {"name": "تایلند 🇹🇭", "budget": 680, "bonus": "ship", "bonus_val": 1.25, "flag": "🇹🇭"},
    "malaysia": {"name": "مالزی 🇲🇾", "budget": 670, "bonus": "air", "bonus_val": 1.25, "flag": "🇲🇾"},
    "philippines": {"name": "فیلیپین 🇵🇭", "budget": 660, "bonus": "ship", "bonus_val": 1.25, "flag": "🇵🇭"},
    "colombia": {"name": "کلمبیا 🇨🇴", "budget": 650, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇨🇴"},
    "nigeria": {"name": "نیجریه 🇳🇬", "budget": 640, "bonus": "soldier", "bonus_val": 1.25, "flag": "🇳🇬"},
    "morocco": {"name": "مراکش 🇲🇦", "budget": 630, "bonus": "drone", "bonus_val": 1.25, "flag": "🇲🇦"},
    "sweden": {"name": "سوئد 🇸🇪", "budget": 620, "bonus": "air", "bonus_val": 1.25, "flag": "🇸🇪"},
    "switzerland": {"name": "سوئیس 🇨🇭", "budget": 610, "bonus": "defense", "bonus_val": 1.3, "flag": "🇨🇭"},
    "singapore": {"name": "سنگاپور 🇸🇬", "budget": 600, "bonus": "ship", "bonus_val": 1.25, "flag": "🇸🇬"},
    "romania": {"name": "رومانی 🇷🇴", "budget": 590, "bonus": "tank", "bonus_val": 1.2, "flag": "🇷🇴"},
    "chile": {"name": "شیلی 🇨🇱", "budget": 580, "bonus": "ship", "bonus_val": 1.2, "flag": "🇨🇱"},
    "finland": {"name": "فنلاند 🇫🇮", "budget": 570, "bonus": "air", "bonus_val": 1.2, "flag": "🇫🇮"},
    "iraq": {"name": "عراق 🇮🇶", "budget": 560, "bonus": "soldier", "bonus_val": 1.2, "flag": "🇮🇶"},
    "newzealand": {"name": "نیوزیلند 🇳🇿", "budget": 550, "bonus": "ship", "bonus_val": 1.2, "flag": "🇳🇿"},
    "peru": {"name": "پرو 🇵🇪", "budget": 540, "bonus": "soldier", "bonus_val": 1.2, "flag": "🇵🇪"},
    "venezuela": {"name": "ونزوئلا 🇻🇪", "budget": 530, "bonus": "missile", "bonus_val": 1.2, "flag": "🇻🇪"},
    "czechia": {"name": "چک 🇨🇿", "budget": 520, "bonus": "tank", "bonus_val": 1.2, "flag": "🇨🇿"},
    "bangladesh": {"name": "بنگلادش 🇧🇩", "budget": 510, "bonus": "soldier", "bonus_val": 1.2, "flag": "🇧🇩"},
    "hungary": {"name": "مجارستان 🇭🇺", "budget": 500, "bonus": "tank", "bonus_val": 1.2, "flag": "🇭🇺"},
    "belgium": {"name": "بلژیک 🇧🇪", "budget": 490, "bonus": "air", "bonus_val": 1.2, "flag": "🇧🇪"},
    "austria": {"name": "اتریش 🇦🇹", "budget": 480, "bonus": "defense", "bonus_val": 1.2, "flag": "🇦🇹"},
    "norway": {"name": "نروژ 🇳🇴", "budget": 470, "bonus": "ship", "bonus_val": 1.2, "flag": "🇳🇴"},
    "denmark": {"name": "دانمارک 🇩🇰", "budget": 460, "bonus": "air", "bonus_val": 1.2, "flag": "🇩🇰"},
    "portugal": {"name": "پرتغال 🇵🇹", "budget": 440, "bonus": "ship", "bonus_val": 1.2, "flag": "🇵🇹"},
    "syria": {"name": "سوریه 🇸🇾", "budget": 430, "bonus": "missile", "bonus_val": 1.2, "flag": "🇸🇾"},
    "jordan": {"name": "اردن 🇯🇴", "budget": 420, "bonus": "air", "bonus_val": 1.2, "flag": "🇯🇴"},
    "serbia": {"name": "صربستان 🇷🇸", "budget": 410, "bonus": "tank", "bonus_val": 1.2, "flag": "🇷🇸"},
    "azerbaijan": {"name": "آذربایجان 🇦🇿", "budget": 400, "bonus": "drone", "bonus_val": 1.25, "flag": "🇦🇿"},
    "afghanistan": {"name": "افغانستان 🇦🇫", "budget": 390, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇦🇫"},
    "lebanon": {"name": "لبنان 🇱🇧", "budget": 380, "bonus": "missile", "bonus_val": 1.15, "flag": "🇱🇧"},
    "yemen": {"name": "یمن 🇾🇪", "budget": 370, "bonus": "missile", "bonus_val": 1.15, "flag": "🇾🇪"},
    "oman": {"name": "عمان 🇴🇲", "budget": 360, "bonus": "ship", "bonus_val": 1.15, "flag": "🇴🇲"},
    "qatar": {"name": "قطر 🇶🇦", "budget": 350, "bonus": "air", "bonus_val": 1.15, "flag": "🇶🇦"},
    "kuwait": {"name": "کویت 🇰🇼", "budget": 340, "bonus": "air", "bonus_val": 1.15, "flag": "🇰🇼"},
    "georgia": {"name": "گرجستان 🇬🇪", "budget": 330, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇬🇪"},
    "armenia": {"name": "ارمنستان 🇦🇲", "budget": 320, "bonus": "defense", "bonus_val": 1.15, "flag": "🇦🇲"},
    "kazakhstan": {"name": "قزاقستان 🇰🇿", "budget": 310, "bonus": "tank", "bonus_val": 1.15, "flag": "🇰🇿"},
    "uzbekistan": {"name": "ازبکستان 🇺🇿", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇺🇿"},
    "mongolia": {"name": "مغولستان 🇲🇳", "budget": 300, "bonus": "tank", "bonus_val": 1.15, "flag": "🇲🇳"},
    "cuba": {"name": "کوبا 🇨🇺", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇨🇺"},
    "bolivia": {"name": "بولیوی 🇧🇴", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇧🇴"},
    "paraguay": {"name": "پاراگوئه 🇵🇾", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇵🇾"},
    "uruguay": {"name": "اروگوئه 🇺🇾", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇺🇾"},
    "ecuador": {"name": "اکوادور 🇪🇨", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇪🇨"},
    "guatemala": {"name": "گواتمالا 🇬🇹", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇬🇹"},
    "costarica": {"name": "کاستاریکا 🇨🇷", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇨🇷"},
    "panama": {"name": "پاناما 🇵🇦", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇵🇦"},
    "jamaica": {"name": "جامائیکا 🇯🇲", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇯🇲"},
    "trinidad": {"name": "ترینیداد 🇹🇹", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇹🇹"},
    "bahamas": {"name": "باهاما 🇧🇸", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇧🇸"},
    "croatia": {"name": "کرواسی 🇭🇷", "budget": 350, "bonus": "ship", "bonus_val": 1.15, "flag": "🇭🇷"},
    "bulgaria": {"name": "بلغارستان 🇧🇬", "budget": 340, "bonus": "tank", "bonus_val": 1.15, "flag": "🇧🇬"},
    "slovakia": {"name": "اسلواکی 🇸🇰", "budget": 330, "bonus": "tank", "bonus_val": 1.15, "flag": "🇸🇰"},
    "lithuania": {"name": "لیتوانی 🇱🇹", "budget": 320, "bonus": "air", "bonus_val": 1.15, "flag": "🇱🇹"},
    "latvia": {"name": "لتونی 🇱🇻", "budget": 310, "bonus": "air", "bonus_val": 1.15, "flag": "🇱🇻"},
    "estonia": {"name": "استونی 🇪🇪", "budget": 300, "bonus": "cyber", "bonus_val": 1.15, "flag": "🇪🇪"},
    "belarus": {"name": "بلاروس 🇧🇾", "budget": 350, "bonus": "missile", "bonus_val": 1.15, "flag": "🇧🇾"},
    "moldova": {"name": "مولداوی 🇲🇩", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇩"},
    "cyprus": {"name": "قبرس 🇨🇾", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇨🇾"},
    "malta": {"name": "مالت 🇲🇹", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇲🇹"},
    "iceland": {"name": "ایسلند 🇮🇸", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇮🇸"},
    "luxembourg": {"name": "لوکزامبورگ 🇱🇺", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇱🇺"},
    "ireland": {"name": "ایرلند 🇮🇪", "budget": 350, "bonus": "air", "bonus_val": 1.15, "flag": "🇮🇪"},
    "sudan": {"name": "سودان 🇸🇩", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇸🇩"},
    "ethiopia": {"name": "اتیوپی 🇪🇹", "budget": 350, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇪🇹"},
    "kenya": {"name": "کنیا 🇰🇪", "budget": 320, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇰🇪"},
    "ghana": {"name": "غنا 🇬🇭", "budget": 310, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇬🇭"},
    "senegal": {"name": "سنگال 🇸🇳", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇸🇳"},
    "tanzania": {"name": "تانزانیا 🇹🇿", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇹🇿"},
    "uganda": {"name": "اوگاندا 🇺🇬", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇺🇬"},
    "zambia": {"name": "زامبیا 🇿🇲", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇿🇲"},
    "zimbabwe": {"name": "زیمبابوه 🇿🇼", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇿🇼"},
    "angola": {"name": "آنگولا 🇦🇴", "budget": 320, "bonus": "missile", "bonus_val": 1.15, "flag": "🇦🇴"},
    "mozambique": {"name": "موزامبیک 🇲🇿", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇿"},
    "madagascar": {"name": "ماداگاسکار 🇲🇬", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇬"},
    "cameroon": {"name": "کامرون 🇨🇲", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇨🇲"},
    "ivorycoast": {"name": "ساحل عاج 🇨🇮", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇨🇮"},
    "mali": {"name": "مالی 🇲🇱", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇱"},
    "burkina": {"name": "بورکینافاسو 🇧🇫", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇧🇫"},
    "niger": {"name": "نیجر 🇳🇪", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇳🇪"},
    "chad": {"name": "چاد 🇹🇩", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇹🇩"},
    "somalia": {"name": "سومالی 🇸🇴", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇸🇴"},
    "rwanda": {"name": "رواندا 🇷🇼", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇷🇼"},
    "nepal": {"name": "نپال 🇳🇵", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇳🇵"},
    "srilanka": {"name": "سریلانکا 🇱🇰", "budget": 320, "bonus": "ship", "bonus_val": 1.15, "flag": "🇱🇰"},
    "myanmar": {"name": "میانمار 🇲🇲", "budget": 330, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇲"},
    "cambodia": {"name": "کامبوج 🇰🇭", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇰🇭"},
    "laos": {"name": "لائوس 🇱🇦", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇱🇦"},
    "brunei": {"name": "برونئی 🇧🇳", "budget": 350, "bonus": "ship", "bonus_val": 1.15, "flag": "🇧🇳"},
    "papua": {"name": "پاپوآ گینه نو 🇵🇬", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇵🇬"},
    "fiji": {"name": "فیجی 🇫🇯", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇫🇯"},
    "solomon": {"name": "جزایر سلیمان 🇸🇧", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇸🇧"},
    "vanuatu": {"name": "وانواتو 🇻🇺", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇻🇺"},
    "samoa": {"name": "ساموآ 🇼🇸", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇼🇸"},
    "kiribati": {"name": "کیریباتی 🇰🇮", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇰🇮"},
    "tonga": {"name": "تونگا 🇹🇴", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇹🇴"},
    "seychelles": {"name": "سیشل 🇸🇨", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇸🇨"},
    "mauritius": {"name": "موریس 🇲🇺", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇲🇺"},
    "maldives": {"name": "مالدیو 🇲🇻", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇲🇻"},
    "bhutan": {"name": "بوتان 🇧🇹", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇧🇹"},
    "tajikistan": {"name": "تاجیکستان 🇹🇯", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇹🇯"},
    "kyrgyzstan": {"name": "قرقیزستان 🇰🇬", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇰🇬"},
    "turkmenistan": {"name": "ترکمنستان 🇹🇲", "budget": 300, "bonus": "missile", "bonus_val": 1.15, "flag": "🇹🇲"},
    "northkorea": {"name": "کره شمالی 🇰🇵", "budget": 400, "bonus": "missile", "bonus_val": 1.3, "flag": "🇰🇵"},
    "haiti": {"name": "هائیتی 🇭🇹", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇭🇹"},
    "honduras": {"name": "هندوراس 🇭🇳", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇭🇳"},
    "elsalvador": {"name": "السالوادور 🇸🇻", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇸🇻"},
    "nicaragua": {"name": "نیکاراگوئه 🇳🇮", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇳🇮"},
    "dominican": {"name": "جمهوری دومینیکن 🇩🇴", "budget": 320, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇩🇴"},
    "albania": {"name": "آلبانی 🇦🇱", "budget": 310, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇦🇱"},
    "macedonia": {"name": "مقدونیه 🇲🇰", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇰"},
    "bosnia": {"name": "بوسنی 🇧🇦", "budget": 310, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇧🇦"},
    "kosovo": {"name": "کوزوو 🇽🇰", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇽🇰"},
    "montenegro": {"name": "مونته‌نگرو 🇲🇪", "budget": 300, "bonus": "ship", "bonus_val": 1.15, "flag": "🇲🇪"},
    "andorra": {"name": "آندورا 🇦🇩", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇦🇩"},
    "monaco": {"name": "موناکو 🇲🇨", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇲🇨"},
    "sanmarino": {"name": "سان مارینو 🇸🇲", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇸🇲"},
    "vatican": {"name": "واتیکان 🇻🇦", "budget": 300, "bonus": "defense", "bonus_val": 1.15, "flag": "🇻🇦"},
    "libya": {"name": "لیبی 🇱🇾", "budget": 350, "bonus": "tank", "bonus_val": 1.15, "flag": "🇱🇾"},
    "tunisia": {"name": "تونس 🇹🇳", "budget": 340, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇹🇳"},
    "mauritania": {"name": "موریتانی 🇲🇷", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇲🇷"},
    "gambia": {"name": "گامبیا 🇬🇲", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇬🇲"},
    "guinea": {"name": "گینه 🇬🇳", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇬🇳"},
    "liberia": {"name": "لیبریا 🇱🇷", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇱🇷"},
    "sierraleone": {"name": "سیرالئون 🇸🇱", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇸🇱"},
    "togo": {"name": "توگو 🇹🇬", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇹🇬"},
    "benin": {"name": "بنین 🇧🇯", "budget": 300, "bonus": "soldier", "bonus_val": 1.15, "flag": "🇧🇯"},
}

EQUIPMENT = {
    "tank": {"name": "تانک 🛡️", "price": 80, "attack": 15, "defense": 20},
    "jet": {"name": "جنگنده ✈️", "price": 120, "attack": 25, "defense": 10},
    "ship": {"name": "ناو جنگی 🚢", "price": 150, "attack": 20, "defense": 25},
    "soldier": {"name": "سرباز 🪖", "price": 50, "attack": 10, "defense": 10},
    "missile": {"name": "موشک 🚀", "price": 200, "attack": 35, "defense": 0},
    "defense": {"name": "پدافند 🛡️", "price": 130, "attack": 0, "defense": 30},
    "drone": {"name": "پهپاد 🤖", "price": 90, "attack": 18, "defense": 5},
}

RESOURCES = {
    "oil": {"name": "نفت 🛢️", "buy_price": 50, "sell_price": 70},
    "goods": {"name": "کالای غیرنفتی 📦", "buy_price": 30, "sell_price": 45}
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
    
    # ✨ اگر ادمین است، فقط منوی ادمین را نشان بده
    if is_admin_user:
        kb["inline_keyboard"] = [
            [{"text": "🔧 پنل مدیریت (پشتیبان)", "callback_data": "menu_admin"}],
            [{"text": "📩 ارسال پیام به کاربر", "callback_data": "admin_prompt_msg"}],
            [{"text": "💰 مدیریت بودجه کاربران", "callback_data": "admin_manage_budget"}],
            [{"text": "👥 لیست کل کاربران", "callback_data": "admin_list_users"}]
        ]
        return kb
    
    # منوی عادی برای بازیکنان
    kb["inline_keyboard"] = [
        [{"text": "🌍 انتخاب کشور", "callback_data": "menu_country"}],
        [{"text": "🏪 فروشگاه", "callback_data": "menu_shop"}, {"text": "📦 انبار و تجارت", "callback_data": "menu_inventory"}],
        [{"text": "⚔️ اتاق جنگ (حمله)", "callback_data": "menu_war"}, {"text": "🤝 اتحادیه‌ها", "callback_data": "menu_alliance"}],
        [{"text": "🎰 لاتاری", "callback_data": "menu_lottery"}, {"text": "👤 پروفایل من", "callback_data": "menu_profile"}],
        [{"text": "💰 دریافت حقوق روزانه", "callback_data": "action_daily"}]
    ]
    return kb

def admin_menu_kb():
    war_status = "✅ فعال" if get_setting('war_enabled') == 'true' else "❌ غیرفعال"
    return {"inline_keyboard": [
        [{"text": f"⚙️ وضعیت جنگ: {war_status}", "callback_data": "admin_toggle_war"}],
        [{"text": "📩 ارسال پیام به کاربر", "callback_data": "admin_prompt_msg"}],
        [{"text": "💰 مدیریت بودجه کاربران", "callback_data": "admin_manage_budget"}],
        [{"text": "👥 لیست کل کاربران", "callback_data": "admin_list_users"}]
    ]}

# ═══════════════════════════════════════════
#  منطق بازی و منوها
# ═══════════════════════════════════════════
def handle_callback(chat_id, data, cb_id):
    answer_callback(cb_id)
    user = get_user(chat_id)
    admin_user = is_admin(chat_id)
    
    # ✨ اگر ادمین است و می‌خواهد وارد بخش بازی شود، اجازه نده
    if admin_user and data in ["menu_country", "menu_shop", "menu_inventory", "menu_war", "menu_alliance", "menu_lottery", "menu_profile", "action_daily"]:
        send_message(chat_id, "🚫 *شما به عنوان پشتیبان، امکان بازی ندارید!*\n\nلطفاً از پنل مدیریت استفاده کنید.", reply_markup=main_menu_kb(is_admin_user=True))
        return
    
    if data == "menu_main":
        msg = "🌍 *به بازی جنگ جهانی خوش آمدید!*\n\nاز منوی زیر بخش مورد نظر را انتخاب کنید:"
        kb = main_menu_kb(is_admin_user=admin_user)
        send_message(chat_id, msg, reply_markup=kb)

    elif data == "menu_profile":
        if not user or not user['country']:
            send_message(chat_id, "❌ شما هنوز کشوری انتخاب نکرده‌اید!", reply_markup=main_menu_kb())
            return
        c_info = COUNTRIES[user['country']]
        inv_text = "\n".join([f"• {RESOURCES[k]['name']}: {v}" for k, v in user['inventory'].items() if v > 0]) or "_(خالی)_"
        msg = f"👤 *پروفایل فرمانده*\n\n🏳️ کشور: {c_info['name']}\n🤝 اتحادیه: {user['alliance']}\n🎖️ سطح: {user['level']} (XP: {user['xp']}/{user['level']*100})\n💰 بودجه: {user['budget']}\n🏆 برد: {user['wins']} | 💀 باخت: {user['losses']}\n\n📦 *انبار منابع:*\n{inv_text}"
        send_message(chat_id, msg, reply_markup=main_menu_kb())

    elif data == "menu_country":
        if user and user['country']:
            send_message(chat_id, f"⚠️ شما متعلق به {COUNTRIES[user['country']]['name']} هستید.", reply_markup=main_menu_kb())
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
            row = [{"text": items[i][1]["name"], "callback_data": f"select_country:{items[i][0]}"}]
            if i + 1 < len(items):
                row.append({"text": items[i+1][1]["name"], "callback_data": f"select_country:{items[i+1][0]}"})
            kb["inline_keyboard"].append(row)
        send_message(chat_id, "🌍 *کشور خود را انتخاب کنید:*\n_(هر کشور فقط متعلق به یک فرمانده است)_", reply_markup=kb)

    elif data.startswith("select_country:"):
        country_key = data.split(":")[1]
        new_user = {"chat_id": chat_id, "country": country_key, "budget": COUNTRIES[country_key]['budget'], 
                    "equipment": {}, "wins": 0, "losses": 0, "xp": 0, "level": 1, "last_daily": 0, 
                    "alliance": "بدون اتحادیه", "inventory": {}}
        save_user(new_user)
        send_message(chat_id, f"✅ {COUNTRIES[country_key]['name']} با موفقیت انتخاب شد!\n💰 بودجه اولیه: {COUNTRIES[country_key]['budget']}", reply_markup=main_menu_kb())

    elif data == "menu_shop":
        if not user or not user['country']:
            send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
            return
        prices = get_equipment_prices()
        text = f"🏪 *فروشگاه تجهیزات*\n💰 بودجه شما: {user['budget']}\n\n"
        kb = {"inline_keyboard": []}
        for k, v in EQUIPMENT.items():
            text += f"🔹 {v['name']} | ⚔️{v['attack']} 🛡️{v['defense']} | 💰{prices[k]}\n"
            kb["inline_keyboard"].append([{"text": f"خرید {v['name']}", "callback_data": f"buy_eq:{k}"}])
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
            send_message(chat_id, f"✅ {EQUIPMENT[eq_key]['name']} خریداری شد!", reply_markup=main_menu_kb())
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
            text += f"🔸 {res_info['name']}: تعداد {amount}\n   (خرید: 💰{res_info['buy_price']} | فروش: 💰{res_info['sell_price']})\n"
            kb["inline_keyboard"].append([
                {"text": f"خرید {res_info['name']}", "callback_data": f"trade_buy:{res_key}"},
                {"text": f"فروش {res_info['name']}", "callback_data": f"trade_sell:{res_key}"}
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
            send_message(chat_id, f"✅ {RESOURCES[res_key]['name']} خریداری شد.", reply_markup=main_menu_kb())
        else:
            send_message(chat_id, "❌ بودجه کافی نیست!", reply_markup=main_menu_kb())

    elif data.startswith("trade_sell:"):
        res_key = data.split(":")[1]
        if user['inventory'].get(res_key, 0) > 0:
            user['inventory'][res_key] -= 1
            user['budget'] += RESOURCES[res_key]['sell_price']
            save_user(user)
            send_message(chat_id, f"✅ {RESOURCES[res_key]['name']} فروخته شد.", reply_markup=main_menu_kb())
        else:
            send_message(chat_id, "❌ این کالا را در انبار ندارید!", reply_markup=main_menu_kb())

    elif data == "menu_war":
        if get_setting('war_enabled') != 'true':
            send_message(chat_id, "🚫 *جنگ جهانی متوقف شده است!*\nپشتیبان فعلاً امکان حمله را غیرفعال کرده است.", reply_markup=main_menu_kb())
            return
        if not user or not user['country']:
            send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, country, level FROM users WHERE country IS NOT NULL AND chat_id != ?", (chat_id,))
        targets = cursor.fetchall()
        
        if not targets:
            send_message(chat_id, "🌍 در حال حاضر کشور دیگری برای حمله وجود ندارد!", reply_markup=main_menu_kb())
            return
            
        text = "⚔️ *انتخاب هدف برای حمله*\n\nکشور مورد نظر خود را انتخاب کنید:"
        kb = {"inline_keyboard": []}
        for t in targets:
            t_country = COUNTRIES[t[1]]['name']
            kb["inline_keyboard"].append([{"text": f"⚔️ حمله به {t_country} (سطح {t[2]})", "callback_data": f"attack_confirm:{t[0]}"}])
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

        report = f"⚔️ *گزارش نبرد*\n\n🔴 شما: ⚔️{p1_atk} 🛡️{p1_def}\n🔵 دشمن: ⚔️{p2_atk} 🛡️{p2_def}\n━━━━━━━━━━━━━━\n"
        
        if dmg1 > dmg2:
            loot = int(target_user['budget'] * 0.15)
            target_loss = int(target_user['budget'] * 0.15)
            user['wins'] += 1; user['xp'] += 50; user['budget'] += loot
            target_user['losses'] += 1; target_user['budget'] -= target_loss
            
            if target_user['equipment'] and random.random() < 0.3:
                lost_eq = random.choice(list(target_user['equipment'].keys()))
                target_user['equipment'][lost_eq] -= 1
                if target_user['equipment'][lost_eq] <= 0: del target_user['equipment'][lost_eq]
                report += f"💥 شما یک عدد {EQUIPMENT[lost_eq]['name']} از دشمن نابود کردید!\n"

            report += f"🏆 *شما پیروز شدید!*\n💰 غنیمت: +{loot}\n📈 تجربه: +50"
            if user['xp'] >= user['level'] * 100:
                user['level'] += 1; user['budget'] += 500; user['xp'] = 0
                report += f"\n\n🎉 *تبریک! به سطح {user['level']} رسیدید (+500 بودجه)*"

        elif dmg2 > dmg1:
            penalty = int(user['budget'] * 0.10)
            user['losses'] += 1; user['budget'] -= penalty
            target_user['wins'] += 1; target_user['xp'] += 50; target_user['budget'] += penalty
            report += f"💀 *شما شکست خوردید!*\n💸 هزینه تعمیرات: -{penalty}"
            
            if user['equipment'] and random.random() < 0.2:
                lost_eq = random.choice(list(user['equipment'].keys()))
                user['equipment'][lost_eq] -= 1
                if user['equipment'][lost_eq] <= 0: del user['equipment'][lost_eq]
                report += f"\n💥 یک عدد {EQUIPMENT[lost_eq]['name']} شما در نبرد نابود شد!"
        else:
            report += "🤝 *نبرد مساوی!* هیچ‌کس سود یا زیانی نکرد."

        save_user(user)
        save_user(target_user)
        send_message(chat_id, report, reply_markup=main_menu_kb())
        send_message(target_id, f"⚠️ *شما مورد حمله قرار گرفتید!*\n\n{report}", reply_markup=main_menu_kb())

    elif data == "menu_alliance":
        if not user or not user['country']:
            send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.", reply_markup=main_menu_kb())
            return
        text = f"🤝 *مدیریت اتحادیه*\n\nاتحادیه فعلی شما: *{user['alliance']}*\n\nبرای تغییر نام اتحادیه، عبارت زیر را به صورت پیام متنی برای ربات بفرستید:\n`اتحادیه نام_جدید`"
        kb = {"inline_keyboard": [[{"text": "🔙 بازگشت", "callback_data": "menu_main"}]]}
        send_message(chat_id, text, reply_markup=kb)

    elif data == "menu_lottery":
        text = "🎰 *لاتاری شانس*\n\nهزینه بلیط: 💰 100\n🥇 شانس 10%: برنده 1,000 سکه\n🏆 شانس 1%: برنده 5,000 سکه"
        kb = {"inline_keyboard": [
            [{"text": "🎟️ خرید بلیط (100 سکه)", "callback_data": "lottery_play"}],
            [{"text": "🔙 بازگشت", "callback_data": "menu_main"}]
        ]}
        send_message(chat_id, text, reply_markup=kb)

    elif data == "lottery_play":
        if user['budget'] < 100:
            send_message(chat_id, "❌ بودجه کافی برای خرید بلیط ندارید!", reply_markup=main_menu_kb())
            return
        user['budget'] -= 100
        roll = random.randint(1, 100)
        if roll == 1:
            prize = 5000; user['budget'] += prize; msg = f"🎉 *جکپات!* شما برنده {prize} سکه شدید!"
        elif roll <= 10:
            prize = 1000; user['budget'] += prize; msg = f"✅ *تبریک!* شما برنده {prize} سکه شدید!"
        else:
            msg = "❌ *متأسفانه برنده نشدید.* دوباره تلاش کنید!"
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
            send_message(chat_id, "✅ *حقوق روزانه دریافت شد!* (+300 سکه)", reply_markup=main_menu_kb())
        else:
            rem = 86400 - (now - user['last_daily'])
            send_message(chat_id, f"⏳ زمان باقیمانده: {rem // 3600} ساعت و {(rem % 3600) // 60} دقیقه", reply_markup=main_menu_kb())

    elif data == "menu_admin":
        if not is_admin(chat_id):
            send_message(chat_id, "❌ دسترسی محدود است!", reply_markup=main_menu_kb())
            return
        send_message(chat_id, "🔧 *پنل مدیریت*", reply_markup=admin_menu_kb())

    elif data == "admin_toggle_war":
        current = get_setting('war_enabled')
        new_val = 'false' if current == 'true' else 'true'
        set_setting('war_enabled', new_val)
        send_message(chat_id, f"✅ وضعیت جنگ به «{'فعال' if new_val == 'true' else 'غیرفعال'}» تغییر کرد.", reply_markup=admin_menu_kb())

    elif data == "admin_prompt_msg":
        if not is_admin(chat_id): return
        send_message(chat_id, "📩 *ارسال پیام خصوصی به کاربر*\n\nلطفاً شناسه کاربر و پیام را دقیقاً به این فرمت ارسال کنید:\n`send_msg 123456789 سلام، این یک پیام تست از پشتیبانی است.`", reply_markup=admin_menu_kb())

    elif data == "admin_list_users":
        if not is_admin(chat_id): return
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, country, budget, wins FROM users")
        rows = cursor.fetchall()
        msg = "👥 *لیست کاربران*\n\n"
        for r in rows:
            c_name = COUNTRIES.get(r[1], {"name": "نامشخص"})["name"] if r[1] else "بدون کشور"
            msg += f"🆔 `{r[0]}` | {c_name} | 💰{r[2]} | 🏆{r[3]}\n"
        send_message(chat_id, msg, reply_markup=admin_menu_kb())

    elif data == "admin_manage_budget":
        if not is_admin(chat_id): return
        send_message(chat_id, "💰 *مدیریت بودجه*\n\nلطفاً شناسه کاربر و مبلغ را به این فرمت بفرستید:\n`add_money 123456789 1000` (افزایش)\n`remove_money 123456789 500` (کاهش)", reply_markup=admin_menu_kb())


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
                            
                            # مدیریت اتحادیه
                            if text.startswith("اتحادیه "):
                                if not user or not user['country']:
                                    send_message(chat_id, "❌ ابتدا کشور انتخاب کنید.")
                                    continue
                                new_alliance = text.replace("اتحادیه ", "").strip()
                                user['alliance'] = new_alliance
                                save_user(user)
                                send_message(chat_id, f"✅ اتحادیه شما به «{new_alliance}» تغییر کرد.", reply_markup=main_menu_kb())
                            
                            # مدیریت پیام خصوصی ادمین
                            elif text.startswith("send_msg ") and admin_user:
                                parts = text.split(maxsplit=2)
                                if len(parts) >= 3:
                                    try:
                                        target_id = int(parts[1])
                                        msg_text = parts[2]
                                        res = send_message(target_id, f"📩 *پیام از طرف پشتیبانی:*\n\n{msg_text}")
                                        if res and res.get('ok'):
                                            send_message(chat_id, f"✅ پیام با موفقیت برای کاربر `{target_id}` ارسال شد.")
                                        else:
                                            send_message(chat_id, f"❌ خطا در ارسال پیام. آیا کاربر ربات را استارت کرده است؟\nخطا: {res}")
                                    except ValueError:
                                        send_message(chat_id, "❌ فرمت اشتباه است. شناسه کاربر باید یک عدد باشد.")
                                else:
                                    send_message(chat_id, "❌ فرمت اشتباه است. مثال: `send_msg 123456789 متن پیام`")
                            
                            elif text.startswith("add_money ") and admin_user:
                                parts = text.split()
                                if len(parts) == 3:
                                    t_id, amount = int(parts[1]), int(parts[2])
                                    t_user = get_user(t_id)
                                    if t_user:
                                        t_user['budget'] += amount
                                        save_user(t_user)
                                        send_message(chat_id, f"✅ {amount} سکه به کاربر {t_id} اضافه شد.")
                                        send_message(t_id, f"🎁 ادمین {amount} سکه به بودجه شما اضافه کرد!")
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
                                        send_message(chat_id, f"✅ {amount} سکه از کاربر {t_id} کسر شد.")
                                        send_message(t_id, f"⚠️ ادمین {amount} سکه از بودجه شما کسر کرد!")
                                    else:
                                        send_message(chat_id, "❌ کاربر یافت نشد.")
                            
                            # ✨ اگر ادمین است، منوی ادمین را نشان بده
                            elif admin_user:
                                send_message(chat_id, "🔧 *پنل مدیریت پشتیبان*\n\nشما به عنوان پشتیبان، امکان بازی ندارید.\nاز منوی زیر استفاده کنید:", reply_markup=main_menu_kb(is_admin_user=True))
                            
                            # ✨ اگر کاربر عادی است و کشور ندارد
                            elif not user or not user['country']:
                                send_message(chat_id, "👋 به بازی جنگ جهانی خوش آمدید!\nلطفاً از دکمه زیر کشور خود را انتخاب کنید:", reply_markup=main_menu_kb())
                            
                            # ✨ ارسال پیام به گروه همگانی
                            elif not text.startswith('/') and not text.startswith("اتحادیه ") and not text.startswith("send_msg ") and not text.startswith("add_money ") and not text.startswith("remove_money "):
                                # ✨ اگر ادمین است، با پرچم سازمان ملل ارسال کن
                                if admin_user:
                                    msg = f"🇺🇳 *سازمان ملل متحد*\n\n{text}"
                                else:
                                    c_info = COUNTRIES[user['country']]
                                    msg = f"{c_info['flag']} *{c_info['name']}*\n\n{text}"
                                
                                res = send_message(GROUP_CHAT_ID, msg)
                                if res and res.get('ok'):
                                    send_message(chat_id, "✅ پیام شما در گروه همگانی ارسال شد.", reply_markup=main_menu_kb(is_admin_user=admin_user))
                                else:
                                    send_message(chat_id, "❌ خطا در ارسال به گروه. مطمئن شوید ربات ادمین گروه است.", reply_markup=main_menu_kb(is_admin_user=admin_user))
            
            elif response.status_code == 401:
                print("❌ توکن اشتباه است!")
                time.sleep(10)
        except Exception as e:
            print(f"❌ خطا: {e}")
            time.sleep(3)
        time.sleep(1)

if __name__ == '__main__':
    main()