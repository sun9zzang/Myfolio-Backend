import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.errors.errors import ManagedErrors
from app.core.schemas.errors import ErrorList
from app.core.schemas.users import User, UserInDB


class _TestUserData:
    wrong_email = []
    wrong_username = []
    wrong_password = []

    invalid_token = []
    invalid_token_prefix = []


@pytest.fixture(params=[])
def invalid_authorization_header(request):
    return request.param


@pytest.fixture(params=_TestUserData.invalid_token)
def invalid_token(request):
    return request.param


@pytest.fixture(params=_TestUserData.invalid_token_prefix)
def invalid_token_prefix(request):
    return request.param


# POST /v1/users
# 신규 유저를 생성합니다.
class TestV1UsersPOST:

    # 유효하지 않은 유저 정보 필드로 유저 생성 불가
    @pytest.mark.parametrize(
        "wrong_field, wrong_value",
        [
            ("email", "Abc.example.com"),
            ("email", "A@b@c@example.com"),
            ("email", r"a\"b(c)d,e:f;g<h>i[j\k]l@example.com"),
            ("email", 'just"not"right@example.com'),
            ("email", 'this is"not\\allowed@example.com'),
            ("email", 'this\\ still"notallowed@example.com'),
            ("email", "weird@examplecom"),  # no dots on domain-part
            (
                "email",
                "weir.do@examplecom",
            ),  # dots on local-part, no dots on domain-part
            ("username", "악"),  # too short
            # ("username", "qq"),  # too short
            ("username", "으악악악악엥뜨악힝"),  # too long
            ("username", "qwertyqwertyqwerty"),  # too long
            ("username", "후asdf하qwer히qwe"),  # too long
            # ("username", "ㅁㄴㅇㄹ"),  # 완성형 한글이 아님
            ("password", "패쓰와드패쓰와드"),  # only korean
            ("password", "thisispass와d123"),  # contains korean
            ("password", "onlyalphapwd"),  # only alphas
            ("password", "135871394137"),  # only digits
            ("password", "short"),  # too short
            (
                "password",
                "tooooo000000000000000000looooo0000000000000000000ng"
                "babyyyyyyyyyyyyyyyyyyyyyyyy",
            ),  # too long
            ("password", "hgowrgwf@@@"),  # no digits
            ("password", "$$$$3213743"),  # no alphas
            # ("password", "password1234"),  # too weak
        ],
    )
    def test_cannot_create_user_with_wrong_field(
        self,
        app: FastAPI,
        user_dict: dict,
        client: TestClient,
        wrong_field: str,
        wrong_value: str,
    ):
        user_dict.update({wrong_field: wrong_value})
        print(f"attempting to create user with invalid field - user_dict: {user_dict}")
        response = client.post(
            app.url_path_for("users:create-user"),
            json=user_dict,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST, ""
        assert (
            response.json()["errors"][0]["code"] == "invalid_" + wrong_field
        ), ""  # todo

    # 중복된 필드로 유저 생성 요청 불가
    def test_cannot_create_user_with_duplicated_field(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
    ):
        raise NotImplementedError

    # 유효한 필드로 유저 생성 요청 가능
    def test_can_create_user(
        self,
        app: FastAPI,
        user_dict: dict,
        client: TestClient,
    ):
        print(f"attempting to create user - user_dict: {user_dict}")
        response = client.post(
            app.url_path_for("users:create-user"),
            json=user_dict,
        )

        assert response.status_code == status.HTTP_201_CREATED, ""
        assert User(**response.json()).dict() == user_dict, ""


class TestV1UsersRetrieveUserGET:

    # 잘못된 user_id로 유저 정보 요청 불가
    @pytest.mark.parametrize(
        "invalid_user_id",
        [
            "abcdef",
            "가나다",
            "?",
        ],
    )
    def test_cannot_retrieve_user_with_invalid_syntax(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
        invalid_user_id: str,
    ):
        print(
            "attempting to retrieve user with invalid syntax"
            f" - invalid_user_id: {invalid_user_id}"
        )
        response = client.get(
            app.url_path_for("users:retrieve-user", user_id=invalid_user_id)
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST, ""
        assert (
            response.json() == ErrorList().append(ManagedErrors.bad_request).dict()
        ), ""

    # 존재하지 않는 user_id로 유저 정보 요청 불가
    def test_cannot_retrieve_user_with_not_existing_user_id(
        self,
        app: FastAPI,
        client: TestClient,
    ):
        raise NotImplementedError

    # 존재하는 유저 정보 요청 가능
    def test_can_retrieve_user(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
    ):
        print(f"attempting to retrieve user - user_id: {user.user_id}")
        response = client.get(
            app.url_path_for("users:retrieve-user", user_id=user.user_id)
        )

        assert response.status_code == status.HTTP_200_OK, ""
        assert response.json() == user.dict(
            exclude={"salt": True, "hashed_password": True}
        ), ""


class TestV1UsersUpdateUserPATCH:

    # Authorization header 없이 유저 업데이트 요청 불가
    def test_cannot_update_user_without_authentication(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
    ):
        print("attempting to update user without authentication...")

        raise NotImplementedError

    # 유효하지 않은 인증 정보로 유저 업데이트 요청 불가
    def test_cannot_update_user_with_invalid_authentication(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
        authorization_header_key: str,
    ):
        header = {authorization_header_key: ...}
        client.headers.update(header)
        print(
            f"attempting to update user with invalid authentication - header: {header}"
        )

        raise NotImplementedError
