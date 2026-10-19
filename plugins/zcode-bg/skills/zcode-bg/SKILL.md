---
name: zcode-bg
description: 自定义 ZCode 桌面端的壁纸与半透明主题。当用户想换背景、调透明度、截图微调主题效果、或回滚外观时使用。
---

# zcode-bg 背景主题

用 `scripts/bg_patch.py` 给 ZCode 桌面端加壁纸和毛玻璃效果。机制：解包 app.asar 到
`resources/app/`，注入壁纸与 CSS，再把 app.asar 改名为 app.asar.disabled 使解包目录生效。
**从不修改 app.asar 内容；回滚 = 改名回来。**

## 关键路径

- 安装位置：脚本自动探测（--asar / ZCODE_ASAR / config.json 的 asar_path / 常见位置 / 运行中进程）
- 脚本：`${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py`
- 机制参考：https://github.com/Badboy000000/zcode-background-diy （MIT）

## 流程

1. **detect 先行**：`python <脚本> detect`，只读。关注 zcode_running、patch_enabled、
   statusbar_injected_in_unpacked（与状态条插件的共存检查）。
2. **意图优先于参数**：确认壁纸来源（本地图）、视觉方向、档位
   （subtle=含蓄 / balanced=平衡 / immersive=沉浸）。用户没图时先问，别自作主张。
3. **应用**：要求 ZCode 完全退出（托盘退出，关窗口不算）。执行
   `python <脚本> apply --wallpaper <图> --preset <档>`，五步全 [成功] 后让用户重开。
   注意：用户退出 ZCode 后本会话会中断——把下一步指令明确留给用户，等ta重开后说"继续"。
4. **截图微调**：让用户发截图，按现象调参：
   - 壁纸看不见 → 先查 app.asar.disabled 是否存在、index.html 里有没有样式表链接
   - 壁纸太暗/太闷 → 调低 background、panel、sidebar、overlay（换 immersive 或降 preset 值）
   - 文字/输入框难读 → 只升 input、card、popover、menu、toast、tooltip（+0.08~0.15）
   - 文字和壁纸打架 → 先升 overlay 0.04~0.08，别急着整体调不透明
   - 改了没反应 → 必须完全重启 ZCode
   微调 = 用 --css 提供手工改过的 CSS 重新 apply（先 rollback 再 apply）。
5. **升级注意**：ZCode 客户端更新前先 rollback；更新后重新 apply（脚本会自动重新解包新版 asar）。
   状态条插件同理需要重打（它的补丁在 asar 里）。

## 红线

- ZCode 运行中绝不执行 apply/rollback（文件被锁，脚本也会拒绝）。
- 不删除 app.asar.disabled（它是"补丁已启用"的标志）；不删除 dated 备份。
- 用户没授权不改主题；换图/换档都要先说一声。
