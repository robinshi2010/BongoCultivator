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
    old_dir = get_legacy_data_dir()
    
    # 如果路径相同，不需要迁移 (比如开发环境下)
    if os.path.abspath(new_dir) == os.path.abspath(old_dir):
        logger.info(f"数据目录未变更 ({new_dir})，无需迁移。")
        return

    logger.info(f"检查数据迁移: OLD={old_dir} -> NEW={new_dir}")
    
    files_to_migrate = ["user_data.db", "save_data.json"]
    
    migrated_count = 0
    try:
        # 确保新目录存在
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
            
        for filename in files_to_migrate:
            new_path = os.path.join(new_dir, filename)
            old_path = os.path.join(old_dir, filename)
            
            # 只有当新文件不存在，旧文件存在时才迁移
            # 避免覆盖用户在新版本下已经产生的进度
            if not os.path.exists(new_path) and os.path.exists(old_path):
                logger.info(f"正在迁移 {filename} ...")
                shutil.copy2(old_path, new_path)
                logger.info(f"成功迁移 {filename}")
                migrated_count += 1
            elif os.path.exists(new_path):
                logger.info(f"新位置已存在 {filename}，跳过迁移。")
                
    except Exception as e:
        logger.error(f"数据迁移过程中发生错误: {e}")
        
    if migrated_count > 0:
        logger.info(f"数据迁移完成，共迁移 {migrated_count} 个文件。")
    else:
        logger.info("无需执行数据迁移。")
