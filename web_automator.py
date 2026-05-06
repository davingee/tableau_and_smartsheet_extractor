from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from playwright.async_api import async_playwright  # pyright: ignore[reportMissingImports]


class WebAutomator:
    async def screenshot_smartsheet(
        self,
        url: str,
        image_path: str,
        width: int = 1920,
        height: int = 2080,
        wait_time: int = 10,
        click_what: str | None = None,
    ) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--force-device-scale-factor=2", "--high-dpi-support=1"],
            )
            context = await browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=3,
            )
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(wait_time * 1000)
            if click_what:
                btn = page.get_by_label(click_what)
                await btn.wait_for(state="visible", timeout=10000)
                await btn.click()
                await page.wait_for_timeout(1000)
            await page.evaluate("() => document.fonts && document.fonts.ready")
            await page.screenshot(path=image_path, full_page=True, animations="disabled", type="png")
            await browser.close()
        return image_path

    async def get_tableau_report_links(self, url: str) -> list[dict]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector('[data-testid="VizCard"]')
            title_links = page.locator('a[class*="title"]')
            count = await title_links.count()
            results = []
            for i in range(count):
                link = title_links.nth(i)
                results.append({
                    "Title": await link.text_content(),
                    "URL": "https://public.tableau.com" + await link.get_attribute("href"),
                })
            await browser.close()
        return results

    async def screenshot_tableau(
        self,
        url: str,
        image_path: str,
        width: int = 2840,
        height: int = 4160,
        wait_time: int = 7,
    ) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--force-device-scale-factor=2", "--high-dpi-support=1"],
            )
            context = await browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=2,
            )
            page = await context.new_page()
            page.set_default_navigation_timeout(120000)
            page.set_default_timeout(60000)
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            iframe = page.locator('iframe[title="Data Visualization"]')
            await iframe.wait_for(state="visible", timeout=120000)
            src = await iframe.get_attribute("src")
            if not src:
                raise RuntimeError("iframe src not found")
            direct_url = self._force_no_home(src)
            viz_page = await context.new_page()
            await viz_page.goto(direct_url, wait_until="domcontentloaded", timeout=120000)
            await viz_page.wait_for_timeout(wait_time * 1000)
            await viz_page.screenshot(path=image_path, full_page=False, type="png")
            await browser.close()
        return image_path

    def _force_no_home(self, src_url: str) -> str:
        parsed = urlparse(src_url)
        qs = parse_qs(parsed.query)
        qs[":showVizHome"] = ["no"]
        qs[":toolbar"] = ["n"]
        return urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))
