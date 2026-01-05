"""
数据库 Schema 自动迁移模块
Plan 46 补充: 解决版本更新后旧数据库结构不兼容的问题

SQLModel/SQLAlchemy 的 create_all() 只会创建新表，不会给已存在的表添加新列。
该模块在启动时检测并自动添加缺失的列，确保数据库结构与代码模型匹配。
"""
import sqlite3
from src.logger import logger


# 定义 player_status 表的所有列及其默认值
# 格式: (列名, SQLite类型, 默认值)
PLAYER_STATUS_COLUMNS = [
    ("id", "INTEGER PRIMARY KEY CHECK (id = 1)", None),
    ("layer_index", "INTEGER", "0"),
    ("current_exp", "INTEGER", "0"),
    ("money", "INTEGER", "0"),
    ("stat_body", "INTEGER", "10"),
    ("stat_mind", "INTEGER", "0"),
    ("stat_luck", "INTEGER", "0"),
    ("talent_points", "INTEGER", "0"),
    ("talent_json", "TEXT", "'{}'"),
    ("last_save_time", "INTEGER", "0"),
    ("last_login_time", "INTEGER", "0"),
    ("equipped_title", "TEXT", None),
    ("death_count", "INTEGER", "0"),
    ("legacy_points", "INTEGER", "0"),
    ("daily_reward_claimed", "TEXT", None),
    ("last_market_refresh_time", "INTEGER", "0"),
]


def get_existing_columns(conn, table_name: str) -> set:
    """获取表中已存在的列名"""
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = {row[1] for row in cursor.fetchall()}
    return columns


def migrate_player_status(conn):
    """
    检查并迁移 player_status 表
    为缺失的列添加定义
    """
    existing_columns = get_existing_columns(conn, "player_status")
    
    if not existing_columns:
        # 表不存在，将由 SQLModel create_all() 创建
        return 0
    
    added_count = 0
    
    for col_name, col_type, default_value in PLAYER_STATUS_COLUMNS:
        if col_name not in existing_columns:
            # 构建 ALTER TABLE 语句
            if default_value is not None:
                sql = f"ALTER TABLE player_status ADD COLUMN {col_name} {col_type.split()[0]} DEFAULT {default_value}"
            else:
                sql = f"ALTER TABLE player_status ADD COLUMN {col_name} {col_type.split()[0]}"
            
            try:
                conn.execute(sql)
                logger.info(f"数据库迁移: 添加列 player_status.{col_name}")
                added_count += 1
            except Exception as e:
                logger.warning(f"添加列 {col_name} 失败: {e}")
    
    return added_count


def run_schema_migrations(db_path: str) -> bool:
    """
    运行所有 schema 迁移
    :param db_path: 数据库文件路径
    :return: 是否有迁移执行
    """
    import os
    
    if not os.path.exists(db_path):
        logger.info("数据库文件不存在，跳过迁移 (将由 SQLModel 创建)")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        total_changes = 0
        
        # 迁移 player_status 表
        total_changes += migrate_player_status(conn)
        
        # 未来可以添加其他表的迁移...
        # total_changes += migrate_other_table(conn)
        
        conn.commit()
        conn.close()
        
        if total_changes > 0:
            logger.info(f"数据库 Schema 迁移完成，共更新 {total_changes} 项")
            return True
        else:
            logger.debug("数据库 Schema 已是最新，无需迁移")
            return False
            
    except Exception as e:
        logger.error(f"数据库迁移失败: {e}")
        return False
