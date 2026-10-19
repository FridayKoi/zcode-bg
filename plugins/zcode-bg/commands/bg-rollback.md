---
description: 一键还原 ZCode 原版外观（回滚背景主题补丁）
---

用户要还原 ZCode 原版外观。执行：

1. 运行 `python "${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py" rollback`。
2. 若提示 ZCode 正在运行，告知用户先完全退出（托盘右键退出），退出后本会话中断，重开后说"继续回滚"，再执行第 1 步。
3. 成功后指导用户重新打开 ZCode，确认界面恢复原样。
4. 提醒：解包目录 `resources\app\` 会保留，不影响运行；状态条插件不受回滚影响。
