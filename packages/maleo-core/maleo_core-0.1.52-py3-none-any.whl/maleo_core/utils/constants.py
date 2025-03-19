import re

EMAIL_REGEX:str = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
TOKEN_COOKIE_KEY_NAME="token"
REFRESH_TOKEN_DURATION_DAYS:int = 7
ACCESS_TOKEN_DURATION_MINUTES:int = 5
SORT_COLUMN_PATTERN = re.compile(r'^[a-z_]+\.(asc|desc)$')
DATE_FILTER_PATTERN = re.compile(
    r'^[a-z_]+(?:\|from::\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?(?:\|to::\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?$'
)