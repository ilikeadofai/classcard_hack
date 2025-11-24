# learning_types/memorization.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def run_memorization(driver, num_d):
    print("암기학습을 시작합니다...")
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div[1]").click()
    time.sleep(0.5)  # 1초 → 0.5초
    driver.find_element(By.CSS_SELECTOR, "#wrapper-learn > div.start-opt-body > div > div > div > div.m-t > a").click()
    
    # 카드 1 시작 전 대기시간 추가
    print("첫 번째 카드 로딩을 기다리는 중...")
    time.sleep(2)  # 3초 대기
    
    for i in range(1, num_d):
        print(f"\n=== 카드 {i} 처리 시작 ===")
        print(f"현재 URL: {driver.current_url}")
        time.sleep(1)  # 2초 → 1초
        
        # 특정 카드 요소 선택 (카드 인덱스 사용)
        card_selectors = [
            f"/html/body/div[2]/div[1]/div/div[2]/div[3]/div[{i}]",
            f"//div[@class='flip-body']/div[{i}]",
            f"//div[contains(@class, 'flip-card')][{i}]",
            f"//div[contains(@class, 'card-item')][{i}]"
        ]
        
        current_card = None
        for selector in card_selectors:
            try:
                current_card = driver.find_element(By.XPATH, selector)
                print(f"카드 {i} 요소 찾음: {selector}")
                break
            except:
                continue
        
        if current_card is None:
            print(f"카드 {i} 요소를 찾을 수 없습니다. 다음 카드로 넘어갑니다.")
            continue
        
        # 현재 카드 내에서 .card-cover 찾기
        try:
            card_cover = current_card.find_element(By.CSS_SELECTOR, ".card-cover")
            driver.execute_script("arguments[0].click();", card_cover)
            print(f"카드 {i} 커버 클릭 완료")
        except:
            print(f"카드 {i} 커버를 찾을 수 없습니다. 다음 카드로 넘어갑니다.")
            continue
            
        time.sleep(1.25)  # 3초 → 1.25초
        
        # Shift+Space 키보드 단축키로 다음 카드로 넘어가기
        try:
            actions = ActionChains(driver)
            actions.key_down(Keys.SHIFT).send_keys(Keys.SPACE).key_up(Keys.SHIFT).perform()
            print(f"카드 {i} Shift+Space로 다음 카드로 넘어가기 완료")
        except Exception as e:
            print(f"카드 {i} Shift+Space 실행 중 오류: {e}")
            # 백업 방법: 일반 Space 키
            try:
                actions = ActionChains(driver)
                actions.send_keys(Keys.SPACE).perform()
                print(f"카드 {i} Space 키로 다음 카드로 넘어가기 완료")
            except:
                print(f"카드 {i} 키보드 단축키 실패")
        
        print(f"=== 카드 {i} 처리 완료 ===\n")
        time.sleep(1)  # 2초 → 0.75초
    
    time.sleep(0.5)  # 1초 → 0.5초
    try:
        driver.find_element(By.CSS_SELECTOR,
                            "body > div.study-header-body > div > div:nth-child(1) > div:nth-child(1) > a"
                            ).click()
    except:
        print("학습 완료 버튼을 찾을 수 없습니다.")
    
    print("암기학습이 완료되었습니다.")
