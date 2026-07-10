# 国产化部署约束(ADR-0007)

## 状态

Accepted。V2 grilling Q6 落定。

## 背景

赛题明文两条红线,任一不满足即判 0 分:

1. "软件需部署在自主指令系统 LoongArch 架构 + 麒麟高级服务器版运行(不满足该要求视为 0 分)。"
2. "数据库需采用国产数据库。"

`ADR-0001` 已把 AI 算力全走云端,砍掉本地大模型这一最大兼容性黑洞。但其余常驻进程链(Python + Redis + KingbaseES + Nginx)在 LoongArch/麒麟上的可得性与容量,仍需逐项钉死,否则部署阶段随时卡死、评审现场跑不起来。

`CONTEXT.md` 原风险表只写"龙芯环境不兼容 → 尽早搭建麒麟测试环境",缓解是姿态而非落地步骤。本 ADR 把姿态固化成可执行约束。

## 决策

### 一、运行方式:裸部署优先,Docker 为可选非推荐路径

四核 8GB 不适合五个容器各跑一套 runtime。**KingbaseES 宿主安装**(麒麟官方 loongarch64 安装包),**FastAPI 以 systemd 裸跑**,前端 Nginx 宿主跑静态。Docker 仅作为文档列出的可选部署方式,不作为推荐路径。

赛题要的是"在麒麟上跑得起来",不是"容器化好看"。裸部署降低一层 runtime 间接性、便于排障、便于现场演示 `systemctl status` 全绿。

### 二、内存预算(写死并实测校准)

| 组件 | 预算 |
|------|------|
| KingbaseES | ~3 GB |
| Redis | ~0.5 GB |
| FastAPI 主服务 | ~1.5 GB |
| (已并入 FastAPI 主服务) | - GB |
| Nginx + 前端静态 | ~0.3 GB |
| 系统 + 召回/解析峰值 | ~1.7 GB |
| 合计 | ≤ 8 GB |

预算写入 `deploy/部署架构.md`,各项实测后更新。任一组件超预算即在本 ADR 记一条 Consequences 并调预算。

### 三、loongarch64 依赖可得性清单

新建 `deploy/依赖可得性清单.md`,逐行记组件 / 版本 / 获取方式(麒麟源 / 官方 loongarch wheel / 源码编译)/ 备选 / 实测状态。关键项:

- **Python**:麒麟自带源 3.9 或 3.12,看虚机给什么。或 loongarch wheels。
- **Python**:麒麟自带源(3.9 或 3.12,看虚机给什么)或 loongarch wheels。
- **KingbaseES V8R6**:麒麟版安装包(国产数据库,赛题要求)。
- **Redis**:麒麟源 apt/yum 或源码编译。
- **docling**:loongarch64 wheel 缺失时降级纯 Python(pdfplumber + python-docx 统揽,赛题只要 PDF/DOC 解析)。见 `ADR-0003`。
- **pdfplumber / python-docx**:需验证 loongarch64 wheel 或纯 Python 可装。
- **ECharts / 前端**:纯 JS,无障碍。

这条清单是评委现场能否一键跑起来的命门。

### 四、麒麟虚机冒烟 = day3 前必须过的关卡

虚机到手(Q6 申请已提交),第一时间不是写业务代码,而是冒烟:

- KingbaseES 起库、JDBC 连得上;
- FastAPI 起得来、连得上库;
- 前端静态可访问。

冒烟过了再往里塞业务。冒烟本身写进 21 天版计划的 day3 之前。**绝不让麒麟验证拖到 day19 部署日才暴露问题。**

### 五、无人值守安装

`install.sh` 做到:从软件源装依赖 → 起服务 → 跑数据初始化,**全程无人值守**。

依赖**绝不**打进安装包(赛题明文禁止把 `site-packages` / `node_modules` 压进包),依赖写在 requirements/配置里,安装或部署时从软件源(PyPI/npm/apt 等)网络下载安装,以大幅减小包体积。

这条写进 `docs/提交清单.md`「安装部署」条目的验收标准。

## Considered Options

- **A 全 Docker 五容器**:漂亮但 8GB 紧张,且 loongarch64 镜像可得性逐项未验,风险叠加。
- **B 全裸部署(采纳为主)**:KingbaseES 宿主 + systemd 裸跑,容量最省、排障最直接、`systemctl status` 演示最直观。
- **C 混合**:KingbaseES / Nginx 宿主,其余容器——可选,作为 `deploy/部署架构.md` 里列出的备选路径之一。

## Consequences

- 新建 `deploy/依赖可得性清单.md`、`deploy/部署架构.md`,并随冒烟实测更新。
- 21 天版计划在 day3 之前插入「麒麟虚机冒烟」关卡,未过不进业务。
- AI 服务 `docling` 依赖可能的降级路径(pdfplumber + python-docx)需在解析模块保留开关。
- `install.sh` 与打包脚本须从软件源拉依赖,禁打包第三方依赖目录。
- 本 ADR 的容量约束继承自 `ADR-0001`(已排除本地大模型 / PyTorch),二者口径一致。
