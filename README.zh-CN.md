# GCW

把经过授权的线上网站恢复为可在本地运行、可以部署、并且有证据可核验的项目。

<p align="center">
  <a href="./README.md">English</a> · <strong>简体中文</strong>
</p>

<img src="./assets/banner.webp" alt="GCW — 以证据驱动的网站恢复" width="100%">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

GCW 是 Gao Copy Website 的缩写。它是一套 Agent Skill 和工具脚本，适合处理一种很具体的情况：网站所有者丢失了源码，但公开生产站点仍然在线。

GCW 不会把浏览器里的压缩产物冒充成原始源码。它会区分哪些事实直接来自生产环境，哪些信息只能部分确认，哪些内容仍是推断。最后得到的不只是一份能运行的项目，还包括可复查的证据和验证结果。

## GCW 能恢复什么

- 公开路由、HTML、样式、脚本、字体、图片、音频、模型和 Shader 文本
- DOM、Canvas、WebGL、WebGPU、Worker、iframe 和媒体渲染面
- 时间、鼠标、滚动、视口、主题、Storage 与界面状态产生的输入
- 桌面端和移动端的成对截图，以及可量化的图像差异
- 静态部署行为、路由 Smoke Test 和 GitHub Actions 截图回归

登录后内容、私有服务端逻辑、原始注释、Git 历史和凭证不属于恢复范围。

## 三种恢复层级

| 层级 | 适用情况 | 结果 |
|---|---|---|
| `ARTIFACT_REPLAY` | 公开生产产物仍能在本地运行 | 保持字节和行为的基线，用作视觉对照标准 |
| `PIPELINE_REPLAY` | 已经能还原渲染图和运行时连接关系 | 重建后的 WebGL 或应用管线 |
| `EDITABLE_REBUILD` | 目标是获得长期可维护的源码 | 可读组件，并持续和已验证基线对照 |

<img src="./assets/features.webp" alt="GCW 工作流：公开证据、恢复、验证与部署" width="100%">

GCW 通常先建立 Artifact Replay。有了稳定的对照标准，后续可编辑重构才不容易越改越偏。

## 快速开始

### 1. 安装两个联动 Skills

使用 GCW 执行完整的高保真复刻流程前，先安装两个专业分析 Skills：

```bash
npx skills add https://github.com/lixiaolin94/skills/tree/main/web-shader-extractor
npx skills add zanwei/design-dna
```

`web-shader-extractor` 负责 Canvas、WebGL、WebGPU、Shader 和渲染管线取证；`design-dna` 负责字体、间距、配色、布局、响应式和视觉效果分析。GCW 自带的盘点与对比脚本可以独立运行，但完整的创意网站复刻流程需要这两个 Skills。

如果你的 Agent 使用自定义 Skills 根目录，请把两个文件夹安装到对应位置。本工作区固定使用单数形式的 `.agent/skills`；如果安装器建议使用 `.agents`，应取消自动安装并手动放入 `.agent/skills`，不要建立桥接目录。

### 2. 安装 GCW

把本仓库作为唯一源码，然后用目录联接或符号链接安装到 Agent 的 Skill 目录，文件夹名称保持为 `gcw`。

Windows PowerShell：

```powershell
New-Item -ItemType Junction `
  -Path "D:\your-workspace\.agent\skills\gcw" `
  -Target "D:\path\to\GCW"
```

macOS 或 Linux：

```bash
ln -s /path/to/GCW /path/to/your-workspace/.agent/skills/gcw
```

安装后可以这样调用：

```text
使用 $gcw，把这个经过授权的生产网站恢复为经过验证的本地项目：https://example.com/
```

### 3. 建立证据工作区

```powershell
New-Item -ItemType Directory D:\work\site-recovery
python scripts\init_reconstruction.py D:\work\site-recovery `
  --url https://example.com/
```

GCW 会在目标项目中建立 `.gcw/`，用于保存运行状态、Known Gaps、QA 场景、截图、Manifest 和报告。已有证据不会被静默覆盖。

### 4. 盘点公开网站

```powershell
npm install
npm run install:browser
node scripts\site_inventory.mjs `
  --url https://example.com/ `
  --out D:\work\site-recovery\.gcw\evidence\network\site-inventory.json
```

归档资源前先检查盘点结果。需要移除查询参数中的敏感信息，并把抓取范围限制在已经授权的站点源内。

## 跨 Agent 使用

只要 Agent 能读取 `SKILL.md`、执行 Python 和 Node.js，并且能找到联动 Skills，就可以编排 GCW 的完整流程。GCW 的核心脚本也能脱离 Agent 单独运行，因此其他自动化系统可以直接调用脚本。

完整流程必须联动 `web-shader-extractor` 和 `design-dna`。`browser-qa` 属于可选增强，因为 GCW 已自带 Playwright 截图、路由 Smoke Test 和数值图像 Diff。运行 `npm run check` 可以同时检查两个必需 Skill 的路径、Playwright、Chromium、Pillow 和可选的 Blender。目录联接或符号链接只是安装方式，多个 Agent 仍然读取同一份项目源码。

## 视觉验证

在配置文件中定义源站和候选站的成对场景，然后运行：

```powershell
node scripts\capture_compare.mjs `
  --config D:\work\site-recovery\.gcw\capture-scenarios.json `
  --output D:\work\site-recovery\.gcw\results

python scripts\batch_image_diff.py `
  D:\work\site-recovery\.gcw\results `
  --diff-dir D:\work\site-recovery\.gcw\results\diff
```

截图工具会使用两个独立浏览器进程，并同步随机种子、Playwright Clock、视口、DPR 和页面就绪条件。GPU 驱动、视频、跨域 iframe、Worker 和合成器时间仍可能造成动态误差。这些区域应当单独记录，不能通过放宽所有阈值来掩盖。

## 工具清单

| 脚本 | 用途 |
|---|---|
| `init_reconstruction.py` | 建立非破坏性的证据工作区 |
| `site_inventory.mjs` | 盘点公开路由、资源、字体和渲染面 |
| `capture_compare.mjs` | 在一致条件下截取源站和候选站状态 |
| `batch_image_diff.py` | 输出指标、Diff 图、Markdown 和 JSON 报告 |
| `route_smoke.py` | 检查公开预览路由与关键文字 |
| `blender_replace_text.py` | 根据参考模型边界生成新的 GLTF 或 GLB 文字 |
| `install_ci.py` | 安装 GCW Runner 和 GitHub Actions 截图门禁 |

完整工作流见 [SKILL.md](./SKILL.md)。[references](./references/) 中整理了恢复层级、Gate、QA 场景和依赖说明。

## 环境要求

- Python 3.10 或更高版本
- Node.js 20 或更高版本
- Pillow，用于图像 Diff
- Playwright 和 Chromium，用于资源盘点和截图
- `web-shader-extractor` 和 `design-dna`，用于完整的高保真复刻流程
- Blender 4.x 或更高版本，只在替换 3D 文字时需要

```powershell
python -m pip install -r requirements.txt
npm install
npm run install:browser
npm run check
```

## 验证方式

GCW 会把工具验证和网站验证分开。仓库会检查运行依赖、脚本语法、证据目录、路由 Smoke Test、图像 Diff 报告、CI 安装器和可选的 Blender 路径。

每个恢复项目仍需单独定义就绪条件、交互矩阵、视觉阈值和 Known Gaps。GCW 工具检查通过，不代表某个具体网站已经恢复完成。

## 安全与边界

GCW 只用于你拥有或明确获得授权的网站。

- 不绕过登录、密码、付费墙或其他访问控制。
- 不提交生产 Bundle 或配置中暴露的凭证。
- 精确生产产物与可编辑近似实现分开保存。
- 使用 `SOURCE`、`PARTIAL`、`GUESS` 标记事实等级。
- 仍有 P0、P1 或 P2 问题时，不应宣布恢复完成。

## 致谢

GCW 会调用两个 Companion Skills 完成专业分析：

- [web-shader-extractor](https://github.com/lixiaolin94/skills/tree/main/web-shader-extractor)，由 [lixiaolin94](https://github.com/lixiaolin94) 维护，负责 WebGL、WebGPU、Canvas、Shader 和渲染管线取证。
- [design-dna](https://github.com/zanwei/design-dna)，由 [zanwei](https://github.com/zanwei) 维护，负责设计 Token、视觉风格和特效的结构化提取。

感谢两位维护者和所有贡献者公开这些 Skills。GCW 只把它们作为联动工作流调用，没有把上游源码打包进本仓库。两个上游项目均采用 MIT License，具体条款和更新以各自仓库为准。

## 许可证

GCW 使用 [MIT License](./LICENSE)。
