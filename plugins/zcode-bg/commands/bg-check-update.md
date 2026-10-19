---
description: 检查 zcode-bg 是否有新版本（只访问 GitHub API，不上传任何数据）
---

运行 `python "${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py" check-update`。

把结果翻译成大白话告诉用户：当前版本、最新版本、是否有更新、Release 链接。
如果有更新，提示两种更新方式：`update` 子命令，或客户端插件市场更新。
说明：该命令只会向 GitHub 查询版本信息，不发送任何本地数据。
