import telebot
from telebot import types
import requests
import re
import random

# --- [ إعدادات البوت ] ---
API_TOKEN = '8607469728:AAHcfCIOrLeCyVxu_a5MO8yW-m6YkPyrgmQ'
bot = telebot.TeleBot(API_TOKEN)

# قاموس لتحديد الدول بناءً على مفتاح الرقم
COUNTRY_MAP = {
    '1': 'USA/Canada 🇺🇸🇨🇦',
    '44': 'United Kingdom 🇬🇧',
    '48': 'Poland 🇵🇱',
    '33': 'France 🇫🇷',
    '49': 'Germany 🇩🇪',
    '31': 'Netherlands 🇳🇱',
    '46': 'Sweden 🇸🇪',
    '372': 'Estonia 🇪🇪',
    '351': 'Portugal 🇵🇹',
    '34': 'Spain 🇪🇸',
    '7': 'Russia/Kazakhstan 🇷🇺🇰🇿',
    '380': 'Ukraine 🇺🇦',
    '91': 'India 🇮🇳'
}

def get_country_name(number):
    for code in sorted(COUNTRY_MAP.keys(), key=len, reverse=True):
        if number.startswith(code):
            return COUNTRY_MAP[code]
    return "Unknown Country 🌍"

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    services = [
        ("✈️ Telegram", "tele"), ("💬 WhatsApp", "whatsapp"),
        ("🎮 Roblox (All Countries 🌍)", "roblox"), ("📸 Instagram", "insta"),
        ("🎵 TikTok", "tiktok"), ("📘 Facebook", "fb")
    ]
    for name, data in services:
        markup.add(types.InlineKeyboardButton(name, callback_data=data))
    return markup

def get_numbers_universal():
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        # بنسحب من المصدر الأسرع حالياً
        url = "https://temp-number.com/countries"
        response = requests.get(url, headers=headers, timeout=10)
        found = re.findall(r'\+\d{10,15}', response.text)
        for f in found:
            results.append(f.replace('+', ''))
    except: pass
    
    if not results: # مصدر احتياطي
        try:
            url_alt = "https://anonymsms.com/"
            res_alt = requests.get(url_alt, headers=headers, timeout=10)
            found_alt = re.findall(r'\d{10,15}', res_alt.text)
            results.extend(found_alt)
        except: pass
    
    return list(set(results))

def fetch_otp_universal(number):
    headers = {'User-Agent': 'Mozilla/5.0'}
    sources = [f"https://temp-number.com/number-{number}", f"https://anonymsms.com/number/{number}/"]
    for url in sources:
        try:
            response = requests.get(url, headers=headers, timeout=7)
            if "code" in response.text.lower() or "verification" in response.text.lower():
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                msgs = soup.find_all('td')
                for m in msgs:
                    content = m.text.strip()
                    if len(content) > 3: return True, content, url
        except: continue
    return False, "⏳ مفيش أكواد وصلت لسه.. جرب كمان 30 ثانية.", None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "أهلاً يا إمبراطور 👑\nتم تحديث نظام كشف الدول ✅\nاختر المنصة:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "main_menu":
        bot.edit_message_text("اختر المنصة اللي محتاج رقمها:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
        return

    if call.data.startswith("otp_"):
        number = call.data.replace("otp_", "")
        bot.answer_callback_query(call.id, "جاري فحص الكود... 🔍")
        success, message_text, link = fetch_otp_universal(number)
        if success:
            bot.send_message(call.message.chat.id, f"📩 **الكود:**\n`{message_text}`\n\n🔗 الرابط: {link}")
        else:
            bot.send_message(call.message.chat.id, message_text)

    else:
        platform = call.data.replace("change_", "")
        bot.answer_callback_query(call.id, "🚀 جاري صيد رقم جديد...")
        nums = get_numbers_universal()
        
        if not nums:
            bot.send_message(call.message.chat.id, "⚠️ المصدر معلق، جرب تاني.")
            return

        n = random.choice(nums)
        country_name = get_country_name(n) # هنا بنعرف الدولة
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📥 Get OTP (جلب الكود)", callback_data=f"otp_{n}"))
        markup.add(types.InlineKeyboardButton("🔄 تغيير الرقم", callback_data=f"change_{platform}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="main_menu"))
        
        bot.edit_message_text(f"✨ **رقم جديد لـ {platform.upper()}:**\n\n✅ الرقم: `+{n}`\n🌍 الدولة: **{country_name}**", 
                              call.message.chat.id, call.message.message_id, 
                              reply_markup=markup, parse_mode='Markdown')

print("🚀 بوت الإمبراطور (كاشف الدول) جاهز...")
bot.infinity_polling()
