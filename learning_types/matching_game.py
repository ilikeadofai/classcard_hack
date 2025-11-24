# learning_types/matching_game.py
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException

def run_matching_game(driver, da_e, da_k):
    print("매칭게임을 시작합니다...")
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div[5]").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR,
                        "#wrapper-learn > div.start-opt-body > div > div.container-bottom > div > div.btn-blue.btn-opt-start"
                        ).click()
    time.sleep(3.5)
    past_cards = ""
    while True:
        try:
            html = BeautifulSoup(driver.page_source, "html.parser")

            unsorted_cards = dict()
            match_body = html.find("div", class_="match-body")
            if match_body is None:
                raise NotImplementedError
            cards = match_body.get_text(strip=True)  # type: ignore

            if past_cards == cards:
                raise NotImplementedError
            for i in range(4):
                left_card = html.find("div", id=f"left_card_{i}")
                if left_card is None:
                    continue
                score_span = left_card.find("span", class_="card-score")  # type: ignore
                if score_span is None:
                    continue
                score = int(score_span.get_text(strip=True))  # type: ignore
                score_span.decompose()  # type: ignore
                question = left_card.get_text(strip=True)  # type: ignore
                unsorted_cards[f"{question}_{i}"] = score

            sorted_lists = sorted(unsorted_cards.items(), key=lambda item: item[1])

            for k, _ in sorted_lists:
                word, order = k.split("_")
                answer = da_k[da_e.index(word)]

                for j in range(4):
                    right_card_elem = html.find("div", id=f"right_card_{j}")
                    if right_card_elem is None:
                        continue
                    right_card = right_card_elem.get_text(strip=True)  # type: ignore
                    if right_card == answer:
                        left_element = driver.find_element(By.ID, f"left_card_{order}")
                        right_element = driver.find_element(By.ID, f"right_card_{j}")
                        try:
                            left_element.click()
                            right_element.click()
                        except ElementClickInterceptedException:
                            action = ActionChains(driver)
                            action.click(on_element=left_element)
                            action.click(on_element=right_element)
                            action.perform()
                            action.reset_actions()
                        raise NotImplementedError
                    else:
                        continue
        except NotImplementedError:
            try:
                if driver.find_element(By.CLASS_NAME, "rank-info").size["height"] > 0:
                    print("매칭게임이 완료되었습니다.")
                    driver.find_element(By.CSS_SELECTOR, ".btn-default").click()
                    time.sleep(1)
                    break
                else:
                    past_cards = cards
            except NoSuchElementException:
                past_cards = cards
        except KeyboardInterrupt:
            print("\n사용자에 의해 종료되었습니다.")
            break
