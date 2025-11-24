# learning_types/spelling.py
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

def run_spelling(driver, num_d, da_e, da_k):
    print(f"\n[스펠 학습] 사용자 최적화 (0.5초) 모드...")
    # print(f"※ 목표: {num_d-1}개 단어")

    # 1. 학습 시작 버튼 처리
    try:
        start_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-opt-start"))
        )
        start_btn.click()
        # print("학습 시작 버튼 클릭됨")
    except:
        pass
    
    time.sleep(2)

    # 2. 정답 데이터 로드
    try:
        raw_data = driver.execute_script("return study_data;")
        answer_map = {item['card_idx']: item['front'] for item in raw_data}
        # print(f"[시스템] 정답 데이터 {len(answer_map)}개 로드 완료")
    except Exception as e:
        print(f"[오류] 정답 데이터 로드 실패: {e}")
        return

    # 3. 학습 루프
    last_card_id = None
    wait_tick = 0
    
    success_count = 0
    total_count = len(answer_map)

    while True:
        try:
            # (1) 종료 감지
            if driver.find_elements(By.ID, "study_end") and driver.find_element(By.ID, "study_end").is_displayed():
                print("\n✅ 학습이 완료되었습니다. (종료 화면 감지)")
                break
            if driver.find_elements(By.CLASS_NAME, "study-end-body") and driver.find_element(By.CLASS_NAME, "study-end-body").is_displayed():
                print("\n✅ 학습이 완료되었습니다. (종료 화면 감지)")
                break

            # (2) 새 카드 찾기
            current_card = None
            new_card_id = None
            
            cards = driver.find_elements(By.CSS_SELECTOR, "div.CardItem.showing")
            
            if not cards:
                time.sleep(0.5)
                continue

            # 방금 푼 카드(last_card_id)가 아닌 녀석을 찾음
            for card in cards:
                try:
                    idx = card.get_attribute("data-idx")
                    if idx != last_card_id:
                        current_card = card
                        new_card_id = idx
                        break
                except StaleElementReferenceException:
                    continue 

            # 새 카드를 못 찾았으면 대기
            if current_card is None:
                wait_tick += 1
                if wait_tick > 20: 
                    # print("   🚨 갇힘 감지. 스페이스바 입력.")
                    ActionChains(driver).send_keys(Keys.SPACE).perform()
                    wait_tick = 0
                time.sleep(0.5) 
                continue
            
            # 새 카드 발견!
            wait_tick = 0
            time.sleep(0.5) 

            # (3) 정답 가져오기
            answer = answer_map.get(new_card_id, "unknown")
            if answer == "unknown":
                # print("   정답 모름 -> 엔터")
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                last_card_id = new_card_id
                continue

            # (4) 정답 주입 (JS Native Setter)
            try:
                target_input = driver.execute_script("""
                    var card = arguments[0];
                    if (!card || !document.body.contains(card)) return null;

                    var input = card.querySelector(".card-bottom input[name='input_answer']");
                    if (!input) return null;
                    
                    var answer = arguments[1];

                    input.disabled = false;
                    input.readOnly = false;
                    input.style.display = 'block';

                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeInputValueSetter.call(input, answer);

                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    return input;
                """, current_card, answer)

                if target_input:
                    # print(f"   -> '{answer}' 주입 완료")
                    time.sleep(0.5) 
                    
                    # (5) 엔터
                    actions = ActionChains(driver)
                    actions.move_to_element(target_input).click()
                    actions.pause(0.1)
                    actions.send_keys(Keys.ENTER)
                    actions.perform()

                    last_card_id = new_card_id 
                    success_count += 1
                    
                    # print("   -> 제출 완료")
                    time.sleep(0.8) 

                    # (6) 스페이스바
                    ActionChains(driver).send_keys(Keys.SPACE).perform()
                    
                    # 버튼 클릭 보조
                    driver.execute_script("""
                        var btn = document.querySelector('.btn-short-change-next') || document.querySelector('.btn-confirm');
                        if(btn && btn.offsetParent !== null) btn.click();
                    """)

                else:
                    continue

            except StaleElementReferenceException:
                continue

        except Exception as e:
            # print(f"   [오류] {e}")
            time.sleep(1)
            continue

    print(f"[스펠 학습] {success_count}개 완료. 종료.")
    time.sleep(2)
