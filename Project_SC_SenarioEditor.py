import json
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QListWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox, 
    QTextEdit,
    QStackedWidget,
    QInputDialog,
    QMessageBox,
)

if getattr(sys, "frozen", False):
    BASE_PATH = Path(sys.executable).parent
else:
    BASE_PATH = Path(__file__).parent

SETTINGS_PATH = BASE_PATH / "data" / "settings.json"

def open_settings(self):
    with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
        self.settings = json.load(file)

def save_settings(self):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            self.settings,
            file,
            ensure_ascii=False,
            indent=2
        )



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        open_settings(self)

        self.scenario_data = None

        self.new_scenario_button = QPushButton("새 시나리오 만들기")
        self.new_scenario_button.clicked.connect(self.new_scenario)

        self.load_button = QPushButton("시나리오 파일 불러오기", self)
        self.load_button.clicked.connect(self.open_file)

        self.delete_event_button = QPushButton("선택된 이벤트 삭제", self)
        self.delete_event_button.clicked.connect(self.delete_event_list_item)

        self.save_button = QPushButton("시나리오 파일 저장", self)
        self.save_button.clicked.connect(self.save_file)

        self.moveup_event_button = QPushButton("↑", self)
        self.moveup_event_button.clicked.connect(self.moveup_event_list_item)

        self.movedown_event_button = QPushButton("↓", self)
        self.movedown_event_button.clicked.connect(self.movedown_event_list_item)

        self.add_event_button = QPushButton("이벤트 추가", self)
        self.add_event_button.clicked.connect(self.add_event_list_item)

        self.load_button.show()

        self.event_list = QListWidget(self)
        self.event_list.move(0, 40)
        self.event_list.resize(600, 400)
        self.event_list.currentRowChanged.connect(self.select_event)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.new_scenario_button)
        left_layout.addWidget(self.load_button)
        left_layout.addWidget(self.event_list)
        left_layout.addWidget(self.add_event_button)
        left_layout.addWidget(self.moveup_event_button)
        left_layout.addWidget(self.movedown_event_button)
        left_layout.addWidget(self.delete_event_button)
        left_layout.addWidget(self.save_button)

        self.editor_stack = QStackedWidget()


        self.empty_label = QLabel(
            "편집할 이벤트가 없습니다.\n"
            "시나리오를 불러오거나 새 이벤트를 추가해주세요."
        )

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.empty_label)
        right_layout.addWidget(self.editor_stack)
        self.empty_label.show()
        self.editor_stack.hide()

        # 대사 편집창

        self.speaker_combo = QComboBox()
        self.expression_combo = QComboBox()
        self.position_combo = QComboBox()
        self.dialogue_text_edit = QTextEdit()

        self.add_speaker_button = QPushButton("+")
        self.edit_speaker_button = QPushButton("수정")
        self.delete_speaker_button = QPushButton("삭제")
        
        self.add_expression_button = QPushButton("+")
        self.edit_expression_button = QPushButton("수정")
        self.delete_expression_button = QPushButton("삭제")

        self.add_position_button = QPushButton("+")
        self.edit_position_button = QPushButton("수정")
        self.delete_position_button = QPushButton("삭제")

        self.add_background_button = QPushButton("+")
        self.edit_background_button = QPushButton("수정")
        self.delete_background_button = QPushButton("삭제")

        self.add_transition_button = QPushButton("+")
        self.edit_transition_button = QPushButton("수정")
        self.delete_transition_button = QPushButton("삭제")

        self.speaker_combo.addItems(self.settings["speakers"])
        self.expression_combo.addItems(self.settings["expressions"])
        self.position_combo.addItems(self.settings["positions"])

        self.dialogue_editor = QWidget()

        dialogue_layout = QVBoxLayout()

        dialogue_layout.addWidget(QLabel("화자"))
        self.speaker_combo.currentTextChanged.connect(self.change_speaker)
        dialogue_layout.addWidget(self.speaker_combo)
        self.add_speaker_button.clicked.connect(lambda: self.add_setting(self.speaker_combo,"speakers"))
        dialogue_layout.addWidget(self.add_speaker_button)
        self.edit_speaker_button.clicked.connect(lambda: self.edit_setting(self.speaker_combo,"speakers"))
        dialogue_layout.addWidget(self.edit_speaker_button)
        self.delete_speaker_button.clicked.connect(lambda: self.delete_setting(self.speaker_combo, "speakers"))
        dialogue_layout.addWidget(self.delete_speaker_button)

        dialogue_layout.addWidget(QLabel("표정"))
        self.expression_combo.currentTextChanged.connect(self.change_expression)
        dialogue_layout.addWidget(self.expression_combo)
        self.add_expression_button.clicked.connect(lambda: self.add_setting(self.expression_combo, "expressions"))
        dialogue_layout.addWidget(self.add_expression_button)
        self.edit_expression_button.clicked.connect(lambda: self.edit_setting(self.expression_combo, "expressions"))
        dialogue_layout.addWidget(self.edit_expression_button)
        self.delete_expression_button.clicked.connect(lambda: self.delete_setting(self.expression_combo, "expressions"))
        dialogue_layout.addWidget(self.delete_expression_button)


        dialogue_layout.addWidget(QLabel("위치"))
        self.position_combo.currentTextChanged.connect(self.change_position)
        dialogue_layout.addWidget(self.position_combo)
        self.add_position_button.clicked.connect(lambda: self.add_setting(self.position_combo, "positions"))
        dialogue_layout.addWidget(self.add_position_button)
        self.edit_position_button.clicked.connect(lambda: self.edit_setting(self.position_combo, "positions"))
        dialogue_layout.addWidget(self.edit_position_button)
        self.delete_position_button.clicked.connect(lambda: self.delete_setting(self.position_combo, "positions"))
        dialogue_layout.addWidget(self.delete_position_button)


        dialogue_layout.addWidget(QLabel("대사"))
        self.dialogue_text_edit.textChanged.connect(self.change_dialogue_text)
        dialogue_layout.addWidget(self.dialogue_text_edit)


        self.dialogue_editor.setLayout(dialogue_layout)

        self.editor_stack.addWidget(self.dialogue_editor)


        # 지문 편집창

        self.narration_text_edit = QTextEdit()

        self.narration_editor = QWidget()

        narration_layout = QVBoxLayout()

        narration_layout.addWidget(QLabel("지문"))
        self.narration_text_edit.textChanged.connect(self.change_narration_text)
        narration_layout.addWidget(self.narration_text_edit)


        self.narration_editor.setLayout(narration_layout)

        self.editor_stack.addWidget(self.narration_editor)


        #배경 편집 창

        self.background_combo = QComboBox()

        self.background_combo.addItems(self.settings["backgrounds"])

        self.background_editor = QWidget()

        background_layout = QVBoxLayout()

        background_layout.addWidget(QLabel("배경"))
        self.background_combo.currentTextChanged.connect(self.change_background)
        background_layout.addWidget(self.background_combo)
        self.add_background_button.clicked.connect(lambda: self.add_setting(self.background_combo, "backgrounds"))
        background_layout.addWidget(self.add_background_button)
        self.edit_background_button.clicked.connect(lambda: self.edit_setting(self.background_combo, "backgrounds"))
        background_layout.addWidget(self.edit_background_button)
        self.delete_background_button.clicked.connect(lambda: self.delete_setting(self.background_combo, "backgrounds"))
        background_layout.addWidget(self.delete_background_button)

        self.background_editor.setLayout(background_layout)

        self.editor_stack.addWidget(self.background_editor)


        #화면 전환 편집 창

        self.transition_combo = QComboBox()

        self.transition_combo.addItems(self.settings["transitions"])

        self.transition_editor = QWidget()

        transition_layout = QVBoxLayout()

        transition_layout.addWidget(QLabel("화면 전환 효과"))
        self.transition_combo.currentTextChanged.connect(self.change_transition_type)
        transition_layout.addWidget(self.transition_combo)
        self.add_transition_button.clicked.connect(lambda: self.add_setting(self.transition_combo, "transitions"))
        transition_layout.addWidget(self.add_transition_button)
        self.edit_transition_button.clicked.connect(lambda: self.edit_setting(self.transition_combo, "transitions"))
        transition_layout.addWidget(self.edit_transition_button)
        self.delete_transition_button.clicked.connect(lambda: self.delete_setting(self.transition_combo, "transitions"))
        transition_layout.addWidget(self.delete_transition_button)

        self.transition_editor.setLayout(transition_layout)

        self.editor_stack.addWidget(self.transition_editor)

        # 메인 창에 붙이기
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)
        # self.new_scenario()

    # 새로운 시나리오 만들기
    def new_scenario(self):
        # if self.scenario_data is not None:
        if self.event_list.count() > 0:
            result = QMessageBox.question(
            self,
            "새 시나리오 작성",
            "현재 작업 중인 시나리오가 있습니다. \n현재 작업 중인 파일의 저장을 권장합니다. \n정말 새 시나리오를 만드시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
            )
            if result == QMessageBox.No:
                return

        self.scenario_data = {
            "ScenarioEvents": []
        }
        self.scenario_events = self.scenario_data["ScenarioEvents"]
        self.event_list.clear()

    def select_event(self, index):
        if index < 0:
            self.editor_stack.hide()
            self.empty_label.show()
            return

        self.editor_stack.show()
        self.empty_label.hide()     
        
        self.current_index = index

        event = self.scenario_events[index]
        match event["type"]:
            case "dialogue":
                self.editor_stack.setCurrentIndex(0)

                self.speaker_combo.setCurrentText(event["speaker"])
                self.expression_combo.setCurrentText(event["expression"])
                self.position_combo.setCurrentText(event.get("position", "Center"))
                self.dialogue_text_edit.setPlainText(event["text"])

            case "narration":
                self.editor_stack.setCurrentIndex(1)
                self.narration_text_edit.setPlainText(event["text"])

            case "background":
                self.editor_stack.setCurrentIndex(2)

                self.background_combo.setCurrentText(event["background"])

            case "transition":
                self.editor_stack.setCurrentIndex(3)     

                self.transition_combo.setCurrentText(event["transition_type"])   


    # 새 항목 추가
    def add_setting(self, combo, setting_key):
        text, ok = QInputDialog.getText(
            self,
            "요소 추가",
            "새 요소 이름:"
        )

        if ok and text:
            combo.addItem(text)
            self.settings[setting_key].append(text)
            save_settings(self)

    # 기존 항목 수정
    def edit_setting(self, combo, setting_key):
        current_name = combo.currentText()
        index = combo.currentIndex()

        new_name, ok = QInputDialog.getText(
            self,
            "화자 " + "\"" + current_name + "\"" + "의 이름 수정",
            "변경할 이름: ",
            text=current_name
        )

        if ok and new_name:
            self.settings[setting_key][index] = new_name
            combo.setItemText(index, new_name)
            save_settings(self)

    # 기존 항목 삭제
    def delete_setting(self, combo, setting_key):
        current_name = combo.currentText()

        result = QMessageBox.question(
            self,
            "요소 삭제",
            f"'{current_name}' 항목을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )

        if result == QMessageBox.Yes:
            if len(self.settings[setting_key]) <= 1:
                QMessageBox.warning(
                    self,
                    "삭제 불가",
                    "요소는 최소 1개 이상 있어야 합니다."
                )
                return
            index = combo.currentIndex()
            self.settings[setting_key].pop(index)
            combo.removeItem(index)
            save_settings(self)
    
    # 항목 내용 변경
    def change_speaker(self, value):
        self.scenario_events[self.current_index]["speaker"] = value
        self.update_event_list_item()

    def change_expression(self, value):
        self.scenario_events[self.current_index]["expression"] = value
        self.update_event_list_item()

    def change_position(self, value):
        self.scenario_events[self.current_index]["position"] = value
        self.update_event_list_item()

    def change_dialogue_text(self):
        value = self.dialogue_text_edit.toPlainText()

        self.scenario_events[self.current_index]["text"] = value
        self.update_event_list_item()

    def change_narration_text(self):
        value = self.narration_text_edit.toPlainText()

        self.scenario_events[self.current_index]["text"] = value
        self.update_event_list_item()


    def change_background(self, value):
        self.scenario_events[self.current_index]["background"] = value
        self.update_event_list_item()

    def change_transition_type(self, value):
        self.scenario_events[self.current_index]["transition_type"] = value
        self.update_event_list_item()

    # 이벤트 관리
    def add_event_list_item(self):
        event_type, ok = QInputDialog.getItem(
            self,
            "이벤트 추가",
            "이벤트 타입:",
            ["dialogue", "narration", "background", "transition"],
            0,
            False
        )

        if ok:
            match event_type:
                case "dialogue":
                    new_event = {
                        "type": "dialogue",
                        "speaker": self.settings["speakers"][0],
                        "expression": self.settings["expressions"][0],
                        "position": self.settings["positions"][0],
                        "text": ""
                    }

                case "narration":
                    new_event = {
                        "type": "narration",
                        "text": ""
                    }

                case "background":
                    new_event = {
                        "type": "background",
                        "background": self.settings["backgrounds"][0]
                    }

                case "transition":
                    new_event = {
                        "type": "transition",
                        "transition_type": self.settings["transitions"][0]
                    }

            self.scenario_events.append(new_event)
            self.refresh_event_list()

            new_index = len(self.scenario_events) - 1
            self.event_list.setCurrentRow(new_index)

    def update_event_list_item(self):
        event = self.scenario_events[self.current_index]
        item = self.event_list.item(self.current_index)

        match event["type"]:
            case "dialogue":
                item.setText(
                    f'{self.current_index} dialogue '
                    f'{event["speaker"]} '
                    f'{event["expression"]} '
                    f'{event["text"]}'
                )

            case "narration":
                item.setText(
                    f'{self.current_index} narration '
                    f'{event["text"]}'
                )

            case "background":
                item.setText(
                    f'{self.current_index} background '
                    f'{event["background"]}'
                )

            case "transition":
                item.setText(
                    f'{self.current_index} transition '
                    f'{event["transition_type"]}'
                )

    def delete_event_list_item(self):
        del self.scenario_events[self.current_index]
        self.event_list.takeItem(self.current_index)

    def moveup_event_list_item(self):
        if self.current_index <= 0:
            return
        event = self.scenario_events.pop(self.current_index)
        self.scenario_events.insert(self.current_index - 1, event)
        self.event_list.setCurrentRow(self.current_index - 1)
        self.refresh_event_list()

    def movedown_event_list_item(self):
        if self.current_index >= len(self.scenario_events) - 1:
            return
        event = self.scenario_events.pop(self.current_index)
        self.scenario_events.insert(self.current_index + 1, event)
        self.event_list.setCurrentRow(self.current_index + 1)
        self.refresh_event_list()

    def refresh_event_list(self):
        self.event_list.clear()
        for index, event in enumerate(self.scenario_events):
            event_type = event["type"]

            match event_type:
                case "dialogue":
                    speaker = event["speaker"]
                    expression = event["expression"]
                    text = event["text"]

                    self.event_list.addItem(f"{index} {event_type} {speaker} {expression} {text}")

                case "narration":
                    text = event["text"]

                    self.event_list.addItem(f"{index} {event_type} {text}")

                case "background":
                    background = event["background"]

                    self.event_list.addItem(f"{index} {event_type} {background}")

                case "transition":
                    transition_type = event["transition_type"]

                    self.event_list.addItem(f"{index} {event_type} {transition_type}")

                case _:
                    print("알 수 없는 타입")


    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "대본 불러오기",
            "",
            "JSON 파일 (*.json)"
        )

        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.scenario_data = json.load(file)

                if "ScenarioEvents" not in self.scenario_data:
                    QMessageBox.warning(
                        self,
                        "잘못된 파일",
                        "시나리오 파일이 아닙니다.\n올바른 시나리오 JSON 파일을 선택해주세요."
                    )
                    return
                
            self.scenario_events = self.scenario_data["ScenarioEvents"]

            self.event_list.clear()


            for index, event in enumerate(self.scenario_events):
                event_type = event["type"]

                match event_type:
                    case "dialogue":
                        speaker = event["speaker"]
                        expression = event["expression"]
                        text = event["text"]

                        self.event_list.addItem(f"{index} {event_type} {speaker} {expression} {text}")

                    case "narration":
                        text = event["text"]

                        self.event_list.addItem(f"{index} {event_type} {text}")

                    case "background":
                        background = event["background"]

                        self.event_list.addItem(f"{index} {event_type} {background}")

                    case "transition":
                        transition_type = event["transition_type"]

                        self.event_list.addItem(f"{index} {event_type} {transition_type}")

                    case _:
                        print("대본에 알 수 없는 타입이 있습니다.")
            
    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "대본 저장",
            "",
            "JSON 파일 (*.json)"
        )

        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(
                    self.scenario_data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )


def main():
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()


main()