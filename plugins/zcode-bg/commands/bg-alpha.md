---
description: 微调单个界面元素的透明度（免重启），如 surface=0.5
argument-hint: [键=数值 ...] 或 --reset
---

运行 `python "${ZCODE_PLUGIN_ROOT}/scripts/bg_patch.py" hot alpha $ARGUMENTS`

可调键（v0.7 色调分离架构，深浅主题自适应）：
- background —— 工作区/root 底色
- card —— 工作区消息/文件卡片
- sidebar —— 左侧栏独立底色（JS 定位容器绘制）
- surface —— 分组小组件
- menu —— 右键菜单/弹层
- input —— 输入框
- overlay —— 整体压暗层

数值越小越透（0=全透，0.95=几乎不透明）。
文字难读时升 surface/input/card；壁纸太闷时降 background/sidebar/overlay。
注意：面板 GUI 的 localStorage 覆盖优先于这里；被遮蔽时让用户在面板点"全部恢复默认"。
