import string

SHORT_URL_LENGTH = 7
ALLOWED_CHARACTERS = string.digits + string.ascii_letters
DEFAULT_EXPIRATION_PERIOD_DAYS = 30
MAX_RETRIES_FOR_URL_CLASH = 10