# -*- coding: utf-8 -*-
# Generate architecture diagram image for the docs
from PIL import Image, ImageDraw, ImageFont
import os

os.chdir(r"C:\Users\Administrator\Desktop\Zhihire-StarMap")
img_dir = os.path.join("docs", "images")
os.makedirs(img_dir, exist_ok=True)

# ---- Architecture Diagram ----
w, h = 800, 520
img = Image.new("RGB", (w, h), "white")
draw = ImageDraw.Draw(img)

colors = {
    "frontend": "#4A90D9",
    "backend": "#50B86C",
    "db": "#E67E22",
    "ai": "#9B59B6",
    "deploy": "#E74C3C",
    "box_bg": "#F0F4F8",
    "text": "#2C3E50",
    "line": "#95A5A6",
}

try:
    font18 = ImageFont.truetype("arial.ttf", 18)
    font14 = ImageFont.truetype("arial.ttf", 14)
    font11 = ImageFont.truetype("arial.ttf", 11)
except:
    font18 = ImageFont.load_default()
    font14 = font18
    font11 = font18

def draw_box(x, y, w, h, fill_color, border_color="#333", label="", sub="", radius=6):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=fill_color, outline=border_color, width=2)
    if label:
        bbox = draw.textbbox((0,0), label, font=font14)
        tx = x + (w - (bbox[2]-bbox[0])) // 2
        ty = y + (h - (bbox[3]-bbox[1])) // 2 - 6
        draw.text((tx, ty), label, fill="#fff", font=font14)
    if sub:
        bbox = draw.textbbox((0,0), sub, font=font11)
        tx = x + (w - (bbox[2]-bbox[0])) // 2
        ty = y + h - 22
        draw.text((tx, ty), sub, fill="rgba(255,255,255,180)", font=font11)

def draw_arrow(x1, y1, x2, y2):
    draw.line([(x1, y1), (x2, y2)], fill=colors["line"], width=2)
    # arrow head
    dx, dy = x2 - x1, y2 - y1
    angle = 0.3
    length = 10
    nx1 = x2 - length * (dx * 0.97 + dy * 0.23) / ((dx**2+dy**2)**0.5)
    ny1 = y2 - length * (dy * 0.97 - dx * 0.23) / ((dx**2+dy**2)**0.5)
    nx2 = x2 - length * (dx * 0.97 - dy * 0.23) / ((dx**2+dy**2)**0.5)
    ny2 = y2 - length * (dy * 0.97 + dx * 0.23) / ((dx**2+dy**2)**0.5)
    draw.polygon([(x2, y2), (nx1, ny1), (nx2, ny2)], fill=colors["line"])

# Title
draw.text((20, 12), "智聘星图 (Zhihire StarMap) — 系统架构图", fill=colors["text"], font=font18)

# Layer boxes
# Frontend
draw_box(60, 50, 680, 100, colors["frontend"], label="前端展示层 (Vue 3 + Element Plus + ECharts)", sub="TypeScript | Axios | Vue Router")
# Backend
draw_box(60, 190, 680, 130, colors["backend"], label="后端服务层 (FastAPI + Python 3.12)", sub="SQLAlchemy 2.0 Async | JWT Auth | Celery Background Tasks")
# Inside backend sub-boxes
sub_items = [("API 路由层", 80, 210, 140, 30), ("业务服务层", 240, 210, 140, 30),
             ("核心算法层", 400, 210, 140, 30), ("基础设施层", 560, 210, 140, 30)]
for lbl, sx, sy, sw, sh in sub_items:
    draw_box(sx, sy, sw, sh, "#27AE60", label=lbl, sub="")

# DeepSeek
draw_box(400, 340, 200, 55, colors["ai"], label="DeepSeek LLM API", radius=20)
draw_arrow(500, 340, 500, 320)

# Database
draw_box(130, 340, 250, 55, colors["db"], label="KingbaseES (人大金仓数据库)", radius=20)
draw_arrow(255, 340, 255, 320)

# Deployment
draw_box(60, 420, 680, 45, colors["deploy"], label="部署环境: 银河麒麟 V11 + LoongArch (龙芯)")
draw_arrow(255, 395, 255, 420)
draw_arrow(500, 395, 500, 420)

# Arrows: Frontend -> Backend
draw_arrow(400, 150, 400, 190)
draw.text((410, 160), "HTTP (REST API)", fill=colors["line"], font=font11)

img.save(os.path.join(img_dir, "architecture.png"))
print("Architecture diagram saved.")
