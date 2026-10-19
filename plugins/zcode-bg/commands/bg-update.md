---
description: 更新 zcode-bg 到最新版（下载 Release；补丁启用时热替换面板脚本，重启生效）
---

运行 `python "${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py" update`（可加 --force 强制重下）。

- 若输出“已热替换注入的面板脚本”：告知用户重启 ZCode 生效；插件包本体（命令/文档）
  建议在客户端插件市场里同步更新。
- 若输出“当前未启用主题补丁”：说明需要完全退出 ZCode 后，用新下载目录里的
  bg_patch.py 执行 apply（脚本会打印具体路径）。
- 说明：该命令会从 GitHub 下载 Release 包，不发送任何本地数据。
