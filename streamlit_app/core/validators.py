import re

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def valid_email(email):
    return bool(EMAIL_REGEX.match(email))
