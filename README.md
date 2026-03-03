Static Site Engineering Practice (based on Hugo)
这是一个基于 Hugo 引擎构建的自动化静态站点项目。本项目不仅是一个内容载体，更是对 自动化部署流水线 (CI/CD) 和 本地内容预处理工程化 的一次深度实践。

技术栈与工程亮点
引擎: 使用 Hugo 进行高性能静态页面生成。

自动化: 编写 PowerShell (ps1) 脚本实现了一键式工作流，涵盖了从内容同步、格式校准到自动化部署的全过程。

内容管理: 结合 Obsidian 构建了本地化知识库，通过脚本实现私有库与公开站点的单向同步。

CI/CD: 集成了 GitHub Actions（或 Git 脚本），确保内容更新的持续交付。

自动化脚本逻辑 (run-all.ps1)
为了解决跨平台内容迁移时的格式兼容与效率问题，我开发了配套的自动化脚本：

Sync & Clean: 从原始库提取最新内容至部署目录。

Format Transform: 自动处理 Obsidian 特有的 Markdown 语法，将其转换为标准的 Hugo 前置元数据（Front Matter）。

Build & Deploy: 调用 Hugo 引擎生成静态资源，并通过 Git 自动化指令推送到远程仓库。
