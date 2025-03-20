from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QStackedWidget, QSplitter, QPushButton, QLabel, QSlider, QCheckBox, QRadioButton, QLineEdit, QGroupBox, QVBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import sys

class PyWin(QMainWindow):
    def __init__(self, width=800, height=600, x=0, y=0):
        super().__init__()
        screen = QApplication.primaryScreen().geometry()  # 현재 화면 크기 가져오기

        if x == 0 and y == 0:
            x = (screen.width() - width) // 2  # 중앙 정렬 (X 좌표)
            y = (screen.height() - height) // 2  # 중앙 정렬 (Y 좌표)

        self.setGeometry(x, y, width, height)
        self.central_widget = QWidget()  # 중앙 위젯
        self.setCentralWidget(self.central_widget)

        self.layout = None  # 레이아웃 기본 값

    def set(self, bg=None, transparency=None):
        """ 배경 색상, 이미지, 투명도 설정 """
        if bg:
            if bg.startswith("#"):  # HEX 색상 코드
                self.setStyleSheet(f"background-color: {bg};")
            else:  # 이미지 파일로 처리
                pixmap = QPixmap(bg)
                palette = self.palette()
                palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
                self.setPalette(palette)

        if transparency is not None:
            self.setWindowOpacity(transparency)  # 0.0 (완전 투명) ~ 1.0 (완전 불투명)

        return self  # 메서드 체이닝 지원

    def lay(self, *components):
        """ 위젯을 추가하고 레이아웃 설정 """
        if not self.layout:
            self.layout = QVBoxLayout()  # 기본 레이아웃 (세로 방향)

        # 주어진 위젯들을 레이아웃에 추가
        for comp in components:
            if isinstance(comp, QPushButton):
                self.layout.addWidget(comp)
            elif isinstance(comp, QLabel):
                self.layout.addWidget(comp)
            elif isinstance(comp, QSlider):
                self.layout.addWidget(comp)
            elif isinstance(comp, QCheckBox):
                self.layout.addWidget(comp)
            elif isinstance(comp, QRadioButton):
                self.layout.addWidget(comp)
            elif isinstance(comp, QLineEdit):
                self.layout.addWidget(comp)
        
        self.central_widget.setLayout(self.layout)  # 중앙 위젯에 레이아웃 설정
        return self  # 메서드 체이닝 지원

    def setlay(self, layout_name="vertical"):
        """ 레이아웃 유형 설정 """
        if layout_name == "horizontal":
            self.layout = QHBoxLayout()  # 가로 레이아웃
        elif layout_name == "vertical":
            self.layout = QVBoxLayout()  # 세로 레이아웃
        elif layout_name == "grid":
            self.layout = QGridLayout()  # 그리드 레이아웃
        elif layout_name == "form":
            self.layout = QFormLayout()  # 폼 레이아웃
        elif layout_name == "stacked":
            self.layout = QStackedWidget()  # 스택형 레이아웃
        elif layout_name == "split":
            self.layout = QSplitter(Qt.Orientation.Horizontal)  # 분할 레이아웃
        else:
            raise ValueError("지원되지 않는 레이아웃 유형입니다.")

        self.central_widget.setLayout(self.layout)  # 변경된 레이아웃 설정
        return self  # 메서드 체이닝 지원

    def label_button(self, text, width=100, height=50):
        """ 텍스트가 있는 버튼 생성 """
        button = QPushButton(text)
        button.setFixedSize(width, height)
        return button

    def icon_button(self, text, icon_path, width=100, height=50):
        """ 아이콘과 텍스트가 있는 버튼 생성 """
        button = QPushButton(text)
        icon = QIcon(icon_path)  # 아이콘 경로로 아이콘 설정
        button.setIcon(icon)
        button.setIconSize(QSize(32, 32))  # 아이콘 크기 설정
        button.setFixedSize(width, height)
        return button

    def slider(self, min_value=0, max_value=100, initial_value=50):
        """ 슬라이더 위젯 생성 """
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(initial_value)
        return slider

    def checkbox(self, text, checked=False):
        """ 체크박스 생성 """
        checkbox = QCheckBox(text)
        checkbox.setChecked(checked)
        return checkbox

    def radio_button(self, text):
        """ 라디오 버튼 생성 """
        radio_button = QRadioButton(text)
        return radio_button

    def text_input(self, placeholder="Enter text"):
        """ 텍스트 입력 필드 생성 """
        text_input = QLineEdit()
        text_input.setPlaceholderText(placeholder)
        return text_input

    def set_shortcut(self, button, shortcut):
        """ 버튼에 단축키 할당 """
        button.setShortcut(shortcut)
        return button

    def resize_window(self, width, height):
        """ 창 크기 조정 """
        self.resize(width, height)
        return self  # 메서드 체이닝 지원

    def show_error(self, message):
        """ 오류 메시지 출력 """
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec()

# PyWin을 함수로 쉽게 호출할 수 있도록 래퍼 함수 제공
def window(width=800, height=600, x=0, y=0):
    app = QApplication.instance() or QApplication(sys.argv)  # 기존 앱 인스턴스 사용
    win = PyWin(width, height, x, y)
    return win, app
