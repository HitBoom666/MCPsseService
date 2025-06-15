from db_operations import DatabaseManager

def create_sponge_city_table():
    """创建海绵城市平台URL存储表"""
    db = DatabaseManager()
    
    # 定义表结构
    table_columns = [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("page_name", "TEXT NOT NULL"),
        ("subpage_name", "TEXT"),
        ("url", "TEXT NOT NULL"),
        ("description", "TEXT"),
        ("remarks", "TEXT"),
        ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]
    
    try:
        # 创建表
        db.create_table("sponge_city_urls", table_columns)
        print("海绵城市平台URL存储表创建成功！")
        
        # 插入数据
        url_data = [
            (None, "首页", "登录页面", "http://159.75.69.88:9301/#/login", "平台登录入口", "需要账号密码", None, None),
            (None, "项目管理", "项目库管理", "http://159.75.69.88:9301/#/project/library", "项目信息管理", "包含项目基本信息", None, None),
            (None, "项目管理", "技术审查", "http://159.75.69.88:9301/#/project/designApproval", "项目技术审查", "包含设计审查信息", None, None),
            (None, "监测监控", "监测数据", "http://159.75.69.88:9301/#/monitoring/monitorData", "实时监测数据", "包含各类监测指标", None, None),
            (None, "监测监控", "数据分析", "http://159.75.69.88:9301/#/monitoring/monitorAnalyze", "数据统计分析", "包含数据分析结果", None, None),
            (None, "绩效考核", "总体成效", "http://159.75.69.88:9301/#/performanceEvaluation/constructionEffectiveness/constructionEffectiveness", "建设成效评估", "包含总体评估结果", None, None),
            (None, "绩效考核", "片区成效", "http://159.75.69.88:9301/#/performanceEvaluation/regionalAssessment/regionalAssessment", "片区评估", "包含片区评估结果", None, None),
            (None, "系统管理", "用户管理", "http://159.75.69.88:9301/#/sys/user/list", "用户权限管理", "包含用户信息管理", None, None),
            (None, "系统管理", "机构管理", "http://159.75.69.88:9301/#/sys/organizationManage/list", "组织机构管理", "包含机构信息管理", None, None),
            (None, "海绵一张图", "全域总览", "http://47.93.136.18:8098/#/", "全域监测总览", "包含全域监测数据", None, None),
            (None, "海绵一张图", "城市特征", "http://47.93.136.18:8098/#/urbanCharacteristics", "城市特征分析", "包含城市特征数据", None, None)
        ]
        
        # 插入数据
        db.insert_data("sponge_city_urls", url_data)
        print("URL数据插入成功！")
        
        # 查询并显示数据
        results = db.query_data("sponge_city_urls")
        print("\n海绵城市平台URL列表:")
        for row in results:
            print(row)
            
    except Exception as e:
        print(f"操作出错: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    create_sponge_city_table() 