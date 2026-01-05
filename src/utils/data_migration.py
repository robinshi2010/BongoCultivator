import os
import shutil
import logging
from src.utils.path_helper import get_user_data_dir, get_legacy_data_dir
from src.logger import logger

def check_and_migrate_data():
    """
    检查旧版存储位置是否有数据。
    如果有，且新版位置为空，则迁移数据。
    """
    new_dir = get_user_data_dir()
    old_dir_legacy = get_legacy_data_dir()
    
    # 尝试查找上一版本的数据目录 (BongoCultivator -> BongoCultivation)
    old_dir_v1 = new_dir.replace("BongoCultivator", "BongoCultivation")
    
    source_dirs = []
    if os.path.exists(old_dir_v1) and old_dir_v1 != new_dir:
        source_dirs.append(old_dir_v1)
    if os.path.exists(old_dir_legacy) and old_dir_legacy != new_dir:
        source_dirs.append(old_dir_legacy)
        
    if not source_dirs:
        logger.info(f"未发现旧数据目录，无需迁移。")
        return
        
    files_to_migrate = ["user_data.db", "save_data.json"]
    migrated_count = 0
    
    # 确保新目录存在
    if not os.path.exists(new_dir):
        try:
            os.makedirs(new_dir)
        except Exception as e:
            logger.error(f"创建数据目录失败: {e}")
            return

    import sqlite3
    
    def get_db_progress(db_path):
        """返回 (layer_index, exp)，出错或空则返回 (-1, -1)"""
        if not os.path.exists(db_path): return -1, -1
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # 检查表是否存在
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='player_status'")
            if not cur.fetchone(): 
                conn.close()
                return -1, -1
            
            cur.execute("SELECT layer_index, current_exp, death_count FROM player_status WHERE id=1")
            row = cur.fetchone()
            conn.close()
            # Handle case where death_count column might be missing in very old DBs (though schema migration runs before this? No, migration runs first)
            # Actually schema migration runs in database.py init, which is AFTER this.
            # So selecting death_count might fail on old DBs.
            # We should wrap in try/except or select *
            if row: 
                return row[0], row[1], row[2]
        except Exception as e:
            # Try fallback for older schema without death_count
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("SELECT layer_index, current_exp FROM player_status WHERE id=1")
                row = cur.fetchone()
                conn.close()
                if row: return row[0], row[1], 0 # Default death_count 0
            except:
                pass
            # logger.warning(f"Check db progress failed for {db_path}: {e}")
            pass
        return 0, 0, 0 # 默认初始状态
        
    for source_dir in source_dirs:
        # logger.info(f"检查旧数据目录: {source_dir}")
        for filename in files_to_migrate:
            new_path = os.path.join(new_dir, filename)
            old_path = os.path.join(source_dir, filename)
            
            if not os.path.exists(old_path):
                continue
                
            do_migrate = False
            
            if not os.path.exists(new_path):
                do_migrate = True
            elif filename == "user_data.db":
                # 智能判断: 如果新档是初始状态，旧档有进度，则覆盖
                n_layer, n_exp, n_death = get_db_progress(new_path)
                o_layer, o_exp, o_death = get_db_progress(old_path)
                
                # 新档几乎没玩 (Layer0, Exp<100) 且 没死过 (Death=0)
                # 如果 Death > 0 说明是转世档，不能覆盖
                is_new_empty = (n_layer == 0 and n_exp < 100 and n_death == 0) or (n_layer == -1)
                is_old_valid = (o_layer > 0) or (o_layer == 0 and o_exp > 100) or (o_death > 0)
                
                if is_new_empty and is_old_valid:
                    logger.info(f"检测到新存档为空 (L{n_layer}), 旧存档有进度 (L{o_layer})，执行强制迁移覆盖。")
                    # 备份一下新档以防万一
                    try:
                        shutil.move(new_path, new_path + ".bak_empty")
                    except: pass
                    do_migrate = True
            
            if do_migrate:
                try:
                    logger.info(f"正在迁移 {filename} 从 {source_dir} ...")
                    shutil.copy2(old_path, new_path)
                    logger.info(f"成功迁移 {filename}")
                    migrated_count += 1
                except Exception as e:
                    logger.error(f"迁移 {filename} 失败: {e}")
            else:
                 pass # 已存在且有数据，跳过

    if migrated_count > 0:
        logger.info(f"数据迁移完成，共迁移 {migrated_count} 个文件。")
    else:
        logger.info("无需执行数据迁移或新位置已有数据。")
    return

# 保留旧函数签名以便兼容，下面是覆盖原逻辑
def check_and_migrate_data_legacy_backup():
    # Only for reference, overwritten by above logic logic integrated
    pass
