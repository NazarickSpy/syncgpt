import os
import logging
import json
import asyncio
import sqlite3
import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from datetime import datetime

# Konfigurasi
BOT_TOKEN = "8545370979:AAFH2E9VNtksMsXnBfHvEsLfgX-MKXLX6Vc"
LOGO_URL = "https://g.top4top.io/p_35568o9i71.png"
ADMIN_ID = "6208011594"

# API Keys
GEMINI_API_KEY = "AIzaSyA4BnoJUxOopad0gnJDyFKBRcT6yrZlxPg"
OPENROUTER_API_KEY = "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"

# File konfigurasi
USER_CONFIG_FILE = "user_configs.json"
DB_FILE = "bot_statistics.db"
PROMPT_FILE = "prompt.txt"

# Rate limiting
last_request_time = 0
REQUEST_DELAY = 2

# 25+ MODEL AI
AVAILABLE_MODELS = {
    # OpenAI Models
    "gpt-4o": {
        "name": "🤖 GPT-4o",
        "id": "gpt-4o",
        "provider": "OpenAI",
        "description": "Model terbaru OpenAI - Multimodal",
        "type": "openrouter"
    },
    "gpt-4-turbo": {
        "name": "🚀 GPT-4 Turbo", 
        "id": "gpt-4-turbo",
        "provider": "OpenAI",
        "description": "GPT-4 Turbo - Cepat dan powerful",
        "type": "openrouter"
    },
    "gpt-3.5-turbo": {
        "name": "⚡ GPT-3.5 Turbo",
        "id": "gpt-3.5-turbo",
        "provider": "OpenAI", 
        "description": "GPT-3.5 Turbo - Ringan dan cepat",
        "type": "openrouter"
    },
    
    # Google Gemini Models
    "gemini-2.0-flash": {
        "name": "🌀 Gemini 2.0 Flash",
        "id": "gemini-2.0-flash-exp",
        "provider": "Google",
        "description": "Gemini 2.0 Flash - Terbaru Google",
        "type": "gemini"
    },
    "gemini-1.5-flash": {
        "name": "⚡ Gemini 1.5 Flash",
        "id": "gemini-1.5-flash", 
        "provider": "Google",
        "description": "Gemini 1.5 Flash - Stabil & efisien",
        "type": "gemini"
    },
    "gemini-1.5-pro": {
        "name": "🎯 Gemini 1.5 Pro",
        "id": "gemini-1.5-pro",
        "provider": "Google",
        "description": "Gemini 1.5 Pro - Kualitas tinggi",
        "type": "gemini"
    },
    
    # Anthropic Claude Models
    "claude-3-5-sonnet": {
        "name": "🎨 Claude 3.5 Sonnet", 
        "id": "anthropic/claude-3-5-sonnet",
        "provider": "Anthropic",
        "description": "Claude 3.5 Sonnet - Kreatif & analitis",
        "type": "openrouter"
    },
    "claude-3-opus": {
        "name": "🏆 Claude 3 Opus",
        "id": "anthropic/claude-3-opus",
        "provider": "Anthropic",
        "description": "Claude 3 Opus - Paling canggih",
        "type": "openrouter"
    },
    "claude-3-sonnet": {
        "name": "💼 Claude 3 Sonnet",
        "id": "anthropic/claude-3-sonnet",
        "provider": "Anthropic",
        "description": "Claude 3 Sonnet - Seimbang & efisien",
        "type": "openrouter"
    },
    "claude-3-haiku": {
        "name": "🌪️ Claude 3 Haiku",
        "id": "anthropic/claude-3-haiku", 
        "provider": "Anthropic",
        "description": "Claude 3 Haiku - Super cepat",
        "type": "openrouter"
    },
    
    # xAI Grok Models
    "grok-beta": {
        "name": "🤣 Grok Beta",
        "id": "x-ai/grok-beta",
        "provider": "xAI",
        "description": "Grok Beta - Humoris & informatif",
        "type": "openrouter"
    },
    
    # Meta Llama Models  
    "llama-3-70b": {
        "name": "🦙 Llama 3 70B",
        "id": "meta-llama/llama-3-70b-instruct",
        "provider": "Meta",
        "description": "Llama 3 70B - Open source terbaik",
        "type": "openrouter"
    },
    "llama-3-8b": {
        "name": "🐑 Llama 3 8B",
        "id": "meta-llama/llama-3-8b-instruct", 
        "provider": "Meta",
        "description": "Llama 3 8B - Ringan & cepat",
        "type": "openrouter"
    },
    
    # Mistral Models
    "mistral-large": {
        "name": "🌬️ Mistral Large",
        "id": "mistralai/mistral-large",
        "provider": "Mistral", 
        "description": "Mistral Large - Multibahasa canggih",
        "type": "openrouter"
    },
    "mistral-7b": {
        "name": "💨 Mistral 7B",
        "id": "mistralai/mistral-7b-instruct",
        "provider": "Mistral",
        "description": "Mistral 7B - Efisien & cepat",
        "type": "openrouter"
    },
    
    # DeepSeek Models
    "deepseek-chat": {
        "name": "🔍 DeepSeek Chat",
        "id": "deepseek/deepseek-chat",
        "provider": "DeepSeek", 
        "description": "DeepSeek Chat - Cerdas & gratis",
        "type": "openrouter"
    },
    "deepseek-coder": {
        "name": "💻 DeepSeek Coder",
        "id": "deepseek/deepseek-coder",
        "provider": "DeepSeek",
        "description": "DeepSeek Coder - Spesialis coding",
        "type": "openrouter"
    },
    
    # Microsoft Models
    "wizardlm-2": {
        "name": "🧙‍♂️ WizardLM 2",
        "id": "microsoft/wizardlm-2-8x22b", 
        "provider": "Microsoft",
        "description": "WizardLM 2 - Complex instructions",
        "type": "openrouter"
    },
    
    # Code Specialist Models
    "codestral": {
        "name": "👨‍💻 Codestral",
        "id": "mistralai/codestral-latest",
        "provider": "Mistral",
        "description": "Codestral - Spesialis coding",
        "type": "openrouter"
    },
    "code-llama": {
        "name": "🐪 Code Llama",
        "id": "meta-llama/codellama-70b-instruct",
        "provider": "Meta",
        "description": "Code Llama - Spesialis programming",
        "type": "openrouter"
    },
    
    # Creative Models
    "midjourney-prompt": {
        "name": "🎨 Midjourney Helper",
        "id": "gpt-4o",
        "provider": "OpenAI",
        "description": "Bantu buat prompt Midjourney & AI art",
        "type": "openrouter"
    }
}

# Text multilingual - DIPERBAIKI: Format markdown yang benar
TEXTS = {
    "id": {
        "welcome": "👋 *Halo {name}!*\n\n🤖 *Selamat datang di Multi-AI Assistant*\n\n🚀 *Infrastruktur AI Canggih*\n\n📊 *{total_models}+ Model AI Terintegrasi:*\n• 🤖 OpenAI: GPT-4o, GPT-4 Turbo\n• 🌀 Google: Gemini 2.0, Gemini 1.5 Pro\n• 🎨 Anthropic: Claude 3.5 Sonnet\n• 🤣 xAI: Grok Beta\n• 🦙 Meta: Llama 3 70B\n• 🌬️ Mistral: Large, Medium\n• 🔍 DeepSeek: Coder, Researcher\n• 👨‍💻 Spesialis Pemrograman\n\n🔧 *Pilih bahasa yang diinginkan:*",        
        "main_menu": "🤖 *Multi-AI Assistant*\n\n⚙️ *Konfigurasi Saat Ini:*\n🔄 *Model Aktif:* {model}\n🌐 *Bahasa Interface:* {language}\n📊 *Model Tersedia:* {total_models}\n\n🛠️ *Layanan yang Didukung:*\n• 📝 Pembuatan Konten & Dokumentasi\n• 💻 Pengembangan Software & Pemrograman\n• 📊 Analisis Data & Business Intelligence\n• 🎨 Desain Kreatif & Konten Digital\n• 🔧 Solusi Teknis & Infrastruktur IT\n• 📚 Konten Edukasi & Tutorial\n• 🎨 Prompt Generasi Seni AI\n• 🤖 Otomasi Proses & Scripting\n\n📋 *Pilih opsi:*",        
        "ai_chat": "🤖 *{model} - Sesi Aktif*\n\n💬 *Siap menerima permintaan*\n\n📝 *Jenis Permintaan yang Didukung:*\n• Pengembangan teknis & generasi kode\n• Analisis data & business intelligence\n• Strategi konten & pengembangan kreatif\n• Infrastruktur & solusi teknis\n• Penjelasan edukasi & tutorial\n• Optimasi proses & otomasi\n\n🎯 *Contoh Implementasi:*\n• \"Buat script Python web scraping dengan rotasi proxy dan error handling\"\n• \"Analisis dataset penjualan dan berikan insight kinerja kuartalan\"\n• \"Buat arsitektur sistem untuk platform e-commerce yang scalable\"\n• \"Generate prompt Midjourney untuk landscape urban cyberpunk\"\n• \"Optimalkan query database dan implementasikan strategi caching\"\n• \"Desain struktur REST API untuk backend aplikasi mobile\"\n\n✍️ *Masukkan permintaan teknis Anda...*"
    },
    "en": {
        "welcome": "👋 *Hello {name}!*\n\n🤖 *Welcome to Multi-AI Assistant*\n\n🚀 *Advanced AI Infrastructure*\n\n📊 *{total_models}+ AI Models Integrated:*\n• 🤖 OpenAI: GPT-4o, GPT-4 Turbo\n• 🌀 Google: Gemini 2.0, Gemini 1.5 Pro\n• 🎨 Anthropic: Claude 3.5 Sonnet\n• 🤣 xAI: Grok Beta\n• 🦙 Meta: Llama 3 70B\n• 🌬️ Mistral: Large, Medium\n• 🔍 DeepSeek: Coder, Researcher\n• 👨‍💻 Coding Specialists\n\n🔧 *Select your preferred language:*",
        "main_menu": "🤖 *Multi-AI Assistant*\n\n⚙️ *Current Configuration:*\n🔄 *Active Model:* {model}\n🌐 *Interface Language:* {language}\n📊 *Available Models:* {total_models}\n\n🛠️ *Supported Services:*\n• 📝 Content Creation & Documentation\n• 💻 Software Development & Programming\n• 📊 Data Analysis & Business Intelligence\n• 🎨 Creative Design & Digital Content\n• 🔧 Technical Solutions & IT Infrastructure\n• 📚 Educational Content & Tutorials\n• 🎨 AI Art Generation Prompts\n• 🤖 Process Automation & Scripting\n\n📋 *Select an option:*",        
        "ai_chat": "🤖 *{model} - Session Active*\n\n💬 *Ready for your request*\n\n📝 *Supported Request Types:*\n• Technical development & code generation\n• Data analysis & business intelligence\n• Content strategy & creative development\n• Infrastructure & technical solutions\n• Educational explanations & tutorials\n• Process optimization & automation\n\n🎯 *Example Implementations:*\n• \"Develop a Python web scraping script with proxy rotation and error handling\"\n• \"Analyze sales dataset and provide quarterly performance insights\"\n• \"Create system architecture for scalable e-commerce platform\"\n• \"Generate Midjourney prompts for cyberpunk urban landscape\"\n• \"Optimize database queries and implement caching strategy\"\n• \"Design REST API structure for mobile application backend\"\n\n✍️ *Enter your technical request...*"
    }
}

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_system_prompt():
    """Baca system prompt dari file prompt.txt"""
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return content
            else:
                return "You are a helpful AI assistant."
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return "You are a helpful AI assistant."

def init_database():
    """Initialize database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_stats (
            id INTEGER PRIMARY KEY,
            total_users INTEGER DEFAULT 0,
            total_messages INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            message_count INTEGER DEFAULT 0,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            language TEXT DEFAULT 'id'
        )
    ''')
    
    cursor.execute('INSERT OR IGNORE INTO bot_stats (id, total_users, total_messages) VALUES (1, 0, 0)')
    conn.commit()
    conn.close()

def update_user_stats(user_id, username, first_name):
    """Update statistik pengguna"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO user_activity 
        (user_id, username, first_name, message_count, last_active)
        VALUES (?, ?, ?, COALESCE((SELECT message_count FROM user_activity WHERE user_id = ?), 0) + 1, CURRENT_TIMESTAMP)
    ''', (user_id, username, first_name, user_id))
    
    cursor.execute('UPDATE bot_stats SET total_messages = total_messages + 1 WHERE id = 1')
    
    cursor.execute('SELECT COUNT(*) FROM user_activity')
    total_users = cursor.fetchone()[0]
    cursor.execute('UPDATE bot_stats SET total_users = ? WHERE id = 1', (total_users,))
    
    conn.commit()
    conn.close()

def load_user_config(user_id):
    """Load konfigurasi user"""
    if os.path.exists(USER_CONFIG_FILE):
        try:
            with open(USER_CONFIG_FILE, "r") as f:
                configs = json.load(f)
                user_config = configs.get(str(user_id), {"model": "gpt-4o", "language": "id"})
                return user_config
        except:
            return {"model": "gpt-4o", "language": "id"}
    return {"model": "gpt-4o", "language": "id"}

def save_user_config(user_id, config):
    """Simpan konfigurasi user"""
    if os.path.exists(USER_CONFIG_FILE):
        try:
            with open(USER_CONFIG_FILE, "r") as f:
                configs = json.load(f)
        except:
            configs = {}
    else:
        configs = {}
    
    configs[str(user_id)] = config
    with open(USER_CONFIG_FILE, "w") as f:
        json.dump(configs, f, indent=2)

def get_text(user_id, key, **kwargs):
    """Dapatkan text berdasarkan bahasa user"""
    user_config = load_user_config(user_id)
    language = user_config.get("language", "id")
    text = TEXTS[language].get(key, key)
    
    if 'total_models' not in kwargs:
        kwargs['total_models'] = len(AVAILABLE_MODELS)
        
    return text.format(**kwargs) if kwargs else text

def clean_markdown(text):
    """Bersihkan text dari karakter markdown"""
    if not text:
        return text
    
    clean_text = text
    replacements = {
        '**': '', 
        '__': '', 
        '`': '',
        '```': '',
        '[': '(',
        ']': ')',
        '_': ' '
    }
    
    for old, new in replacements.items():
        clean_text = clean_text.replace(old, new)
    
    return clean_text

async def call_openrouter_api(prompt, model_id):
    """Panggil Open Router API - DIPERBAIKI"""
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        system_prompt = get_system_prompt()
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://telegram.org",
            "X-Title": "Telegram AI Bot"
        }
        
        data = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "❌ No response from AI model"
        else:
            error_detail = response.text
            print(f"OpenRouter API Error {response.status_code}: {error_detail}")
            return f"❌ API Error {response.status_code}: {error_detail}"
        
    except Exception as e:
        print(f"OpenRouter API Exception: {str(e)}")
        return f"❌ Error: {str(e)}"

async def call_api(prompt, model_id, model_type):
    """Panggil API berdasarkan tipe model"""
    global last_request_time
    
    current_time = time.time()
    time_since_last = current_time - last_request_time
    if time_since_last < REQUEST_DELAY:
        await asyncio.sleep(REQUEST_DELAY - time_since_last)
    
    last_request_time = time.time()
    
    if model_type == "gemini":
        return await call_gemini_api(prompt, model_id)
    else:
        return await call_openrouter_api(prompt, model_id)

async def send_long_message(update, text, model_name, user_id):
    """Kirim pesan panjang sebagai file txt jika perlu"""
    try:
        clean_text = clean_markdown(text)
        clean_model_name = clean_markdown(model_name)
        
        if len(clean_text) <= 3500:
            try:
                await update.message.reply_text(
                    f"🤖 *{clean_model_name}*\n\n{clean_text}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception:
                # Fallback tanpa markdown jika masih error
                await update.message.reply_text(
                    f"🤖 {clean_model_name}\n\n{clean_text}",
                    parse_mode=None
                )
        else:
            filename = f"response_{user_id}_{int(time.time())}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"AI Model: {model_name}\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(text)
            
            await update.message.reply_document(
                document=open(filename, "rb"),
                filename=f"ai_response.txt",
                caption=f"🤖 {clean_model_name}\n📁 Response panjang"
            )
            
            os.remove(filename)
            
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text(
            f"🤖 {model_name}\n\n{clean_markdown(text)[:2000]}...",
            parse_mode=None
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "No username"
    first_name = update.effective_user.first_name
    
    update_user_stats(user_id, username, first_name)
    
    keyboard = [
        [InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data="set_lang_id")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.message.reply_photo(
            photo=LOGO_URL,
            caption=get_text(user_id, "welcome", name=first_name),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        # Fallback jika ada error markdown
        print(f"Markdown error: {e}")
        await update.message.reply_photo(
            photo=LOGO_URL,
            caption=clean_markdown(get_text(user_id, "welcome", name=first_name)),
            reply_markup=reply_markup,
            parse_mode=None
        )

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    language = query.data.replace("set_lang_", "")
    
    user_config = load_user_config(user_id)
    user_config["language"] = language
    save_user_config(user_id, user_config)
    
    await query.answer()
    await show_main_menu_from_callback(query, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await show_main_menu_common(update.message, user_id)

async def show_main_menu_from_callback(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    await show_main_menu_common(query.message, user_id)

async def show_main_menu_common(message, user_id):
    user_config = load_user_config(user_id)
    current_model = AVAILABLE_MODELS[user_config["model"]]["name"]
    language_name = "🇮🇩 Indonesia" if user_config.get("language", "id") == "id" else "🇺🇸 English"
    
    keyboard = [
        [InlineKeyboardButton("🤖 AI Chat", callback_data="ai_chat")],
        [InlineKeyboardButton("⚙️ Change Model", callback_data="change_model")],
        [InlineKeyboardButton("🌐 Change Language", callback_data="change_language")],
        [InlineKeyboardButton("📊 Model Info", callback_data="model_info")],
        [InlineKeyboardButton("👤 About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = get_text(user_id, "main_menu", 
                      model=current_model,
                      language=language_name)
    
    try:
        await message.reply_photo(
            photo=LOGO_URL,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        # Fallback jika ada error markdown
        print(f"Markdown error in main menu: {e}")
        await message.reply_photo(
            photo=LOGO_URL,
            caption=clean_markdown(caption),
            reply_markup=reply_markup,
            parse_mode=None
        )

async def change_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    keyboard = []
    
    # Group models by provider
    providers = {}
    for model_key, model_info in AVAILABLE_MODELS.items():
        provider = model_info['provider']
        if provider not in providers:
            providers[provider] = []
        providers[provider].append((model_key, model_info))
    
    for provider, models in providers.items():
        keyboard.append([InlineKeyboardButton(f"▫️ {provider}", callback_data="header")])
        for model_key, model_info in models:
            keyboard.append([InlineKeyboardButton(model_info['name'], callback_data=f"set_model_{model_key}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_caption(
            caption=f"⚙️ *Pilih Model AI*\n\n📊 *Total {len(AVAILABLE_MODELS)} Model Tersedia*\n\nPilih model AI yang ingin digunakan:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Error in change_model: {e}")
        await query.edit_message_caption(
            caption=f"⚙️ Pilih Model AI\n\n📊 Total {len(AVAILABLE_MODELS)} Model Tersedia\n\nPilih model AI yang ingin digunakan:",
            reply_markup=reply_markup,
            parse_mode=None
        )

async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    model_key = query.data.replace("set_model_", "")
    user_id = query.from_user.id
    
    if model_key not in AVAILABLE_MODELS:
        await query.answer("❌ Invalid model!")
        return
    
    user_config = load_user_config(user_id)
    user_config["model"] = model_key
    save_user_config(user_id, user_config)
    
    model_info = AVAILABLE_MODELS[model_key]
    await query.answer(f"✅ Model diubah ke {model_info['name']}")
    
    await main_menu_callback(update, context)

async def model_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    user_config = load_user_config(user_id)
    current_model = AVAILABLE_MODELS[user_config["model"]]
    
    info_text = f"🤖 *Model Saat Ini:* {current_model['name']}\n"
    info_text += f"🏢 *Provider:* {current_model['provider']}\n"
    info_text += f"📝 *Deskripsi:* {current_model['description']}\n\n"
    
    info_text += "*Semua Model Tersedia:*\n"
    for model_key, model_info in AVAILABLE_MODELS.items():
        status = "✅" if model_key == user_config["model"] else "🔹"
        info_text += f"{status} {model_info['name']} - {model_info['provider']}\n"
    
    keyboard = [
        [InlineKeyboardButton("⚙️ Change Model", callback_data="change_model")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_caption(
            caption=info_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Error in model_info: {e}")
        await query.edit_message_caption(
            caption=clean_markdown(info_text),
            reply_markup=reply_markup,
            parse_mode=None
        )

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    user_config = load_user_config(user_id)
    current_model = AVAILABLE_MODELS[user_config["model"]]
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_caption(
            caption=get_text(user_id, "ai_chat", model=current_model['name']),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Error in ai_chat: {e}")
        await query.edit_message_caption(
            caption=clean_markdown(get_text(user_id, "ai_chat", model=current_model['name'])),
            reply_markup=reply_markup,
            parse_mode=None
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pesan dari user"""
    if update.message and update.message.chat.type == 'private':
        user_id = update.effective_user.id
        username = update.effective_user.username or "No username"
        first_name = update.effective_user.first_name
        user_message = update.message.text
        
        update_user_stats(user_id, username, first_name)
        
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            user_config = load_user_config(user_id)
            model_info = AVAILABLE_MODELS[user_config["model"]]
            model_id = model_info["id"]
            model_name = model_info["name"]
            model_type = model_info["type"]
            
            response = await call_api(user_message, model_id, model_type)
            
            await send_long_message(update, response, model_name, user_id)
            
        except Exception as e:
            print(f"Error: {e}")
            await update.message.reply_text("❌ Error, coba lagi nanti.")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    about_text = "🤖 *Multi-AI Assistant*\n\n"
    about_text += f"📊 *{len(AVAILABLE_MODELS)}+ AI Models*\n"
    about_text += "🌐 *Multi-language Support*\n"
    about_text += "💬 *Chat & Task Processing*\n\n"
    about_text += "*Core Capabilities:*\n"
    about_text += "• 🤖 25+ Latest AI Architectures\n"
    about_text += "• 💻 Code Generation & Analysis\n"
    about_text += "• 📝 Content & Documentation\n"
    about_text += "• 📊 Data Processing & Insights\n"
    about_text += "• 🎨 Creative Implementation\n"
    about_text += "• 🔧 Technical Solutions\n\n"
    about_text += "🔗 *Professional AI Infrastructure*"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_caption(
            caption=about_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Error in about: {e}")
        await query.edit_message_caption(
            caption=clean_markdown(about_text),
            reply_markup=reply_markup,
            parse_mode=None
        )

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    user_config = load_user_config(user_id)
    current_model = AVAILABLE_MODELS[user_config["model"]]["name"]
    language_name = "🇮🇩 Indonesia" if user_config.get("language", "id") == "id" else "🇺🇸 English"
    
    keyboard = [
        [InlineKeyboardButton("🤖 AI Chat", callback_data="ai_chat")],
        [InlineKeyboardButton("⚙️ Change Model", callback_data="change_model")],
        [InlineKeyboardButton("🌐 Change Language", callback_data="change_language")],
        [InlineKeyboardButton("📊 Model Info", callback_data="model_info")],
        [InlineKeyboardButton("👤 About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = get_text(user_id, "main_menu", 
                      model=current_model,
                      language=language_name)
    
    try:
        await query.edit_message_caption(
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Error in main_menu_callback: {e}")
        await query.edit_message_caption(
            caption=clean_markdown(caption),
            reply_markup=reply_markup,
            parse_mode=None
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"Exception while handling an update: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi error, silakan coba lagi nanti."
            )
    except Exception as e:
        print(f"Error in error handler: {e}")

def main():
    # Initialize database
    init_database()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", show_main_menu))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(set_language, pattern="^set_lang_"))
    application.add_handler(CallbackQueryHandler(ai_chat, pattern="ai_chat"))
    application.add_handler(CallbackQueryHandler(change_model, pattern="change_model"))
    application.add_handler(CallbackQueryHandler(model_info, pattern="model_info"))
    application.add_handler(CallbackQueryHandler(about, pattern="about"))
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="main_menu"))
    
    # Model selection handlers
    for model_key in AVAILABLE_MODELS.keys():
        application.add_handler(CallbackQueryHandler(set_model, pattern=f"set_model_{model_key}"))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 MULTI-AI BOT STARTED!")
    print(f"📊 Total Models: {len(AVAILABLE_MODELS)} AI")
    print("🤖 GPT-4o, Gemini 2.0, Claude 3.5, Grok, Llama 3, dll...")
    print("💬 Ready to help with any task!")
    print("📝 Using prompt from: prompt.txt")
    
    application.run_polling()

if __name__ == "__main__":
    main()