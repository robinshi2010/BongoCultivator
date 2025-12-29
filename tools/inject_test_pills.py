import sqlite3
import os

DB_PATH = 'user_data.db'

def inject_pills():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {os.path.abspath(DB_PATH)}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if items exist in definitions (to avoid FK errors if FK enabled, though SQLite default usually doesn't enforce unless turned on)
        # But let's just insert.
        
        items_to_add = [
            ('pill_gather_qi', 10),      # 聚气散 (加修为)
            ('pill_body_basic', 5),      # 壮骨丸 (加体魄)
            ('pill_break_found', 3),     # 筑基辅药 (突破用)
            ('pill_speed_wind', 5),      # 疾风散 (Buff)
            ('pill_detox_0', 5)          # 避毒珠 (Utility)
        ]

        print("开始注入测试丹药...")
        for item_id, count in items_to_add:
            # 使用 UPSERT 语法: 如果存在则增加数量，如果不存在则插入
            # 注意: 如果之前的逻辑是直接覆盖(excluded.count), 这里我们改成累加
            cursor.execute("""
                INSERT INTO player_inventory (item_id, count) 
                VALUES (?, ?)
                ON CONFLICT(item_id) DO UPDATE SET count = count + ?
            """, (item_id, count, count))
            
            print(f" -> 已添加: {item_id} x{count}")

        conn.commit()
        print("注入完成！请重启游戏查看储物袋。")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inject_pills()
