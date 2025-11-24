# learning_types/test.py
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

def run_test(driver, num_d, da_e, da_k, da_kn, da_ked, time_1, da_e_clean, da_k_clean):
    print("[테스트 학습] 점수 자동 확인 모드...")

    # ==================================================
    # 1단계: [다음] 버튼 (재응시 화면일 경우)
    # ==================================================
    try:
        print("   [1/4] '다음' 버튼 확인 중...")
        next_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".layer.retry-layer .btn-condition-next"))
        )
        driver.execute_script("arguments[0].click();", next_btn)
        print("   -> '다음' 클릭 완료.")
        #time.sleep(2) 
    except TimeoutException:
        print("   -> '다음' 버튼 없음 (패스)")
    except Exception as e:
        print(f"   -> [체크] 다음 버튼: {e}")

    # ==================================================
    # 2단계: [테스트 시작] 버튼
    # ==================================================
    try:
        print("   [2/4] '테스트 시작' 버튼 확인 중...")
        start_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".layer.prepare-layer .btn-quiz-start"))
        )
        driver.execute_script("arguments[0].classList.remove('disabled'); arguments[0].click();", start_btn)
        print("   -> '테스트 시작' 클릭 완료.")
        time.sleep(1) 
    except TimeoutException:
        try:
            alt_btn = driver.find_element(By.CSS_SELECTOR, ".btn-test-start")
            driver.execute_script("arguments[0].click();", alt_btn)
            print("   -> (대체) '테스트 시작' 클릭.")
            time.sleep(1)
        except:
            print("   -> '시작' 버튼 못 찾음 (이미 진행 중?)")

    # ==================================================
    # 3단계: [재응시] 팝업 확인
    # ==================================================
    try:
        print("   [3/4] 재응시 팝업 확인 중...")
        confirm_modal = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.ID, "confirmModal"))
        )
        if confirm_modal.is_displayed():
            print("   -> [알림] 팝업 감지. 버튼 클릭.")
            ok_btn = confirm_modal.find_element(By.CSS_SELECTOR, ".btn-ok")
            driver.execute_script("arguments[0].click();", ok_btn)
            time.sleep(1)
    except:
        pass

    # ==================================================
    # 4단계: [새로 시작] 팝업 확인
    # ==================================================
    try:
        print("   [4/4] '새로 시작' 팝업 확인 중...")
        # 모달이 여전히 떠있는지 확인
        if driver.find_element(By.ID, "confirmModal").is_displayed():
            danger_btn = driver.find_element(By.CSS_SELECTOR, "#confirmModal .btn-danger")
            if danger_btn.is_displayed():
                print("   -> [알림] '새로 시작' 버튼 클릭.")
                driver.execute_script("arguments[0].click();", danger_btn)
                #time.sleep(2)
    except:
        pass

    # ==================================================
    # 5단계: 문제 풀이 (점수 감지 기능 추가)
    # ==================================================
    print("\n[진행] 문제 풀이 시작!")
    
    norm_da_e = [normalize_text(x) for x in da_e]
    norm_da_k = [normalize_text(x) for x in da_k]

    while True:
        try:
            # (1) ★ [핵심 수정] 종료 및 점수 감지
            # 점수판 타이틀: .test-end-msg-title (예: "97점이에요!")
            try:
                score_ele = driver.find_elements(By.CSS_SELECTOR, ".test-end-msg-title")
                if score_ele and score_ele[0].is_displayed():
                    score_text = score_ele[0].text.strip()
                    print(f"\n✅ 테스트 종료! 획득 점수: {score_text}")
                    break
                
                # 혹은 URL이나 일반 종료 화면 감지
                if driver.find_elements(By.CLASS_NAME, "test-score-body") or "score" in driver.current_url:
                    print("\n✅ 테스트 종료 화면 감지.")
                    break
            except:
                pass

            # (2) 문제 찾기
            try:
                current_card = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".flip-card.showing"))
                )
                q_box = current_card.find_element(By.CSS_SELECTOR, ".flip-card-front .box")
                q_text = normalize_text(q_box.text)
            except:
                time.sleep(1)
                continue

            # (3) 정답 찾기
            ans_norm = "unknown"
            ans_raw = None

            if q_text in norm_da_e:
                idx = norm_da_e.index(q_text)
                ans_norm = normalize_text(da_k[idx])
                ans_raw = da_k[idx]
            elif q_text in norm_da_k:
                idx = norm_da_k.index(q_text)
                ans_norm = normalize_text(da_e[idx])
                ans_raw = da_e[idx]
            else:
                for i, k in enumerate(norm_da_k):
                    if q_text in k:
                        ans_norm = normalize_text(da_e[i])
                        ans_raw = da_e[i]
                        break
                if ans_norm == "unknown":
                    for i, e in enumerate(norm_da_e):
                        if q_text in e:
                            ans_norm = normalize_text(da_k[i])
                            ans_raw = da_k[i]
                            break

            # (4) 뒤집기
            ActionChains(driver).send_keys(Keys.SPACE).perform()
            time.sleep(0.5)

            # (5) 정답 클릭
            labels = current_card.find_elements(By.CSS_SELECTOR, ".flip-card-back label")
            
            if labels:
                clicked = False
                # 1차: 정확 일치
                for lbl in labels:
                    lbl_text = normalize_text(lbl.text)
                    if ans_norm == lbl_text:
                        driver.execute_script("arguments[0].click();", lbl)
                        clicked = True
                        break
                # 2차: 부분 일치
                if not clicked and ans_norm != "unknown":
                    for lbl in labels:
                        lbl_text = normalize_text(lbl.text)
                        if len(ans_norm) > 1 and (ans_norm in lbl_text or lbl_text in ans_norm):
                            driver.execute_script("arguments[0].click();", lbl)
                            clicked = True
                            break
                
                if not clicked:
                    random.choice(labels).click()

            else:
                try:
                    input_box = current_card.find_element(By.CSS_SELECTOR, "input.subjective-input")
                    if ans_raw:
                        input_box.clear()
                        input_box.send_keys(ans_raw)
                        input_box.send_keys(Keys.ENTER)
                except:
                    pass

            time.sleep(1.5)

        except Exception:
            time.sleep(1)
            continue

    print("[테스트 학습] 프로세스 종료")
    #time.sleep(1)
    
    # 결과 화면 나가기
    try:
        driver.execute_script("document.querySelector('.btn-exit').click();")
    except:
        pass
