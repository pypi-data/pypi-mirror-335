# 导入playwright的异步API模块
from playwright.async_api import async_playwright

# 浏览器管理器类，用于处理浏览器相关操作
class BrowserManager:
    def __init__(self):
        # 初始化浏览器实例为空
        self.browser = None
        # 初始化页面实例为空
        self.page = None
        # 初始化控制台日志列表
        self.console_logs = []
        # 初始化截图字典
        self.screenshots = {}

    async def ensure_browser(self):
        # 如果浏览器实例不存在，则创建新的浏览器实例
        if not self.browser:
            # 启动playwright
            playwright = await async_playwright().start()
            # 启动Chrome浏览器，设置为有界面模式
            self.browser = await playwright.chromium.launch(headless=False)
            # 创建新的浏览器上下文，设置视口大小和设备缩放比例
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                device_scale_factor=1,
            )
            # 在上下文中创建新的页面
            self.page = await context.new_page()

            # 定义控制台消息处理函数
            async def handle_console_message(msg):
                # 格式化日志条目
                log_entry = f"[{msg.type}] {msg.text}"
                # 将日志添加到控制台日志列表
                self.console_logs.append(log_entry)
                # Simulate a server notification
                print({
                    "method": "notifications/resources/updated",
                    "params": {"uri": "console://logs"},
                })

            # 注册控制台消息事件处理器
            self.page.on("console", handle_console_message)

        # 返回页面实例
        return self.page