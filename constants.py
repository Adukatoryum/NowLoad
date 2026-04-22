# =============================================================
# constants.py — NowLoad
# Усе зменныя лічбы і факты. Абнаўляць раз у паўгода.
# Апошняе абнаўленне: студзень 2026
# =============================================================

# --- ПОЛЬШЧА — мінімальная зарплата ---
MIN_WAGE_HOURLY_PL = 31.40          # PLN/гадзіна, brutto
MIN_WAGE_MONTHLY_PL = 4806          # PLN/месяц, brutto

# --- Działalność nierejestrowana ---
# 75% ад мінімальнай зарплаты. Мяняецца разам з мінімалкай.
NIEREJESTROWANA_LIMIT_PL = 3499.50  # PLN/месяц (актуальна студзень 2026)

# --- Ulga dla młodych (Zero PIT да 26 гадоў) ---
# Толькі для umowa o pracę і umowa zlecenie. Для umowa o dzieło — не дзейнічае.
ULGA_MLODYCH_LIMIT_PL = 85528       # PLN/год (не індэксавалася з 2022)

# --- PIT ---
PIT_FREE_AMOUNT_PL = 30000          # PLN/год — квота без падатку
PIT_RATE_1_PL = 12                  # % — стаўка да 120 000 PLN
PIT_RATE_2_PL = 32                  # % — стаўка вышэй 120 000 PLN
PIT_DEADLINE = "30 красавіка"       # Тэрмін падачы дэкларацыі

# --- Падарункі (Groups) ---
# Перыядычна мяняюцца — праверыць перад абнаўленнем
GIFT_GROUP_1_PL = 36120             # PLN — блізкія родзічы (бацькі, дзеці, браты/сёстры)
GIFT_GROUP_2_PL = 27090             # PLN — астатнія родзічы
GIFT_GROUP_3_PL = 5733              # PLN — чужыя людзі

# --- Узрост ---
MIN_AGE_WORK_PL = 15                # Мінімальны ўзрост для афіцыйнай працы ў Польшчы
MIN_AGE_WORK_LT = 14                # Мінімальны ўзрост для лёгкай працы ў Літве
MIN_AGE_NIEREJESTROWANA = 18        # Działalność nierejestrowana — толькі з 18 гадоў

# --- Рабочы час для непаўнагадовых (Польшча) ---
MAX_HOURS_UNDER_16 = 6              # гадзін у дзень (да 16 гадоў)
MAX_HOURS_16_17 = 8                 # гадзін у дзень (16–17 гадоў)
NIGHT_WORK_START = "22:00"          # забаронена праца пасля
NIGHT_WORK_END = "06:00"            # і да

# --- Тыпы дагавораў ---
# Толькі назвы — умовы ўнутры кантэнту
CONTRACT_PRACA = "umowa o pracę"
CONTRACT_ZLECENIE = "umowa zlecenie"
CONTRACT_DZIELO = "umowa o dzieło"
CONTRACT_B2B = "umowa B2B"

# --- Сэрвісы пераводаў ---
# Статус Revolut/Wise для беларусаў — дынамічны, правяраць на сайце сэрвісу
TRANSFER_WARNING = "⚠️ Перад выкарыстаннем як асноўны рахунак — правер умовы на сайце сэрвісу"

# --- Кантакты арганізацый ---
PIP_PHONE = "801 002 006"           # Дзяржаўная інспекцыя працы
PIP_URL = "pip.gov.pl"
CERT_URL = "cert.pl"
UOKIK_URL = "uokik.gov.pl"
BELARUSAM_HOURS = "пн–пт 11–19"
BELARUSAM_URL = "belarusam.pl"
SIP_URL = "interwencjaprawna.pl"    # Stowarzyszenie Interwencji Prawnej
BIALDOM_PHONE = "+48 695 807 059"   # Беларускі Дом у Варшаве
POLICE = "112"
URZAD_PRACY_URL = "praca.gov.pl"

# --- Платформы для пошуку працы ---
PLATFORM_PRACUJ = "pracuj.pl"
PLATFORM_OLX = "olx.pl/praca"
PLATFORM_NOFLUFF = "nofluffjobs.com"
PLATFORM_LINKEDIN = "linkedin.com"
PLATFORM_JOOBLE = "jooble.org"

# --- Фрыланс-платформы ---
PLATFORM_FIVERR = "fiverr.com"
PLATFORM_KWORK = "kwork.ru"         # ⚠️ Правяраць даступнасць з Польшчы
PLATFORM_USEME = "useme.com"        # Польская платформа, афіцыйны дагавор

# --- Банкі для падлеткаў/мігрантаў ---
BANK_PKO = "PKO BP"
BANK_MBANK = "mBank"
BANK_SANTANDER = "Santander"
BANK_NOTE = "Кожны банк мае свае патрабаванні да дакументаў. Правяраць на сайце."

# --- Метадычная пазнака ---
UPDATED = "студзень 2026"
NEXT_UPDATE = "ліпень 2026"
