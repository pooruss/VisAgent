import os
import io
import time
from copy import deepcopy
from PIL import Image, ImageDraw, ImageFont
import base64
import playwright
import playwright.sync_api
import logging
import json
from VAgent.environment.base import BaseEnvironment
from VAgent.models import EnvState, BoundingBox, Document, ActionStatusCode
from VAgent.environment.web_action.action_schema import ACTION_SCHEMA
from VAgent.document.base import BaseDocument
from VAgent.utils.image import img_to_base64, base64_to_image
from VAgent.utils.utils import generate_url_id
from VAgent.utils.element_filter import filter_elements

class WebEnvironment(BaseEnvironment):
    def __init__(self, config):
        super().__init__(config)
        self.state = EnvState()
        self.config = config
        self.width = self.config.web_env.width
        self.height = self.config.web_env.height
        self.timeout = self.config.web_env.timeout
        self.web_cfg = {
            'browser_args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                f'--window-size={self.width},{self.height}'
            ],
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'screen': {
                'width': self.width,
                'height': self.height
            },
            'timeout': self.timeout,
        }
        self.playwright = None
        self.browser = None
        self.page = None
        self.base_url = None
        self.base_document = None
        self.bbox2scroll = dict()
        self.scroll2bbox = dict()
        self.cookies = []
        self.elements_extract_js_code = open(os.path.join(
            os.path.dirname(__file__), "js", "web_elements.js")).read()
        self.action_schema = ACTION_SCHEMA
        self.set_cookies()

    def set_cookies(self):
        for website_cookie_file in os.listdir(self.config.web_env.cookie_path):
            # if "tencent" not in website_cookie_file:
            #     continue
            website_cookie = json.load(open(os.path.join(self.config.web_env.cookie_path, website_cookie_file), "r"))
            self.cookies.extend(website_cookie)
        for cookie_elem in self.cookies:
            cookie_elem["sameSite"] = "None"
        # print(self.cookies)

    def screenshot(self,) -> Image.Image:
        """Render the current page into an image.

        :return Image: The image of the current page.
        """
        screenshot = self.page.screenshot(timeout=self.timeout)
        return Image.open(io.BytesIO(screenshot))

    def _draw_bbox(self, screenshot: Image.Image=None) -> str:
        """Render the current page into an image, draw bbox for elems and encode it into base64.

        :return str: The base64 encoded image of the current page.
        """
        if not screenshot:
            screenshot = self.screenshot()
            # screenshot.show()

        # Update self screenshot state here
        self.state.screenshot = screenshot

        if self.config.web_env.debug:
            timestamp = str(int(time.time()))
            screenshot_path = f"debug_figs/debugscreenshot_{timestamp}.png"
            screenshot.save(screenshot_path)
            logging.info(f"Debug screenshot saved to {screenshot_path}")
            screenshot.show()

        ft = ImageFont.truetype(self.config.web_env.bbox.font_ttf, size=self.config.web_env.bbox.font_size)
        draw = ImageDraw.Draw(screenshot)
        try:
            elems = self._extract_elements()
        except Exception as e:
            print(f"Extracting elements from web page failed: {e}")
            elems = []
        for idx, elem in enumerate(elems):
            if "uid" not in elem:
                idx += 1
            else:
                idx = elem["uid"]
            bbox = elem['bbox']
            draw.rectangle(
                [bbox['x'], bbox['y'], bbox['x'] +
                    bbox['width'], bbox['y'] + bbox['height']],
                outline="red",
                width=2
            )
            draw.text(
                [bbox['x']+bbox['width']//2, bbox['y']+bbox['height']//2],
                str(idx),
                fill="magenta",
                font=ft
            )
        screenshot_png = io.BytesIO()

        if self.config.web_env.debug:
            timestamp = str(int(time.time()))
            screenshot_path = f"debug_figs/debugscreenshot_{timestamp}.png"
            screenshot.save(screenshot_path)
            logging.info(f"Debug screenshot saved to {screenshot_path}")
            screenshot.show()

        screenshot.save(screenshot_png, format='PNG')
        screenshot_png.seek(0)

        # Update self screenshot bbox state here
        self.state.screenshot_bbox = Image.open(screenshot_png)

        return base64.b64encode(screenshot_png.read()).decode('utf-8')

    def _setup_browser(self):
        """Setup or restart a browser instance.

        :return Browser: The browser instance.
        """
        if self.playwright is not None:
            self.browser.close()
            self.playwright.stop()
        self.playwright = playwright.sync_api.sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True, args=self.web_cfg['browser_args'])
        self.context = self.browser.new_context(
            user_agent=self.web_cfg["user_agent"],
            screen=self.web_cfg['screen']
        )
        self.page = self.context.new_page()
        self.page.context.add_cookies(self.cookies)
        return self.browser

    def _check_browser(self):
        """Check if the browser is ready.
        """
        if self.page is None:
            self._setup_browser()

    def _extract_elements(self):
        """Extract elements from the current page.
        """
        elems = self.page.evaluate(self.elements_extract_js_code)
        for idx, elem in enumerate(elems):
            elem['index'] = idx + 1
        self.page_elements = elems
        # 对elements根据位置重新排序，确保同一页面在不同时间访问，提取出的elements前后顺序不变
        self.page_elements = filter_elements(self.page_elements, view_port={"width": self.width, "height": self.height})
        return elems

    def _look_page(self):
        """Look at the current page."""
        self.page.wait_for_load_state("domcontentloaded", timeout=self.timeout)
        self.page.wait_for_load_state("load", timeout=self.timeout)
        
        bbox_data = self._draw_bbox()

        # Update self state
        self.state.bbox_description = f"Bounding Boxes:\n"
        self.state.document.bounding_boxes = []
        for index, elem in enumerate(self.page_elements):
            button_text = elem["text"]
            self.state.bbox_description += f"{index+1}: {button_text}\n"
            coordinates = elem["bbox"]
            bbox = BoundingBox(identifier=index+1, description=button_text, coordinates=coordinates)
            self.state.document.add_bounding_box(bbox)
        self.state.xml_content = self.page_elements

        top_document = None
        if self.base_document:
            # retrieve document
            self.state.screenshot_bbox.show()
            retrieved_documents = self.base_document.retrieve_documents(self.state.document)
            # gold reference
            if len(retrieved_documents) > 0:
                top_document = retrieved_documents[0]
        
        return {
            "type": "composite",
            "data": [
                {
                    "type": "binary",
                    "media_type": "image/png",
                    "data": bbox_data
                },
                {
                    "type": "simple",
                    "data": [{"index": index, "tagName": elem["tagName"], "text": elem["text"], "xpath": elem["xpath"], "bbox": elem["bbox"]} for index, elem in enumerate(self.page_elements)]
                }
            ],
            "document": top_document
        }

    def _scroll_for_info(self):
        self.bbox2scroll = dict()
        self.scroll2bbox = dict()
        new_state = True
        max_scorll = 9.0
        cur_scroll = 1.0
        cur_document = deepcopy(self.state.document)
        cur_bbox_num = len(cur_document.bounding_boxes)
        # self.state.screenshot_bbox.show()
        while cur_scroll <= max_scorll and new_state:
            # scroll
            self.scroll(y=1.0)
            
            cur_bboxes = deepcopy(self.state.document.bounding_boxes)

            # append new boxes if any
            new_state = False
            for cur_index, cur_bbox in enumerate(cur_bboxes):
                if cur_bbox not in cur_document.bounding_boxes:
                    cur_bbox_num += 1
                    cur_bbox.identifier = cur_bbox_num
                    cur_document.add_bounding_box(cur_bbox)
                    self.bbox2scroll[cur_bbox_num] = cur_scroll
                    self.scroll2bbox[cur_scroll] = cur_index
                    new_state = True
            cur_scroll += 1.0

        # scroll back
        self.scroll(y=-9.0)
        self.state.document = cur_document
        
        return

    def goto(self, url: str):
        """Load document for given url and go to the given url.

        :param string url: The url to go.
        """
        url_id = generate_url_id(url)
        if os.path.exists(os.path.join(self.config.document.document_path, url_id)):
            document_path = os.path.join(self.config.document.document_path, url_id)
            self.base_document = BaseDocument(document_path=document_path)
        self._check_browser()
        self.page.goto(url, timeout=self.timeout)
        self.base_url = url
        time.sleep(3)
        self._look_page()
        # self._scroll_for_info()
        return

    def click(self, element_index: int = None, x: float=None, y: float=None):
        """Click the target element or position on the web page.

        Click the element under the mouse cursor if neither element_index nor position is provided.

        :param integer? element_index: The index of the element to click.
        :param object? position: The position to click. Example: {"x": 0.5, "y": 0.3}, which means click the position at 50% width and 30% height. Always use relative position.
        """
        if x is not None and y is not None:
            position = {"x": float(x), "y": float(y)}
        else:
            position = None
        self._check_browser()
        if element_index is not None and element_index > 0:
            if element_index-1 < len(self.page_elements):
                # offset
                element = self.page_elements[element_index-1]
                # print(element)
                bbox = element['bbox']
            else:
                raise RuntimeError
                cur_document = deepcopy(self.state.document)
                scroll = self.bbox2scroll[element_index]
                self.scroll(y=scroll)
                bbox = cur_document.bounding_boxes[element_index-1].coordinates
            try:
                with self.context.expect_page(timeout=3000) as new_page_info:
                    self.page.mouse.click(bbox['x']+bbox['width']//2, bbox['y']+bbox['height']//2)
                    # self.new_page.mouse.click(bbox['x']+bbox['width']//2, bbox['y']+bbox['height']//2)
                if self.page.url != new_page_info.value.url:
                    print("Switch to a new page...")
                    self.page = new_page_info.value
            except Exception as e:
                print(f"No new page detected after clicking: {e}")
                pass
            
            time.sleep(3)
            data = self._look_page()
            # self._scroll_for_info()
            return data

        if position is not None:
            x = int(self.page.viewport_size["width"] * position['x'])
            y = int(self.page.viewport_size["height"] * position['y'])
            self.page.mouse.click(x, y)
            time.sleep(3)
            data = self._look_page()
            # self._scroll_for_info()
            return data

        self.page.mouse.down()
        self.page.mouse.up()
        self.page.wait_for_timeout(self.timeout)
        data = self._look_page()
        # self._scroll_for_info()
        return data

    def scroll(self, x: float = 0.0, y: float = 0.6):
        """Scroll the web page.
        Example: {"x": 0.0, "y": 0.3}, which means scroll the page to 0% width and 30% height. Always use relative position.

        :param number? x: The percentage of page width to scroll. Defaults to 0.0.
        :param number? y: The percentage of page height to scroll. Defaults to 0.6.
        """
        x = float(x)
        y = float(y)
        self._check_browser()
        x = float(self.page.viewport_size["width"] * x)
        y = float(self.page.viewport_size["height"] * y)
        self.page.mouse.wheel(x, y)
        self.page.wait_for_timeout(1000)
        return self._look_page()

    def typing(self, text: str = None):
        """Type the given text by triggering keyborad events.
        You can also use shortcut keys of the browser by this.

        Example:
        - Type 'Hello World' and press 'Enter': `typing(text='Hello World')`
        - Rollback to the previous page: `typing(press='Alt+ArrowLeft')`

        :param string? text: The text to type.
        :param string? press: The key to press, can be a combination of any keys. Defaults to 'Enter' . Example: 'Enter', 'Alt+ArrowLeft','Shift+KeyW'.
        """
        self._check_browser()
        self.page.keyboard.type(text)
        self.page.wait_for_timeout(self.timeout)
        data = self._look_page()
        # self._scroll_for_info()
        return data
    
    def hotkey(self, press: str = "Enter", times: int = 1):
        self._check_browser()
        try:
            with self.context.expect_page(timeout=3000) as new_page_info:
                for _ in range(int(times)):
                    self.page.keyboard.press(press)
                print("Switch to a new page...")
            self.page.wait_for_timeout(self.timeout)
            if self.page.url != new_page_info.value.url:
                self.page = new_page_info.value
        except Exception as e:
            print(f"No new page detected after clicking: {e}")
            pass    
        data = self._look_page()
        # self._scroll_for_info()
        return data

    def write_file(self, text: str = "", file_path: str = "./"):
        with open(os.path.join(self.config.workspace_root, file_path), "r") as target_file:
            target_file.write(text)
        target_file.close()
        return None
    
    def read_file(self, file_path: str = "./"):
        with open(os.path.join(self.config.workspace_root, file_path), "r") as target_file:
            content = target_file.read()
        target_file.close()
        return content

    def step(self, action):
        action_name = action.name
        action_inputs = action.arguments
        try:
            # Every action include one bbox drawing, every bbox drawing execute one screenshot if self.state.screenshot is None. State updation is inside the bbox drawing.
            if action_name == "mouse_click":
                data = self.click(**action_inputs)
            elif action_name == "keyboard_write":
                data = self.typing(**action_inputs)
            elif action_name == "keyboard_press":
                data = self.hotkey(**action_inputs)
            elif action_name == "mouse_scroll":
                if "x" not in action_inputs or "y" not in action_inputs:
                    x = action_inputs.get("x", 0.0)
                    y = action_inputs.get("y", 0.6)
                data = self.scroll(**action_inputs)
            elif action_name == "write_file":
                data = self.write_file(**action_inputs)
            elif action_name == "read_file":
                data = self.read_file(**action_inputs)
            else:
                raise ValueError(f"Invalid action: {action_name}")
        except Exception as e:
            # raise e
            return ActionStatusCode.FAILED, f"Action failed due to error: {e}"
        
        # print("please wait 3 seconds...")
        time.sleep(3)
    
        if action.name != "read_file":
            return ActionStatusCode.SUCCESS, "Action success."
        else:
            return ActionStatusCode.SUCCESS, data
    
    
if __name__ == '__main__':
    import asyncio
    
