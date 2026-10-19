# zcode-bg

[中文](README.md) | [English](README.en.md)

给 [ZCode](https://zcode.z.ai) 桌面端换上**壁纸 + 半透明毛玻璃主题**，并且**一键可逆**。

> ⚠️ 第三方非官方插件。它会修改 ZCode 客户端的资源文件（方式见下文「原理」），
> 客户端每次更新后需要重新应用。请阅读「风险与免责」后再使用。

## 功能

- 🖼️ **壁纸**：任意本地图片，自动压缩到合适尺寸（最长边 2560px）
- 🎛️ **7 项独立透明度控制**：工作区底色 / 工作区卡片 / 侧栏 / 分组小组件 / 菜单弹层 / 输入框 / 整体压暗
- 🧩 **工具条调色板按钮**：直接嵌在 ZCode 工具栏，点开即面板，点面板外自动收起
- 🖱️ **滑杆 + 精确数值输入**：0 ~ 0.95，即时生效
- 🔗 **工作区+侧栏联动**：一根总控同步调两侧
- 💾 **5 个自定义预设槽位**：保存/应用，重启不丢
- 🌗 **深浅主题自适应**：每令牌独立色调（深色=暗玻璃、浅色=白玻璃），两种模式文字都可读
- ⚡ **CSS 热更新**：改参数约 2 秒生效，无需重启 ZCode
- 🧪 **取色探针**：点任意界面区域，输出 12 层祖先的类名与背景，遇到不听话的区域可自助定位
- 🧯 **纯净模式**：一键恢复 ZCode 原版外观（含隐藏壁纸），随时退出
- 🔒 **零遥测、零上传**：所有数据留在本机（唯一网络请求是 npx 拉取固定版本的官方 asar 工具）

## 原理（完全可审计）

ZCode 启动时优先加载 `resources/app.asar`，其次才是 `resources/app/` 目录。本插件：

1. 解包 `app.asar` 到 `resources/app/`（仅此一次）；
2. 在解包目录注入壁纸、主题 CSS 和设置面板脚本；
3. 把 `app.asar` 改名为 `app.asar.disabled`，让解包目录生效。

**它从不改写 app.asar 的内容**；回滚 = 把名字改回来。所有注入代码都是纯本地
CSS/JS，不含任何上报逻辑。

## 依赖

- Python 3.8+
- Node.js（用于 `npx @electron/asar`，版本固定为 4.3.1）

## 安装

### 方式一：本地目录（开发/自用推荐）

1. 把本仓库 `plugins/zcode-bg` 放到任意目录（或直接克隆整个仓库）；
2. 在 ZCode：**设置 → 插件 → 添加插件市场 → 选择目录**，选中含 `marketplace.json`
   的**仓库根目录**；
3. 在市场里找到 **zcode-bg** 并安装；
4. 按插件命令说明执行 `/bg-apply`（或让助手运行 `scripts/bg_patch.py apply`）。
   应用时要求 ZCode 已完全退出（托盘右键退出）。

### 方式二：直接运行脚本

```bash
python plugins/zcode-bg/scripts/bg_patch.py detect     # 只读检查（找安装位置/补丁状态）
python plugins/zcode-bg/scripts/bg_patch.py apply --wallpaper <图片路径> --preset balanced
python plugins/zcode-bg/scripts/bg_patch.py rollback   # 还原
```

`apply`/`rollback` 要求 ZCode 完全退出。

### 安装位置探测顺序

`--asar` 参数 → 环境变量 `ZCODE_ASAR` → 插件根目录 `config.json` 的 `asar_path`
→ 常见安装位置（`%LOCALAPPDATA%\Programs\ZCode`、`Program Files`、各盘符下的
`ZCode` / `App tools\ZCode`）→ 运行中的 ZCode 进程路径。都找不到时用 `--asar`
手动指定 `...\resources\app.asar`。

## 使用

面板入口在工具栏——**文件夹与上传按钮之间**那个调色板图标：

![工具栏调色板按钮](docs/images/toolbar-button.png)

- **面板**：点击调色板按钮 → 调滑杆/输入数值/选壁纸/存槽位；
- **对话命令**（安装后以 `/bg-` 开头）：`/bg-apply`、`/bg-rollback`、`/bg-status`、
  `/bg-preset`、`/bg-wallpaper`、`/bg-alpha`；
- **纯净模式**：面板「诊断」区按钮，恢复原版外观且保留你的参数，随时取回。

## 风险与免责

- 本插件**修改 ZCode 客户端资源文件**。客户端更新会覆盖注入内容，需要重新运行
  `apply`（面板和参数会保留）。
- 与 ZCode 官方无关；修改客户端软件**可能违反其用户协议**，使用风险自负。
- 界面令牌与 DOM 结构随版本变化。**实测版本：ZCode v3.15.3 (Windows)**。
  若某区域失效，用面板里的「取色探针」拿到类名链后提交 issue。
- 首次应用前**务必完全退出 ZCode**；`rollback` 随时可还原，`resources/app/`
  解包目录保留不影响运行。

## 卸载

1. 运行 `rollback`（或恢复 `app.asar.disabled` 为 `app.asar`）；
2. 在插件管理里卸载插件；
3. 可选：删除 `resources/app/` 解包目录。

## FAQ

**Windows 上提示找不到 `python3`？**
部分系统里 `python3` 指向微软商店的占位程序。让 `python3` 解析到真实 Python
（例如在 Python 安装目录创建 `python3.exe` 副本），或让助手用 `python` 运行脚本。

**浅色模式怎么调都奇怪？**
浅色主题 + 明亮壁纸的对比空间有限。插件为浅色模式提供白色柔光罩（overlay 滑杆），
建议 overlay ≥ 0.2；深色模式观感最佳。

**为什么 GUI 选图会自动压缩？**
浏览器 localStorage 配额约 5MB 且 base64 膨胀 33%，原始大图存不下。需要无损原图时，
通过命令换图：`hot wallpaper --path <原图路径>`（文件层直接引用，不经过 localStorage）。

**面板里的调整和命令调整哪个优先？**
面板（localStorage）优先；「全部恢复默认」→ 纯净模式会清除临时效果，你的滑杆值仍保留。

## 目录结构

```
marketplace.json              # 本地市场清单
plugins/zcode-bg/
├── .zcode-plugin/plugin.json # 插件清单
├── assets/zcode-bg-panel.js  # 设置面板（注入渲染层）
├── commands/*.md             # /bg-* 命令
├── skills/zcode-bg/SKILL.md  # 助手技能文档
└── scripts/bg_patch.py       # detect / apply / rollback / hot
scripts/release.py            # 打包 zip + sha256
```

## 致谢

- 解包目录注入 / `app.asar.disabled` 机制参考
  [zcode-background-diy](https://github.com/Badboy000000/zcode-background-diy)（MIT）。

## License

MIT — 见 [LICENSE](LICENSE)。
