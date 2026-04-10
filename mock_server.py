from flask import Flask, request, jsonify

app = Flask(__name__)

# 模拟注册接口
@app.route('/api/user/register', methods=['POST'])
def register():
    data = request.json
    # 模拟业务逻辑：密码长度校验
    if len(data.get('password', '')) < 6:
        return jsonify({"code": 400, "message": "密码长度不能少于6位"}), 400
    # 模拟注册成功
    return jsonify({"code": 0, "message": "success", "data": {"user_id": "12345"}})

# 模拟登录接口
@app.route('/api/user/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == 'testuser' and data.get('password') == '123456':
        return jsonify({"code": 0, "data": {"token": "mock_token_xxxx"}})
    return jsonify({"code": 401, "message": "用户名或密码错误"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)