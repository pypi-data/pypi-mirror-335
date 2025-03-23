import base64
import random
from typing import List, Tuple, Dict
from DrissionPage import ChromiumPage


class RequestInterceptor:
    def __init__(self, page: ChromiumPage):
        self.handler = None
        self.page = page
        self.args = ()
        # Enable network events
        self.page.run_cdp('Network.enable')

        # Enable target discovery to detect iframes
        self.page.run_cdp('Target.setDiscoverTargets', discover=True)
        self.targets = {}  # Store iframe targets

        # Set up callbacks
        self.page.driver.set_callback('Target.targetCreated', self._handle_target_created)
        self.page.driver.set_callback('Target.targetDestroyed', self._handle_target_destroyed)

    def _handle_target_created(self, **params):
        target_info = params.get('targetInfo', {})
        target_id = target_info.get('targetId')

        # Only attach to iframe targets
        if target_info.get('type') == 'iframe':
            # Attach to the target
            session_id = self.page.run_cdp('Target.attachToTarget',
                                           targetId=target_id,
                                           flatten=True).get('sessionId')
            if session_id:
                self.targets[target_id] = session_id
                # Enable network interception for this target
                self.page.run_cdp('Network.enable', sessionId=session_id)
                self.page.run_cdp('Network.setRequestInterception',
                                  patterns=[{'urlPattern': "*", "interceptionStage": "Request"}],
                                  sessionId=session_id)

    def _handle_target_destroyed(self, **params):
        target_id = params.get('targetId')
        if target_id in self.targets:
            del self.targets[target_id]

    def intercept(self):
        # Set up interception for main frame
        self.page.run_cdp('Network.setRequestInterception',
                          patterns=[{'urlPattern': "*", "interceptionStage": "Request"}])
        self.page.driver.set_callback('Network.requestIntercepted', self._handle_interception, immediate=True)

    def _handle_interception(self, **params):
        session_id = params.get('sessionId')  # Will be present for iframe requests
        request = params['request']
        interception_id = params['interceptionId']

        # Create Request object
        req = Request(self.page, request, interception_id, session_id)

        # Call user-defined handler
        if self.handler:
            self.handler(req, *self.args)

    def set_handler(self, handler, *args):
        """
        设置处理函数,不应被手动调用
        :param handler: 处理请求函数
        :param args: 想要转递给处理函数的参数
        :return:
        """
        self.handler = handler
        self.args = args
        self.intercept()


class DrssionPage_Enhance:
    def __init__(self, page: ChromiumPage):
        self.page = page
        page.add_init_js("""
        function getRandomInt(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }

        let screenX = getRandomInt(800, 1200);
        let screenY = getRandomInt(400, 600);

        Object.defineProperty(MouseEvent.prototype, 'screenX', { value: screenX });

        Object.defineProperty(MouseEvent.prototype, 'screenY', { value: screenY });
        """)

    def generate_mouse_path(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[float, float]]:
        """生成从(x1,y1)到(x2,y2)的模拟鼠标路径"""
        path = []
        x, y = x1, y1
        while abs(x - x2) > 3 or abs(y - y2) > 3:
            diff = abs(x - x2) + abs(y - y2)
            speed = random.randint(1, 2)
            if diff < 20:
                speed = random.randint(1, 3)
            else:
                speed *= diff / 45

            x += min(speed, abs(x2 - x)) * (1 if x < x2 else -1)
            y += min(speed, abs(y2 - y)) * (1 if y < y2 else -1)
            path.append((x, y))

        return path

    def set_webgl_renderer(self, renderer: str):
        """
        为当前tab设置WebGL渲染器信息
        :param renderer: WebGL渲染器字符串
        :return: None
        """
        script = f"""
            (() => {{
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    // UNMASKED_RENDERER_WEBGL
                    if (parameter === 37446) {{
                        return "{renderer}";
                    }}
                    return getParameter.apply(this, arguments);
                }};
            }})();
            """
        self.page.run_cdp('Page.addScriptToEvaluateOnNewDocument', source=script)

    def route(self, handler,*args) -> RequestInterceptor:
        """
        :param handler:处理请求的函数，接收一个Request对象
        :param args: 想要转递给处理函数的参数
        :return:
        """
        # Enable Network domain
        interceptor = RequestInterceptor(self.page)
        interceptor.set_handler(handler,*args)
        return interceptor


class Request:
    def __init__(self, page: ChromiumPage, request, interception_id, session_id=None):
        self.page = page
        self.request = request
        self.interception_id = interception_id
        self.session_id = session_id

    def continue_request(self):
        if self.session_id:
            self.page.run_cdp('Network.continueInterceptedRequest',
                              interceptionId=self.interception_id,
                              sessionId=self.session_id)
        else:
            self.page.run_cdp('Network.continueInterceptedRequest',
                              interceptionId=self.interception_id)

    def get_reason_phrase(self, status_code: int) -> str:
        reason_phrases: Dict[int, str] = {
            200: 'OK',
            301: 'Moved Permanently',
            302: 'Found',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error',
            502: 'Bad Gateway',
            503: 'Service Unavailable',
        }
        return reason_phrases.get(status_code, 'Unknown Status')

    def fulfill(self, status_code: int = 200, headers: dict = None, body: str = None):
        """
        填充替换返回的内容
        :param status_code: 状态码，默认200
        :param headers: 返回的头
        :param body: 返回的内容
        :return:
        """
        reason_phrase = self.get_reason_phrase(status_code)
        headers = headers or {}
        headers['Content-Length'] = str(len(body))
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'text/html'
        response = f'HTTP/1.1 {status_code} {reason_phrase}\r\n'
        for header, value in headers.items():
            response += f'{header}: {value}\r\n'
        response += '\r\n'
        response += body
        base64_response = base64.b64encode(response.encode("utf-8")).decode()
        if self.session_id:
            self.page.run_cdp('Network.continueInterceptedRequest',
                              interceptionId=self.interception_id,
                              rawResponse=base64_response,
                              sessionId=self.session_id)
        else:
            self.page.run_cdp('Network.continueInterceptedRequest',
                              interceptionId=self.interception_id,
                              rawResponse=base64_response)
