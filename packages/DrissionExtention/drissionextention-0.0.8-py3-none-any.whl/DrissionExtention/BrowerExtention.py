import os
import sys
import tempfile
from DrissionPage import ChromiumOptions


def create_cloudflare_extension() -> str:
    manifest_json = """
    {
        "manifest_version": 3,
        "name": "Turnstile Patcher",
        "version": "2.1",
        "content_scripts": [
            {
                "js": [
                    "./script.js"
                ],
                "matches": [
                    "<all_urls>"
                ],
                "run_at": "document_start",
                "all_frames": true,
                "world": "MAIN"
            }
        ]
    }
    """

    script_js = """
    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    let screenX = getRandomInt(800, 1200);
    let screenY = getRandomInt(400, 600);
    Object.defineProperty(MouseEvent.prototype, 'screenX', { value: screenX });
    Object.defineProperty(MouseEvent.prototype, 'screenY', { value: screenY });
    """

    cloudflare_extension_dir = tempfile.mkdtemp()

    with open(os.path.join(cloudflare_extension_dir, "manifest.json"), "w") as f:
        f.write(manifest_json)

    with open(os.path.join(cloudflare_extension_dir, "script.js"), "w") as f:
        f.write(script_js)

    return cloudflare_extension_dir


class BrowerExtention:
    def __init__(self, chrome_option: ChromiumOptions()):
        self.chrome_option = chrome_option

    def patch_browser(self):
        """
        需要在启动浏览器之前调用，修复CDP的问题
        :return:
        """
        cloudflare_extension_dir = create_cloudflare_extension()
        self.chrome_option.add_extension(cloudflare_extension_dir)

    def add_default_argument(self):
        """
        添加默认参数，需要在启动浏览器之前调用
        :return:
        """
        self.chrome_option.set_argument('--no-sandbox')
        self.chrome_option.set_argument("--disable-blink-features=AutomationControlled")
        self.chrome_option.set_pref('credentials_enable_service', False)
        self.chrome_option.set_argument('--hide-crash-restore-bubble')
        self.chrome_option.set_argument('--window-size=1920,1080')
        self.chrome_option.set_argument('--disable-setuid-sandbox')
        self.chrome_option.set_argument('--disable-dev-shm-usage')
        self.chrome_option.set_argument('--no-zygote')
        # 允许监听iframe的网络活动
        #self.chrome_option.set_argument('--disable-site-isolation-trials')

    def start_xvfb_display(self):
        """
        启动虚拟显示器
        :return:headless模式预设值
        """
        if os.name == 'nt':
            print('Windows不支持虚拟显示器')
            return True

        try:
            from xvfbwrapper import Xvfb
        except ImportError:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "xvfbwrapper"])
            from xvfbwrapper import Xvfb

        self.xvfb_display = Xvfb()
        self.xvfb_display.start()
        os.environ['DISPLAY'] = f":{self.xvfb_display.new_display}"
        return False

    def stop_xvfb_display(self):
        """
        停止虚拟显示器
        :return:
        """
        if self.xvfb_display:
            self.xvfb_display.stop()
            self.xvfb_display = None
