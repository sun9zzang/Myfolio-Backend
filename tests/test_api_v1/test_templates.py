import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.errors.errors import ManagedErrors


# POST /v1/templates
# 신규 템플릿을 생성합니다.
