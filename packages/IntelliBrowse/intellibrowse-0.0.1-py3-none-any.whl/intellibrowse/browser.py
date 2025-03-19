from typing import TypeVar

from playwright.async_api import ElementHandle, Locator, Page

T = TypeVar("T", covariant=True)
Element = ElementHandle | Locator


async def js_get_window_rect(page: Page) -> dict[str, int]:
    rect = await page.evaluate(
        """
() => {
    return {
        left: window.screenLeft,
        top: window.screenTop,
        width: window.innerWidth,
        height: window.innerHeight
    };
}
"""
    )
    rect["right"] = rect["left"] + rect["width"]
    rect["bottom"] = rect["top"] + rect["height"]
    return rect


async def get_attribute(
    element: Element, *, attr: str, strict: bool = False, timeout: int = 100
) -> str | None:
    value = await element.get_attribute(attr)
    if strict or value:
        return value

    return await element.evaluate(f"el => el.{attr}")


async def get_tag_name(element: Element):
    return (await get_attribute(element, attr="tagName") or "").lower()


async def get_text(element: Element) -> str:
    return (await get_attribute(element, attr="textContent")) or ""


async def scroll_xy(page: Page, *, xamount: int, yamount: int):
    await page.mouse.wheel(xamount, yamount)


async def scroll_down(page: Page) -> None:
    await scroll_xy(page, xamount=0, yamount=(await js_get_window_rect(page))["height"])


async def scroll_up(page: Page) -> None:
    await scroll_xy(
        page, xamount=0, yamount=-(await js_get_window_rect(page))["height"]
    )


async def scroll_right(page: Page) -> None:
    await scroll_xy(page, xamount=(await js_get_window_rect(page))["width"], yamount=0)


async def scroll_left(page: Page) -> None:
    await scroll_xy(page, xamount=-(await js_get_window_rect(page))["width"], yamount=0)


async def to_bool(element: Locator, neg: bool = False) -> bool:
    b = bool(await element.count())
    return not b if neg else b


async def focus(element: Element, *, timeout: int = 25) -> None:
    await element.focus()
