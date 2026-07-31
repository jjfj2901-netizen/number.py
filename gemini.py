import sqlite3
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from google import genai
from groq import Groq
from mistralai import Mistral

# ==================== 1. الإعدادات والمفاتيح الأساسية ====================
BOT_TOKEN = '8684675007:AAG7mECbWB3KGcarZGBrTmX7B_HyjXquKNM'

GROQ_API_KEY = "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"
MISTRAL_API_KEY = "5loUqah6ZXD5hSTbYfJEeqBi49qBRDmy"
GEMINI_API_KEY = "AIzaSyD4e3dZQBBG1P1cgnVTqDDmPzinameWuHk"

# تهيئة العملاء (Clients) للمكتبات الرسمية لأحدث الإصدارات
groq_client = Groq(api_key=GROQ_API_KEY)
mistral_client = Mistral(api_key=MISTRAL_API_KEY)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ==================== 2. نظام الذاكرة اللانهائية (SQLite) ====================
conn = sqlite3.connect('ai_bot_memory.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS memory (
    user_id INTEGER,
    role TEXT,
    content TEXT
)
''')
conn.commit()

def save_memory(user_id, role, content):
    cursor.execute("INSERT INTO memory (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()

def get_memory_context(user_id):
    cursor.execute("SELECT role, content FROM memory WHERE user_id = ? ORDER BY ROWID DESC LIMIT 20", (user_id,))
    rows = cursor.fetchall()
    context = ""
    for role, content in reversed(rows):
        context += f"{role}: {content}\n"
    return context

# ==================== 3. فريق الذكاء الاصطناعي (AI Agents) ====================

def planner_agent(prompt, history):
    """DeepSeek-R1: التخطيط وتقسيم المشروع الهيكلي"""
    system_prompt = "أنت مهندس معمارية برمجيات عبقري. حلل طلب المستخدم وقسمه لخطة عمل وهيكل ملفات متكامل ودقيق جداً."
    full_prompt = f"سجل المحادثات السابق:\n{history}\n\nالطلب الجديد: {prompt}"
    
    response = groq_client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ]
    )
    return response.choices[0].message.content

def coder_agent(plan, project_type):
    """Qwen 2.5 Coder: كتابة الأكواد البرمجية التفصيلية والضخمة"""
    lines_instruction = "اكتب كوداً ضخماً، متكاملاً، وتفصيلياً جداً بدون أي اختصارات أو تعليقات مثل (اكمل هنا). يجب أن يكون الكود شغالاً واحترافياً ومن 500 إلى 3000 سطر حسب حجم المطلوب."
    system_prompt = f"أنت مبرمج محترف. وظيفتك تحويل خطة المهندس إلى أكواد برمجية كاملة ونظيفة. {lines_instruction}"
    
    response = groq_client.chat.completions.create(
        model="qwen-2.5-coder-32b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"نوع المشروع: {project_type}\n\nالخطة:\n{plan}"}
        ]
    )
    return response.choices[0].message.content

def inspector_agent(code):
    """Gemini 3.6 Flash: فحص الكود وتصحيح الأخطاء"""
    prompt = f"قم بفحص الكود البرمجي التالي بعناية فائقة، وتأكد من خلوه من الأخطاء المنطقية أو النحوية، وأصلحه إن وجد، واخرج الكود النهائي الصافي فقط:\n\n{code}"
    response = gemini_client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt
    )
    return response.text

def doc_agent(code):
    """Mistral: كتابة دليل الاستخدام عبر المكتبة الرسمية الحديثة"""
    try:
        response = mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=[{
                "role": "user", 
                "content": f"اكتب شرحاً احترافياً ودليل تشغيل مبسط باللغة العربية لهذا الكود المبرمج:\n\n{code[:2000]}"
            }]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"تم تجهيز الكود بنجاح (ملاحظة التوثيق: {str(e)})"

# ==================== 4. دوال التحكم والرسائل في البوت ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك يا بطل! 🚀\n"
        "أنا مدير فريق الذكاء الاصطناعي البرمجي (DeepSeek + Qwen + Gemini + Mistral).\n"
        "اطلب أي مشروع أو أداة، وحدد لو كان (مشروع ضخم) عشان ننفذه بأعلى احترافية وأسطر كاملة!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    if not user_text:
        return

    # جلب الذاكرة القديمة وحفظ الطلب الجديد
    history = get_memory_context(user_id)
    save_memory(user_id, "User", user_text)
    
    status_msg = await update.message.reply_text("🔄 جارٍ إيقاظ فريق الذكاء الاصطناعي للعمل على طلبك...")
    
    try:
        # 1. التخطيط (DeepSeek)
        await status_msg.edit_text("🧠 [1/4] DeepSeek-R1 يحلل الفكرة ويضع الهيكل والتخطيط...")
        plan = planner_agent(user_text, history)
        
        # تحديد حجم المشروع بناءً على كلام المستخدم
        is_huge = "ضخم" in user_text or "كبير" in user_text or "3000" in user_text or "500" in user_text
        project_type = "مشروع ضخم (500 - 3000 سطر)" if is_huge else "مشروع قياسي"
        
        # 2. البرمجة والكتابة (Qwen Coder)
        await status_msg.edit_text(f"💻 [2/4] Qwen 2.5 Coder يكتب الكود البرمجي بالتفصيل ({project_type})...")
        raw_code = coder_agent(plan, project_type)
        
        # 3. الفحص والمراجعة (Gemini 3.6 Flash)
        await status_msg.edit_text("🔍 [3/4] Gemini 3.6 Flash يفحص الكود ويصلح أي ثغرات أو أخطاء...")
        final_code = inspector_agent(raw_code)
        
        # 4. التوثيق (Mistral - SDK الرسمي)
        await status_msg.edit_text("📝 [4/4] Mistral يجهز دليل التثبيت والتشغيل...")
        docs = doc_agent(final_code)
        
        # حفظ الإجابة في الذاكرة اللانهائية
        save_memory(user_id, "Assistant", f"تم إنجاز المشروع بنجاح بناءً على الطلب: {user_text}")
        
        # إنشاء ملف الكود وإرساله للمستخدم
        file_name = f"generated_project_{user_id}.py"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(final_code)
            
        await status_msg.delete()
        
        # إرسال النتيجة والملف
        await update.message.reply_text(f"✅ **تم إنجاز المشروع بنجاح!**\n\n📌 **الدليل والشرح:**\n{docs[:3000]}")
        with open(file_name, "rb") as f:
            await update.message.reply_document(document=f, caption="📂 ملف المشروع النهائي الشغال.")
        
        # تنظيف الملف من الجهاز بعد الإرسال
        if os.path.exists(file_name):
            os.remove(file_name)
            
    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء المعالجة: {str(e)}")

# ==================== 5. تشغيل التطبيق ====================
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🤖 بوت تيليجرام يعمل الآن بأحدث مكتبة لـ Mistral...")
    app.run_polling()
