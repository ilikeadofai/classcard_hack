import customtkinter
import threading
import sys
import time
import re
import warnings
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Import existing modules
from utility import word_get
from learning_types import recall, spelling, test

# Configuration
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.see("end")
        self.widget.configure(state="disabled")

    def flush(self):
        pass

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("AutoCard - 클래스카드 자동화")
        self.geometry("900x700")

        # Data
        self.driver = None
        self.class_dict = {}
        self.sets_dict = {}
        self.selected_sets = []
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="AutoCard", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="1. 로그인", command=self.launch_browser_thread)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="2. 클래스 불러오기", command=self.load_classes_thread, state="disabled")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="테마 설정:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                        command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("Dark")

        # Main Area
        self.main_frame = customtkinter.CTkScrollableFrame(self, label_text="대시보드")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Class Selection
        self.class_label = customtkinter.CTkLabel(self.main_frame, text="클래스 선택:", anchor="w")
        self.class_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.class_option_menu = customtkinter.CTkOptionMenu(self.main_frame, values=["(클래스를 먼저 불러오세요)"], command=self.on_class_select)
        self.class_option_menu.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Set Selection
        self.set_label = customtkinter.CTkLabel(self.main_frame, text="세트 선택:", anchor="w")
        self.set_label.grid(row=2, column=0, sticky="w", pady=(10, 5))
        
        self.set_scroll_frame = customtkinter.CTkScrollableFrame(self.main_frame, height=200)
        self.set_scroll_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.set_checkboxes = []
        
        # Placeholder for sets
        self.no_sets_label = customtkinter.CTkLabel(self.set_scroll_frame, text="클래스를 선택하면 세트 목록이 여기에 표시됩니다.")
        self.no_sets_label.grid(row=0, column=0, padx=10, pady=10)

        self.select_all_btn = customtkinter.CTkButton(self.main_frame, text="전체 선택", width=100, command=self.select_all_sets)
        self.select_all_btn.grid(row=4, column=0, sticky="w", pady=(0, 10))

        # Options
        self.options_frame = customtkinter.CTkFrame(self.main_frame)
        self.options_frame.grid(row=5, column=0, sticky="ew", pady=10)
        self.options_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.check_recall = customtkinter.CTkCheckBox(self.options_frame, text="리콜 (Recall)")
        self.check_recall.grid(row=0, column=0, padx=10, pady=10)
        self.check_recall.select()

        self.check_spell = customtkinter.CTkCheckBox(self.options_frame, text="스펠 (Spell)")
        self.check_spell.grid(row=0, column=1, padx=10, pady=10)
        self.check_spell.select()

        self.check_test = customtkinter.CTkCheckBox(self.options_frame, text="테스트 (Test)")
        self.check_test.grid(row=0, column=2, padx=10, pady=10)
        self.check_test.select()

        self.auto_detect_switch = customtkinter.CTkSwitch(self.main_frame, text="미완료 항목만 자동 감지")
        self.auto_detect_switch.grid(row=6, column=0, sticky="w", pady=10)

        # Start Button
        self.start_button = customtkinter.CTkButton(self.main_frame, text="학습 시작", height=50, font=customtkinter.CTkFont(size=16, weight="bold"), fg_color="green", hover_color="darkgreen", command=self.start_learning_thread)
        self.start_button.grid(row=7, column=0, sticky="ew", pady=20)

        # Console Output
        self.console_label = customtkinter.CTkLabel(self.main_frame, text="실행 로그:", anchor="w")
        self.console_label.grid(row=8, column=0, sticky="w", pady=(10, 5))
        self.console_textbox = customtkinter.CTkTextbox(self.main_frame, height=200)
        self.console_textbox.grid(row=9, column=0, sticky="ew", pady=(0, 10))
        self.console_textbox.configure(state="disabled")

        # Redirect stdout
        sys.stdout = TextRedirector(self.console_textbox)
        sys.stderr = TextRedirector(self.console_textbox)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def launch_browser_thread(self):
        threading.Thread(target=self.launch_browser).start()

    def launch_browser(self):
        print(">>> 브라우저를 실행합니다...")
        try:
            warnings.filterwarnings("ignore")
            logging.getLogger('selenium').setLevel(logging.CRITICAL)
            
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--log-level=3')

            try:
                service = Service(ChromeDriverManager().install())
            except:
                service = Service()
            
            self.driver = webdriver.Chrome(options=chrome_options, service=service)
            
            print(">>> 로그인 페이지로 이동합니다.")
            self.driver.get("https://www.classcard.net/Login")
            
            print(">>> 브라우저에서 수동으로 로그인해주세요.")
            print(">>> 로그인이 완료될 때까지 대기합니다...")
            
            WebDriverWait(self.driver, 300).until(
                lambda driver: driver.current_url != "https://www.classcard.net/Login" and "Login" not in driver.current_url
            )
            print(">>> 로그인 감지됨!")
            self.sidebar_button_2.configure(state="normal")
            
        except Exception as e:
            print(f"브라우저 실행 오류: {e}")

    def load_classes_thread(self):
        threading.Thread(target=self.load_classes).start()

    def load_classes(self):
        print(">>> 클래스 목록을 불러옵니다...")
        try:
            # Ensure we are on a page that might have the list, or just try to close popups first
            self.close_popups()
            
            # Optional: Force navigation to Main if we are lost, but usually login redirects there.
            # self.driver.get("https://www.classcard.net/Main") 

            print(f"   (현재 URL: {self.driver.current_url})")

            class_list_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".left-class-list"))
            )
            self.class_dict = {}
            class_names = []
            
            for i, class_item in enumerate(class_list_element.find_elements(By.TAG_NAME, "a")):
                class_name = class_item.text
                href = class_item.get_attribute("href")
                class_id = href.split("/")[-1] if href else None
                
                if class_id == "joinClass" or class_id is None:
                    break
                
                self.class_dict[class_name] = class_id
                class_names.append(class_name)
            
            if class_names:
                self.class_option_menu.configure(values=class_names)
                self.class_option_menu.set(class_names[0])
                self.on_class_select(class_names[0])
                print(f">>> {len(class_names)}개의 클래스를 찾았습니다.")
            else:
                print(">>> 클래스를 찾을 수 없습니다. (목록이 비어있음)")

        except Exception as e:
            print(f"클래스 로딩 오류: {e}")
            print("   -> 힌트: 브라우저가 메인 화면(클래스 목록이 있는 화면)에 있는지 확인해주세요.")

    def on_class_select(self, class_name):
        class_id = self.class_dict.get(class_name)
        if class_id:
            threading.Thread(target=self.load_sets, args=(class_id,)).start()

    def load_sets(self, class_id):
        print(f">>> 세트 목록을 불러옵니다 (ID: {class_id})...")
        try:
            self.driver.get(f"https://www.classcard.net/ClassMain/{class_id}")
            time.sleep(1)
            
            sets_div = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/div[2]/div[3]/div")
            sets = sets_div.find_elements(By.CLASS_NAME, "set-items")
            
            self.sets_dict = {}
            
            # Clear existing checkboxes and placeholder
            for cb in self.set_checkboxes:
                cb.destroy()
            self.set_checkboxes = []
            if hasattr(self, 'no_sets_label') and self.no_sets_label.winfo_exists():
                self.no_sets_label.destroy()

            for i, set_item in enumerate(sets):
                a_tag = set_item.find_element(By.TAG_NAME, "a")
                
                # Parse title
                a_html = a_tag.get_attribute('innerHTML')
                soup = BeautifulSoup(a_html, 'html.parser')
                if soup.span: soup.span.decompose()
                title_text = soup.get_text(strip=True)
                
                set_id = a_tag.get_attribute("data-idx")
                
                self.sets_dict[i] = {
                    "title": title_text,
                    "set_id": set_id
                }
                
                # Create Checkbox
                cb = customtkinter.CTkCheckBox(self.set_scroll_frame, text=f"{i+1}. {title_text}")
                cb.grid(row=i, column=0, sticky="w", padx=5, pady=2)
                self.set_checkboxes.append(cb)
            
            print(f">>> {len(self.sets_dict)}개의 세트를 불러왔습니다.")

        except Exception as e:
            print(f"세트 로딩 오류: {e}")

    def select_all_sets(self):
        # Check if all are currently selected
        all_selected = all(cb.get() == 1 for cb in self.set_checkboxes)
        
        if all_selected:
            # Deselect all
            for cb in self.set_checkboxes:
                cb.deselect()
            self.select_all_btn.configure(text="전체 선택")
        else:
            # Select all
            for cb in self.set_checkboxes:
                cb.select()
            self.select_all_btn.configure(text="전체 해제")

    def start_learning_thread(self):
        threading.Thread(target=self.start_learning).start()

    def start_learning(self):
        if not self.driver:
            print("오류: 브라우저가 실행되지 않았습니다.")
            return

        # Get selected sets
        selected_indices = []
        for i, cb in enumerate(self.set_checkboxes):
            if cb.get() == 1:
                selected_indices.append(i)
        
        if not selected_indices:
            print("오류: 선택된 세트가 없습니다.")
            return

        # Get selected types
        types = []
        if self.check_recall.get(): types.append(2)
        if self.check_spell.get(): types.append(3)
        if self.check_test.get(): types.append(5)
        
        if not types:
            print("오류: 학습 유형이 선택되지 않았습니다.")
            return

        class_name = self.class_option_menu.get()
        class_id = self.class_dict.get(class_name)

        print(f"\n>>> {len(selected_indices)}개 세트의 학습을 시작합니다...")
        
        # Auto-detect logic
        if self.auto_detect_switch.get() == 1:
            print(">>> 자동 감지 모드: 미완료된 항목만 확인합니다...")
            # Reuse logic from main.py (simplified here)
            # We need to iterate and check status
            final_plan = {} # {set_idx: [types]}
            
            for idx in selected_indices:
                set_info = self.sets_dict[idx]
                set_id = set_info['set_id']
                self.driver.get(f"https://www.classcard.net/set/{set_id}/{class_id}")
                
                try:
                    html = self.driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    needed = []
                    
                    # Check Recall
                    if 2 in types:
                        recall_elem = soup.select_one(".recall-total-rate")
                        rate = int(recall_elem['data-rate']) if recall_elem and recall_elem.get('data-rate') else 0
                        if rate < 100: needed.append(2)
                    
                    # Check Spell
                    if 3 in types:
                        spell_elem = soup.select_one(".spell-total-rate")
                        rate = int(spell_elem['data-rate']) if spell_elem and spell_elem.get('data-rate') else 0
                        if rate < 100: needed.append(3)

                    # Check Test
                    if 5 in types:
                        test_score = 0
                        test_btn = soup.select_one(".btn-start-speedquiz .right")
                        if test_btn:
                            score_text = test_btn.text.strip()
                            if "점" in score_text:
                                numbers = re.findall(r'\d+', score_text)
                                if numbers: test_score = int(numbers[0])
                        if test_score < 100: needed.append(5)
                    
                    if needed:
                        final_plan[idx] = needed
                        # Convert codes to text
                        type_map = {2: "리콜", 3: "스펠", 5: "테스트"}
                        needed_text = [type_map.get(x, str(x)) for x in needed]
                        print(f"   -> {set_info['title']}: 학습 필요 {needed_text}")
                    else:
                        print(f"   -> {set_info['title']}: 완료됨.")
                        
                except Exception as e:
                    print(f"세트 확인 오류 ({idx}): {e}")

        else:
            # Normal mode: Do all selected types for all selected sets
            final_plan = {idx: types for idx in selected_indices}

        # Execution Loop
        import random
        time_1 = round(random.uniform(0.7, 1.3), 4)
        time_2 = round(random.uniform(1.7, 2.3), 4)

        for idx, type_list in final_plan.items():
            set_info = self.sets_dict[idx]
            for ch_d in type_list:
                self.process_single_learning(class_id, set_info, ch_d, time_1, time_2)

        print("\n>>> 모든 작업이 완료되었습니다!")

    def process_single_learning(self, class_id, set_info, ch_d, time_1, time_2):
        type_name = {2: "리콜", 3: "스펠", 5: "테스트"}.get(ch_d, "알수없음")
        print(f"\n>>> 진행 중: {set_info['title']} (유형: {type_name})")
        set_id = set_info['set_id']
        
        self.driver.get(f"https://www.classcard.net/set/{set_id}/{class_id}")
        self.close_popups()
        
        word_d = word_get(self.driver, 0)
        if not word_d:
            print("❌ 단어 데이터를 가져오는데 실패했습니다.")
            return

        da_e, da_k, da_kn, da_kyn, da_ked, da_sd, da_e_clean, da_k_clean = word_d
        num_d = len(da_e) + 1

        try:
            if ch_d != 5: self.close_popups()
            
            btn_selector = ""
            if ch_d == 2: btn_selector = ".btn-recall"
            elif ch_d == 3: btn_selector = ".btn-spell"
            elif ch_d == 5: btn_selector = ".btn-start-speedquiz"

            target_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, btn_selector))
            )
            self.driver.execute_script("arguments[0].click();", target_btn)
            time.sleep(4)
            
            if ch_d != 5: self.close_popups()

            if ch_d == 2:
                recall.run_recall(self.driver, num_d, da_e, da_kyn, time_2)
            elif ch_d == 3:
                spelling.run_spelling(self.driver, num_d, da_e, da_k)
            elif ch_d == 5:
                test.run_test(self.driver, num_d, da_e, da_k, da_kn, da_ked, time_1, da_e_clean, da_k_clean)

        except Exception as e:
            print(f"❌ 학습 중 오류 발생: {e}")

    def close_popups(self):
        try:
            self.driver.execute_script("""
                $('.modal').modal('hide');
                $('.btn-close').click();
                $('.close').click();
                $('#gb_ad_layer').remove();
                if (window.location.href.indexOf('ClassTest') === -1) {
                    $('.layer').hide();
                }
                document.querySelectorAll('.modal, .overlay').forEach(p => p.style.display = 'none');
            """)
            time.sleep(0.2)
        except:
            pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
