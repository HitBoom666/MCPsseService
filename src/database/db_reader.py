import sqlite3
from typing import Dict, List, Tuple
import os
from src.config.config_loader import ConfigLoader

class DatabaseReader:
    def __init__(self, db_name: str = None):
        """初始化数据库读取器
        
        Args:
            db_name (str): 数据库文件名，如果为None则使用配置中的名称
        """
        # 获取配置
        config = ConfigLoader()
        
        # 如果没有指定数据库名，使用配置中的名称
        if db_name is None:
            db_name = config.database_config.get('name', 'project_storage.db')
        
        # 设置数据库文件路径
        if config.database_config.get('path'):
            # 如果配置中有绝对路径，使用配置路径
            if os.path.isabs(config.database_config['path']):
                self.db_name = config.database_config['path']
            else:
                # 相对路径，从项目根目录开始
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                self.db_name = os.path.join(project_root, config.database_config['path'])
        else:
            # 如果配置中没有指定路径，使用默认路径
            current_dir = os.path.dirname(__file__)
            data_dir = os.path.join(current_dir, "Data")
            self.db_name = os.path.join(data_dir, db_name)
            
        self.conn = None
        self.cursor = None
        print(f"数据库路径: {self.db_name}")

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

    def get_all_tables(self) -> List[str]:
        """获取数据库中所有表的名称
        
        Returns:
            List[str]: 表名列表
        """
        if not self.conn:
            self.connect()
            
        try:
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                AND name NOT LIKE 'sqlite_%'
            """)
            tables = [table[0] for table in self.cursor.fetchall()]
            return tables
        except sqlite3.Error as e:
            print(f"获取表列表时出错: {e}")
            return []

    def get_table_columns(self, table_name: str) -> List[str]:
        """获取指定表的所有列名
        
        Args:
            table_name (str): 表名
            
        Returns:
            List[str]: 列名列表
        """
        if not self.conn:
            self.connect()
            
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in self.cursor.fetchall()]
            return columns
        except sqlite3.Error as e:
            print(f"获取表列信息时出错: {e}")
            return []

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

    def format_results(self, table_name: str, results: List[Tuple], columns: List[str] = None) -> str:
        """将查询结果转换为格式化的字符串
        
        Args:
            table_name (str): 表名
            results (List[Tuple]): 查询结果
            columns (List[str], optional): 列名列表，如果为None则自动获取
            
        Returns:
            str: 格式化后的字符串
        """
        if not results:
            return f"表 {table_name} 没有数据"
            
        # 如果没有提供列名，则获取列名
        if columns is None:
            columns = self.get_table_columns(table_name)
            
        # 计算每列的最大宽度
        col_widths = [len(col) for col in columns]
        for row in results:
            for i, value in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(value)))
                
        # 创建表头
        header = " | ".join(f"{col:{width}}" for col, width in zip(columns, col_widths))
        separator = "-+-".join("-" * width for width in col_widths)
        
        # 创建数据行
        rows = []
        for row in results:
            formatted_row = " | ".join(f"{str(value):{width}}" for value, width in zip(row, col_widths))
            rows.append(formatted_row)
            
        # 组合所有部分
        output = [
            f"\n表 {table_name} 的数据:",
            header,
            separator,
            *rows,
            f"\n共 {len(results)} 条记录"
        ]
        
        return "\n".join(output)

    def read_all_data(self) -> str:
        """读取所有表的所有数据
        
        Returns:
            str: 格式化后的所有表数据
        """
        all_output = []
        tables = self.get_all_tables()
        
        for table in tables:
            try:
                # 获取列名
                columns = self.get_table_columns(table)
                print(f"\n表 {table} 的列: {', '.join(columns)}")
                
                # 获取数据
                data = self.query_data(table)
                
                # 格式化并添加输出
                all_output.append(self.format_results(table, data, columns))
                    
            except sqlite3.Error as e:
                print(f"读取表 {table} 数据时出错: {e}")
                
        return "\n".join(all_output)
    
    def read_data_by_table(self, table_name: str) -> str:
        """读取指定表的所有数据
        
        Returns:
            str: 格式化后的所有表数据
        """
        try:
            # 获取列名
            table = table_name
            columns = self.get_table_columns(table)
            print(f"\n表 {table} 的列: {', '.join(columns)}")
                
            # 获取数据
            data = self.query_data(table)
                
            # 格式化并添加输出
            output = self.format_results(table, data, columns)
                    
        except sqlite3.Error as e:
            print(f"读取表 {table} 数据时出错: {e}")  
        return output

def main():
    """主函数，用于测试数据库读取功能"""
    reader = DatabaseReader()
    
    try:
        # 读取所有数据
        formatted_output = reader.read_all_data()
        print(formatted_output)
            
    finally:
        reader.disconnect()

if __name__ == "__main__":
    main() 