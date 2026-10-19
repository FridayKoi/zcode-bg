---
description: 给 ZCode 桌面端应用壁纸与半透明主题（需要关闭 ZCode 后执行脚本）
argument-hint: [壁纸图片路径] [subtle|balanced|immersive]
---

用户要应用背景主题。参数：$ARGUMENTS

执行流程：

1. 若参数里没有壁纸路径，先向用户确认用哪张图（本地路径）。
2. 若参数里没有档位，默认 balanced，并向用户确认（subtle=含蓄 / balanced=平衡 / immersive=沉浸）。
3. 检查 `python "${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py" detect`：
   - 如果 `zcode_running` 为 true，告知用户：请完全退出 ZCode（托盘右键退出）。退出后本会话会中断，用户重开后说"继续"，再执行第 4 步。
   - 如果 `patch_enabled(app.asar.disabled)` 为 true，先提醒用户需要 rollback 才能换新主题。
4. ZCode 已关闭时执行 apply（壁纸路径 + --preset），确认五步全部 [成功]。
5. 指导用户重新打开 ZCode，查看效果。若壁纸太透/太实、文字难读，按 skills/zcode-bg/SKILL.md 的微调表调整 preset 或生成自定义 CSS 重新 apply。
