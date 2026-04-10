import allure


@allure.feature("用户模块")
@allure.story("获取用户信息")
class TestUserInfo:

    @allure.title("获取用户信息-已登录状态")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_user_info_authenticated(self, logged_in_client, registered_user):
        from service.user_service import UserService
        service = UserService(logged_in_client)

        response = service.get_user_info()

        assert response.status_code == 200
        data = response.json().get("data", {})
        assert data.get("username") == registered_user["username"]
        assert data.get("email") == registered_user["email"]

    @allure.title("获取用户信息-未登录状态")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_user_info_unauthenticated(self, user_service):
        response = user_service.get_user_info()

        assert response.status_code == 401
        assert "未登录" in response.json().get("message", "")