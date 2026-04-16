# mock_server.py
from flask import Flask, request, jsonify
import pymysql
import logging

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 数据库配置 (请确保与 env.yaml 一致) ---
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123",  # <-- 修改为你的真实密码
    "database": "test_db",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}


def get_db_connection():
    try:
        # 尝试连接，设置连接超时为2秒，防止卡死
        return pymysql.connect(connect_timeout=2, **DB_CONFIG)
    except Exception as e:
        print(f"数据库连接异常: {e}")
        return None


@app.route('/api/user/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # 基础校验
    if password == "" or password is None:  # 对应测试用例中的 "" -> "密码不能为空"
        return jsonify({"code": 400, "message": "密码不能为空"}), 400
    if len(password) < 6:  # 对应测试用例中的 "123" -> "密码长度不能少于6位"
        return jsonify({"code": 400, "message": "密码长度不能少于6位"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"code": 500, "message": "数据库连接失败，请检查MySQL服务"}), 500

    try:
        with conn.cursor() as cursor:
            # 查重
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({"code": 400, "message": "用户名已存在"}), 400

            # 写入数据库
            sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, password, email))
            conn.commit()
            user_id = cursor.lastrowid
            print(f">>> [MockLog] 成功入库: ID={user_id}, User={username}")
            return jsonify({"code": 0, "data": {"user_id": user_id}})
    except Exception as e:
        conn.rollback()  # 出错回滚
        print(f">>> [MockLog] 数据库操作失败: {e}")
        return jsonify({"code": 500, "message": str(e)}), 500
    finally:
        conn.close()


@app.route('/api/user/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if not user or user['password'] != password:
                return jsonify({"code": 401, "message": "密码错误或用户不存在"}), 401
            token = f"mock_token_{user['id']}"
            return jsonify({"code": 0, "data": {"token": token, "username": username}})
    finally:
        conn.close()


@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    auth = request.headers.get('Authorization', '')
    user_id = auth.split('_')[-1] if '_' in auth else None
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user: return jsonify({"code": 401, "message": "未登录"}), 401
            return jsonify({"code": 0, "data": {"username": user['username'], "email": user['email']}})
    finally:
        conn.close()





if __name__ == '__main__':
    app.run(port=5000, debug=True)