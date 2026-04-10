from common.api_client import ApiClient


class UserService:
    """用户模块接口服务"""

    def __init__(self, client: ApiClient = None):
        self.client = client or ApiClient()

    def register(self, username, password, email, **kwargs):
        """
        用户注册接口
        POST /api/user/register
        """
        payload = {
            "username": username,
            "password": password,
            "email": email,
            **kwargs
        }
        return self.client.post("/api/user/register", json=payload)

    def login(self, username, password):
        """
        用户登录接口
        POST /api/user/login
        """
        payload = {
            "username": username,
            "password": password
        }
        return self.client.post("/api/user/login", json=payload)

    def get_user_info(self):
        """
        获取当前用户信息
        GET /api/user/info
        """
        return self.client.get("/api/user/info")

    def update_user_info(self, **kwargs):
        """
        更新用户信息
        PUT /api/user/info
        """
        return self.client.put("/api/user/info", json=kwargs)

    def logout(self):
        """
        用户登出
        POST /api/user/logout
        """
        return self.client.post("/api/user/logout")