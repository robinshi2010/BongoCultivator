import os
import sqlite3
from typing import List, Tuple
from sqlmodel import create_engine, Session, SQLModel, select, text
from src.utils.path_helper import get_user_data_dir
from src.logger import logger
from src.models import (
    PlayerStatus, PlayerInventory, MarketStock,
    ActivityLog, ItemDefinition, Recipe, Achievement, 
    EventDefinition, EventHistory, PlayerEvent, SystemMetadata
)

DB_FILE = os.path.join(get_user_data_dir(), "user_data.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

class DatabaseManager:
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = DATABASE_URL
        self.engine = create_engine(db_url)
        self._init_db()

    def get_session(self):
        return Session(self.engine)
        
    def _get_conn(self):
        # Legacy support for parts I haven't refactored yet or raw access
        return sqlite3.connect(DB_FILE)

    def _init_db(self):
        try:
            # Plan 46: 自动执行 Schema 迁移 (在 SQLModel 初始化之前)
            # 解决旧存档缺失新字段导致的问题
            from src.utils.schema_migration import run_schema_migrations
            run_schema_migrations(DB_FILE)
            
            SQLModel.metadata.create_all(self.engine)
            
            # Ensure PlayerStatus exists
            with self.get_session() as session:
                player = session.get(PlayerStatus, 1)
                if not player:
                    player = PlayerStatus(id=1)
                    session.add(player)
                    session.commit()
                    
            logger.info("数据库初始化完成 (SQLModel)")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")

    def insert_activity(self, timestamp: int, keys: int, mouse: int):
        """
        插入一条分钟级活动记录
        """
        try:
            with self.get_session() as session:
                log = ActivityLog(timestamp=timestamp, keys_count=keys, mouse_count=mouse)
                session.add(log)
                session.commit()
        except Exception as e:
            logger.error(f"保存活动记录失败: {e}")

    def get_activities_by_range(self, start_ts: int, end_ts: int):
        """
        查询指定时间范围内的活动记录
        Returns raw tuples (timestamp, keys, mouse) to match legacy interface expected by StatsWindow
        """
        try:
            with self.get_session() as session:
                statement = select(ActivityLog.timestamp, ActivityLog.keys_count, ActivityLog.mouse_count).\
                            where(ActivityLog.timestamp >= start_ts).\
                            where(ActivityLog.timestamp <= end_ts).\
                            order_by(ActivityLog.timestamp)
                results = session.exec(statement).all()
                return results
        except Exception as e:
            logger.error(f"查询活动记录失败: {e}")
            return []

    def get_aggregated_stats(self, start_ts: int, end_ts: int, group_by: str = 'hour'):
        """
        获取聚合统计数据 (Raw SQL for SQLite complexity with formatting)
        """
        valid_groups = {
            'hour': "%H",
            'day': "%Y-%m-%d",
            'date_hour': "%Y-%m-%d %H:00"
        }
        fmt = valid_groups.get(group_by, "%H")
        
        try:
            with self.get_session() as session:
                # Use raw SQL for date formatting convenience in SQLite
                sql = text(f"""
                    SELECT 
                        strftime('{fmt}', timestamp, 'unixepoch', 'localtime') as time_bucket,
                        SUM(keys_count), 
                        SUM(mouse_count),
                        COUNT(*)
                    FROM activity_logs_minute 
                    WHERE timestamp >= :start_ts AND timestamp <= :end_ts
                    GROUP BY time_bucket
                    ORDER BY time_bucket ASC
                """)
                result = session.exec(sql, params={"start_ts": start_ts, "end_ts": end_ts})
                return result.fetchall()
        except Exception as e:
            logger.error(f"统计查询失败 ({group_by}): {e}")
            return []

    def log_event(self, event_type: str, message: str, timestamp: int):
        """
        Record a significant game event.
        """
        try:
            with self.get_session() as session:
                log = PlayerEvent(timestamp=timestamp, event_type=event_type, message=message)
                session.add(log)
                session.commit()
        except Exception as e:
            logger.error(f"Failed to log event: {e}")

    def get_recent_events(self, limit: int = 50):
        """
        Get recent events for display.
        """
        try:
            with self.get_session() as session:
                statement = select(PlayerEvent).order_by(PlayerEvent.timestamp.desc()).limit(limit)
                return session.exec(statement).all()
        except Exception as e:
            logger.error(f"Failed to fetch events: {e}")
            return []

# Global instance
db_manager = DatabaseManager()
