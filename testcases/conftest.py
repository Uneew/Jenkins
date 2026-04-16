import pytest
import allure
import pymysql
from faker import Faker
from config.settings import config  # 自动读取你的 env.yaml 配置
from common.api_client import ApiClient
from service.user_service import UserService

fake = Faker()

class DBExecutor:
    """
    [课题三] 数据库工具类：封装连接、执行和查询逻辑
    用于实现测试开发中的“落库校验”和“环境初始化”
    """
    def __init__(self, db_conf):
        self.conf = db_conf
        self.conn = None
        self.cursor = None

    def connect(self):
        """建立数据库连接，若配置缺失或连接失败则返回 False"""
        if not self.conf:
            return False
        try:
            self.conn = pymysql.connect(
                host=self.conf.get("host", "127.0.0.1"),
                port=self.conf.get("port", 3306),
                user=self.conf.get("user", "root"),
                password=self.conf.get("password", ""),
                database=self.conf.get("database", "test_db"),
                charset=self.conf.get("charset", "utf8mb4"),
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            # 容错处理：连接失败仅打印警告，不阻塞整体测试流程
            print(f"\n⚠️ 数据库连接失败: {e}。测试将跳过 DB 深度校验。")
            return False

    def execute(self, sql, params=None):
        """执行 SQL（增删改）并提交"""
        if self.cursor:
            try:
                self.cursor.execute(sql, params)
                self.conn.commit()
            except Exception as e:
                print(f"❌ SQL执行失败: {e}")
                self.conn.rollback()

    def fetch_one(self, sql, params=None):
        # ！！！【测开高阶技巧】强制刷新当前的事务 Read View ！！！
        self.conn.commit()

        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()

    def close(self):
        """安全关闭连接"""
        if self.conn:
            self.cursor.close()
            self.conn.close()

# --- 数据库相关 Fixtures ---

@pytest.fixture(scope="session")
def db_executor():
    """初始化数据库执行器（Session 级别，全局唯一）"""
    # 从你的 settings.py 的 env_config 中提取 db_config
    db_conf = config.env_config.get("db_config")
    executor = DBExecutor(db_conf)
    executor.connect()
    yield executor
    executor.close()

@pytest.fixture(scope="session")
def db(db_executor):
    """db_executor 的便捷简写别名"""
    return db_executor

@pytest.fixture(scope="session", autouse=True)
def init_db(db_executor):
    """
    [亮点] 自动化环境初始化：
    测试开始前清理所有 test_ 开头的脏数据，保证测试的幂等性。
    """
    if db_executor.conn:
        with allure.step("预置环境：清理数据库中的测试脏数据"):
            db_executor.execute("DELETE FROM users WHERE username LIKE 'test_%'")
    yield

# --- API 服务相关 Fixtures ---

@pytest.fixture(scope="session")
def api_client():
    """基础 API 客户端（无认证状态）"""
    client = ApiClient()
    yield client
    client.close()

@pytest.fixture(scope="function")
def user_service(api_client):
    """用户业务模块服务实例"""
    return UserService(api_client)

@pytest.fixture(scope="function")
def test_user_data():
    """使用 Faker 构造动态测试数据"""
    return {
        "username": f"test_{fake.user_name()}",
        "password": "Test@123456",
        "email": fake.email()
    }

@pytest.fixture(scope="function")
def registered_user(user_service, test_user_data, db_executor):
    """
    前置步骤：注册一个新用户。
    测开核心逻辑：如果数据库已连接，则自动进行落库校验。
    """
    with allure.step(f"前置步骤：注册新用户 {test_user_data['username']}"):
        response = user_service.register(**test_user_data)
        assert response.status_code == 200, f"注册失败: {response.text}"
        user_id = response.json().get("data", {}).get("user_id")

    # [测开亮点] 数据库落库校验
    if db_executor.conn:
        with allure.step("数据库深度断言：验证用户信息是否真实写入 users 表"):
            db_res = db_executor.fetch_one("SELECT * FROM users WHERE id=%s", (user_id,))
            assert db_res is not None, f"数据库同步异常！未找到 ID 为 {user_id} 的记录"
            assert db_res["username"] == test_user_data["username"]
            assert db_res["email"] == test_user_data["email"]

    return {
        **test_user_data,
        "user_id": user_id
    }

@pytest.fixture(scope="function")
def logged_in_client(user_service, registered_user):
    """
    前置步骤：登录并返回带有 Authorization Token 的 API 客户端。
    用于测试“获取用户信息”等需要登录态的接口。
    """
    with allure.step(f"用户登录以获取 Token: {registered_user['username']}"):
        login_resp = user_service.login(
            registered_user["username"],
            registered_user["password"]
        )
        assert login_resp.status_code == 200
        token = login_resp.json().get("data", {}).get("token")

    # 创建一个独立的客户端实例并注入 Token
    client = ApiClient()
    client.set_auth_token(token)
    yield client
    client.close()