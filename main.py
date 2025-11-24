# main.py

import time
import warnings
import random
import os
import logging
import sys
import traceback
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# [추가됨] EXE 실행 시 드라이버 자동 설치를 위해 필요
from webdriver_manager.chrome import ChromeDriverManager

from utility import chd_wh, clear_console, word_get, choice_class, choice_set
from learning_types import (
    memorization,
    recall,
    spelling,
    test,
    matching_game
)

a = input(
    """
    >>EULA<<
    
    이 프로그램은 테스트용으로 제작되었습니다.
    
    실제 수업에서의 사용을 절대 금합니다.
    
    계속하시겠습니까? (y/n): 
    """
    )

if a == "n":
    print("프로그램을 종료합니다.")
    quit()

clear_console()
print(r"""
   /$$$$$$              /$$                /$$$$$$                            /$$
  /$$__  $$            | $$               /$$__  $$                          | $$
 | $$  \ $$ /$$   /$$ /$$$$$$    /$$$$$$ | $$  \__/  /$$$$$$   /$$$$$$   /$$$$$$$
 | $$$$$$$$| $$  | $$|_  $$_/   /$$__  $$| $$       |____  $$ /$$__  $$ /$$__  $$
 | $$__  $$| $$  | $$  | $$    | $$  \ $$| $$        /$$$$$$$| $$  \__/| $$  | $$
 | $$  | $$| $$  | $$  | $$ /$$| $$  | $$| $$    $$ /$$__  $$| $$      | $$  | $$
 | $$  | $$|  $$$$$$/  |  $$$$/|  $$$$$$/|  $$$$$$/|  $$$$$$$| $$      |  $$$$$$$
 |__/  |__/ \______/    \___/   \______/  \______/  \_______/|__/       \_______/
 
 Version: 4.0.0 (Previously ClassCard Hack)
    """)

# 설정
warnings.filterwarnings("ignore")
logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--log-level=3')

# [수정됨] 드라이버 자동 설치 및 설정
# service = Service() <-- 기존 코드 대신 아래 코드 사용
try:
    service = Service(ChromeDriverManager().install())
except:
    # 혹시 설치 실패 시 기본 경로 시도 (비상용)
    service = Service()
    
driver = webdriver.Chrome(options=chrome_options, service=service)

clear_console()

# 로그인
print("로그인 페이지로 이동합니다. 수동으로 로그인해주세요.")
driver.get("https://www.classcard.net/Login")

try:
    WebDriverWait(driver, 120).until(
        lambda driver: driver.current_url != "https://www.classcard.net/Login" and "Login" not in driver.current_url
    )
    print("로그인 확인 완료! 잠시 대기...")
except TimeoutException:
    print("로그인 시간이 초과되었습니다.")
    driver.quit()
    quit()

def close_popups(driver):
    """화면을 가리는 팝업창들을 강제로 닫습니다."""
    try:
        driver.execute_script("""
            $('.modal').modal('hide');
            $('.btn-close').click();
            $('.close').click();
            $('#gb_ad_layer').remove();
            // 주의: 테스트 페이지의 중요 레이어도 .layer 클래스를 쓰므로 무조건 숨기면 안됨
            if (window.location.href.indexOf('ClassTest') === -1) {
                $('.layer').hide();
            }
            document.querySelectorAll('.modal, .overlay').forEach(p => p.style.display = 'none');
        """)
        time.sleep(0.2)
    except:
        pass

# 미완료 세트 탐색 함수
def find_uncompleted_sets(driver, class_id, sets_dict):
    print("\n[세트 목록]")
    print("0. 전체 선택")
    for idx, item in sets_dict.items():
        print(f"{idx + 1}. {item['title']}")

    print("\n🔍 미완료 세트 탐색을 시작합니다.")
    print("검사할 세트 범위를 입력하세요 (예: 1~10 또는 1,3,5 또는 0)")
    user_input = input("범위 입력: ").strip()
    
    target_indices = []
    if user_input == '0':
        target_indices = list(sets_dict.keys())
    else:
        try:
            parts = user_input.split(',')
            for part in parts:
                part = part.strip()
                if '~' in part:
                    start, end = map(int, part.split('~'))
                    target_indices.extend(range(start - 1, end))
                elif '-' in part:
                    start, end = map(int, part.split('-'))
                    target_indices.extend(range(start - 1, end))
                else:
                    target_indices.append(int(part) - 1)
        except:
            print("잘못된 입력입니다. 전체를 검사합니다.")
            target_indices = list(sets_dict.keys())
            
    target_indices = sorted(set([i for i in target_indices if i in sets_dict]))
    print(f"총 {len(target_indices)}개 세트를 검사합니다. 잠시만 기다려주세요...\n")

    uncompleted = {
        "Recall": [],
        "Spell": [],
        "Test": []
    }

    for i, idx in enumerate(target_indices):
        set_info = sets_dict[idx]
        set_id = set_info['set_id']
        title = set_info['title']
        
        # 세트 페이지로 이동
        url = f"https://www.classcard.net/set/{set_id}/{class_id}"
        driver.get(url)
        
        try:
            # 페이지 소스 파싱
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            is_fail = False
            fail_reasons = []

            # 1. 리콜 (100% 이상이어야 완료)
            recall_rate = 0
            recall_elem = soup.select_one(".recall-total-rate")
            if recall_elem and recall_elem.get('data-rate'):
                recall_rate = int(recall_elem['data-rate'])
            if recall_rate < 100:
                uncompleted["Recall"].append(str(idx+1))
                fail_reasons.append(f"리콜({recall_rate}%)")
                is_fail = True

            # 2. 스펠 (100% 이상이어야 완료)
            spell_rate = 0
            spell_elem = soup.select_one(".spell-total-rate")
            if spell_elem and spell_elem.get('data-rate'):
                spell_rate = int(spell_elem['data-rate'])
            if spell_rate < 100:
                uncompleted["Spell"].append(str(idx+1))
                fail_reasons.append(f"스펠({spell_rate}%)")
                is_fail = True

            # 3. 테스트 (100점이어야 완료)
            test_score = 0
            test_btn = soup.select_one(".btn-start-speedquiz .right")
            if test_btn:
                score_text = test_btn.text.strip()
                if "점" in score_text:
                    numbers = re.findall(r'\d+', score_text)
                    if numbers:
                        test_score = int(numbers[0])
            
            if test_score < 100:
                uncompleted["Test"].append(str(idx+1))
                fail_reasons.append(f"테스트({test_score}점)")
                is_fail = True
            
            # 로그 출력
            progress_msg = f"[{i+1}/{len(target_indices)}] {idx+1}번 확인: (R:{recall_rate}% S:{spell_rate}% T:{test_score}점)"
            
            if is_fail:
                print(f"\n   ⚠️ [미완료 감지] {idx+1}. {title} -> {', '.join(fail_reasons)}")
                print(progress_msg, end="\r")
            else:
                print(f"\r{progress_msg}", end="")

        except Exception as e:
            print(f"\n   [오류] {idx+1}번 세트 확인 실패: {e}")

    print("\n\n" + "="*40)
    print("         📝 미완료 세트 목록")
    print("="*40)
    if uncompleted["Recall"]:
        print(f"리콜: {', '.join(uncompleted['Recall'])}")
    if uncompleted["Spell"]:
        print(f"스펠: {', '.join(uncompleted['Spell'])}")
    if uncompleted["Test"]:
        print(f"테스트: {', '.join(uncompleted['Test'])}")
    
    if not any(uncompleted.values()):
        print("🎉 모든 학습이 완료되었습니다.")
        
    print("="*40 + "\n")
    
    # [수정됨] 미완료된 세트의 인덱스와 필요한 학습 유형을 반환
    # 반환 형식: {set_index: [type_code, ...]}
    uncompleted_map = {}
    
    # 리콜 (Code: 2)
    for idx_str in uncompleted["Recall"]:
        idx = int(idx_str) - 1
        if idx not in uncompleted_map: uncompleted_map[idx] = []
        uncompleted_map[idx].append(2)
        
    # 스펠 (Code: 3)
    for idx_str in uncompleted["Spell"]:
        idx = int(idx_str) - 1
        if idx not in uncompleted_map: uncompleted_map[idx] = []
        uncompleted_map[idx].append(3)
        
    # 테스트 (Code: 5)
    for idx_str in uncompleted["Test"]:
        idx = int(idx_str) - 1
        if idx not in uncompleted_map: uncompleted_map[idx] = []
        uncompleted_map[idx].append(5)
    
    # 각 세트별 학습 유형 정렬
    for idx in uncompleted_map:
        uncompleted_map[idx].sort()
    
    input("확인하셨으면 엔터를 눌러 학습 선택으로 이동하세요...")
    return uncompleted_map


def process_learning(driver, class_id, set_info, ch_d, time_1, time_2):
    set_id = set_info['set_id']
    print(f"\n>>> '{set_info['title']}' 준비 중...")
    
    # 1. 세트 페이지 이동
    driver.get(f"https://www.classcard.net/set/{set_id}/{class_id}")
    close_popups(driver)

    # 2. 단어 수집
    word_d = word_get(driver, 0)
    if not word_d:
        print("❌ 단어 데이터 수집 실패. 건너뜁니다.")
        return

    da_e, da_k, da_kn, da_kyn, da_ked, da_sd, da_e_clean, da_k_clean = word_d
    num_d = len(da_e) + 1

    # 3. 학습 페이지 진입
    print(f"🚀 학습 진입 버튼 클릭 시도 (유형: {ch_d})...")
    try:
        # 테스트(5번)일 때는 팝업 제거를 신중하게 함 (테스트 레이어 보호)
        if ch_d != 5: 
            close_popups(driver)
        
        # 버튼 선택자 (1암기, 4매칭 삭제됨)
        btn_selector = ""
        if ch_d == 2: btn_selector = ".btn-recall"
        elif ch_d == 3: btn_selector = ".btn-spell"
        elif ch_d == 5: btn_selector = ".btn-start-speedquiz"

        target_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, btn_selector))
        )
        driver.execute_script("arguments[0].click();", target_btn)
        print("   -> 클릭 성공! 화면 전환 대기...")
        time.sleep(4) 

    except Exception as e:
        print(f"❌ 진입 실패: {e}")
        return

    print(f"====== 학습 시작 ======\n")
    
    # 테스트(5번)일 때는 팝업 청소 생략
    if ch_d != 5: 
        close_popups(driver)

    if ch_d == 2:
        recall.run_recall(driver, num_d, da_e, da_kyn, time_2)
    elif ch_d == 3:
        spelling.run_spelling(driver, num_d, da_e, da_k)
    elif ch_d == 5:
        test.run_test(driver, num_d, da_e, da_k, da_kn, da_ked, time_1, da_e_clean, da_k_clean)

    print(f"\n====== 학습 완료 ======\n")
    time.sleep(1)


def main():
    time_1 = round(random.uniform(0.7, 1.3), 4)
    time_2 = round(random.uniform(1.7, 2.3), 4)

    try:
        # 클래스 선택
        class_dict = {}
        try:
            class_list_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".left-class-list"))
            )
            for i, class_item in enumerate(class_list_element.find_elements(By.TAG_NAME, "a")):
                class_temp = {"class_name": class_item.text}
                href = class_item.get_attribute("href")
                class_temp["class_id"] = href.split("/")[-1] if href else None
                
                if class_temp["class_id"] == "joinClass" or class_temp["class_id"] is None:
                    break
                class_dict[i] = class_temp
        except:
            print("클래스 목록을 찾지 못했습니다.")
            return
        
        if not class_dict:
            print("가입된 클래스가 없습니다.")
            return
            
        choice_class_val = choice_class(class_dict=class_dict) if len(class_dict) > 1 else 0
        class_id = class_dict[choice_class_val].get("class_id")
        
        driver.get(f"https://www.classcard.net/ClassMain/{class_id}")
        time.sleep(1)

        # 세트 선택
        sets_div = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/div[2]/div[3]/div")
        sets = sets_div.find_elements(By.CLASS_NAME, "set-items")
        sets_dict = {}
        for i, set_item in enumerate(sets):
            a_tag = set_item.find_element(By.TAG_NAME, "a")
            
            # [수정됨] 텍스트 중복 문제 해결을 위해 innerHTML 파싱
            a_html = a_tag.get_attribute('innerHTML')
            soup = BeautifulSoup(a_html, 'html.parser')
            
            # span 태그(카드 수) 제거 후 텍스트만 추출
            if soup.span:
                soup.span.decompose()
            
            title_text = soup.get_text(strip=True)
            
            # [수정됨] 카드 수에서 숫자만 추출 (예: "37 카드" -> "37")
            raw_card_num = a_tag.find_element(By.TAG_NAME, "span").text
            clean_card_num = re.sub(r'[^0-9]', '', raw_card_num)
            
            set_temp = {
                "card_num": clean_card_num,
                "title": title_text,
                "set_id": a_tag.get_attribute("data-idx")
            }
            sets_dict[i] = set_temp

        # 미완료 세트 확인
        check_uncompleted = input("\n미완료된 세트를 확인하시겠습니까? (y/n): ").lower()
        
        auto_learn_mode = False
        uncompleted_map = {}
        choice_set_vals = []
        
        if check_uncompleted == 'y':
            uncompleted_map = find_uncompleted_sets(driver, class_id, sets_dict)
            # 확인 후 다시 세트 목록 페이지로 복귀
            driver.get(f"https://www.classcard.net/ClassMain/{class_id}")
            time.sleep(1)
            
            if uncompleted_map:
                auto_learn = input(f"\n검색된 {len(uncompleted_map)}개의 미완료 세트를 바로 학습하시겠습니까? (y/n): ").lower()
                if auto_learn == 'y':
                    auto_learn_mode = True
                    print(f"▶ {len(uncompleted_map)}개 세트의 부족한 학습 유형을 자동으로 진행합니다.")

        if not auto_learn_mode:
            choice_set_vals = choice_set(sets_dict)
            ch_d_list = chd_wh()
            
            # 수동 모드 실행
            for ch_d in ch_d_list:
                for choice_set_val in choice_set_vals:
                    process_learning(driver, class_id, sets_dict[choice_set_val], ch_d, time_1, time_2)
        else:
            # 자동 학습 모드 실행 (부족한 유형만 골라서 학습)
            sorted_indices = sorted(uncompleted_map.keys())
            for set_idx in sorted_indices:
                required_types = uncompleted_map[set_idx]
                for ch_d in required_types:
                    process_learning(driver, class_id, sets_dict[set_idx], ch_d, time_1, time_2)

        print("\n✅ 모든 작업이 완료되었습니다.")

    except Exception as e:
        print("\n[치명적 오류 발생]")
        print(traceback.format_exc())
        input("엔터 키를 누르면 종료합니다...")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
