# GCW

<div align="center">

[English](./README.md) · [简体中文](./README.zh-CN.md)

**以证据驱动的网站拆解、忠实复刻与创意重构。**

<p align="center">
  <img src="assets/readme/hero_collage.svg" alt="GCW——以证据驱动的网站重构" width="100%">
</p>

[![CI](https://github.com/idonafraid-create/GCW/actions/workflows/ci.yml/badge.svg)](https://github.com/idonafraid-create/GCW/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/github/v/release/idonafraid-create/GCW)](https://github.com/idonafraid-create/GCW/releases/latest)

</div>

GCW 是一套面向已授权公开网站的 Agent Skill 与工具集。它先从真实运行证据中提取路由、交互状态、响应式行为、素材和 GPU 渲染信息，再把这些证据整理成可审计的规格，最后进入实现。

最终成果可以是技术拆解、可运行回放，或具备清晰 Creative 后续路径的可编辑忠实复刻。

> 截图只有一帧。活的网站有千万帧。

GCW 就是 Gao Copy Website。对，名字就这么直白。

<p align="center">
  <img src="assets/readme/section-orchestration-zh.svg" width="100%" alt="证据编排：GCW 的核心差异">
</p>

截图只能记录一个画面。忠实复刻还必须解释页面在不同路由、断点、悬停和聚焦状态、加载过程、外部数据以及 WebGL 或 Shader 管线中的真实行为。

GCW 始终分开处理三件事：

- **证据**——实际观察到了什么。
- **忠实实现**——什么实现复现了已确认基线。
- **Creative**——基线通过评审后，哪些内容才允许创新。

这种分离让视觉相似度能够被验证，也避免把生产 Bundle 回放误当成可维护源码。

<p align="center">
  <img src="assets/readme/section-quickstart-zh.svg" width="100%" alt="快速开始">
</p>

### 1. 安装

把 GCW 克隆到稳定目录，再链接到 Agent 的 Skill 目录：

```powershell
git clone https://github.com/idonafraid-create/GCW.git D:\path\to\GCW
New-Item -ItemType Junction `
  -Path D:\path\to\.agent\skills\gcw `
  -Target D:\path\to\GCW
```

macOS 或 Linux 使用符号链接：

```bash
ln -s /path/to/GCW /path/to/.agent/skills/gcw
```

安装并检查工具环境：

```bash
npm ci
npm run install:browser
python -m pip install -r requirements.txt
npm run check
```

环境要求：Node.js 20+、Python 3.10+、通过 Playwright 安装的 Chromium，以及安装在 `.agent/skills/design-dna` 的 [design-dna](https://github.com/zanwei/design-dna)。所有 teardown 深度（包括 `minimal`）都强制 Design DNA。Canvas/WebGL/WebGPU/Shader 目标还须在 `.agent/skills/web-shader-extractor` 安装 [web-shader-extractor](https://github.com/lixiaolin94/skills/tree/main/web-shader-extractor)，并运行 `npm run check:gpu`。

### 2. 直接说明目标

例如：

```text
使用 GCW 分析这个已授权网站，只产出技术拆解。

使用 GCW 为这个已授权网站制作可编辑忠实复刻。

使用 GCW 制作可编辑忠实复刻，和我一起验收后，再继续已批准的 Creative 改造。
```

每次构建开始前，GCW 都会让你选择最终交付契约，不会替你默认选择：

| 选择 | Final deliverable | Editability target |
|---|---|---|
| **A** | 仅研究或可运行回放 | 可运行回放 |
| **B** | 可编辑忠实复刻 | 可维护源码 |
| **C** | 可编辑忠实复刻，验收后继续 Creative | 可维护源码 |

选择 B 不会永久失去 Creative。你可以在评审 Gate 明确升级为 C，以后仍可升级到 C，也可以从已验收的 B 交付中恢复 Creative。

## 你会得到什么

<p align="center">
  <img src="assets/readme/features_collage.svg" alt="GCW 的证据、重构与验证能力" width="100%">
</p>

根据任务范围，GCW 会留下：

- 与捕获证据关联的最终版 `SITE_SPEC.md`；
- 路由、交互、响应式、素材、网络和 GPU 清单；
- 原站与本地实现的视觉回归结果；
- 包含来源和已知差异的实现决策记录；
- B/C 交付所需的可维护源码入口、`REPLACE_GUIDE.md` 和可编辑性证据。

`ARTIFACT_REPLAY` 可以作为判断基线的 oracle，但不能作为 B/C 最终候选通过正式交付 Gate。

<p align="center">
  <img src="assets/readme/section-how-it-works-zh.svg" width="100%" alt="GCW 怎样工作">
</p>

```text
TEARDOWN_PHASE -> FAITHFUL_CLONE -> REVIEW_GATE -> CREATIVE_REBUILD
```

1. **观察**路由、状态、素材、渲染系统和复用边界。
2. **规格化**基线，并把结论标记为 source、partial 或 guess。
3. **复刻**：根据证据选择源码适配、干净重建或已授权生产恢复。
4. **验证**：在评审前检查构建、路由、响应式状态、运行时独立性和视觉差异。

需要生产恢复时，`MAINTAINABLE_REBUILD` 是把恢复证据转化为可维护源码的正式策略名称。

视觉系统分析由 [design-dna](https://github.com/zanwei/design-dna) 提供；GPU 目标还需要 [web-shader-extractor](https://github.com/lixiaolin94/skills/tree/main/web-shader-extractor)。它们的原生证据保持各自权威，GCW 只负责协调，不复制第二份结论。

<p align="center">
  <img src="assets/readme/section-docs-zh.svg" width="100%" alt="文档入口">
</p>

| 需求 | 从这里开始 |
|---|---|
| 完整 Agent 工作流 | [SKILL.md](./SKILL.md) |
| 复刻模式与 A/B/C 契约 | [references/clone-modes.md](./references/clone-modes.md) |
| 阶段与交付 Gate | [references/gates.md](./references/gates.md) |
| 网站规格 | [references/site-spec.md](./references/site-spec.md) |
| 恢复策略 | [references/recovery-tiers.md](./references/recovery-tiers.md) |
| 运行时独立性 | [references/runtime-independence.md](./references/runtime-independence.md) |
| 工具与脚本参考 | [references/tooling.md](./references/tooling.md) |
| QA 场景 | [references/qa-scenarios.md](./references/qa-scenarios.md) |

运行完整仓库 Gate：

```bash
npm run verify
```

## 安全与复用

GCW 只应用于你拥有、获得许可或得到明确授权复刻的网站。除非另行授权，私有内容和需登录内容不在范围内。代码、字体、图片、模型、数据和品牌必须分别核查复用权利。

GCW 会记录证据和不确定性，但不会把已部署产物推定为原始源码。

## 致谢

GCW 借鉴并使用了 [design-dna](https://github.com/zanwei/design-dna)、[web-shader-extractor](https://github.com/lixiaolin94/skills/tree/main/web-shader-extractor) 与 [Playwright](https://playwright.dev/) 的方法和工具。

<p align="center">
  <a href="https://github.com/oil-oil/beautify-github-readme">
    <img src="assets/readme/made-with-beautify.svg" width="300" alt="README made with beautify-github-readme">
  </a>
</p>

## 许可证

[MIT](./LICENSE)
