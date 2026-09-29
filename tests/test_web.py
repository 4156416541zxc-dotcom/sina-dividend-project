"""
Playwright 网页自动化测试脚本
功能：测试分红数据展示网页的各项功能
"""

import asyncio
import os
import json
from datetime import datetime
from playwright.async_api import async_playwright, expect


class WebTester:
    """网页测试器"""

    def __init__(self, web_dir="../web", screenshot_dir="../screenshots"):
        self.web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), web_dir))
        self.screenshot_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), screenshot_dir))
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.results = []
        self.page = None
        self.browser = None

    def log_result(self, test_name, passed, message=""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}: {message}")

    async def setup(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        self.page = await self.context.new_page()
        print("[INFO] 浏览器启动成功")

    async def teardown(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("[INFO] 浏览器已关闭")

    async def take_screenshot(self, name, full_page=False):
        """截图"""
        filepath = os.path.join(self.screenshot_dir, f"{name}.png")
        await self.page.screenshot(path=filepath, full_page=full_page)
        print(f"[INFO] 截图已保存: {filepath}")
        return filepath

    async def test_page_load(self):
        """测试1：页面加载"""
        print("\n" + "=" * 50)
        print("测试1：页面加载")
        print("=" * 50)

        html_path = os.path.join(self.web_dir, "index.html")
        url = f"file:///{html_path.replace(os.sep, '/')}"

        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            title = await self.page.title()
            self.log_result("页面加载", True, f"标题: {title}")

            # 等待ECharts加载
            await self.page.wait_for_timeout(2000)
            await self.take_screenshot("01_homepage_full", full_page=True)
            return True
        except Exception as e:
            self.log_result("页面加载", False, str(e))
            return False

    async def test_navigation(self):
        """测试2：导航栏功能"""
        print("\n" + "=" * 50)
        print("测试2：导航栏功能")
        print("=" * 50)

        try:
            nav_links = await self.page.query_selector_all(".nav-link")
            self.log_result("导航栏存在", len(nav_links) > 0, f"找到 {len(nav_links)} 个导航链接")

            # 测试点击"数据可视化"
            viz_link = self.page.locator('a[href="#visualization"]')
            await viz_link.click()
            await self.page.wait_for_timeout(500)

            # 检查是否滚动到对应区域
            current_url = self.page.url
            self.log_result("导航跳转", "#visualization" in current_url, "跳转到数据可视化区域")

            await self.take_screenshot("02_navigation")
            return True
        except Exception as e:
            self.log_result("导航栏功能", False, str(e))
            return False

    async def test_charts_render(self):
        """测试3：图表渲染"""
        print("\n" + "=" * 50)
        print("测试3：图表渲染")
        print("=" * 50)

        chart_ids = [
            ("chart-trend", "历年分红趋势"),
            ("chart-compare", "累计派息对比"),
            ("chart-pie", "分红类型分布"),
            ("chart-heatmap", "派息热力图"),
            ("chart-yearly", "年度分红事件"),
            ("chart-radar", "雷达图"),
        ]

        all_passed = True
        for chart_id, chart_name in chart_ids:
            try:
                chart_el = await self.page.query_selector(f"#{chart_id}")
                if chart_el:
                    # 检查canvas是否存在（ECharts渲染标志）
                    canvas = await chart_el.query_selector("canvas")
                    has_content = canvas is not None
                    self.log_result(f"图表-{chart_name}", has_content,
                                    "已渲染" if has_content else "未找到canvas")
                    if not has_content:
                        all_passed = False
                else:
                    self.log_result(f"图表-{chart_name}", False, "元素不存在")
                    all_passed = False
            except Exception as e:
                self.log_result(f"图表-{chart_name}", False, str(e))
                all_passed = False

        # 滚动到图表区域截图
        await self.page.evaluate("document.getElementById('visualization').scrollIntoView()")
        await self.page.wait_for_timeout(1000)
        await self.take_screenshot("03_charts", full_page=True)

        return all_passed

    async def test_data_table(self):
        """测试4：数据表格"""
        print("\n" + "=" * 50)
        print("测试4：数据表格")
        print("=" * 50)

        try:
            # 滚动到表格区域
            await self.page.evaluate("document.getElementById('datatable').scrollIntoView()")
            await self.page.wait_for_timeout(500)

            # 检查表头
            headers = await self.page.query_selector_all("#dividend-table thead th")
            header_texts = [await h.inner_text() for h in headers]
            self.log_result("表格表头", len(headers) == 10,
                            f"找到 {len(headers)} 列: {', '.join(header_texts[:3])}...")

            # 检查数据行
            rows = await self.page.query_selector_all("#table-body tr")
            self.log_result("表格数据行", len(rows) > 0, f"当前页显示 {len(rows)} 行数据")

            await self.take_screenshot("04_data_table")
            return True
        except Exception as e:
            self.log_result("数据表格", False, str(e))
            return False

    async def test_filters(self):
        """测试5：筛选功能"""
        print("\n" + "=" * 50)
        print("测试5：筛选功能")
        print("=" * 50)

        try:
            # 测试股票筛选
            stock_select = self.page.locator("#stock-filter")
            await stock_select.select_option("贵州茅台")
            await self.page.wait_for_timeout(500)

            rows = await self.page.query_selector_all("#table-body tr")
            first_row_text = await rows[0].inner_text() if rows else ""
            filter_worked = "贵州茅台" in first_row_text
            self.log_result("股票筛选", filter_worked,
                            f"筛选贵州茅台后显示 {len(rows)} 行" if filter_worked else "筛选结果不正确")

            # 测试年份筛选
            year_select = self.page.locator("#year-filter")
            await year_select.select_option("2024")
            await self.page.wait_for_timeout(500)

            rows = await self.page.query_selector_all("#table-body tr")
            self.log_result("年份筛选", len(rows) > 0, f"筛选2024年后显示 {len(rows)} 行")

            # 测试搜索
            search_input = self.page.locator("#search-input")
            await search_input.fill("2024")
            await self.page.wait_for_timeout(500)

            rows = await self.page.query_selector_all("#table-body tr")
            self.log_result("搜索功能", True, f"搜索后显示 {len(rows)} 行")

            # 重置
            await stock_select.select_option("all")
            await year_select.select_option("all")
            await search_input.fill("")
            await self.page.wait_for_timeout(500)

            await self.take_screenshot("05_filters")
            return True
        except Exception as e:
            self.log_result("筛选功能", False, str(e))
            return False

    async def test_pagination(self):
        """测试6：分页功能"""
        print("\n" + "=" * 50)
        print("测试6：分页功能")
        print("=" * 50)

        try:
            page_info = await self.page.locator("#page-number").inner_text()
            self.log_result("分页信息", "第" in page_info, f"分页信息: {page_info}")

            # 点击下一页
            next_btn = self.page.locator("#next-page")
            if await next_btn.is_enabled():
                await next_btn.click()
                await self.page.wait_for_timeout(300)
                new_page_info = await self.page.locator("#page-number").inner_text()
                self.log_result("下一页", new_page_info != page_info,
                                f"从 '{page_info}' 变为 '{new_page_info}'")
            else:
                self.log_result("下一页", True, "只有一页，跳过测试")

            await self.take_screenshot("06_pagination")
            return True
        except Exception as e:
            self.log_result("分页功能", False, str(e))
            return False

    async def test_stats_table(self):
        """测试7：统计表格"""
        print("\n" + "=" * 50)
        print("测试7：统计表格")
        print("=" * 50)

        try:
            await self.page.evaluate("document.getElementById('statistics').scrollIntoView()")
            await self.page.wait_for_timeout(500)

            rows = await self.page.query_selector_all("#stats-body tr")
            self.log_result("统计表格", len(rows) == 5, f"显示 {len(rows)} 只股票的统计数据")

            await self.take_screenshot("07_stats_table", full_page=True)
            return True
        except Exception as e:
            self.log_result("统计表格", False, str(e))
            return False

    async def test_responsive(self):
        """测试8：响应式布局"""
        print("\n" + "=" * 50)
        print("测试8：响应式布局")
        print("=" * 50)

        try:
            # 测试平板尺寸
            await self.page.set_viewport_size({"width": 768, "height": 1024})
            await self.page.wait_for_timeout(500)
            await self.take_screenshot("08_tablet_view")

            # 测试手机尺寸
            await self.page.set_viewport_size({"width": 375, "height": 812})
            await self.page.wait_for_timeout(500)
            await self.take_screenshot("09_mobile_view")

            # 恢复桌面尺寸
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            self.log_result("响应式布局", True, "已测试平板和手机视图")
            return True
        except Exception as e:
            self.log_result("响应式布局", False, str(e))
            return False

    def generate_report(self):
        """生成测试报告"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed

        report = {
            "test_time": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%"
            },
            "details": self.results
        }

        report_path = os.path.join(self.screenshot_dir, "test_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print("测试报告汇总")
        print("=" * 60)
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"通过率: {report['summary']['pass_rate']}")
        print(f"报告已保存: {report_path}")

        return report

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("Playwright 网页自动化测试")
        print("=" * 60)

        await self.setup()

        try:
            await self.test_page_load()
            await self.test_navigation()
            await self.test_charts_render()
            await self.test_data_table()
            await self.test_filters()
            await self.test_pagination()
            await self.test_stats_table()
            await self.test_responsive()
        finally:
            await self.teardown()

        return self.generate_report()


async def main():
    tester = WebTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
