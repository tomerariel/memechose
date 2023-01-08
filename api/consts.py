import string

SHORT_URL_LENGTH = 7
ALLOWED_CHARACTERS = string.digits + string.ascii_letters

# the following values should probably be env variables
DEFAULT_EXPIRATION_PERIOD_DAYS = 90
MAX_RETRIES_FOR_URL_CLASH = 10
DEFAULT_GRACE_PERIOD_DAYS = 5
DEFAULT_EXPIRED_URLS_ITERATION_BATCH_SIZE = 1000
