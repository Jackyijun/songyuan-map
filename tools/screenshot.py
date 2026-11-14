# -*- coding: utf-8 -*-
"""（可选）用无头浏览器给成品截图，并检查页面有没有脚本错误。

需要：pip install playwright && python -m playwright install chromium
  python tools/screenshot.py            截首屏节点（config.FIRST，1120 年）的浅色、深色与手机宽度
"""
import asyncio, os, sys
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "docs" / "index.html").as_uri()
OUT = ROOT / "build"
sys.path.insert(0, str(ROOT / "src"))
import config as C
FIRST = str(C.FIRST)                # 首屏节点，与 GEO.first 一致

async def main():
    OUT.mkdir(exist_ok=True)
    async with async_playwright() as p:
        kw = {"executable_path": os.environ["CHROMIUM_PATH"]} if os.environ.get("CHROMIUM_PATH") else {}
        b = await p.chromium.launch(**kw)
        errors = []
        for name, vp, scheme in [("desktop-light", (1440, 900), "light"), ("desktop-dark", (1440, 900), "dark"), ("phone", (400, 860), "light")]:
            ctx = await b.new_context(viewport={"width": vp[0], "height": vp[1]}, color_scheme=scheme)
            pg = await ctx.new_page()
            pg.on("pageerror", lambda e, n=name: errors.append((n, str(e))))
            await pg.goto(PAGE); await pg.wait_for_timeout(1500)
            # 依次切换全部时间节点、两种着色，确保不报错
            n = await pg.locator(".tick").count()
            for cm in ("zhen", "pol"):
                await pg.click(f'#cmode [data-cm="{cm}"]')
                for j in range(n): await pg.click(f'.tick[data-j="{j}"]')
            await pg.locator(".tick", has_text=FIRST).first.click(); await pg.wait_for_timeout(600)
            path = OUT / f"shot-{name}.png"
            await pg.screenshot(path=str(path)); print("wrote", path)
            await ctx.close()
        await b.close()
        print("脚本错误：", errors or "无")

asyncio.run(main())
