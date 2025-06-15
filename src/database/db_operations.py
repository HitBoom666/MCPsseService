import sqlite3
from typing import List, Tuple, Any
import os

class DatabaseManager:
    def __init__(self, db_name: str = "project_storage.db"):
        """初始化数据库管理器
        
        Args:
            db_name (str): 数据库文件名
        """
        # 确保Data目录存在
        data_dir = os.path.join(os.path.dirname(__file__), "Data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        # 设置数据库文件路径
        self.db_name = os.path.join(data_dir, db_name)
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接到数据库"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"成功连接到数据库: {self.db_name}")
        except sqlite3.Error as e:
            print(f"连接数据库时出错: {e}")

    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            print("数据库连接已关闭")

    def create_table(self, table_name: str, columns: List[Tuple[str, str]]):
        """创建新表
        
        Args:
            table_name (str): 表名
            columns (List[Tuple[str, str]]): 列定义列表，每个元素为(列名, 数据类型)
        """
        if not self.conn:
            self.connect()
            
        columns_def = ", ".join([f"{col[0]} {col[1]}" for col in columns])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        
        try:
            self.cursor.execute(query)
            self.conn.commit()
            print(f"表 {table_name} 创建成功")
        except sqlite3.Error as e:
            print(f"创建表时出错: {e}")

    def insert_data(self, table_name: str, data: List[Tuple[Any, ...]]):
        """插入数据到表中
        
        Args:
            table_name (str): 表名
            data (List[Tuple[Any, ...]]): 要插入的数据列表
        """
        if not self.conn:
            self.connect()
            
        # 获取列数
        placeholders = ", ".join(["?" for _ in data[0]])
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        
        try:
            self.cursor.executemany(query, data)
            self.conn.commit()
            print(f"成功插入 {len(data)} 条数据到 {table_name}")
        except sqlite3.Error as e:
            print(f"插入数据时出错: {e}")

    def query_data(self, table_name: str, conditions: str = None) -> List[Tuple]:
        """查询数据
        
        Args:
            table_name (str): 表名
            conditions (str, optional): WHERE条件语句
            
        Returns:
            List[Tuple]: 查询结果
        """
        if not self.conn:
            self.connect()
            
        query = f"SELECT * FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"
            
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"查询数据时出错: {e}")
            return []

def main():
    """主函数，用于测试数据库操作"""
    # 创建数据库管理器实例
    db = DatabaseManager()
    
    # 创建项目统计表
    project_columns = [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("项目名称", "TEXT NOT NULL"),
        ("项目简介", "TEXT NOT NULL"),
        ("项目投资金额", "REAL NOT NULL"),
        ("开始时间", "DATE NOT NULL"),
        ("结束时间", "DATE NOT NULL"),
        ("项目难点", "TEXT"),
        ("对接人", "TEXT"),
        ("项目执行情况", "TEXT"),
        ("项目进度", "TEXT")
    ]
    db.create_table("项目统计", project_columns)
    
    # 插入项目数据
    project_data = [
        (None, "临沂市污水处理厂升级改造项目", "提升污水处理能力，改善出水水质标准", 5000.0, "2024-01-01", "2024-12-31", "设备老化严重，需要在不影响生产的情况下进行改造", "张工", "正常进行中", "45%"),
        (None, "济南市自来水厂水质提升工程", "优化水处理工艺，保障居民用水安全", 3000.0, "2024-02-15", "2024-11-30", "水源水质波动大，需要增加预处理工艺", "李工", "正常进行中", "30%"),
        (None, "青岛市河道综合治理项目", "改善河道生态环境，提升城市景观", 8000.0, "2024-03-01", "2025-06-30", "河道淤泥处理难度大，周边居民区密集", "王工", "正常进行中", "20%"),
        (None, "烟台市城市管网改造工程", "更新老旧管网，提高供水效率", 6000.0, "2024-01-15", "2024-12-31", "地下管线复杂，需要精确定位", "赵工", "正常进行中", "60%"),
        (None, "潍坊市大气污染治理项目", "减少工业废气排放，改善空气质量", 4000.0, "2024-02-01", "2024-10-31", "工业废气成分复杂，处理难度大", "刘工", "正常进行中", "40%"),
        (None, "淄博市土壤修复示范工程", "治理污染土壤，恢复土地功能", 3500.0, "2024-03-15", "2025-03-14", "土壤污染类型多样，修复周期长", "孙工", "正常进行中", "15%"),
        (None, "济宁市农村污水处理项目", "建设农村污水处理设施，改善环境", 2500.0, "2024-01-20", "2024-09-30", "分散式处理难度大，运维成本高", "周工", "正常进行中", "50%"),
        (None, "泰安市饮用水源地保护工程", "保护水源地环境，确保供水安全", 2800.0, "2024-02-10", "2024-11-30", "水源地周边环境复杂，保护难度大", "吴工", "正常进行中", "35%"),
        (None, "威海市海洋环境治理项目", "治理海洋污染，保护海洋生态", 7000.0, "2024-03-01", "2025-02-28", "海洋环境复杂，监测难度大", "郑工", "正常进行中", "25%"),
        (None, "日照市工业废水处理升级项目", "提升废水处理能力，达标排放", 4500.0, "2024-01-10", "2024-12-31", "工业废水成分复杂，处理标准高", "钱工", "正常进行中", "55%"),
        (None, "德州市地下水修复工程", "治理地下水污染，恢复水质", 3200.0, "2024-02-20", "2025-01-19", "地下水污染范围大，修复周期长", "孙工", "正常进行中", "40%"),
        (None, "聊城市城市黑臭水体治理", "消除黑臭水体，改善城市环境", 3800.0, "2024-03-10", "2024-12-31", "水体流动性差，治理难度大", "李工", "正常进行中", "30%"),
        (None, "滨州市工业固废处理项目", "规范固废处理，实现资源化利用", 4200.0, "2024-01-25", "2024-11-30", "固废种类多，处理工艺复杂", "王工", "正常进行中", "45%"),
        (None, "菏泽市农村环境综合整治", "改善农村人居环境，提升生活品质", 2800.0, "2024-02-15", "2024-10-31", "农村环境问题多样，整治难度大", "张工", "正常进行中", "50%"),
        (None, "枣庄市矿区生态修复工程", "修复矿区生态环境，恢复植被", 5500.0, "2024-03-01", "2025-02-28", "矿区地形复杂，修复难度大", "赵工", "正常进行中", "25%"),
        (None, "东营市油田环境治理项目", "治理油田污染，保护生态环境", 6500.0, "2024-01-15", "2024-12-31", "油田污染类型特殊，治理难度大", "刘工", "正常进行中", "35%"),
        (None, "临沂市农村饮用水安全工程", "保障农村饮水安全，改善水质", 2200.0, "2024-02-01", "2024-09-30", "农村供水分散，管理难度大", "周工", "正常进行中", "60%"),
        (None, "济南市城市垃圾分类处理项目", "推广垃圾分类，实现资源回收", 4800.0, "2024-03-15", "2024-12-31", "垃圾分类意识薄弱，推广难度大", "吴工", "正常进行中", "40%"),
        (None, "青岛市工业废气治理工程", "控制工业废气排放，改善空气质量", 5200.0, "2024-01-20", "2024-11-30", "废气成分复杂，处理标准高", "郑工", "正常进行中", "45%"),
        (None, "烟台市海岸带生态修复项目", "修复海岸带生态，保护海洋环境", 5800.0, "2024-02-10", "2025-01-09", "海岸带环境脆弱，修复难度大", "钱工", "正常进行中", "30%")
    ]
    db.insert_data("项目统计", project_data)
    
    # 查询数据
    results = db.query_data("项目统计")
    print("\n项目统计查询结果:")
    for row in results:
        print(row)
    
    # 断开连接
    db.disconnect()

if __name__ == "__main__":
    main() 