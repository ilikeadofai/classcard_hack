# AutoCard (구 Classcard Hack)

## 소개

**AutoCard**는 Classcard(클래스카드) 웹사이트의 학습을 자동으로 완료해주는 도구입니다.
기존의 콘솔 기반 방식에서 벗어나, **편리한 GUI(그래픽 인터페이스)**를 제공하여 누구나 쉽게 사용할 수 있습니다.

> ⚠️ **주의**: 본 프로그램은 교육/연구/개인 실험 목적으로만 사용하세요. 실제 수업/평가에 악용 시 발생하는 불이익은 사용자 본인에게 있습니다.

---

## ✨ 주요 기능

- **모던한 GUI**: 검은색 테마의 깔끔한 인터페이스 제공
- **자동 감지 모드**: 미완료된 세트만 자동으로 찾아 학습 (리콜, 스펠, 테스트)
- **다중 선택**: 여러 세트를 체크박스로 손쉽게 선택 가능
- **학습 유형 선택**: 리콜, 스펠, 테스트 중 원하는 유형만 선택 가능
- **로그인 자동화**: 브라우저를 띄워 수동 로그인 후 자동으로 연동

---

## 🚀 실행 방법

### 1. EXE 파일로 실행 (추천)

1. [Releases](https://github.com/ilikeadofai/classcard_hack/releases) 페이지에서 최신 `AutoCard.exe`를 다운로드합니다.
2. 파일을 실행합니다. (보안 경고가 뜰 경우 '추가 정보' -> '실행' 클릭)
3. **"1. 로그인"** 버튼을 눌러 브라우저를 엽니다.
4. 브라우저에서 클래스카드에 로그인합니다.
5. **"2. 클래스 불러오기"** 버튼을 누르고 클래스를 선택합니다.
6. 학습할 세트를 체크합니다. (또는 "미완료 항목만 자동 감지" 스위치를 켭니다)
7. **"학습 시작"** 버튼을 누르면 자동으로 학습이 진행됩니다.

### 2. 소스 코드로 실행

Python 3.10 이상이 필요합니다.

```bash
# 저장소 클론
git clone https://github.com/ilikeadofai/classcard_hack.git
cd classcard_hack

# 가상환경 생성 및 패키지 설치
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt

# 실행
python gui.py
```

---

## 🛠️ 기술 스택

- **Language**: Python 3.12
- **GUI**: CustomTkinter
- **Automation**: Selenium WebDriver
- **Build**: PyInstaller

---

## 🔒 바이러스 탐지 관련

이 프로그램은 `PyInstaller`로 패키징되었으며, 브라우저를 제어하는 `Selenium`을 포함하고 있어 일부 백신에서 오탐(False Positive)할 수 있습니다.
소스 코드는 100% 공개되어 있으므로, 의심스럽다면 직접 소스 코드를 실행해서 사용하실 수 있습니다.

---

## 라이선스

Apache License 2.0
