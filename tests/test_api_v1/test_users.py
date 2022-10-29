import pytest
from fastapi import FastAPI, status


# POST /v1/users
# 신규 유저를 생성합니다.
class TestUsersPost:
    @pytest.mark.parametrize(

    )
    def test_cannot_create_user_with_wrong_field(
        self,
        app: FastAPI,

    ):