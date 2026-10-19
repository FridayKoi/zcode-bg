---
description: 一键还原 ZCode 原版外观（自动弹出进度窗口，退出后自动完成）
---

1. 运行 `python "${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py" rollback`。
2. 若输出"已弹出进度窗口"：告知用户**完全退出 ZCode**，窗口会自动完成还原，然后重开。
   完成前不要提前重开。
3. 成功后重开确认界面恢复原样；状态条插件不受影响。
4. 解包目录会保留，不影响运行，下次 apply 会重新解包覆盖。
