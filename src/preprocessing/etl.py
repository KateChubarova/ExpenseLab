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

CARD_MASK = "4249 XXXX XXXX 5215"

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

    if re.fullmatch(r"\d{8,}", s):
        return None

    # /OPT/X/////...
    s = re.sub(r"^/OPT(/[^ ]*)*\s*", "", s, flags=re.IGNORECASE).strip()

    s = DATE_TAIL_RE.sub("", s).strip()

    s = re.sub(r"^UBR\*\s*PENDING\.UBER\.COM\b", "UBER", s, flags=re.IGNORECASE)
    s = re.sub(r"\bUBER\s*\*\s*", "UBER ", s, flags=re.IGNORECASE)
    s = re.sub(r"\bEATS\s+PENDING\b", "EATS", s, flags=re.IGNORECASE)

    s = PAYMENT_PROVIDERS_RE.sub("", s).strip()

    dom = re.search(r"\b([a-z0-9-]+\.(pl|com|uk))\b", s, flags=re.IGNORECASE)
    letters = re.sub(r"[^A-Za-z]", "", s)
    if dom and len(letters) < 8:
        return dom.group(1).upper()

    tail = re.compile(rf"(?:\s+{CITY_RE}){{1,3}}\s+{CC_RE}\s*$", flags=re.IGNORECASE)
    s = tail.sub("", s).strip()

    tail2 = re.compile(rf"(?:\s+{CITY_RE})+\s+{CC_RE}\s*$", flags=re.IGNORECASE)
    s = tail2.sub("", s).strip()

    if re.search(r"\bDomestic transfer\b", s, re.IGNORECASE):
        return "DOMESTIC TRANSFER"
    if re.search(r"\bOwn Transfer\b", s, re.IGNORECASE):
        return "OWN TRANSFER"
    if re.search(r"\bBLIK\b.*\btransfer\b", s, re.IGNORECASE):
        return "BLIK TRANSFER"
    if re.search(r"\bPRZELEW\b", s, re.IGNORECASE):
        return "PRZELEW"

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

    df.drop(columns=['Na konto/Z konta'], inplace=True)

    df = df.rename(columns={
        "Numer rachunku/karty": "account",
        "Data transakcji": "transaction date",
        "Data rozliczenia": "settlement date",
        "Rodzaj transakcji": "transaction type",
        "Odbiorca/Zleceniodawca": "recipient",
        "Opis": "description",
        "Obciążenia": "debits",
        "Uznania": "credits",
        "Waluta": "currency",
        "Saldo": "saldo",
    })

    df["account"] = df["account"].astype(str).str.strip()
    df = df[df["account"] != CARD_MASK]

    df["description_norm"] = df["description"].apply(normalize_desc)

    df["category"] = df["description_norm"].apply(categorize)

    df.loc[
        (df['credits'] > 0) &
        (~df['description_norm'].str.contains('OWN TRANSFER', na=False)),
        'category'
    ] = 'return'

    df.loc[
        df['transaction type'].str.contains('WYPŁATA GOTÓWKI', na=False),
        'category'
    ] = 'cash'

    return df
