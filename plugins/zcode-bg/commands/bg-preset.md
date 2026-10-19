---
description: 免重启切换背景主题透明度档位
argument-hint: [subtle|balanced|immersive]
---

运行 `python "${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py" hot preset --name $ARGUMENTS`
（参数为空时问用户要哪档：subtle=含蓄 / balanced=平衡 / immersive=沉浸）。
成功后告知用户：约 2 秒内生效，无需重启；没变化说明热更新引擎还没重启激活过。
