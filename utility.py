# utility.py
import time
import json
import re
import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import requests

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def word_get(driver, num_d) -> list:
    da_e, da_k, da_kn, da_kyn, da_ked, da_sd = [[""] * num_d for _ in range(6)]

    for i in range(1, num_d):
        da_e[i] = driver.find_element(By.XPATH,
            f"//*[@id='tab_set_all']/div[2]/div[{i}]/div[4]/div[1]/div[1]/div/div"
        ).text
        # 원본 그대로 저장 (구분자/공백 제거하지 않음)

    # print("[DEBUG] 저장된 영어 단어 리스트:", da_e)

    try:
        for i in range(1, num_d):
            url = driver.find_element(By.XPATH, f"//*[@id='tab_set_all']/div[2]/div[{i}]/div[4]/div[1]/div[3]/a").get_attribute('data-src')
            lv = [part for part in url.split("/") if part]
            upload_index = next((index for index, part in enumerate(lv) if "uploads" in part), None)
            if upload_index is not None:
                lv = lv[upload_index:]
            da_sd[i] = "/" + "/".join(lv)
    except NoSuchElementException:
        pass

    driver.find_element(By.CSS_SELECTOR,
        "#tab_set_all > div.card-list-title > div > div:nth-child(1) > a"
    ).click()
    time.sleep(0.5)
    
    for i in range(1, num_d):
        ko_d = driver.find_element(By.XPATH,
            f"//*[@id='tab_set_all']/div[2]/div[{i}]/div[4]/div[2]/div[1]/div/div"
        ).text
        ko_d = ko_d.split("\n")
        #명. 동. 형. 부. 와 같은 품사 표기 제거(options)
        POS_MARKERS = ['명', '동', '형', '부'] 
        pattern = r'\b(?:' + '|'.join(POS_MARKERS) + r')\.\s*'
        edit_ko_d = [re.sub(pattern, '', line) for line in ko_d]

        if len(ko_d) == 1:
            da_k[i] = ko_d[0]
            da_kn[i] = ko_d[0]
            da_kyn[i] = ko_d[0]
            da_ked[i] = edit_ko_d[0]
        else:
            da_k[i] = "\n".join(ko_d)
            da_kn[i] = ", ".join(ko_d)
            da_kyn[i] = " ".join(ko_d)
            da_ked[i] = ", ".join(edit_ko_d)

    da_e_clean = [re.sub(r'[;,	\s]+', '', e) for e in da_e]  # 혹시 남아있으면
    da_e_clean = [re.sub(r'[;,\s]+', '', e) for e in da_e]  # 최종적으로 nul문자 없이
    da_k_clean = [re.sub(r'[;,\s]+', '', k) for k in da_k]
    # ...
    # print("[DEBUG] 저장된 영어 단어 리스트:", da_e)
    # print("[DEBUG] 저장된 한글 뜻 리스트:", da_k)
    # print("[DEBUG] 테스트용 영어 단어 리스트:", da_e_clean)
    # print("[DEBUG] 테스트용 한글 뜻 리스트:", da_k_clean)
    return [da_e, da_k, da_kn, da_kyn, da_ked, da_sd, da_e_clean, da_k_clean]

def chd_wh() -> list[int]:
    print(
        """
주의사항: 능률보카 단어장으로만 테스트되었습니다.
가끔가다가 중간에 몇개씩 틀릴수도 있는데 그냥 넘어가주세요.
(저도 이유를 모르거든요 ㅎ)
---------------------------
학습 유형을 선택해주세요!!
[1] 암기학습(API 요청 변조)(작동 보장 X)
[2] 리콜학습(API 요청 변조)(작동 보장 X)
[3] 스펠학습(API 요청 변조)(작동 보장 X)
[4] 매칭게임(API 요청 변조)(작동 보장 X)
[5] 테스트학습(매크로)
[6] QuizBattle(매크로)(작동 보장 X)
[7] 암기학습(매크로)(작동 보장 X)
[8] 리콜학습(매크로)
[9] 스펠학습(매크로)
[10] 매칭게임(매크로)(작동 보장 X)
---------------------------
Developed by NellLucas(서재형)
Fixed by Fixed by SD HS Student
    """
    )
    while True:
        try:
            ch_s = input("학습 유형 번호를 선택하세요 (여러 개는 콤마로 구분, 예: 8,9,5): ").strip()
            nums = [int(part.strip()) for part in ch_s.split(",")]
            if all(1 <= n <= 10 for n in nums):
                break
            else:
                raise ValueError
        except ValueError:
            print("올바른 학습 유형(1~10)을 콤마로 구분해서 입력해주세요. 예: 8,9,5")
        except KeyboardInterrupt:
            print("\n사용자에 의해 종료되었습니다.")
            quit()
    return nums

def choice_set(sets: dict) -> list[int]:
    clear_console()
    print("학습할 세트를 선택해주세요. (여러 개는 쉼표로 구분, 범위는 ~로, 전체는 'all')")
    print("예: 1,3~5,7  또는  all")
    print("Ctrl + C 를 눌러 종료")
    for idx, set_item in sets.items():
        print(f"[{idx+1}] {set_item.get('title')} | {set_item.get('card_num')}")
    while True:
        try:
            ch_s = input(">>> ").strip().lower()
            if ch_s == "all":
                selected = list(range(len(sets)))
                break
            else:
                nums = []
                for part in ch_s.split(","):
                    part = part.strip()
                    if "~" in part:
                        start, end = part.split("~")
                        start, end = int(start), int(end)
                        if start > end:
                            raise ValueError
                        nums.extend(list(range(start, end+1)))
                    else:
                        nums.append(int(part))
                if all(1 <= n <= len(sets) for n in nums):
                    selected = sorted(set(n - 1 for n in nums))
                    break
                else:
                    raise ValueError
        except ValueError:
            print("세트 번호를 올바르게 입력해주세요. 예: 1,3~5,7 또는 all")
        except KeyboardInterrupt:
            quit()
    clear_console()
    selected_names = ", ".join([sets[n].get("title") for n in selected])
    print(f"선택한 세트: {selected_names}")
    return selected

def choice_class(class_dict: dict) -> int:
    os.system("cls")
    print("학습할 클래스를 선택해주세요.")
    print("Ctrl + C 를 눌러 종료")
    for class_item in class_dict:
        print(f"[{class_item+1}] {class_dict[class_item].get('class_name')}")
    while True:
        try:
            ch_c = int(input(">>> "))
            if ch_c >= 1 and ch_c <= len(class_dict):
                break
            else:
                raise ValueError
        except ValueError:
            print("클래스를 다시 입력해주세요.")
        except KeyboardInterrupt:
            quit()
    os.system("cls")
    print(f"{class_dict[ch_c-1].get('class_name')}를 선택하셨습니다.")
    return ch_c - 1

def classcard_api_post(
    user_id: int,
    set_id: int,
    class_id: int,
    view_cnt: int,
    activity: int,
) -> None:
    url = "https://www.classcard.net/ViewSetAsync/resetAllLog"
    payload = f"set_idx={set_id}&activity={activity}&user_idx={user_id}&view_cnt={view_cnt}&class_idx={class_id}"
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    requests.request("POST", url, data=payload, headers=headers)
    print("API 요청 변조에 성공하였습니다!")
