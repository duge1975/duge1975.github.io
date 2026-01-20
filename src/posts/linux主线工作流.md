---
title: linux主线工作流
date: 2026-01-20
slug: linux-mainline
---
## 1 linxu相关文档
官方文档大全，包含内核主线、驱动等文档：[https://www.kernel.org/doc/](https://www.kernel.org/doc/)

内核的中文文档：[https://docs.linuxkernel.org.cn/](https://docs.linuxkernel.org.cn/)

关于提交PATCH的文档：[submitting-patches.rst](https://www.kernel.org/doc/html/latest/process/submitting-patches.html)

### 一些相关参考
中科大Linux用户协会文档：[https://101.lug.ustc.edu.cn/](https://101.lug.ustc.edu.cn/)

## 2 linux主线支持推进的注意事项
linux上游需要clock、pinctrl、reset的dt-bindings和驱动的支持，然后再接受dts