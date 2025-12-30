# Plan 25: 接入 Supabase 实现云存档与账户系统 (Supabase Cloud Save)

## 问题描述 (Problem)
目前游戏仅支持本地存档，数据易丢失且无法跨设备同步。用户希望拥有账号系统（邮箱验证），以便留存数据，并在未来接收更新通知。

## 目标 (Goals)
1.  **账号体系**: 实现基于 Supabase 自带 Auth 的邮箱注册与登录功能。
2.  **云存档**: 将本地的 `save_data.json` (或核心数据) 同步到 Supabase 数据库。
3.  **UI入口**: 在设置菜单或主界面增加“账号/云同步”入口。

## 技术方案 (Solution)
*   **Backend SaaS**: Supabase (PostgreSQL + GoTrue Auth).
*   **Python Client**: 使用 `supabase` 官方库 (需 `pip install supabase`).

## 实施步骤 (Implementation Steps)

### 步骤 1: 环境搭建
*   在 `requirements.txt` 中添加 `supabase`.
*   在 `src/config.py` 或环境变量中配置 `SUPABASE_URL` and `SUPABASE_KEY`. (注意：客户端 Key 是安全的，但不应暴露 Service Role Key).

### 步骤 2: 封装 `AuthService`
*   创建 `src/services/auth_service.py`.
*   实现 `sign_up(email, password)`: 发送验证邮件.
*   实现 `sign_in(email, password)`: 获取 Session/Token.
*   实现 `get_user()`: 检查当前登录状态.

### 步骤 3: 数据库 Schema (Supabase 端)
*   你需要手动或通过脚本在 Supabase 创建表 `user_saves`:
    *   `id`: uuid (primary key)
    *   `user_id`: uuid (foreign key to auth.users)
    *   `save_data`: jsonb
    *   `updated_at`: timestamp
*   配置 RLS (Row Level Security) 策略，确保用户只能读写自己的存档。

### 步骤 4: 云存档逻辑 (`CloudSaveManager`)
*   **上传 (Upload)**: `upsert` 数据到 `user_saves` 表。
*   **下载 (Download)**: 登录成功后，查询最新的存档并覆盖本地（需提示用户确认）。
*   **自动同步**: 在关键节点（如关闭游戏、渡劫成功）尝试后台静默上传。

### 步骤 5: UI 实现
*   在 `SettingsWindow` 或右键菜单增加“云存档” Tab。
*   制作登录/注册表单 UI。
*   显示当前账号状态及最后同步时间。

### 步骤 6: 邮件通知 (Future)
*   收集到的 Email 存储在 Supabase Auth Users 中，后续可导出或通过 Edge Functions 发送更新邮件。

## 注意事项
*   网络请求应异步执行，避免阻塞 GUI 线程（使用 `QThread` 或 `asyncio`）。
*   处理网络失败的情况（弱网环境）。
