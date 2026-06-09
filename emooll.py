import random
import asyncio
import os
import sys
import smtplib
import time
from email.mime.text import MIMEText
from telethon import TelegramClient, events, Button
print("البوت اشتغل يا عبده، أنا شايفك!")

# --- [ الإعدادات الملكية ] ---
API_ID = 33898633
API_HASH = 'c7d017aaab551f55ae2653ba05bcfa23'
MAIN_BOT_TOKEN = '8848015325:AAGZalWRJ0IwEOTR28dYceZaeXGpHwSFDJ8'
ADMIN_BOT_TOKEN = '8695659334:AAEzpSnuPTpXmuN7J5MHMP7e7-j6zTEgEZ4'
OWNER_ID = 8334340779 

# تنظيف الجلسات القديمة لضمان ربط جديد نظيف
for file in os.listdir():
    if file.endswith(".session"):
        try:
            os.remove(file)
        except:
            pass

main_bot = TelegramClient('MAIN_V135', API_ID, API_HASH)
admin_bot = TelegramClient('ADMIN_V135', API_ID, API_HASH)

# تتبع حالات المستخدمين لمنع تداخل العمليات
user_states = {}

# --- [ محرك البيانات اللحظي ] ---
def get_db(name):
    f = f"{name}.txt"
    if not os.path.exists(f): 
        return set()
    with open(f, "r") as file:
        content = file.read().strip()
        if content:
            return set(content.split(","))
        else:
            return set()

def save_db(name, data):
    with open(f"{name}.txt", "w") as file: 
        file.write(",".join(list(data)))

# --- [ وظيفة الإرسال الحقيقي مع إرسال Report Send للبوت ] ---
async def start_real_attack(event, gmail, pwd, target, subj, body, count, chat_id):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail, pwd)
        
        for i in range(1, count + 1):
            # التحقق إذا قام المستخدم بإلغاء العملية أو بدء وحدة جديدة
            if user_states.get(chat_id) != "attacking":
                break
                
            msg = MIMEText(body)
            msg['Subject'] = subj
            msg['From'] = gmail
            msg['To'] = target
            
            server.sendmail(gmail, target, msg.as_string())
            
            # إرسال "Report Send" في البوت نفسه لكل بلاغ
            await event.respond(f"✅ {i} : Report Send")
            
            # طباعة في الشاشة السوداء للتأكيد التقني
            print(f"[{i}] Report Send")
            await asyncio.sleep(random.uniform(1.0, 3.0)) 
            
        server.quit()
        return True
    except Exception as e:
        await event.respond(f"❌ فشل الإرسال: {e}")
        return False

# --- [ 1. محرك بوت التدمير (للمستخدمين) ] ---
@main_bot.on(events.CallbackQuery)
async def main_callbacks(event):
    data = event.data
    chat_id = event.chat_id
    
    # خيار البلاغات المتسلسل
    if data == b"atk":
        user_states[chat_id] = "attacking"
        
        async with main_bot.conversation(chat_id, exclusive=False) as conv:
            await event.answer("⚡ بدء الهجوم...", alert=False)
            
            await conv.send_message("📧 ارسل الجيميل الخاص بك (المرسل):")
            res1 = await conv.get_response()
            if res1.text == "/start":
                user_states[chat_id] = "idle"
                raise events.StopPropagation
            gmail = res1.text
            
            await conv.send_message("🔑 ارسل 'كلمة مرور التطبيق' (App Password):")
            res2 = await conv.get_response()
            if res2.text == "/start":
                user_states[chat_id] = "idle"
                raise events.StopPropagation
            pwd = res2.text
            
            await conv.send_message("🏢 ارسل بريد الشركة المستهدف:")
            res3 = await conv.get_response()
            if res3.text == "/start":
                user_states[chat_id] = "idle"
                raise events.StopPropagation
            target = res3.text
            
            await conv.send_message("📝 ارسل موضوع البلاغ:")
            res4 = await conv.get_response()
            if res4.text == "/start":
                user_states[chat_id] = "idle"
                raise events.StopPropagation
            subj = res4.text
            
            await conv.send_message("📋 ارسل كليشة البلاغ:")
            res5 = await conv.get_response()
            if res5.text == "/start":
                user_states[chat_id] = "idle"
                raise events.StopPropagation
            body = res5.text
            
            await conv.send_message("🔢 الحد الأقصى 1000 بلاغ، لكن ينصح بـ (40) لضمان القبول:\nارسل العدد الآن:")
            res6 = await conv.get_response()
            if res6.text == "/start":
                user_states[chat_id] = "idle"
                raise events.StopPropagation
            num = int(res6.text)
            
            if user_states.get(chat_id) == "attacking":
                await conv.send_message("🚀 **بدء المراسلة الحقيقية.. تابع التقدم:**")
                await start_real_attack(event, gmail, pwd, target, subj, body, num, chat_id)
                await conv.send_message("🏁 **اكتملت المهمة بنجاح!**")
                user_states[chat_id] = "idle"

    # خيار تشكيلات الإبادة
    elif data == b"cb":
        user_states[chat_id] = "idle"
        await event.delete() # مسح القائمة الرئيسية لتفادي التراكم
        txt = "🔥 **تشكيلات الإبادة (أهداف الإغلاق):**\n\n"
        txt += "📌 **إغلاق المجموعات:** استخدم `abuse@telegram.org` مع كليشة 'Violating Terms'.\n"
        txt += "📌 **إغلاق القنوات:** استخدم `dmca@telegram.org` للبلاغات المتعلقة بحقوق الملكية.\n"
        txt += "📌 **تعطيل الحسابات:** استخدم `support@telegram.org` لوصف الحساب كـ 'Scammer'.\n"
        txt += "📌 **إبادة المحتوى الإباحي:** استخدم `stopCA@telegram.org` للبلاغات الحساسة."
        
        btns = [[Button.inline("❌ خروج", b"exit_panel")]]
        await event.respond(txt, buttons=btns)

    # خيار إيميلات دعم تليجرام الشاملة
    elif data == b"emails":
        user_states[chat_id] = "idle"
        await event.delete() # مسح القائمة الرئيسية لتفادي التراكم
        txt = "📧 **قائمة إيميلات دعم تليجرام واستخداماتها:**\n\n"
        txt += "1️⃣ `abuse@telegram.org`\n💡 *الفائدة:* البلاغات العامة، السب، والمجموعات المخالفة.\n\n"
        txt += "2️⃣ `support@telegram.org`\n💡 *الفائدة:* استرجاع حسابات، الإبلاغ عن اختراق، أو مشاكل تقنية.\n\n"
        txt += "3️⃣ `dmca@telegram.org`\n💡 *الفائدة:* إغلاق القنوات التي تسرق محتوى أو تنتهك الحقوق.\n\n"
        txt += "4️⃣ `security@telegram.org`\n💡 *الفائدة:* بلاغات الثغرات الأمنية والتهديدات الخطيرة.\n\n"
        txt += "5️⃣ `sms@telegram.org`\n💡 *الفائدة:* مخصص لمشاكل عدم وصول أكواد التحقق.\n\n"
        txt += "6️⃣ `sticker@telegram.org`\n💡 *الفائدة:* الإبلاغ عن حزم الملصقات المسيئة."
        
        btns = [[Button.inline("❌ خروج", b"exit_panel")]]
        await event.respond(txt, buttons=btns)

    elif data == b"h1":
        user_states[chat_id] = "idle"
        await event.delete() # مسح القائمة الرئيسية لتفادي التراكم
        h = "🔑 **كيفية الحصول على كلمة مرور التطبيق (لجيميل):**\n\n"
        h += "1- افتح حساب جوجل > الأمان.\n"
        h += "2- تأكد من تفعيل 'التحقق بخطوتين'.\n"
        h += "3- ابحث عن خانة 'كلمات مرور التطبيقات'.\n"
        h += "4- اختر 'بريد' ثم نوع الجهاز، سيظهر لك كود من 16 حرف؛ هو المفتاح المطلوب هنا."
        
        btns = [[Button.inline("❌ خروج", b"exit_panel")]]
        await event.respond(h, buttons=btns)

    # عند الضغط على خروج: يمسح الرد الحالي ويرجع القائمة الأصلية مكانها نظيفة
    elif data == b"exit_panel":
        user_states[chat_id] = "idle"
        await event.delete()
        btns = [
            [Button.inline("📢 شن هجوم حقيقي", b"atk")], 
            [Button.inline("🔥 تشكيلات الإبادة", b"cb")],
            [Button.inline("🔑 شرح كلمات المرور", b"h1")],
            [Button.inline("📧 إيميلات الدعم", b"emails")]
        ]
        await main_bot.send_message(
            chat_id, 
            "🚀 **منصة التدمير V71**\n⚙️ اختر نوع العملية للهجوم.", 
            buttons=btns
        )

# --- [ 2. محرك الصلاحيات وبوت الإدارة ] ---
@main_bot.on(events.NewMessage)
async def auth_handler(event):
    chat_id = event.chat_id
    if event.sender_id == OWNER_ID: 
        return
    if event.text == "/start":
        user_states[chat_id] = "idle"
        
        uid = str(event.sender_id)
        u = (event.sender.username or "").lower()
        
        banned = get_db("banned")
        auth = get_db("auth")
        is_public = os.path.exists("all_access.txt")

        if u in banned or uid in banned:
            return await event.respond("⚠️ تم حظرك من قبل الإمبراطور.")

        if not (is_public or u in auth or uid in auth):
            return await event.respond("⚠️ **البوت خاص! اطلب التفعيل من الإمبراطور.**")

        btns = [
            [Button.inline("📢 شن هجوم حقيقي", b"atk")], 
            [Button.inline("🔥 تشكيلات الإبادة", b"cb")],
            [Button.inline("🔑 شرح كلمات المرور", b"h1")],
            [Button.inline("📧 إيميلات الدعم", b"emails")]
        ]
        await event.reply("🚀 **منصة التدمير V71**\n⚙️ اختر نوع العملية للهجوم.", buttons=btns)

@admin_bot.on(events.NewMessage(from_users=OWNER_ID))
async def admin_panel(event):
    if event.text == "/start":
        btns = [
            [Button.inline("🔓 فتح للكل", b"on"), Button.inline("🔒 قفل للكل", b"off")],
            [Button.inline("👤 إضافة يوزر", b"add"), Button.inline("🚫 حظر يوزر", b"ban")]
        ]
        await event.respond("🎮 **لوحة التحكم الإمبراطورية V135**", buttons=btns)

@admin_bot.on(events.CallbackQuery)
async def admin_logic(event):
    if event.data == b"on":
        open("all_access.txt", "w").close()
        await event.edit("✅ تم الفتح للكل! (البوت متاح الآن للجميع)")
        
    elif event.data == b"off":
        if os.path.exists("all_access.txt"): 
            os.remove("all_access.txt")
        await event.edit("🔒 تم القفل! (البوت خاص الآن)")
        
    elif event.data in [b"add", b"ban"]:
        if event.data == b"add":
            mode = "إضافة"
        else:
            mode = "حظر"
        
        async with admin_bot.conversation(OWNER_ID) as conv:
            await conv.send_message(f"👤 ارسل يوزر الشخص (بدون @) لـ {mode}ه:")
            user_input = (await conv.get_response()).text.lower()
            
            auth = get_db("auth")
            banned = get_db("banned")
            
            if event.data == b"add":
                auth.add(user_input)
                banned.discard(user_input)
            else:
                banned.add(user_input)
                auth.discard(user_input)
                
            save_db("auth", auth)
            save_db("banned", banned)
            await conv.send_message(f"✅ تم {mode} المستخدم بنجاح.")

# --- [ تشغيل ] ---
async def start_all():
    print("⚡ جاري تشغيل النسخة المدمجة V135...")
    await main_bot.start(bot_token=MAIN_BOT_TOKEN)
    await admin_bot.start(bot_token=ADMIN_BOT_TOKEN)
    print("✅ النظام نشط! إيميلات الدعم وتشكيلات الإبادة جاهزة.")
    await asyncio.gather(
        main_bot.run_until_disconnected(), 
        admin_bot.run_until_disconnected()
    )

if __name__ == '__main__':
    try: 
        asyncio.run(start_all())
    except: 
        os.execl(sys.executable, sys.executable, *sys.argv)
