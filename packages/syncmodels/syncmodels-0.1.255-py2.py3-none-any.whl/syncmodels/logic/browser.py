import asyncio
import re
import math
from random import uniform
from time import sleep, time
from weakref import WeakKeyDictionary

# from playwright import sync_api as plw
from playwright import async_api as plw
from playwright.async_api._generated import (
    # Page as _Page,
    Playwright as _Browser,
)


class Magic:

    CACHE = WeakKeyDictionary()
    PAUSE = 0.1

    def __init__(self, target, root=None, last=None):
        self._target_ = target
        self._root_ = root or target
        self._last__ = last

    def __getattr__(self, name):
        _next_ = getattr(self._target_, name)
        if isinstance(
            _next_,
            (
                int,
                float,
                str,
                bytes,
                dict,
                list,
                tuple,
            ),
        ):
            return _next_
        return self.__class__(_next_, self._root_)

    async def __call__(self, *args, **kw):
        return await self._target_(*args, **kw)

    async def unique(self, name, validator=None, timeout=100000):
        saved = self.CACHE.setdefault(self, {})
        t0 = time()
        t2 = t0 + timeout / 1000
        pause = self.PAUSE
        tries = 0
        while (t1 := time()) < t2:
            tries += 1
            pause *= 1.5

            try:
                new = self.__getattr__(name)
                if validator:
                    if m := re.search(validator, str(new)):
                        new = new, m.groupdict()
                    else:
                        new = new, None
                        print(f"[{tries}] pause: {pause}")
                        await asyncio.sleep(pause)
                        continue
                if name in saved:
                    last = saved[name]
                    if (validator and last[-1] == new[-1]) or (
                        not validator and last == new
                    ):
                        print(f"[{tries}] pause: {pause}")
                        await asyncio.sleep(pause)
                        continue

                # if tries > 2:
                #     self.PAUSE = 0.5 * self.PAUSE + 0.5 * pause
                # else:
                #     self.PAUSE *= 0.9

                elapsed = time() - t0
                print(f"elapse: {elapsed}")
                # NOTE: (0.8 + 0.1) < 1.0, so will try to reduce time when possible
                self.PAUSE = 0.8 * self.PAUSE + 0.1 * elapsed
                return new
            except Exception as why:
                print(why)

            finally:
                saved[name] = new


class Page(Magic):

    # WAIT_STATES =  ['commit', 'load', 'domcontentloaded', 'networkidle']
    # WAIT_STATES = ["domcontentloaded", "networkidle"]
    WAIT_STATES = []
    WAIT_FUNCTIONS = set(["goto"])

    async def __call__(self, *args, **kw):
        try:
            result = await self._target_(*args, **kw)
            if self._target_.__func__.__name__ in self.WAIT_FUNCTIONS:
                await self._wait_page()
            else:
                _foo = 2
            return result
        except TypeError as why:
            result = self._target_(*args, **kw)
            return result

        except Exception as why:
            print(why)
            raise

        finally:
            pass

    # async def goto(self, *args, **kw):
    #     pass

    async def _wait_page(self):
        page = self._root_
        await page.wait_for_timeout(500)

        # states = ['networkidle']
        # states = ['commit', 'load', 'domcontentloaded', 'networkidle']
        for state in self.WAIT_STATES:
            await page.wait_for_load_state(state)


class BrowserBot(Magic):
    """A bot that controls a browser and provide basic helpers"""

    async def new_page(self):

        page = await self._target_.new_page()
        page = Page(page)
        return page

    async def get_lat_long(self, addresses):

        try:
            ctx = {
                "timeout": 1000,
            }

            page = await self.new_page()

            # Open Google Maps
            await page.goto("https://www.google.es/maps")

            # check if "Accept" condition button appears
            try:
                await page.click("button[aria-label='Aceptar todo']", **ctx)
            except plw.TimeoutError as why:
                _foo = 2

            # Setup map event listener
            # await setup_map_event_listener(page)
            # await human_like_mouse_move(page, 0, 0, 500, 500)

            t0 = time()
            result = {
                address: await get_lat_long(page, address) for address in addresses
            }
            elapsed = time() - t0
            print(f"elapsed: {elapsed}")
            return result
        except Exception as why:
            print(why)
        finally:
            # Close the page
            pass

    async def search(self, query):
        page = await self.new_page()
        q = query.keywords.replace(" ", "+")
        url = f"https://www.duckduckgo.com/{q}"
        await page.goto(url)

        await page.close()
        foo = 1


# Helpers


async def human_like_mouse_move(
    page, start_x, start_y, end_x, end_y, duration=2, steps=30
):
    # Calculate the distance to move
    distance_x = end_x - start_x
    distance_y = end_y - start_y

    mouse = page.mouse

    # Move in small steps
    dt = duration / steps
    t2 = time() + duration
    for step in range(steps):
        # Calculate intermediate position
        x = step / steps * 4 / math.pi
        x = math.sin(x)

        intermediate_x = start_x + distance_x * x + uniform(-5, 5)
        intermediate_y = start_y + distance_y * x + uniform(-5, 5)

        # Move the mouse to the intermediate position
        print(f"{x}: {intermediate_x}, {intermediate_y}")

        await mouse.move(intermediate_x, intermediate_y)

        # Wait a little to simulate human speed (varying delay between steps)
        remain = min(t2 - time(), dt)

        # await asyncio.sleep(uniform(0.0, remain))  # Add random short pauses

    # Finally move to the exact end position
    await mouse.move(end_x, end_y)


async def get_lat_long(page: Page, address):
    # Launch the browser
    # browser = p.chromium.launch(headless=False)
    # browser = await p.firefox.launch(headless=False)
    ctx = {
        "timeout": 1000,
    }

    # # page = await browser.new_page()

    await page.fill("input[id='searchboxinput']", address, **ctx)
    await page.keyboard.press("Enter")

    regexp = r"@(?P<latitude>-?\d+\.\d+),(?P<longitude>-?\d+\.\d+)"
    old = page.url
    # old = await page.unique("url", validator=regexp)

    # Extra wait to ensure the marker appears
    # await page.wait_for_load_state('networkidle')
    # await page.wait_for_timeout(500)
    # await page.reload(wait_until='domcontentloaded')
    # await page.wait_for_load_state('networkidle')
    # await page.wait_for_timeout(1500)

    if False:
        await page.wait_for_timeout(1000)

        # Find the red marker and click on it
        # The red marker usually has a specific class name.
        # We can inspect it using the browser's Developer Tools.
        # try:
        #     # Click on the red marker (Google Maps uses aria-label 'Location' for the marker)
        #     page.click(f"button[title='{address}']")
        #     # Wait a moment for the marker details to show up
        #     page.wait_for_timeout(1000)
        # except:
        #     print("Could not find or click the red marker.")
        #
        #
        # Simulate a click at the center of the map (where the marker is usually positioned)
        # Adjust the coordinates if necessary, depending on the zoom level
        map_width, map_height = (
            page.viewport_size["width"],
            page.viewport_size["height"],
        )
        # Click at the center of the map
        x0, y0 = uniform(0, map_width), uniform(0, map_height)
        x1, y1 = map_width // 2, map_height // 2
        x2, y2 = x1 * uniform(0.8, 0.9), y1 * uniform(0.8, 0.9)

        # await human_like_mouse_move(page, x0, y0, x2, y2)
        # await human_like_mouse_move(page, x2, y2, x1, y1)
        # await human_like_mouse_move(page, x1, y1, x0, y0)

        await page.mouse.click(x1, y1, button="right")
        await page.wait_for_timeout(1000)
        # page.keyboard.press('ArrowDown')
        # page.keyboard.press('ArrowUp')

        focused_element = await page.evaluate_handle(
            "document.activeElement"
        )  # Get the active (focused) element
        box = await focused_element.bounding_box()

        # Now use the mouse click on the element based on its bounding box (left-click)
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        # page.mouse.click(x,y)
        await page.mouse.move(x, y)
        await page.mouse.click(x, y)
        # focused_element.click()

        page.keyboard.press("Enter")

        # get the content from clipboard
        text = await page.evaluate("navigator.clipboard.readText().then(text => text);")
        print(text)

        # text = await page.evaluate(
        #     "navigator.clipboard.readText().then(text => text);"
        # )
        # print(text)

        # 48.8583701, 2.2944812999999997
        # 48.85866656635026, 2.2945885883611203
        # 37.393301554385886, -6.074174555819438
        # 37.3931396, -6.0742281999999985
        # 37.39247473095943, -6.073230418241575
        # Get the current URL

        #  48.858638331535424, 2.2945027576722237
        # diference
        # url  : 37.3931396       , -6.0742282,
        # click: 37.39327598266401, -6.0742496576722225

    # await page.wait_for_load_state('networkidle')
    # await page.reload(wait_until='domcontentloaded')
    # await page.wait_for_load_state('networkidle')
    # await page.wait_for_timeout(1000)

    # await page.reload(wait_until='domcontentloaded')
    # await page.wait_for_timeout(500)

    regexp = r"@(?P<latitude>-?\d+\.\d+),(?P<longitude>-?\d+\.\d+)"
    new = None

    while True:
        # url, geo = await page.unique("url", validator=regexp)
        if page.url != old:
            break
        await page.wait_for_timeout(500)

    url, geo = await page.unique("url", validator=regexp)

    # Use a regex pattern to extract latitude and longitude from the URL
    if geo:
        geo = {k: float(v) for k, v in geo.items()}
    print(f"{address}: {geo}")
    return geo
