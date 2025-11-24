# learning_types/recall.py
import time
import random
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

def normalize_text(text):
    """텍스트 정규화"""
    if not text: return ""
    text = re.sub(r'[^\w\s가-힣]', '', text)
    return text.replace(" ", "").replace("\n", "").lower()

def run_recall(driver, num_d, da_e, da_kyn, time_2):
    print("\n[리콜 학습] 키보드 입력 모드 (로그 숨김)...")
    
    # 1. 학습 시작 버튼 처리
    try:
        start_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-opt-start"))
        )
        start_btn.click()
        # print("   -> 학습 시작 버튼 클릭")
    except:
        pass

    time.sleep(2)
    
    # 데이터 정규화
    norm_da_e = [normalize_text(x) for x in da_e]
    norm_da_k = [normalize_text(x) for x in da_kyn]
    
    current_index = 1
    
    while True:
        try:
            # (1) 종료 감지
            try:
                if driver.find_elements(By.ID, "study_end") and driver.find_element(By.ID, "study_end").is_displayed():
                    print("\n✅ 리콜 학습 완료.")
                    break
            except:
                pass

            # (2) 현재 카드 찾기
            current_card = None
            try:
                current_card = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".CardItem.showing"))
                )
            except:
                time.sleep(1)
                continue

            # (3) 문제 읽기
            q_text = ""
            try:
                q_box = current_card.find_element(By.CSS_SELECTOR, ".card-top .text-normal")
                q_text = normalize_text(q_box.text)
            except:
                time.sleep(0.5)
                continue

            # (4) 보기 요소 찾기
            choices = current_card.find_elements(By.CSS_SELECTOR, ".card-quest-front .back-quest")
            
            if not choices:
                time.sleep(0.5)
                continue

            # (5) 정답 인덱스 찾기
            target_index = -1
            
            # [치트키]
            for i, choice in enumerate(choices):
                if "answer" in choice.get_attribute("class"):
                    target_index = i
                    # print(f"   [{current_index}] 정답 발견(치트): {i+1}번")
                    break
            
            # [정공법]
            if target_index == -1:
                ans_norm = "unknown"
                if q_text in norm_da_e:
                    idx = norm_da_e.index(q_text)
                    ans_norm = norm_da_k[idx]
                elif q_text in norm_da_k:
                    idx = norm_da_k.index(q_text)
                    ans_norm = norm_da_e[idx]
                
                if ans_norm != "unknown":
                    for i, choice in enumerate(choices):
                        try:
                            c_text = normalize_text(choice.find_element(By.CSS_SELECTOR, ".card-quest-list").text)
                            if ans_norm in c_text or c_text in ans_norm:
                                target_index = i
                                # print(f"   [{current_index}] 정답 발견(매칭): {i+1}번")
                                break
                        except:
                            continue

            # (6) 키보드 입력
            actions = ActionChains(driver)
            
            if target_index != -1:
                key_to_press = str(target_index + 1)
                actions.send_keys(key_to_press).perform()
            else:
                # 랜덤
                random_key = str(random.randint(1, len(choices)))
                # print(f"   [{current_index}] 랜덤 입력: {random_key}번")
                actions.send_keys(random_key).perform()
            
            current_index += 1
            time.sleep(1) 

        except Exception as e:
            time.sleep(1)
            continue

    print("[리콜 학습] 종료")
    time.sleep(2)
    
    try:
        if driver.find_elements(By.CSS_SELECTOR, ".btn-study-end-next-section1"):
             driver.execute_script("document.querySelector('.btn-study-end-next-section1').click();")
        else:
             driver.execute_script("document.querySelector('.btn-exit').click();")
    except:
        pass
