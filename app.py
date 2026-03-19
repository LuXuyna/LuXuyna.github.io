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
    'user': 'Lu',
    'password': '7wSpfA8AXByr6TTe',
    'database': 'experiment',
    'charset': 'utf8mb4'
}

# 创建数据表 + 自动添加4列错题字段
def init_db():
    """初始化数据库表，并添加错题列"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建主表
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

        # 自动添加4道错题列（不存在才添加，安全）
        try:
            cursor.execute("ALTER TABLE experiment_results ADD COLUMN error_case_1 INT DEFAULT NULL")
        except: pass
        try:
            cursor.execute("ALTER TABLE experiment_results ADD COLUMN error_case_2 INT DEFAULT NULL")
        except: pass
        try:
            cursor.execute("ALTER TABLE experiment_results ADD COLUMN error_case_3 INT DEFAULT NULL")
        except: pass
        try:
            cursor.execute("ALTER TABLE experiment_results ADD COLUMN error_case_4 INT DEFAULT NULL")
        except: pass

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
    try:
        return send_from_directory('.', 'cases.json')
    except Exception as e:
        print(f"❌ 读取cases.json失败: {e}")
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

# 提交数据接口（已完全修复）
@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()

        # 读取4道错题结果（前端已传过来）
        error_case_1 = data.get('error_case_1')
        error_case_2 = data.get('error_case_2')
        error_case_3 = data.get('error_case_3')
        error_case_4 = data.get('error_case_4')

        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO experiment_results 
        (participant_id, group_name, explanation_style, age, gender, government, 
        gov_exp, ai_exp, answers, post_questionnaire, start_time, end_time,
        error_case_1, error_case_2, error_case_3, error_case_4
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (
            data.get('participant_id'),        # 已修复
            data.get('group_name'),
            data.get('explanation_style'),
            data.get('age'),
            data.get('gender'),
            data.get('government'),
            data.get('gov_exp'),
            data.get('ai_exp'),
            json.dumps(data.get('answers'), ensure_ascii=False),
            json.dumps(data.get('post_questionnaire'), ensure_ascii=False),
            data.get('start_time'),
            data.get('end_time'),
            error_case_1,                      # 已修复
            error_case_2,
            error_case_3,
            error_case_4
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'message': '数据保存成功'})
    
    except Exception as e:
        print(f"❌ 提交数据错误: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 查看数据接口
@app.route('/view-data')
def view_data():
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