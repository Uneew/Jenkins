import pytest
import allure
from faker import Faker
from common.api_client import ApiClient
from service.user_service import UserService

fake = Faker()


@pytest.fixture(scope="session")
def api_client():
    """基础API客户端（无认证）"""
    client = ApiClient()
    yield client
    client.close()


@pytest.fixture(scope="function")
def user_service(api_client):
    """用户服务实例"""
    return UserService(api_client)


@pytest.fixture(scope="function")
def test_user_data():
    """生成测试用户数据"""
    return {
        "username": f"test_{fake.user_name()}",
        "password": "Test@123456",
        "email": fake.email()
    }


@pytest.fixture(scope="function")
def registered_user(user_service, test_user_data):
    """注册一个新用户并返回用户信息"""
    response = user_service.register(**test_user_data)
    assert response.status_code == 200, f"注册失败: {response.text}"
    return {
        **test_user_data,
        "user_id": response.json().get("data", {}).get("user_id")
    }


@pytest.fixture(scope="function")
def logged_in_client(user_service, registered_user):
    """返回已登录的API客户端"""
    # 登录获取token
    login_resp = user_service.login(
        registered_user["username"],
        registered_user["password"]
    )
    assert login_resp.status_code == 200

    token = login_resp.json().get("data", {}).get("token")

    # 创建新的客户端并设置token
    client = ApiClient()
    client.set_auth_token(token)

    yield client
    client.close()