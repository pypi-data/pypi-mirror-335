from typing import Optional, Dict, Any
from playwright.sync_api import Page, Browser, BrowserContext, Playwright, sync_playwright
import time
import os
class PlaywrightTools:
    """Playwright工具类，提供常用的浏览器自动化操作方法"""

    @staticmethod
    async def nav_goto(page: Page, url: str, wait_until: str = "load", timeout: int = 30000) -> None:
        """页面导航
        Args:
            page: Playwright页面对象
            url: 目标URL
            wait_until: 等待页面加载完成的事件
            timeout: 超时时间(毫秒)
        """
        await page.goto(url=url, wait_until=wait_until, timeout=timeout)

    @staticmethod
    def elem_wait_for_selector(page: Page, selector: str, timeout: int = 30000) -> None:
        """等待元素出现
        Args:
            page: Playwright页面对象
            selector: 元素选择器
            timeout: 超时时间(毫秒)
        """
        page.wait_for_selector(selector, timeout=timeout)

    @staticmethod
    def elem_click(page: Page, selector: str, delay: int = 0) -> None:
        """点击元素
        Args:
            page: Playwright页面对象
            selector: 元素选择器
            delay: 点击后等待时间(毫秒)
        """
        page.click(selector)
        if delay:
            time.sleep(delay/1000)

    @staticmethod
    def elem_type(page: Page, selector: str, text: str, delay: int = 0) -> None:
        """输入文本
        Args:
            page: Playwright页面对象
            selector: 元素选择器
            text: 要输入的文本
            delay: 输入后等待时间(毫秒)
        """
        page.type(selector, text)
        if delay:
            time.sleep(delay/1000)

    @staticmethod
    def elem_get_text(page: Page, selector: str) -> str:
        """获取元素文本内容
        Args:
            page: Playwright页面对象
            selector: 元素选择器
        """
        return page.text_content(selector)

    @staticmethod
    def elem_get_attribute(page: Page, selector: str, name: str) -> Optional[str]:
        """获取元素属性值
        Args:
            page: Playwright页面对象
            selector: 元素选择器
            name: 属性名
        """
        return page.get_attribute(selector, name)

    @staticmethod
    def page_screenshot(page: Page, path: str, full_page: bool = False) -> None:
        """截图
        Args:
            page: Playwright页面对象
            path: 保存路径
            full_page: 是否截取完整页面
        """
        page.screenshot(path=path, full_page=full_page)

    @staticmethod
    def page_save_as_pdf(page: Page, path: str, **kwargs) -> None:
        """保存为PDF
        Args:
            page: Playwright页面对象
            path: 保存路径
            **kwargs: 其他PDF选项
        """
        page.pdf(path=path, **kwargs)

    @staticmethod
    def page_execute_script(page: Page, script: str, arg: Any = None) -> Any:
        """执行JavaScript代码
        Args:
            page: Playwright页面对象
            script: JavaScript代码
            arg: 传递给脚本的参数
        """
        return page.evaluate(script, arg)

    @staticmethod
    def page_set_viewport_size(page: Page, width: int, height: int) -> None:
        """设置视窗大小
        Args:
            page: Playwright页面对象
            width: 宽度
            height: 高度
        """
        page.set_viewport_size({"width": width, "height": height})

    @staticmethod
    def browser_add_init_script(page: Page, script: str) -> None:
        """添加页面初始化脚本
        Args:
            context: 浏览器上下文
            script: JavaScript代码
        """
        page.add_init_script(script)

    @staticmethod
    def net_set_extra_http_headers(context: BrowserContext, headers: Dict[str, str]) -> None:
        """设置额外的HTTP请求头
        Args:
            context: 浏览器上下文
            headers: HTTP请求头字典
        """
        context.set_extra_http_headers(headers)

    @staticmethod
    def elem_double_click(page: Page, selector: str, delay: int = 0) -> None:
        """双击元素
        Args:
            page: Playwright页面对象
            selector: 元素选择器
            delay: 双击后等待时间(毫秒)
        """
        page.dblclick(selector)
        if delay:
            time.sleep(delay/1000)

    @staticmethod
    def elem_drag_and_drop(page: Page, source: str, target: str) -> None:
        """拖拽元素
        Args:
            page: Playwright页面对象
            source: 源元素选择器
            target: 目标元素选择器
        """
        page.drag_and_drop(source, target)

    @staticmethod
    def elem_upload_file(page: Page, selector: str, file_paths: list) -> None:
        """上传文件
        Args:
            page: Playwright页面对象
            selector: 文件输入框选择器
            file_paths: 文件路径列表
        """
        page.set_input_files(selector, file_paths)

    @staticmethod
    def elem_press_key(page: Page, key: str) -> None:
        """按下键盘按键
        Args:
            page: Playwright页面对象
            key: 按键名称(例如: 'Enter', 'Tab', 'ArrowDown'等)
        """
        page.keyboard.press(key)

    @staticmethod
    def elem_hover_and_click(page: Page, hover_selector: str, click_selector: str) -> None:
        """悬停后点击元素
        Args:
            page: Playwright页面对象
            hover_selector: 悬停元素选择器
            click_selector: 点击元素选择器
        """
        page.hover(hover_selector)
        page.click(click_selector)

    @staticmethod
    def elem_is_visible(page: Page, selector: str) -> bool:
        """检查元素是否可见
        Args:
            page: Playwright页面对象
            selector: 元素选择器
        """
        return page.is_visible(selector)

    @staticmethod
    def wait_for_network_idle(page: Page, timeout: int = 30000) -> None:
        """等待网络请求完成
        Args:
            page: Playwright页面对象
            timeout: 超时时间(毫秒)
        """
        page.wait_for_load_state('networkidle', timeout=timeout)

    @staticmethod
    def get_cookies(context: BrowserContext) -> list:
        """获取所有cookies
        Args:
            context: 浏览器上下文
        """
        return context.cookies()

    @staticmethod
    def set_cookie(context: BrowserContext, cookie: dict) -> None:
        """设置cookie
        Args:
            context: 浏览器上下文
            cookie: cookie字典，包含name、value等字段
        """
        context.add_cookies([cookie])

    @staticmethod
    def get_table_data(page: Page, table_selector: str) -> list:
        """提取表格数据
        Args:
            page: Playwright页面对象
            table_selector: 表格元素选择器
        """
        return page.evaluate(f"""
            () => {{
                const rows = document.querySelector('{table_selector}').rows;
                return Array.from(rows).map(row => {{
                    return Array.from(row.cells).map(cell => cell.textContent);
                }});
            }}
        """)

    @staticmethod
    def switch_to_frame(page: Page, frame_selector: str) -> None:
        """切换到iframe
        Args:
            page: Playwright页面对象
            frame_selector: iframe元素选择器
        """
        frame = page.frame_locator(frame_selector)
        if frame:
            page = frame

    @staticmethod
    def get_element_count(page: Page, selector: str) -> int:
        """获取元素数量
        Args:
            page: Playwright页面对象
            selector: 元素选择器
        """
        return page.locator(selector).count()

    @staticmethod
    def get_computed_style(page: Page, selector: str, property: str) -> str:
        """获取元素计算后的样式
        Args:
            page: Playwright页面对象
            selector: 元素选择器
            property: CSS属性名
        """
        return page.evaluate(f"window.getComputedStyle(document.querySelector('{selector}')).{property}")

    @staticmethod
    def new_tab(context: BrowserContext, url: str = None) -> Page:
        """打开新标签页
        Args:
            context: 浏览器上下文
            url: 要打开的URL
        """
        page = context.new_page()
        if url:
            page.goto(url)
        return page

    @staticmethod
    def maximize_window(page: Page) -> None:
        """最大化窗口
        Args:
            page: Playwright页面对象
        """
        page.evaluate("window.moveTo(0,0); window.resizeTo(screen.width,screen.height);")

    @staticmethod
    def start_performance_monitor(page: Page) -> None:
        """开始性能监控
        Args:
            page: Playwright页面对象
        """
        page.evaluate("""
            window.performanceData = {
                startTime: performance.now(),
                metrics: []
            };
            setInterval(() => {
                const metrics = performance.memory || {};
                window.performanceData.metrics.push({
                    timestamp: performance.now(),
                    usedJSHeapSize: metrics.usedJSHeapSize,
                    totalJSHeapSize: metrics.totalJSHeapSize
                });
            }, 1000);
        """)

    @staticmethod
    def get_performance_data(page: Page) -> dict:
        """获取性能数据
        Args:
            page: Playwright页面对象
        """
        return page.evaluate("window.performanceData")

    @staticmethod
    def intercept_requests(page: Page, url_pattern: str, callback) -> None:
        """拦截网络请求
        Args:
            page: Playwright页面对象
            url_pattern: URL匹配模式
            callback: 处理请求的回调函数
        """
        page.route(url_pattern, callback)

    @staticmethod
    def stop_intercept_requests(page: Page, url_pattern: str) -> None:
        """停止拦截网络请求
        Args:
            page: Playwright页面对象
            url_pattern: URL匹配模式
        """
        page.unroute(url_pattern)

    @staticmethod
    def get_console_logs(page: Page) -> list:
        """获取控制台日志
        Args:
            page: Playwright页面对象
        """
        return page.evaluate("""
            () => {
                return window.consoleLog || [];
            }
        """)

    @staticmethod
    def clear_console_logs(page: Page) -> None:
        """清除控制台日志
        Args:
            page: Playwright页面对象
        """
        page.evaluate("window.consoleLog = [];")
