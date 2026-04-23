"""
NowLoad — Telegram-бот для беларускіх падлеткаў і моладзі ў эміграцыі.
Навігатар па грошах, працы і правах у краінах ЕС.
Паток: /start → прывітанне → выбар краіны → меню краіны
"""

import logging
import os
import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

from content_poland import MESSAGES as MESSAGES_PL
from content_lithuania import MESSAGES_LT
from content_common import MESSAGES_COMMON
from analytics import log_click, log_feedback

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============================================================
# УВАХОДНЫЯ ЭКРАНЫ (незалежныя ад краіны)
# ============================================================

GREETING = {
    "text": (
        "\u041f\u0440\u044b\u0432\u0456\u0442\u0430\u043d\u043d\u0435! \U0001f44b \u042f NowLoad.\n\n"
        "\u0414\u0430\u043f\u0430\u043c\u0430\u0436\u0443 \u0440\u0430\u0437\u0430\u0431\u0440\u0430\u0446\u0446\u0430 \u0437 \u0433\u0440\u0430\u0448\u044b\u043c\u0430, \u043f\u0440\u0430\u0446\u0430\u0439 \u0456 \u043f\u0440\u0430\u0432\u0430\u043c\u0456.\n\n"
        "\u041f\u0430\u0441\u043f\u0440\u0430\u0431\u0443\u0435\u043c?\n\n"
        "<i>NowLoad. Усё на(ў)ладзіцца.</i>"
    ),
    "buttons": [
        [("Паспрабуем! \u2192", "country_select")],
        [("\U0001f198 Патрэбна дапамога прама зараз", "emergency")],
    ]
}

COUNTRY_SELECT = {
    "text": "У якой краіне ты зараз?",
    "buttons": [
        [("PL Польшча", "country_pl")],
        [("LT Літва", "country_lt")],
        [("EU Іншыя краіны", "country_other")],
        [("BY Беларусь — планую заставацца", "country_by_stay")],
        [("BY Беларусь — планую з'язджаць", "country_by_leave")],
        [("\U0001f198 Патрэбна дапамога прама зараз", "emergency")],
    ]
}

COUNTRY_WELCOME = {
    "poland":    "welcome",
    "lithuania": "lt_welcome",
}

AGE_SELECT = {
    "text": "Колькі табе гадоў?",
    "buttons": [
        [("👦 Менш за 15", "age_under15")],
        [("🧑 15–17 гадоў", "age_15_17")],
        [("🧒 18 і больш", "age_18plus")],
        [("🆘 Патрэбна дапамога прама зараз", "emergency")],
    ]
}

# Маршруты па ўзросту — толькі для раздзелаў з узроставымі падраздзеламі ў v2.0
AGE_ROUTE = {
    "earn_start": {
        "under_15": "earn_under15",
        "15_17":    "earn_15_17",
        "18_plus":  "earn_18plus",
    },
    "can_i_work": {
        "under_15": "can_i_work_under15",
        "15_17":    "can_i_work_15_17",
        "18_plus":  "can_i_work_18plus",
    },
    # career_skills і open_account у v2.0 не маюць узроставых падраздзелаў
}


# ============================================================
# УТЫЛІТЫ
# ============================================================

def build_keyboard(buttons):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in buttons
    ])


def get_message(key: str, user_data: dict = None) -> dict | None:
    """
    Вяртае паведамленне па ключу з улікам краіны.
    Ключ "welcome" аўтаматычна вяртае правільны welcome для краіны.
    """
    country = (user_data or {}).get("country", "poland")
    if key == "welcome":
        key = COUNTRY_WELCOME.get(country, "welcome")
    if country == "lithuania":
        return (
            MESSAGES_LT.get(key)
            or MESSAGES_COMMON.get(key)
            or MESSAGES_PL.get(key)
        )
    return MESSAGES_PL.get(key) or MESSAGES_COMMON.get(key)


def get_section_name(key: str) -> str:
    names = {
        "greeting":                  "Прывітанне",
        "country_select":            "Выбар краіны",
        "age_select":                "Выбар узросту",
        "welcome":                   "Галоўнае меню",
        "lt_welcome":                "Галоўнае меню (LT)",
        "emergency":                 "SOS",
        "emergency_not_paid":        "SOS: Не заплацілі",
        "emergency_scam":            "SOS: Скам",
        "emergency_docs":            "SOS: Дакументы",
        "emergency_other":           "SOS: Іншае",
        "emergency_language":        "SOS: Мова",
        "not_paid":                  "Не заплацілі",
        "not_paid_salary":           "Не заплацілі зарплату",
        "not_paid_fired":            "Выгналі",
        "not_paid_nodocs":           "Без дагавора",
        "scam_check":                "Скам-чэк",
        "scam_info":                 "Скам: інфа",
        "scam_easy_money":           "Скам: лёгкія грошы",
        "scam_signs_work":           "Скам: прыкметы",
        "scam_checklist_info":       "Скам: чэкліст",
        "scam_game":                 "Скам: гульня",
        "can_i_work":                "Ці магу працаваць",
        "can_i_work_info":           "Праца: інфа",
        "can_i_work_under15":        "Праца: да 15",
        "can_i_work_15_17":          "Праца: 15–17",
        "can_i_work_15_17_has_docs": "Праца: 15–17 з картай",
        "can_i_work_18plus":         "Праца: 18+",
        "can_i_work_18_has_docs":    "Праца: 18+ з картай",
        "can_i_work_hours":          "Праца: гадзіны",
        "can_i_work_contracts":      "Праца: дагаворы",
        "can_i_work_game":           "Праца: гульня",
        "documents":                 "Дакументы",
        "docs_pesel":                "PESEL",
        "earn_start":                "Хачу зарабіць",
        "earn_info":                 "Заробак: інфа",
        "earn_under15":              "Заробак: да 15",
        "earn_15_17":                "Заробак: 15–17",
        "earn_18plus":               "Заробак: 18+",
        "earn_offline":              "Афлайн-праца",
        "earn_online":               "Анлайн-заробак",
        "earn_self":                 "Самазаробак",
        "earn_game":                 "Заробак: гульня",
        "career_skills":             "Навыкі / кар'ера",
        "career_info":               "Кар'ера: інфа",
        "career_internship":         "Стажыроўка",
        "career_courses":            "Курсы",
        "career_eu":                 "EU-праграмы",
        "career_polish":             "Польская мова",
        "career_game":               "Кар'ера: гульня",
        "money_hub":                 "Мае грошы",
        "open_account":              "Рахунак у банку",
        "open_account_digital":      "Revolut / Wise",
        "first_money":               "Першыя грошы",
        "send_money":                "Грошы дадому",
        "taxes_info":                "Падаткі: інфа",
        "taxes_declaration":         "Падатковая дэкларацыя",
        "just_arrived":              "Толькі прыехаў",
    }
    return names.get(key, key)


# ============================================================
# АДПРАЎКА ПАВЕДАМЛЕННЯЎ
# ============================================================

async def _send_raw(update: Update, text: str, keyboard):
    if update.callback_query:
        await update.callback_query.message.reply_text(
            text=text, reply_markup=keyboard, parse_mode=None
        )
    else:
        await update.message.reply_text(
            text=text, reply_markup=keyboard, parse_mode=None
        )


async def send_greeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_section"] = "greeting"
    if update.callback_query:
        await update.callback_query.message.reply_text(
            GREETING["text"], reply_markup=build_keyboard(GREETING["buttons"]), parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            GREETING["text"], reply_markup=build_keyboard(GREETING["buttons"]), parse_mode="HTML"
        )


async def send_country_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_section"] = "country_select"
    await _send_raw(update, COUNTRY_SELECT["text"], build_keyboard(COUNTRY_SELECT["buttons"]))


async def send_age_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_section"] = "age_select"
    await _send_raw(update, AGE_SELECT["text"], build_keyboard(AGE_SELECT["buttons"]))


async def send_message(update: Update, key: str, context: ContextTypes.DEFAULT_TYPE):
    msg = get_message(key, context.user_data)
    if not msg:
        logger.warning(f"Ключ не знойдзены: {key}")
        return

    keyboard = build_keyboard(msg["buttons"]) if msg.get("buttons") else None
    text = msg["text"]
    context.user_data["last_section"] = key

    if msg.get("wait_text"):
        context.user_data["waiting_feedback"] = True
        context.user_data["feedback_section"] = context.user_data.get("prev_section", key)
    else:
        context.user_data["waiting_feedback"] = False

    age_keys = {
        "earn_under15": "under_15", "can_work_under15": "under_15",
        "career_under15": "under_15", "earn_15_17": "15_17",
        "can_work_15_17": "15_17", "career_15_17": "15_17",
        "earn_18plus": "18_plus", "can_work_18plus": "18_plus",
        "career_18_25": "18_plus", "earn_18_offline": "18_plus",
        "work_18_has_docs": "18_plus",
    }
    if key in age_keys and "age" not in context.user_data:
        context.user_data["age"] = age_keys[key]

    await _send_raw(update, text, keyboard)


# ============================================================
# ХЭНДЛЕРЫ
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Паток новага карыстальніка:
      /start -> прывітанне -> [Далей] -> выбар краіны -> меню краіны

    Паток карыстальніка які вяртаецца (краіна ўжо вядома):
      /start -> прапанова працягнуць / вярнуцца ў меню
    """
    user_id = update.effective_user.id
    country = context.user_data.get("country")
    last_section = context.user_data.get("last_section")

    # Лагіруем тупік старой сесіі перад скідам
    welcome_key_prev = COUNTRY_WELCOME.get(country, "welcome") if country else None
    if country and last_section and last_section not in ("greeting", "country_select", welcome_key_prev, None):
        log_click(user_id, context.user_data, "dead_end", f"тупік: {get_section_name(last_section)}")

    # Новая сесія
    context.user_data["session_id"] = str(uuid.uuid4())[:8]
    context.user_data["step"] = 0
    context.user_data["last_click_time"] = None
    context.user_data["time_on_prev_sec"] = ""
    context.user_data["is_first_after_welcome"] = False

    if not country:
        await send_greeting(update, context)
        log_click(user_id, context.user_data, "greeting", get_section_name("greeting"))
        return

    welcome_key = COUNTRY_WELCOME.get(country, "welcome")
    if last_section and last_section not in ("greeting", "country_select", welcome_key):
        section_name = get_section_name(last_section)
        await update.message.reply_text(
            f"З вяртаннем! \U0001f44b\n\n"
            f"Ты быў(-ла) ў раздзеле «{section_name}».\n"
            f"Працягнуць?",
            reply_markup=build_keyboard([
                [(f"\u25b6\ufe0f Так, працягнуць", last_section)],
                [("\U0001f3e0 Галоўнае меню", "welcome")],
                [("\U0001f30d Змяніць краіну", "change_country")],
            ])
        )
        log_click(user_id, context.user_data, "start_return", get_section_name(last_section))
    else:
        await send_message(update, "welcome", context)
        log_click(user_id, context.user_data, welcome_key, get_section_name(welcome_key))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    from_key = context.user_data.get("last_section", "unknown")
    to_key = query.data
    context.user_data["prev_section"] = from_key

    # Час на папярэднім раздзеле
    now = datetime.now()
    last_time_str = context.user_data.get("last_click_time")
    if last_time_str:
        delta = now - datetime.fromisoformat(last_time_str)
        context.user_data["time_on_prev_sec"] = int(delta.total_seconds())
    else:
        context.user_data["time_on_prev_sec"] = ""
    context.user_data["last_click_time"] = now.isoformat()

    # Глыбіня сцэнара
    context.user_data["step"] = context.user_data.get("step", 0) + 1

    # Першы раздзел пасля welcome
    context.user_data["is_first_after_welcome"] = (from_key == "welcome")

    log_click(user_id, context.user_data, to_key, get_section_name(to_key))

    if to_key == "country_select":
        await send_country_select(update, context)
        return

    if to_key == "country_pl":
        context.user_data["country"] = "poland"
        context.user_data.pop("age", None)
        await send_age_select(update, context)
        return

    if to_key == "country_lt":
        context.user_data["country"] = "lithuania"
        context.user_data.pop("age", None)
        await send_age_select(update, context)
        return

    if to_key == "change_country":
        context.user_data.pop("country", None)
        context.user_data.pop("age", None)
        await send_country_select(update, context)
        return

    if to_key in ("age_under15", "age_15_17", "age_18plus"):
        age_map = {"age_under15": "under_15", "age_15_17": "15_17", "age_18plus": "18_plus"}
        context.user_data["age"] = age_map[to_key]
        welcome_key = COUNTRY_WELCOME.get(context.user_data.get("country", "poland"), "welcome")
        log_click(user_id, context.user_data, welcome_key, get_section_name("welcome"))
        await send_message(update, "welcome", context)
        return

    # Калі ўзрост вядомы — абыходзім пытанне пра ўзрост у сцэнары
    age = context.user_data.get("age")
    if age and to_key in AGE_ROUTE:
        routed_key = AGE_ROUTE[to_key][age]
        await send_message(update, routed_key, context)
        return

    await send_message(update, to_key, context)


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.user_data.get("waiting_feedback"):
        await update.message.reply_text(
            "Выкарыстоўвай кнопкі для навігацыі \U0001f447\n"
            "Або /start каб пачаць спачатку.",
        )
        return

    feedback_text = update.message.text
    section = context.user_data.get("feedback_section", "unknown")
    log_feedback(user_id, section, "text", feedback_text)
    context.user_data["waiting_feedback"] = False

    await update.message.reply_text(
        "Дзякуй! Твой водгук дапаможа нам зрабіць бот лепшым \U0001f64f\n\n"
        "NowLoad. Усё на(ў)ладзіцца.",
        reply_markup=build_keyboard([
            [("\U0001f3e0 Галоўнае меню", "welcome")],
        ])
    )


# ============================================================
# TEST КАМАНДЫ
# ============================================================

TEST_COMMANDS = [
    ("scam_check",    "/test_scam",      "\u26a0\ufe0f Скам-чэк [PL]",          "poland"),
    ("not_paid",      "/test_notpaid",   "\U0001f621 Не заплацілі [PL]",         "poland"),
    ("can_i_work",    "/test_canwork",   "\u2753 Ці магу працаваць [PL]",        "poland"),
    ("earn_start",    "/test_earn",      "\U0001f4b8 Хачу зарабіць [PL]",        "poland"),
    ("open_account",  "/test_account",   "\U0001f3e6 Рахунак [PL]",              "poland"),
    ("send_money",    "/test_send",      "\U0001f4b1 Перавесці грошы [PL]",      "poland"),
    ("first_money",   "/test_money",     "\U0001f4b0 Першыя грошы [PL]",         "poland"),
    ("just_arrived",  "/test_arrived",   "\U0001f937 Толькі прыехаў [PL]",       "poland"),
    ("career_skills", "/test_career",    "\U0001f3af Кар'ера / навыкі [PL]",     "poland"),
    ("documents",     "/test_docs",      "\U0001f4c4 Дакументы [PL]",            "poland"),
    ("emergency",     "/test_emergency", "\U0001f198 Патрэбна дапамога",         "poland"),
    ("lt_welcome",    "/test_lt",        "\U0001f1f1\U0001f1f9 Меню Літвы",      "lithuania"),
]


async def test_scenario(
    update: Update, context: ContextTypes.DEFAULT_TYPE,
    key: str, country: str = "poland"
):
    context.user_data.clear()
    context.user_data["country"] = country
    context.user_data["session_id"] = "test_" + str(uuid.uuid4())[:6]
    context.user_data["step"] = 0
    await send_message(update, key, context)
    log_click(update.effective_user.id, context.user_data, key, get_section_name(key))


async def test_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["<b>Тэставыя каманды NowLoad</b>\n"]
    for _, cmd, label, _ in TEST_COMMANDS:
        lines.append(f"{label} — <code>{cmd}</code>")
    lines.append("\n/start — Поўны паток (прывітанне → краіна → меню)")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


# ============================================================
# ЗАПУСК
# ============================================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test_menu))

    app.add_handler(CommandHandler("test_scam",      lambda u, c: test_scenario(u, c, "scam_check")))
    app.add_handler(CommandHandler("test_notpaid",   lambda u, c: test_scenario(u, c, "not_paid")))
    app.add_handler(CommandHandler("test_canwork",   lambda u, c: test_scenario(u, c, "can_i_work")))
    app.add_handler(CommandHandler("test_earn",      lambda u, c: test_scenario(u, c, "earn_start")))
    app.add_handler(CommandHandler("test_account",   lambda u, c: test_scenario(u, c, "open_account")))
    app.add_handler(CommandHandler("test_send",      lambda u, c: test_scenario(u, c, "send_money")))
    app.add_handler(CommandHandler("test_money",     lambda u, c: test_scenario(u, c, "first_money")))
    app.add_handler(CommandHandler("test_arrived",   lambda u, c: test_scenario(u, c, "just_arrived")))
    app.add_handler(CommandHandler("test_career",    lambda u, c: test_scenario(u, c, "career_skills")))
    app.add_handler(CommandHandler("test_docs",      lambda u, c: test_scenario(u, c, "documents")))
    app.add_handler(CommandHandler("test_emergency", lambda u, c: test_scenario(u, c, "emergency")))
    app.add_handler(CommandHandler("test_lt",        lambda u, c: test_scenario(u, c, "lt_welcome", "lithuania")))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("NowLoad запушчаны \u2705")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

