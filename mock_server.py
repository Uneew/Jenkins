# mock_server.py
from flask import Flask, request, jsonify

app = Flask(__name__)

# 模拟用户数据存储（内存中）
users_db = {}
next_user_id = 1

@app.route('/api/user/register', methods=['POST'])
def register():
    global next_user_id
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # 模拟密码长度校验
    if not password or len(password) < 6:
        return jsonify({"code": 400, "message": "密码长度不能少于6位"}), 400

    # 模拟用户名已存在
    if username in [u['username'] for u in users_db.values()]:
        return jsonify({"code": 400, "message": "用户名已存在"}), 400

    user_id = str(next_user_id)
    next_user_id += 1
    users_db[user_id] = {
        "user_id": user_id,
        "username": username,
        "password": password,
        "email": email
    }
    return jsonify({"code": 0, "message": "success", "data": {"user_id": user_id}})

@app.route('/api/user/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # 查找用户
    user = next((u for u in users_db.values() if u['username'] == username), None)
    if not user:
        return jsonify({"code": 401, "message": "用户不存在"}), 401
    if user['password'] != password:
        return jsonify({"code": 401, "message": "密码错误"}), 401

    return jsonify({"code": 0, "message": "success", "data": {
        "token": f"mock_token_{user['user_id']}",
        "username": username
    }})

@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    # 从 Header 中获取 Token（简化处理，直接解析 user_id）
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "message": "未登录"}), 401

    token = auth_header[7:]  # 去掉 "Bearer "
    # 模拟从 token 中提取 user_id（此处简化处理）
    try:
        user_id = token.split('_')[-1]
    except:
        return jsonify({"code": 401, "message": "无效的 Token"}), 401

    user = users_db.get(user_id)
    if not user:
        return jsonify({"code": 401, "message": "用户不存在"}), 401

    return jsonify({"code": 0, "message": "success", "data": {
        "user_id": user['user_id'],
        "username": user['username'],
        "email": user['email']
    }})

@app.route('/api/user/info', methods=['PUT'])
def update_user_info():
    # 同样从 Header 中解析 Token
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"code": 401, "message": "未登录"}), 401

    token = auth_header[7:]
    try:
        user_id = token.split('_')[-1]
    except:
        return jsonify({"code": 401, "message": "无效的 Token"}), 401

    user = users_db.get(user_id)
    if not user:
        return jsonify({"code": 401, "message": "用户不存在"}), 401

    data = request.json
    # 更新允许的字段
    if 'email' in data:
        user['email'] = data['email']
    # 可扩展其他字段

    return jsonify({"code": 0, "message": "success", "data": {
        "user_id": user['user_id'],
        "username": user['username'],
        "email": user['email']
    }})

@app.route('/api/user/logout', methods=['POST'])
def logout():
    # 登出只需返回成功（Mock 中无需真实销毁 Token）
    return jsonify({"code": 0, "message": "success"})

if __name__ == '__main__':
    # 允许外部访问，监听 5000 端口
    app.run(host='0.0.0.0', port=5000)