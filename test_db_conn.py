import pymysql

# 1. 配置数据库信息（这就是“拨号盘”）
db_config = {
    "host": "127.0.0.1",  # 本地地址
    "port": 3306,  # MySQL 默认端口
    "user": "root",  # 用户名
    "password": "123",  # 替换为你安装时设定的密码
    "database": "test_db",  # 刚才建的数据库名
    "charset": "utf8mb4",
    # 这一行很重要：让返回的数据变成字典格式，方便读取
    "cursorclass": pymysql.cursors.DictCursor
}

try:
    # 2. 建立连接（像拨通电话）
    connection = pymysql.connect(**db_config)
    print("✅ 数据库连接成功！")

    with connection.cursor() as cursor:
        # 3. 执行 SQL（像在电话里下达指令）
        sql = "SELECT VERSION()"  # 查询 MySQL 版本
        cursor.execute(sql)

        # 4. 获取结果
        result = cursor.fetchone()
        print(f"🔹 当前数据库版本: {result}")

finally:
    # 5. 关闭连接（像挂断电话，必须要做，否则占用资源）
    if 'connection' in locals():
        connection.close()
        print("🔌 连接已安全关闭。")