# Issue tracker: GitHub

本项目的任务、缺陷、需求和 PRD 默认记录在 GitHub Issues 中。

仓库远端：

```text
git@github.com:lmj5201314love/Scania-APS.git
```

## 约定

- 创建 issue：使用 `gh issue create --title "..." --body "..."`
- 查看 issue：使用 `gh issue view <number> --comments`
- 列出 issue：使用 `gh issue list --state open`
- 评论 issue：使用 `gh issue comment <number> --body "..."`
- 添加或移除标签：使用 `gh issue edit <number> --add-label "..."` 或 `--remove-label "..."`
- 关闭 issue：使用 `gh issue close <number> --comment "..."`

在本仓库目录中运行 `gh` 时，优先让 `gh` 从 `git remote -v` 自动识别仓库。

## 当技能要求发布到 issue tracker

创建 GitHub issue。

## 当技能要求读取相关 ticket

使用 `gh issue view <number> --comments` 读取 issue 正文、评论和标签。
