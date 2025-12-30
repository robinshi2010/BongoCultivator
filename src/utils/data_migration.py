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

    for source_dir in source_dirs:
        logger.info(f"尝试从 {source_dir} 迁移数据...")
        for filename in files_to_migrate:
            new_path = os.path.join(new_dir, filename)
            old_path = os.path.join(source_dir, filename)
            
            # 只有当新文件不存在，旧文件存在时才迁移
            if not os.path.exists(new_path) and os.path.exists(old_path):
                try:
                    logger.info(f"正在迁移 {filename} ...")
                    shutil.copy2(old_path, new_path)
                    logger.info(f"成功迁移 {filename}")
                    migrated_count += 1
                except Exception as e:
                    logger.error(f"迁移 {filename} 失败: {e}")
            elif os.path.exists(new_path):
                 pass # 已存在，忽略

    if migrated_count > 0:
        logger.info(f"数据迁移完成，共迁移 {migrated_count} 个文件。")
    else:
        logger.info("无需执行数据迁移或新位置已有数据。")
    return # 结束

# 保留旧函数签名以便兼容，下面是覆盖原逻辑
def check_and_migrate_data_legacy_backup():
    # Only for reference, overwritten by above logic logic integrated
    pass
