"""
Application settings and configuration.

Goal:
- Centralize all constants and tuning knobs for:
  - Data cleaning
  - Type inference
  - Imputation
  - Outlier detection
  - Column matching
  - Performance safeguards
  - Date parsing / export formatting
"""

# =========================
# App metadata & UI
# =========================
APP_TITLE = "AI Data Cleaning & Analysis"
APP_VERSION = "2.1"
AUTHOR = "By Mohamed Alaa"

PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# =========================
# Performance / Capacity
# =========================
# Recommended safe limits for smooth Streamlit UX on local machines
MAX_ROWS_RECOMMENDED = 50_000
MAX_COLS_RECOMMENDED = 80

# Soft limits to auto-switch algorithms for speed (quality trade-offs)
KNN_MAX_ROWS = 30_000
TEXT_CLEAN_MAX_ROWS = 30_000
OUTLIER_MAX_ROWS = 120_000  # IsolationForest can handle more, but UI might be heavy

# When datasets are huge, use sampling for expensive steps
OUTLIER_SAMPLE_ROWS = 50_000

# =========================
# Default parameters
# =========================
DEFAULT_KNN_NEIGHBORS = 3
DEFAULT_CONTAMINATION = 0.03
DEFAULT_MATCH_THRESHOLD = 80

# If you decide to add "lite mode"
DEFAULT_LITE_MODE = False

# =========================
# Parsing / Reading
# =========================
# Date parsing behavior
DATE_PARSE_DAYFIRST = False  # True for dd/mm/yyyy common in some locales
DATE_PARSE_INFER = True
DATE_PARSE_ERRORS = "coerce"  # "coerce" safest

# Export formatting for datetime columns (presentation only)
EXPORT_DATETIME_FORMAT = "%Y-%m-%d"  # date-only
# EXPORT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"  # if you want date+time

# =========================
# Placeholders to treat as missing
# (Recommended to keep here so all tabs/services share the same list)
# =========================
PLACEHOLDER_VALUES = [
    "UNKNOWN", "Unknown", "unknown",
    "ERROR", "Error", "error",
    "N/A", "n/a", "NA", "na", "N/a",
    "NULL", "Null", "null",
    "NONE", "None", "none",
    "NAN", "NaN", "nan",
    "MISSING", "Missing", "missing",
    "NOT AVAILABLE", "Not Available", "not available",
    "NOT FOUND", "Not Found", "not found",
    "UNDEFINED", "Undefined", "undefined",
    "INVALID", "Invalid", "invalid",
    "EMPTY", "Empty", "empty",
    "-", "--", "---",
    "?", "??", "???",
    ".", "..", "...",
    "#N/A", "#VALUE!", "#REF!", "#DIV/0!", "#NAME?",
    "", " ",
]

# =========================
# Keyword dictionaries for type inference & cleaning decisions
# =========================

# Columns that should be whole numbers
INTEGER_KEYWORDS = [
    # English
    "age", "count", "quantity", "qty",
    "number", "num", "no",
    "year", "month", "day",
    "rank", "level", "floor", "room",
    "people", "persons", "children", "kids",
    "employees", "students",
    "score", "points",
    # Arabic
    "عمر", "سن",
    "عدد", "كمية",
    "رقم",
    "سنة", "عام",
    "شهر",
    "يوم",
    "ترتيب",
    "مستوى",
    "طابق",
    "غرفة",
    "اشخاص",
    "اطفال",
    "موظفين",
    "طلاب",
    "نقاط", "درجة",
]

# Columns that look like IDs/codes — treat as categorical (NOT numeric analytics)
ID_KEYWORDS = [
    "id", "uuid", "guid", "code", "key", "ref", "reference",
    "employee_id", "user_id", "client_id", "order_id", "invoice_id",
    "account_id", "ticket_id", "case_id",
    "رقم_تعريف", "كود", "معرف", "مرجع",
]

# Monetary/currency columns (2 decimal rounding)
MONETARY_KEYWORDS = [
    "price", "cost", "amount", "total", "sum", "fee", "charge",
    "spent", "paid", "payment",
    "salary", "wage", "income", "revenue",
    "expense", "budget", "balance", "credit", "debit", "tax",
    "discount", "tip", "bill", "invoice", "rate", "value",
    "subtotal", "grand_total", "net", "gross", "profit", "loss",
    # Arabic
    "سعر", "تكلفة", "مبلغ", "إجمالي", "مجموع", "رسوم",
    "مصروف", "دفع", "راتب", "دخل", "إيراد", "ميزانية", "رصيد",
    "ضريبة", "خصم", "فاتورة", "قيمة",
    "صافي", "إجمالي", "مستحق", "ربح", "خسارة",
]

# Currency markers inside text/numeric strings
CURRENCY_SYMBOLS = ["$", "€", "£", "¥", "EGP", "USD", "EUR", "SAR", "AED", "QAR", "KWD"]

# Date/time columns by name (used to protect from text regex and to parse)
DATE_KEYWORDS = [
    "date", "datetime", "time", "timestamp",
    "created", "updated", "modified",
    "join", "joined", "start", "end",
    "dob", "birth",
    "expiry", "expire", "expiration",
    # Arabic
    "تاريخ", "وقت", "زمن",
    "انضمام", "بدء", "نهاية",
    "ميلاد",
    "انتهاء", "صلاحية",
]

# True/False/Yes/No normalization (if you later add boolean normalization)
BOOL_TRUE_VALUES = {"true", "yes", "y", "1", "on", "صح", "نعم", "اه", "أه"}
BOOL_FALSE_VALUES = {"false", "no", "n", "0", "off", "غلط", "لا", "لأ"}

# Context column priority keywords for AI categorical imputation
CONTEXT_PRIORITY_KEYWORDS = [
    "country", "state", "region", "city", "department", "team",
    "دولة", "بلد", "منطقة", "محافظة", "مدينة", "قسم", "فريق",
]

# Common structured types by name (used to skip aggressive text cleaning)
EMAIL_KEYWORDS = ["email", "e-mail", "mail", "بريد", "ايميل"]
PHONE_KEYWORDS = ["phone", "mobile", "tel", "telephone", "contact", "هاتف", "موبايل", "تليفون", "رقم_هاتف"]
URL_KEYWORDS = ["url", "website", "link", "site", "web", "موقع", "لينك", "رابط"]

# =========================
# Outlier detection config
# =========================
# If you later expose more controls:
OUTLIER_RANDOM_STATE = 42
OUTLIER_DEFAULT_FEATURES_LIMIT = 25  # If numeric columns exceed this, consider selecting top N or sampling

# =========================
# Column matching config (RapidFuzz / fuzzy)
# =========================
MATCH_MIN_LENGTH = 2
MATCH_TOP_K_SUGGESTIONS = 10

# =========================
# Analysis / Visualization
# =========================
# Limits to avoid UI crashes when showing huge correlation matrices
CORR_MAX_COLS = 30

# =========================
# Safety toggles (optional)
# =========================
# If True: aggressively prevent any text cleaning from touching datetime/id/email/url/phone columns
STRICT_STRUCTURED_GUARDS = True