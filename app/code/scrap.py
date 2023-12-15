import asyncio

from code.page_action import *
from code.page_load import *
import code.parse as parse
from code.constant import *
from code.cookies import get_cookies


async def get_page_grades(page: Page):
    grade_table_selector = 'tbody[id^="WD0"]'
    inner_texts = await get_inner_texts(page, grade_table_selector)

    columns = ["이수학년도", "이수학기", "과목코드", "과목명", "과목학점", "성적", "등급", "교수명", "비고"]
    unused_coumnls = set(("비고"))  # 사용 안하는 속성들

    res = parse.parse_table(
        inner_texts, columns, unused_coumnls
    )  # 텍스트를 JSON형식의 딕셔너리로 파싱합니다.
    return res


async def scrap_stat(page: Page):
    status_table_selector = 'tbody[id^="WD5"]'
    columns = [
        "학년도",
        "학기",
        "신청학점",
        "취득학점",
        "P/F학점",
        "평점평균",
        "평점계",
        "산술평균",
        "학기별석차",
        "전체석차",
        "상담여부",
        "유급",
    ]
    inner_texts = await get_inner_texts(page, status_table_selector)
    res = parse.parse_table(inner_texts, columns)
    return res


async def scrap_year_grades(page: Page, semesters: list) -> list[dict]:
    year_grades = []
    for semester in semesters:
        await click_semeseter_dropdown(page, semester)
        year_grades.extend(await get_page_grades(page))

    return year_grades


async def new_tab_scrap_year_grades(
    cookie_list: list[dict], year: str, semesters: list
):
    async with open_browser() as browser:
        page = await load_usaint_page(browser, cookie_list)
        await click_year_dropdown(page, year)
        grade = await scrap_year_grades(page, semesters)
        return grade


async def scrap_all_grades(page: Page, attendence_info: dict):
    total_grades = []
    for year, semesters in attendence_info.items():
        if year != YEAR:
            await click_year_dropdown(page, year)
        year_grades = await scrap_year_grades(page, semesters)
        total_grades.extend(year_grades)
    return total_grades


async def new_tab_scrap_all_grades(
    attendence_info: dict, cookie_list: list[dict]
) -> list[dict]:
    """
    복수 개의 브라우저에서 해당 년도의 성적을 가져온다.
    """
    total_grades = []
    tasks = [
        asyncio.create_task(new_tab_scrap_year_grades(cookie_list, year, semesters))
        for year, semesters in attendence_info.items()
    ]
    total_grades = await asyncio.gather(*tasks)
    return total_grades


async def run_multy_browser_scrapl_all_grades(student_number: str):
    total_grades = []
    async with open_browser() as browser:
        cookie_list = get_cookies(student_number)  # 로그인에 필요한 쿠키 데이터
        page = await load_usaint_page(browser, cookie_list)
        stats = await scrap_stat(page)  # 현재까지의 학적 정보 가져옴
        attendence_info = parse.parse_attenedence(stats)
        years = list(attendence_info.keys())
        first_year = years[0]

        task = asyncio.create_task(scrap_year_grades(page, attendence_info[first_year]))

        if len(years) > 1:
            attendence_info = {
                k: v for k, v in attendence_info.items() if k != first_year
            }
            grades = await new_tab_scrap_all_grades(attendence_info, cookie_list)
            total_grades.extend(grades)

        total_grades.extend(await task)
        return total_grades


async def run_single_browser_scrap_now(student_number: str):
    cookie_list = get_cookies(student_number)
    async with open_browser() as browser:
        page = await load_usaint_page(browser, cookie_list)
        grades = await get_page_grades(page)
        return grades


async def run_single_browser_scrap_all(student_number: str):
    cookie_list = get_cookies(student_number)
    async with open_browser() as browser:
        page = await load_usaint_page(browser, cookie_list)
        stats = await scrap_stat(page)
        attened_semester = parse.parse_attenedence(stats)
        grades = await scrap_all_grades(page, attened_semester)
        return grades