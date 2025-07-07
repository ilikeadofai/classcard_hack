# main.py

import time
from turtle import clear
import warnings
import random
import json
import os
import logging
import sys

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from utility import chd_wh, clear_console, word_get, choice_class, choice_set, classcard_api_post
from learning_types import (
    memorization,
    recall,
    spelling,
    test,
    matching_game,
    matching_game_API,
    quiz_battle
)

a = input(
    """
    ---------------------------------------------이용 약관-----------------------------------------------
    이 프로그램은 교육용 목적으로 만들어졌습니다. 절대 실제 수업에서의 사용을 금지합니다. 계속하시겠습니까? (y/n): 
    ----------------------------------------------------------------------------------------------------
    """
    )

if a == "n":
    print("프로그램을 종료합니다.")
    quit()

clear_console()

print(
        """

        -----------------------------------
        Classcard Hack v3.1.0
        -----------------------------------

        Developed by NellLucas(서재형)
        Fixed by SD HS Student

        몇가지 오류 메세지, 로그가 떠도 무시하세요
        작동만 되면 되잖아요 ㅎㅎ

        """
)

time.sleep(2)

# 경고 및 로그 suppress
warnings.filterwarnings("ignore")
logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

# config.json에서 계정 정보 읽기 (없으면 생성)
if not os.path.exists("config.json"):
    print("config.json 파일이 없습니다. 계정 정보를 입력해 주세요.")
    id_val = input("아이디를 입력하세요: ").strip()
    pw_val = input("비밀번호를 입력하세요: ").strip()
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump({"id": id_val, "pw": pw_val}, f, ensure_ascii=False, indent=4)

with open("config.json", "r", encoding="utf-8") as f:
    account = json.load(f)

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--log-level=3')  # 오류만 출력

# 드라이버 생성 (로그 파일도 버림)
original_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")
service = Service(log_path=os.devnull)
driver = webdriver.Chrome(options=chrome_options, service=service)
sys.stdout.close()
sys.stdout = original_stdout

# 자동 로그인
print("자동 로그인을 진행합니다...")
driver.get("https://www.classcard.net/Login")
id_element = driver.find_element(By.NAME, "login_id")
pw_element = driver.find_element(By.NAME, "login_pwd")
id_element.clear()
id_element.send_keys(account["id"])
pw_element.send_keys(account["pw"])
time.sleep(1)
driver.find_element(By.LINK_TEXT, "로그인").click()
time.sleep(1)

def main():
    try:
        while True:
            # account = get_id()  # 삭제
            
            time_1 = round(random.uniform(0.7, 1.3), 4)
            time_2 = round(random.uniform(1.7, 2.3), 4)

            class_dict = {}
            class_list_element = driver.find_element(
                By.CSS_SELECTOR,
                "body > div.mw-1080 > div:nth-child(6) > div > div > div.left-menu > div.left-item-group.p-t-none.p-r-lg > div.m-t-sm.left-class-list",
            )
            for class_item, i in zip(
                class_list_element.find_elements(By.TAG_NAME, "a"),
                range(len(class_list_element.find_elements(By.TAG_NAME, "a"))),
            ):
                class_temp = {}
                class_temp["class_name"] = class_item.text
                class_temp["class_id"] = class_item.get_attribute("href").split("/")[-1]
                if class_temp["class_id"] == "joinClass":
                    break
                class_dict[i] = class_temp

            if len(class_dict) == 0:
                print("클래스가 없습니다.")
                quit()
            elif len(class_dict) == 1:
                choice_class_val = 0
            else:
                choice_class_val = choice_class(class_dict=class_dict)
            class_id = class_dict[choice_class_val].get("class_id")

            driver.get(f"https://www.classcard.net/ClassMain/{class_id}")
            time.sleep(1)

            sets_div = driver.find_element(
                By.XPATH, "/html/body/div[1]/div[2]/div/div/div[2]/div[3]/div"
            )
            sets = sets_div.find_elements(By.CLASS_NAME, "set-items")
            sets_dict = {}
            for set_item, i in zip(sets, range(len(sets))):
                a_tag = set_item.find_element(By.TAG_NAME, "a")
                set_temp = {}
                set_temp["card_num"] = a_tag.find_element(By.TAG_NAME, "span").text
                set_temp["title"] = a_tag.text.replace(set_temp["card_num"], "")
                set_temp["set_id"] = a_tag.get_attribute("data-idx")
                sets_dict[i] = set_temp

            choice_set_vals = choice_set(sets_dict)
            ch_d_list = chd_wh()  # 여러 개 선택 가능
            for ch_d in ch_d_list:
                for choice_set_val in choice_set_vals:
                    set_site = (
                        f"https://www.classcard.net/set/{sets_dict[choice_set_val]['set_id']}/{class_id}"
                    )
                    driver.get(set_site)
                    time.sleep(1)

                    user_id = int(driver.execute_script("return c_u;"))

                    driver.find_element(By.CSS_SELECTOR,
                        "body > div.test > div.p-b-sm > div.set-body.m-t-25.m-b-lg > div.m-b-md > div > a"
                    ).click()
                    driver.find_element(By.CSS_SELECTOR,
                        "body > div.test > div.p-b-sm > div.set-body.m-t-25.m-b-lg > div.m-b-md > div > ul > li:nth-child(1)"
                    ).click()

                    html = BeautifulSoup(driver.page_source, "html.parser")
                    cards_ele = html.find("div", class_="flip-body")
                    num_d = len(cards_ele.find_all("div", class_="flip-card")) + 1

                    time.sleep(0.5)

                    word_d = word_get(driver, num_d)
                    da_e, da_k, da_kn, da_kyn, da_ked, da_sd, da_e_clean, da_k_clean = word_d

                    print(f"\n====== '{sets_dict[choice_set_val]['title']}' 세트 학습 시작 ======\n")

                    if ch_d == 1:
                        print("암기학습 API 요청 변조 시작")
                        classcard_api_post(user_id, sets_dict[choice_set_val]["set_id"], class_id, num_d, activity=1)
                    elif ch_d == 2:
                        print("리콜학습 API 요청 변조 시작")
                        classcard_api_post(user_id, sets_dict[choice_set_val]["set_id"], class_id, num_d, activity=2)
                    elif ch_d == 3:
                        print("스펠학습 API 요청 변조 시작")
                        classcard_api_post(user_id, sets_dict[choice_set_val]["set_id"], class_id, num_d, activity=3)
                    elif ch_d == 4:
                        match_site = f"https://www.classcard.net/Match/{sets_dict[choice_set_val]['set_id']}?c={class_id}"
                        driver.get(match_site)
                        matching_game_API.run_matching_game_api(driver, match_site)
                    elif ch_d == 5:
                        test.run_test(driver, num_d, da_e, da_k, da_kn, da_ked, time_1, da_e_clean, da_k_clean)
                    elif ch_d == 6:
                        quiz_battle.run_quiz_battle(driver, da_e, da_k, da_sd)
                    elif ch_d == 7:
                        memorization.run_memorization(driver, num_d)
                    elif ch_d == 8:
                        recall.run_recall(driver, num_d, da_e, da_kyn, time_2)
                    elif ch_d == 9:
                        spelling.run_spelling(driver, num_d, da_e, da_k)
                    elif ch_d == 10:
                        matching_game.run_matching_game(driver, da_e, da_k)
                    else:
                        print("잘못된 학습 유형, 프로그램 종료")
                        break

                    print(f"\n====== '{sets_dict[choice_set_val]['title']}' 세트 학습 완료 ======\n")
                    time.sleep(1)

            print("\n✅ 모든 선택한 세트 학습이 완료되었습니다.")
            again = input("다른 세트도 학습하시겠습니까? (y/n): ").strip().lower()
            if again != 'y':
                print("프로그램을 종료합니다.")
                break
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

#hello ;) just a easter egg