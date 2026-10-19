---
description: 给 ZCode 桌面端应用壁纸与半透明主题（自动弹出进度窗口，退出 ZCode 后自动完成）
argument-hint: [壁纸图片路径] [subtle|balanced|immersive]
---

用户要应用背景主题。参数：$ARGUMENTS

执行流程：

1. 若参数里没有壁纸路径，先向用户确认用哪张图（本地路径）。
2. 若参数里没有档位，默认 balanced（subtle=含蓄 / balanced=平衡 / immersive=沉浸）。
3. 运行 `python "${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py" apply --wallpaper "<图>" --preset <档>`。
   - 若输出"已弹出进度窗口"：告知用户**完全退出 ZCode（托盘右键退出）**，窗口会自动完成安装；
     完成后重新打开 ZCode 即可。**完成前不要提前重开**（会中断 asar 改名步骤）。
   - 若直接输出五步成功：说明执行时 ZCode 已退出，让用户重开验证即可。
4. 用户重开后验证：壁纸、面板、状态条。不满意用 hot 命令或面板微调。
