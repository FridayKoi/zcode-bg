---
description: 给 ZCode 桌面端应用壁纸与半透明主题（无需参数，自动弹出进度窗口）
argument-hint: [壁纸图片路径] [subtle|balanced|immersive]
---

用户要应用背景主题。参数：$ARGUMENTS

执行流程：

1. **壁纸**：参数里有路径就用它；没有就用插件自带的默认壁纸（`assets/default-wallpaper.jpg`），
   不需要追问用户（想换图之后再在面板里换）。
2. **档位**：默认 balanced（subtle=含蓄 / balanced=平衡 / immersive=沉浸）。
3. **运行脚本**（插件根目录：优先用 `${ZCODE_PLUGIN_ROOT}`，为空时从插件安装目录定位 `scripts/bg_patch.py`）：
   `python "<插件根目录>/scripts/bg_patch.py" apply --preset balanced`
   （有自定义图时追加 `--wallpaper "<图>"`）
   - 若输出"已弹出进度窗口"：告知用户**完全退出 ZCode（托盘右键退出）**，窗口会自动完成安装；
     完成后重新打开 ZCode 即可。**完成前不要提前重开**（会中断 asar 改名）。
   - 若直接输出五步成功：说明执行时 ZCode 已退出，让用户重开验证即可。
4. 用户重开后验证：壁纸、工具栏调色板、面板、状态条。后续换图/调参直接用面板。
