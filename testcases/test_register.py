import allure
import pytest


@allure.feature("用户模块")
@allure.story("用户注册")
class TestUserRegister:

    @allure.title("正常注册-新用户注册成功")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_success(self, user_service, test_user_data):
        """正向用例：使用有效数据注册"""
        with allure.step("发送注册请求"):
            response = user_service.register(**test_user_data)

        with allure.step("验证响应"):
            assert response.status_code == 200
            assert response.json().get("code") == 0
            assert "user_id" in response.json().get("data", {})

    @allure.title("异常注册-用户名已存在")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_duplicate_username(self, user_service, registered_user):
        """负向用例：使用已存在的用户名注册"""
        with allure.step("使用已存在的用户名注册"):
            response = user_service.register(**registered_user)

        with allure.step("验证返回错误信息"):
            assert response.status_code == 400
            assert "已存在" in response.json().get("message", "")

    @allure.title("异常注册-密码格式不符合要求")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("password,expected_msg", [
        ("123", "密码长度不能少于6位"),
        ("", "密码不能为空"),
    ])
    def test_register_invalid_password(self, user_service, test_user_data,
                                       password, expected_msg):
        """参数化测试：密码边界值验证"""
        test_user_data["password"] = password
        response = user_service.register(**test_user_data)

        assert response.status_code == 400
        assert expected_msg in response.json().get("message", "")