import pandas as pd
import re
import json

CITIES = [
    "WARSZAWA", "WARSAW", "POZNAN", "WROCLAW", "KRAKOW",
    "AMSTERDAM", "CORK", "DUBLIN", "VILNIUS"
]
COUNTRIES = ["POL", "NLD", "IRL", "LTU", "GBR", "USA", "ESP", "EST", "CZE"]

CITY_RE = r"(?:%s)" % "|".join(map(re.escape, CITIES))
CC_RE = r"(?:%s)" % "|".join(map(re.escape, COUNTRIES))

PAYMENT_PROVIDERS_RE = re.compile(
    r"\s+(PayPro S\.A\.|PayU\b.*|SolidGate\b.*|Autopay S\.A\.|ALIPAY LIMITED SA)\s*$",
    flags=re.IGNORECASE
)

DATE_TAIL_RE = re.compile(r"\s+20\d{2}-\d{2}-\d{2}\s*$")


def normalize_desc(s: str) -> str | None:
    if pd.isna(s):
        return None

    s = str(s).replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()

    # чисто цифры (телефон/ID) — выбрасываем
    if re.fullmatch(r"\d{8,}", s):
        return None

    # /OPT/X/////...
    s = re.sub(r"^/OPT(/[^ ]*)*\s*", "", s, flags=re.IGNORECASE).strip()

    # дата в конце
    s = DATE_TAIL_RE.sub("", s).strip()

    # UBER: убрать звёздочки, pending
    s = re.sub(r"^UBR\*\s*PENDING\.UBER\.COM\b", "UBER", s, flags=re.IGNORECASE)
    s = re.sub(r"\bUBER\s*\*\s*", "UBER ", s, flags=re.IGNORECASE)
    s = re.sub(r"\bEATS\s+PENDING\b", "EATS", s, flags=re.IGNORECASE)

    # убрать хвосты провайдеров оплаты
    s = PAYMENT_PROVIDERS_RE.sub("", s).strip()

    # если строка почти вся из кодов, но есть домен — оставить домен
    dom = re.search(r"\b([a-z0-9-]+\.(pl|com|uk))\b", s, flags=re.IGNORECASE)
    letters = re.sub(r"[^A-Za-z]", "", s)
    if dom and len(letters) < 8:
        return dom.group(1).upper()

    # ВАЖНО: срезаем "город(а) + страна" в конце, даже если город повторяется 1-3 раза
    # примеры:
    # "SUPER - PHARM WARSZAWA WARSZAWA POL" -> "SUPER - PHARM"
    # "UBER TRIP AMSTERDAM NLD" -> "UBER TRIP"
    tail = re.compile(rf"(?:\s+{CITY_RE}){{1,3}}\s+{CC_RE}\s*$", flags=re.IGNORECASE)
    s = tail.sub("", s).strip()

    # иногда бывает "WARSZAWA POL" без города из списка в нормальном регистре
    # (на всякий) — ещё раз, но без ограничения повторов:
    tail2 = re.compile(rf"(?:\s+{CITY_RE})+\s+{CC_RE}\s*$", flags=re.IGNORECASE)
    s = tail2.sub("", s).strip()

    # Нормализуем частые переводы
    if re.search(r"\bDomestic transfer\b", s, re.IGNORECASE):
        return "DOMESTIC TRANSFER"
    if re.search(r"\bOwn Transfer\b", s, re.IGNORECASE):
        return "OWN TRANSFER"
    if re.search(r"\bBLIK\b.*\btransfer\b", s, re.IGNORECASE):
        return "BLIK TRANSFER"
    if re.search(r"\bPRZELEW\b", s, re.IGNORECASE):
        return "PRZELEW"

    # финальная косметика
    s = re.sub(r"\s*-\s*", " - ", s).strip()
    s = re.sub(r"\s{2,}", " ", s).strip()

    return s or None


with open("category_rules.json") as f:
    CATEGORY_RULES = json.load(f)


def categorize(desc: str) -> str:
    if pd.isna(desc):
        return "other"

    d = desc.lower()

    for category, patterns in CATEGORY_RULES.items():
        for p in patterns:
            if re.search(p, d):
                return category

    return "other"


def run_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.drop(columns=['Na konto/Z konta', 'Saldo'], inplace=True)

    df = df.rename(columns={
        "Numer rachunku/karty": "Account",
        "Data transakcji": "Transaction date",
        "Data rozliczenia": "Settlement date",
        "Rodzaj transakcji": "Transaction type",
        "Odbiorca/Zleceniodawca": "Recipient",
        "Opis": "Description",
        "Obciążenia": "Debits",
        "Uznania": "Credits",
        "Waluta": "Currency"
    })

    df["Description_norm"] = df["Description"].apply(normalize_desc)

    df["category"] = df["Description_norm"].apply(categorize)

    # 4️⃣ income rule (credits > 0)
    df.loc[
        (df['Credits'] > 0) &
        (~df['Description_norm'].str.contains('OWN TRANSFER', na=False)),
        'category'
    ] = 'return'

    # 5️⃣ cash withdrawal rule
    df.loc[
        df['Transaction type'].str.contains('WYPŁATA GOTÓWKI', na=False),
        'category'
    ] = 'cash'

    return df
