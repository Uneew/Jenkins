import allure


@allure.feature("用户模块")
@allure.story("用户登录")
class TestUserLogin:

    @allure.title("正常登录-用户名密码正确")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, user_service, registered_user):
        response = user_service.login(
            registered_user["username"],
            registered_user["password"]
        )

        assert response.status_code == 200
        assert response.json().get("code") == 0
        data = response.json().get("data", {})
        assert "token" in data
        assert data.get("username") == registered_user["username"]

    @allure.title("异常登录-密码错误")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_wrong_password(self, user_service, registered_user):
        response = user_service.login(
            registered_user["username"],
            "WrongPassword123"
        )

        assert response.status_code == 401
        assert "密码错误" in response.json().get("message", "")

    @allure.title("异常登录-用户不存在")
    def test_login_user_not_exist(self, user_service):
        response = user_service.login("nonexistent_user", "anypassword")

        assert response.status_code == 401
        assert "用户不存在" in response.json().get("message", "")