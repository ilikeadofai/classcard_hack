# learning_types/spelling.py
import time
import re
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def run_spelling(driver, num_d, da_e, da_k):
    print("스펠학습을 시작합니다...")
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div[3]").click()
    driver.find_element(By.CSS_SELECTOR, "#wrapper-learn > div.start-opt-body > div > div > div > div.m-t > a").click()
    time.sleep(2)
    
    try:
        for i in range(1, num_d):
            cash_d = driver.find_element(By.XPATH,
                                         f"//*[@id='wrapper-learn']/div/div/div[2]/div[2]/div[{i}]/div[1]/div/div/div/div[1]/span[1]"
                                         ).text
            cash_d_clean = re.sub(r'[;,\s]+', '', cash_d)
            cash_d_clean = re.sub(r'[^\w가-힣]', '', cash_d_clean)  # 모든 기호 제거
            da_e_clean = [re.sub(r'[;,\s]+', '', e) for e in da_e]
            da_e_clean = [re.sub(r'[^\w가-힣]', '', e) for e in da_e_clean]  # 모든 기호 제거
            da_k_clean = [re.sub(r'[;,\s]+', '', k) for k in da_k]
            da_k_clean = [re.sub(r'[^\w가-힣]', '', k) for k in da_k_clean]  # 모든 기호 제거
            if cash_d.upper() != cash_d.lower():
                try:
                    text = da_k[da_e.index(cash_d)]
                except ValueError:
                    try:
                        text = da_e[da_k.index(cash_d)]
                    except ValueError:
                        # 리스트에 없는 단어면 랜덤 선택
                        if da_k:
                            text = random.choice(da_k)
                        elif da_e:
                            text = random.choice(da_e)
                        else:
                            text = ""
            else:
                try:
                    text = da_e[da_k.index(cash_d)]
                except ValueError:
                    # 리스트에 없는 단어면 랜덤 선택
                    if da_e:
                        text = random.choice(da_e)
                    elif da_k:
                        text = random.choice(da_k)
                    else:
                        text = ""
            in_tag = driver.find_element(By.CSS_SELECTOR,
                                         "#wrapper-learn > div > div > div.study-content.cc-table.middle > div.study-body.fade.in > div.CardItem.current.showing > div.card-bottom > div > div > div > div.text-normal.spell-input > input"
                                         )
            in_tag.click()
            in_tag.send_keys(text)
            driver.find_element(By.XPATH,
                                "//*[@id='wrapper-learn']/div/div/div[3]"
                                ).click()
            time.sleep(1.5)
            try:
                driver.find_element(By.XPATH,
                                    "//*[@id='wrapper-learn']/div/div/div[3]/div[2]"
                                    ).click()
            except:
                pass
            time.sleep(1)
    except NoSuchElementException:
        print("모든 단어가 학습되었습니다.")
    print("스펠학습이 완료되었습니다.")
