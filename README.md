# NowLoad — Telegram-бот

**GitHub:** https://github.com/Adukatoryum/NowLoad

Навігатар па грошах, працы і правах для беларускіх падлеткаў і моладзі ў Польшчы.

---

## Як запусціць бота

### 1. Усталяваць залежнасці

```bash
pip install python-telegram-bot gspread google-auth
```

### 2. Стварыць Telegram-бота

1. Напішы @BotFather у Telegram → `/newbot`
2. Задай імя і юзэрнейм
3. Скапіруй токен

### 3. Запісаць токен у асяроддзе

```bash
export BOT_TOKEN="твой_токен_тут"
```

На Windows:
```
set BOT_TOKEN=твой_токен_тут
```

### 4. Запусціць

```bash
python bot.py
```

Бот пачне апрацоўваць паведамленні. Каб спыніць — Ctrl+C.

---

## Як падключыць Google Sheets (аналітыка)

### Крок 1 — Стварыць Service Account

1. Зайдзі на [console.cloud.google.com](https://console.cloud.google.com)
2. Стварыць новы праект (або выкарыстаць існуючы)
3. Уключыць **Google Sheets API** і **Google Drive API**
4. Перайсці ў «IAM і адміністраванне» → «Акаўнты сэрвісаў» → стварыць новы
5. Спампаваць JSON-ключ → захаваць як `google_creds.json` у папцы бота

### Крок 2 — Стварыць табліцу

1. Стварыць Google Sheets
2. Стварыць два аркушы: `clicks` і `feedback`
3. Дадаць email Service Account (з JSON-файла) у доступ да табліцы (права: рэдактар)
4. Скапіраваць ID табліцы з URL: `docs.google.com/spreadsheets/d/**ТУТ_ID**/edit`

### Крок 3 — Запісаць ID у analytics.py

Адкрыць `analytics.py` і замяніць:
```python
SPREADSHEET_ID = "ЗАМЯНІ_НА_СВОЙ_ID"
```

### Крок 4 — Дадаць загалоўкі (адзін раз)

```bash
python -c "from analytics import setup_headers; setup_headers()"
```

### Праверка падключэння

```bash
python analytics.py
```

---

## Як абнавіць лічбы і факты

Усе зменныя лічбы знаходзяцца ў адным файле: **`constants.py`**

Калі змяніліся мінімальная зарплата, ліміты або кантакты — адкрыць `constants.py` і замяніць патрэбнае значэнне.

Пасля зменаў — перазапусціць бота (`python bot.py`).

**Калі абнаўляць:** студзень і ліпень кожнага года.

Самыя зменлівыя значэнні:
- `MIN_WAGE_HOURLY_PL` і `MIN_WAGE_MONTHLY_PL` — мінімальная зарплата (мяняецца кожны год)
- `NIEREJESTROWANA_LIMIT_PL` — 75% ад мінімальнай зарплаты
- Падарункавыя ліміты (`GIFT_GROUP_*`) — правяраць штогод
- `UPDATED` — пазнака актуальнасці (змяняй разам з лічбамі)

---

## Як дадаць новы раздзел

1. Адкрыць `content_poland.py`
2. Дадаць новы ключ у слоўнік `MESSAGES`:

```python
"my_new_section": {
    "text": "Тэкст паведамлення",
    "buttons": [
        [("Назва кнопкі", "callback_key")],
        [("🏠 Галоўнае меню", "welcome")],
    ]
},
```

3. Дадаць кнопку ў раздзел адкуль павінен быць пераход
4. Калі раздзел мае фідбэк-кнопкі — дадаць адпаведныя ключы:
```python
"feedback_good_my_section": {
    "text": "Дзякуй! 🙏",
    "buttons": [[("🏠 Галоўнае меню", "welcome")]]
},
"feedback_bad_my_section": {
    "text": "Зразумела. Напішы, чаго не хапала:",
    "buttons": [[("🏠 Галоўнае меню", "welcome")]],
    "wait_text": True
},
```
5. У `bot.py` дадаць назву раздзела ў слоўнік `get_section_name()`

---

## Калі бот упаў

### Паглядзець лог памылкі:
Бот піша ўсе памылкі ў тэрмінал. Паглядзі апошнія радкі.

### Частыя прычыны:
- **BOT_TOKEN не ўсталяваны** → праверы `echo $BOT_TOKEN`
- **Памылка ў content_poland.py** → праверы сінтаксіс у змененых радках
- **Google Sheets памылка** → бот усё роўна працуе, аналітыка проста не запісваецца
- **Канфлікт сесій** → перазапусці бота

### Хуткі перазапуск:
```bash
python bot.py
```

---

## Структура файлаў

```
nowload/
├── bot.py                # Асноўная логіка бота
├── constants.py          # Усе зменныя лічбы і факты
├── content_poland.py     # Кантэнт для Польшчы (усе раздзелы)
├── content_common.py     # Кантэнт аднолькавы для ўсіх краін
├── content_lithuania.py  # Кантэнт для Літвы (у распрацоўцы)
├── analytics.py          # Запіс кліклаў і фідбэку ў Google Sheets
├── google_creds.json     # Ключы Google (НЕ дадаваць у git!)
└── README.md             # Гэты файл
```

---

## Бяспека

⚠️ **Ніколі не дадавай у git:**
- `google_creds.json`
- файлы з токенамі

Стварыць `.gitignore`:
```
google_creds.json
.env
__pycache__/
```

---

*NowLoad. Усё наладзіцца.*
