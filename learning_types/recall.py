# learning_types/recall.py
import time
from selenium.webdriver.common.by import By
import random
import re
from selenium.common.exceptions import NoSuchElementException

def run_recall(driver, num_d, da_e, da_kyn, time_2):
    print("리콜학습을 시작합니다...")
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div[2]").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "#wrapper-learn > div.start-opt-body > div > div > div > div.m-t > a").click()
    time.sleep(time_2)
    
    for i in range(1, num_d):
        try:
            cash_d = driver.find_element(By.XPATH,
                                         f"//*[@id='wrapper-learn']/div/div/div[2]/div[2]/div[{i}]/div[1]/div/div/div/div[1]/span"
                                         ).text
            cash_dby = ["", "", ""]
            for j in range(0, 3):
                cash_dby[j] = driver.find_element(By.XPATH,
                                                  f"//*[@id='wrapper-learn']/div/div/div[2]/div[2]/div[{i}]/div[3]/div[{j + 1}]/div[2]/div"
                                                  ).text

            ck = False
            if cash_d.upper() != cash_d.lower():
                try:
                    for j in range(0, 3):
                        if da_e.index(cash_d) == da_kyn.index(cash_dby[j]):
                            driver.find_element(By.XPATH,
                                                f"//*[@id='wrapper-learn']/div/div/div[2]/div[2]/div[{i}]/div[3]/div[{j + 1}]/div[2]"
                                                ).click()
                            ck = True
                            break
                except:
                    pass
                if not ck:
                    print("\nDetected Missing Words!!, Randomly Selected\n")
                    driver.find_element(By.XPATH,
                                        f"//*[@id='wrapper-learn']/div/div/div[2]/div[2]/div[{i}]/div[3]/div[{random.randint(1, 4)}]/div[2]"
                                        ).click()
                    time.sleep(time_2)
                    try:
                        driver.find_element(By.XPATH,
                                            f"//*[@id='wrapper-learn']/div/div/div[3]/div[2]"
                                            ).click()
                    except:
                        pass
            time.sleep(time_2)
        except NoSuchElementException:
            print("리콜학습이 정상적으로 완료되었습니다.")
            break
        except Exception as e:
            print("리콜학습 중 알 수 없는 오류가 발생했습니다:", e)
            break
    print("리콜학습이 완료되었습니다.")
