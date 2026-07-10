# deploy/ 部署目录

> 口径以 ADR-0007（裸部署优先）+ V4 Q9/Q20 为准；本目录是赛题交付物⑤所属位置。
> 本地大模型 / Docker 五容器 / 打包 site_packages 等路径已废弃。

## 文件清单

- `部署架构.md` — 裸部署拓扑 + 内存预算逐项写死 + systemd/Nginx 拓扑
- `依赖可得性清单.md` — loongarch64 各依赖的 wheel/驱动/版本可得性实验记录
- `install.sh` — 无人值守从软件源装依赖、起服务、跑数据初始化（待补）
- `部署文档.md` — 手工部署步骤（交付物⑤，待补）
- `optional/docker/` — Docker 可选非推荐路径（backend.Dockerfile / frontend.Dockerfile，待补）

## 核心原则

1. **裸部署优先**：KingbaseES 宿主安装；FastAPI 用 `systemd` 裸跑；
   Nginx 宿主跑静态。Docker 仅作可选非推荐路径（ADR-0007）。
2. **Redis 可选**：装得上就用，装不上 aiocache 内存缓存兜底（V4 Q20）。
3. **内存预算待实测**：day1-2 冒烟后回填（V4 Q9）。
4. **无人值守安装**：`install.sh` 从软件源（apt/PyPI/npm）装依赖，禁打包依赖目录。
5. **麒麟虚机冒烟关卡**：推 GitHub → 虚机 `git pull` 起骨架验证，
   未过不进业务（详见 ADR-0008 D3）。
