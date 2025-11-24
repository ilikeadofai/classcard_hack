# utility.py
import time
import os
import random
import json
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def choice_class(class_dict):
    print("\n[클래스 선택]")
    for idx, item in class_dict.items():
        print(f"{idx + 1}. {item['class_name']}")
    
    while True:
        try:
            choice = int(input("\n클래스 번호를 입력하세요: ")) - 1
            if choice in class_dict:
                return choice
            print("잘못된 번호입니다.")
        except ValueError:
            print("숫자를 입력해주세요.")

def choice_set(sets_dict):
    print("\n[세트 선택]")
    print("0. 전체 선택")
    for idx, item in sets_dict.items():
        print(f"{idx + 1}. {item['title']} ({item['card_num']} 카드)")
    
    while True:
        try:
            print("\n[입력 예시] 1,3 (개별) 또는 32~61 (범위) 또는 1-5")
            user_input = input("세트 번호를 선택하세요: ")
            
            if user_input.strip() == '0':
                return list(sets_dict.keys())
            
            choices = []
            parts = user_input.split(',')
            
            for part in parts:
                part = part.strip()
                if '~' in part:
                    start, end = map(int, part.split('~'))
                    choices.extend(range(start - 1, end))
                elif '-' in part:
                    start, end = map(int, part.split('-'))
                    choices.extend(range(start - 1, end))
                else:
                    choices.append(int(part) - 1)

            choices = sorted(list(set(choices)))
            valid_choices = [c for c in choices if c in sets_dict]
            
            if valid_choices:
                print(f"▶ 선택된 세트 개수: {len(valid_choices)}개")
                return valid_choices
                
            print("선택 가능한 번호가 없습니다.")
            
        except ValueError:
            print("잘못된 입력 형식입니다.")

def chd_wh():
    print("\n[학습 유형 선택]")
    print("2. 리콜 (Recall)")
    print("3. 스펠 (Spell)")
    print("5. 테스트 (Test)")
    
    while True:
        try:
            user_input = input("\n학습 유형 번호를 선택하세요 (여러 개는 콤마로 구분, 예: 2,3,5): ")
            choices = [int(x.strip()) for x in user_input.split(',')]
            if all(c in [2, 3, 5] for c in choices):
                return choices
            print("2, 3, 5 중에서 선택해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")

def word_get(driver, num_d):
    try:
        wait = WebDriverWait(driver, 10)
        
        # 1. 목록 버튼 클릭 (시도)
        try:
            btn_view = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.set-body div.m-b-md > div > a")
            ))
            btn_view.click()
            time.sleep(1)
        except:
            pass

        # 2. JS 데이터 추출 (1순위)
        raw_data = driver.execute_script("return (typeof study_data !== 'undefined') ? study_data : null;")
        
        da_e, da_k, da_kn, da_kyn, da_ked, da_sd = [], [], [], [], [], []
        da_e_clean, da_k_clean = [], []

        if raw_data:
            print(f"   -> 원본 데이터 추출 성공: {len(raw_data)}개")
            for item in raw_data:
                e = item.get('front', '')
                k = item.get('back', '')
                da_e.append(e)
                da_k.append(k)
                da_kyn.append(k)
                da_e_clean.append(e)
                da_k_clean.append(k)
            return da_e, da_k, da_kn, da_kyn, da_ked, da_sd, da_e_clean, da_k_clean

        # 3. HTML 파싱 (2순위)
        print("   [주의] JS 데이터 없음. HTML 파싱 시도...")
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        items = soup.select('.flip-card')
        if not items: items = soup.select('.CardItem')
        
        for item in items:
            try:
                front_el = item.select_one('.card-front .card-content') or item.select_one('.front') or item.select_one('.card-top .card-content')
                back_el = item.select_one('.card-back .card-content') or item.select_one('.back') or item.select_one('.card-bottom .card-content')
                
                if front_el and back_el:
                    e = front_el.text.strip()
                    k = back_el.text.strip()
                    da_e.append(e)
                    da_k.append(k)
                    da_kyn.append(k)
                    da_e_clean.append(e)
                    da_k_clean.append(k)
            except:
                continue

        print(f"   -> HTML 파싱 완료: {len(da_e)}개")
        
        if not da_e: return None
        return da_e, da_k, da_kn, da_kyn, da_ked, da_sd, da_e_clean, da_k_clean

    except Exception as e:
        print(f"   [데이터 수집 오류] {e}")
        return None
