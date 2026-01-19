---
title: git常用操作汇总.md
date: 2026-01-18
slug: git-learning
---

## 1 git rebase
- 文档 ：<a href="https://git-scm.cn/docs/git-rebase" target="_blank">https://git-scm.cn/docs/git-rebase</a>
### 将next基础上的topic分支，rebase到master
git rebase --onto master next topic

这是使用 `rebase --onto` 将基于一个分支的主题分支移植到另一个分支的方法，假装您从后者分支又分叉了主题分支。

首先，假设您的 `topic` 分支基于 `next` 分支。例如，`topic` 中开发的功能依赖于 `next` 中的某些功能。

```text
o---o---o---o---o---o  master
         \
          o---o---o---o---o---o  next
                               \
                                o---o---o  topic
```
我们想让 topic 分支从 master 分支分叉；例如，因为 topic 所依赖的功能已合并到更稳定的 master 分支。我们希望我们的树看起来像这样：

## 2 git format-patch
- 文档 ：<a href="https://git-scm.com/docs/git-format-patch/zh_HANS-CN" target="_blank">https://git-scm.com/docs/git-format-patch/zh_HANS-CN</a>

使用参数：--subject-prefix='PATCH RESEND net-next' -v6 -3，实现如下效果
[PATCH RESEND net-next v6 0/3] Add DWMAC glue driver for Motorcomm YT6801