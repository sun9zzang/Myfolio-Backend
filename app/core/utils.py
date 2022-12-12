import re

from app.core.config import config


def validate_email(email: str) -> bool:
    # email의 형식이 올바른지 검사합니다.
    # email의 중복 여부는 검사하지 않습니다.

    # 1. email의 길이가 settings.EMAIL_MAX_LENGTH를 넘지 않아야 함
    # 2. email이 settings.EMAIL_REGEX와 match되어야 함
    if (
        len(email) <= config.USERS_EMAIL_MAX_LENGTH
        and re.compile(config.USERS_EMAIL_REGEX).match(email) is not None
    ):
        return True
    else:
        return False


def validate_username(username: str) -> bool:
    # username의 형식이 올바른지 검사합니다.
    # username의 중복 여부는 검사하지 않습니다.

    # todo validate username
    # 1. username의 길이가 2 이상 16 이하여야 함
    if 2 <= len(username) <= 16:
        return True
    else:
        return False


def validate_password(password: str) -> bool:
    # password의 형식이 올바른지 검사합니다.

    # todo password strength score validation
    # 1. password의 길이가 8 이상 50 이하여야 함
    if 8 <= len(password) <= 50:
        return True
    else:
        return False
