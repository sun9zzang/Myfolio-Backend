import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient


# POST /v1/users
# 신규 유저를 생성합니다.
class TestUsersPost:
    @pytest.mark.parametrize(
        "wrong_field, wrong_value, error_detail",
        [
            ("email", "Abc.example.com", ""),
            ("email", "A@b@c@example.com", ""),
            ("email", r"a\"b(c)d,e:f;g<h>i[j\k]l@example.com", ""),
            ("email", 'just"not"right@example.com', ""),
            ("email", 'this is"not\\allowed@example.com', ""),
            ("email", 'this\\ still"notallowed@example.com', ""),
            ("email", "weird@examplecom", ""),  # no dots on domain-part
            ("email", "weir.do@examplecom", ""),  # dots on local-part, no dots on domain-part
            ("username", "악", ""),  # too short
            ("username", "qq", ""),  # too short
            ("username", "으악악악악엥뜨악힝", ""),  # too long
            ("username", "qwertyqwertyqwerty", ""),  # too long
            ("username", "후asdf하qwer히qwe", ""),  # too long
            # ("username", "ㅁㄴㅇㄹ", ""),  # 완성형 한글이 아님
            ("password", "패쓰와드패쓰와드", ""),  # only korean
            ("password", "thisispass와d123", ""),  # contains korean
            ("password", "onlyalphapwd", ""),  # only alphas
            ("password", "135871394137", ""),  # only digits
            ("password", "short", ""),  # too short
            ("password", "tooooo000000000000000000looooo0000000000000000000ng", ""),  # too long
            ("password", "hgowrgwf@@@", ""),  # no digits
            ("password", "$$$$3213743", ""),  # no alphas
            # ("password", "password1234", ""),  # too weak
        ],
    )
    def test_cannot_create_user_with_wrong_field(
        self,
        app: FastAPI,
        user_data: dict,
        client: TestClient,
        wrong_field: str,
        wrong_value: str,
        error_detail: str,
    ):
        user_data.update({wrong_field: wrong_value})

        response = client.post(app.url_path_for("users:"))
