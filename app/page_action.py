from playwright.async_api import expect, Page
from constant import *


async def click_button(page: Page, selector: str):
    """
    셀렉터로 지정한 버튼을 클릭한다.

    Args:
        selector (str): 버튼을 위한 선택자

    Returns:
        bool: 클릭이 정상적으로 진행되면 참
    """
    loc = page.locator(selector)
    try:
        await expect(loc).to_be_enabled(timeout=500)  # 버튼이 클릭 가능한 상태가 될때 까지 대기
        await loc.click(timeout=500)  # 클릭 실시.
        print(f"click success {selector}")

    except Exception as e:
        raise Exception("Click is not possible", selector, e)


async def click_dropdown(page: Page, dropdown_selector: str, value_selector: str):
    for _ in range(3):
        try:
            await click_button(page, dropdown_selector)  # 드랍다운 버튼 클릭
            async with page.expect_request_finished(
                lambda request: request.method == "POST", timeout=4000
            ) as req:
                await click_button(page, value_selector)  # 드랍 다운에서 값 클릭
            print("Request Value: ", await req.value)

            break

        except Exception as e:
            if await click_popup(page):
                continue
            print(e)


async def click_semeseter_dropdown(page: Page):
    semester_drop_selector = 'input[role="combobox"][value$="학기"]'
    last_semester = USAINT_SEMESTER  # 초기 학기 값은 유세인트의 디폴트 값

    # 현재 로딩된 년도와 쿼리한 년도가 다른 경우
    async def wrapper(semester: int | str):
        semester_selector = (
            f'div[class~="lsListbox__value"][data-itemkey="09{semester}"]'
        )
        try:
            nonlocal last_semester
            if semester == last_semester:
                print(f"Skip semester click {semester}")
                return

            await click_dropdown(page, semester_drop_selector, semester_selector)
            last_semester = semester

        except Exception as e:
            print(e)

    return wrapper


async def click_year_dropdown(page: Page, year: int | str):
    """
    년도와 학기 설정을 위한 버튼을 클릭한다.

    Args:
        year (int, optional): 년도. Defaults to YEAR.
        semester (int, optional): 학기. Defaults to SEMESTER.
    """
    # 년도의 드랍다운 버튼과 년도 원소 셀렉터
    year_drop_selector = 'input[role="combobox"][value^="20"]'
    year_selector = f'div[class~="lsListbox__value"][data-itemkey="{year}"]'
    await click_dropdown(page, year_drop_selector, year_selector)
    await page.wait_for_load_state("domcontentloaded")


async def click_popup(page: Page):
    try:
        await page.click(".urPWFloatRight", timeout=1000)
        print("Click popup..")
        return True

    except Exception as e:
        print("No pop up...")
        return False
