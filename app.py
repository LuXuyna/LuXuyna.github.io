from flask import Flask, render_template, request, jsonify, send_from_directory
import pymysql
import datetime
import json
import os

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'Lu',        # 你在宝塔创建的数据库用户名
    'password': '7wSpfA8AXByr6TTe',      # 你在宝塔设置的密码
    'database': 'experiment', # 你在宝塔创建的数据库名
    'charset': 'utf8mb4'
}

# 创建数据表
def init_db():
    """初始化数据库表"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建实验数据表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiment_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            participant_id VARCHAR(100) NOT NULL,
            group_name VARCHAR(50),
            explanation_style VARCHAR(50),
            age INT,
            gender VARCHAR(10),
            government VARCHAR(100),
            gov_exp VARCHAR(10),
            ai_exp VARCHAR(10),
            answers JSON,
            post_questionnaire JSON,
            start_time DATETIME,
            end_time DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 数据库初始化成功！")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 提供 cases.json 文件
@app.route('/cases.json')
def serve_cases():
    """直接返回cases.json文件内容"""
    try:
        return send_from_directory('.', 'cases.json')
    except Exception as e:
        print(f"❌ 读取cases.json失败: {e}")
        # 如果文件不存在，返回模拟数据
        mock_cases = [
            {
                "案件编号": "C01", 
                "领域": "民生保障", 
                "案件名称": "老旧小区改造信访件",
                "简要案情描述": "某小区居民多次反映老旧小区改造进度缓慢，涉及300余户居民",
                "群众人数": 320,
                "网络舆情热度（分）": 85,
                "历史信访记录次数（次）": 15,
                "风险评估分数（分）": 75,
                "风险等级": "高",
                "是否临近敏感时间节点": "是",
                "标准处理建议": "列入重点督办名单"
            }
        ]
        return jsonify(mock_cases)

# 提交数据接口
@app.route('/submit', methods=['POST'])
def submit():
    """接收前端提交的实验数据"""
    try:
        data = request.get_json()
        
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO experiment_results 
        (participant_id, group_name, explanation_style, age, gender, government, 
         gov_exp, ai_exp, answers, post_questionnaire, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (
            data.get('participantId'),
            data.get('group'),
            data.get('explanationStyle'),
            data.get('demographics', {}).get('age'),
            data.get('demographics', {}).get('gender'),
            data.get('demographics', {}).get('government'),
            data.get('demographics', {}).get('govExp'),
            data.get('demographics', {}).get('aiExp'),
            json.dumps(data.get('answers', []), ensure_ascii=False),
            json.dumps(data.get('postQuestionnaire', {}), ensure_ascii=False),
            data.get('startTime'),
            data.get('endTime')
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'message': '数据保存成功'})
    
    except Exception as e:
        print(f"❌ 提交数据错误: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 查看数据接口（可选，方便调试）
@app.route('/view-data')
def view_data():
    """查看已提交的数据（可选）"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM experiment_results ORDER BY created_at DESC LIMIT 10")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)