from enum import Enum

from app.core.schemas.errors import Error


class AssertionStrings:
    @staticmethod
    def status_code(status_code: int) -> str:
        return f"HTTP response status code가 {status_code}이(가) 아닙니다."

    @staticmethod
    def errors(*errors: Error) -> str:
        return f"Error code가 [{', '.join([error.code for error in errors])}]이(가) 아닙니다."


class UserTestData(Enum):
    email = "test@test.com"
    username = "test_username"
    password = "p@ssw0rd"


class TestParamData:

    # Authorization
    invalid_tokens = [
        "iamnottoken",
        "youthinkiamrealtoken??",
        "토큰토큰토큰토작은토큰얼큰토큰",
    ]
    invalid_token_prefixes = [
        "iamnotprefix",
        "Basic",
        "Digest",
        "Token",
        "JWT",
    ]
    wrong_credential_items = [
        {"email": "wrong@example.com"},
        {"password": "wrong_p@ssw0rd"},
        {"email": "wrong@example.com", "password": "wrong_p@ssw0rd"},
    ]

    # Users
    invalid_email_values = [
        "Abc.example.com",
        "A@b@c@example.com",
        r"a\"b(c)d,e:f;g<h>i[j\k]l@example.com",
        'just"not"right@example.com',
        'this is"not\\allowed@example.com',
        'this\\ still"notallowed@example.com',
        "weird@examplecom",
        "weir.do@examplecom",
    ]
    invalid_username_values = [
        "악",
        "으악악악악엥뜨악힝",
        "qwertyqwertyqwerty",
        "후asdf하qwer히qwe",
        "ㅁㄴㅇㄹ",
    ]
    invalid_password_values = [
        "패쓰와드패쓰와드",
        "thisispass와d123",
        "onlyalphapwd",
        "135871394137",
        "short",
        (
            "tooooo000000000000000000looooo0000000000000000000ng"
            "babyyyyyyyyyyyyyyyyyyyyyyyy"
        ),
        "hgowrgwf@@@",
        "$$$$3213743",
    ]
