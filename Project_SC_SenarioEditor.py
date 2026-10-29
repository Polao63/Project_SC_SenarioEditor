# TODO: 진입등장 애니메이션 여부 체크 옵션
# 영문 옵션 -> 한글로 변환 (왼쪽, 오른쪽, 중앙 으로 지정하면 -> left, right, center 로 읽게 만들어야함.)

from ScenarioPreview import ScenarioPreview
import json
import shutil
import os
import tempfile
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
    QSplitter,
)
from PySide6.QtCore import Qt, QUrl, QSignalBlocker
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

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

        self.scenario_data = {
            "ScenarioEvents": []
        }

        self.scenario_events = self.scenario_data["ScenarioEvents"]
        self.current_index = -1

        self.is_modified = False

        self.setWindowTitle("ProjectSC Scenario Editor")


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

        self.scenario_preview = ScenarioPreview()

        self.right_splitter = QSplitter(Qt.Vertical)
        self.right_splitter.addWidget(self.scenario_preview)

        self.editor_container = QWidget()
        editor_layout = QVBoxLayout(self.editor_container)
        editor_layout.addWidget(self.empty_label)
        editor_layout.addWidget(self.editor_stack)

        self.right_splitter.addWidget(self.editor_container)
        self.right_splitter.setSizes([500, 400])

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.right_splitter)

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

        self.add_sound_button = QPushButton("+")
        self.edit_sound_button = QPushButton("수정")
        self.delete_sound_button = QPushButton("삭제")

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


        dialogue_layout.addWidget(QLabel("(등장시 배치할)위치"))
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

        self.background_preview = QLabel()
        pixmap = QPixmap("backgrounds/TEST_BG01.jpg")
        self.background_preview.setPixmap(pixmap)

        self.background_preview.setFixedSize(480, 270)

        self.background_preview.setPixmap(
            pixmap.scaled(
                480,
                270,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        background_layout.addWidget(self.background_preview)

        self.background_combo.currentTextChanged.connect(self.change_background)
        
        background_layout.addWidget(self.background_combo)
        self.add_background_button.clicked.connect(self.add_background_resource)
        
        background_layout.addWidget(self.add_background_button)
        self.edit_background_button.clicked.connect(
            self.edit_background_resource
        )

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



        # 사운드 파일 관련

        self.audio_player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.audio_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)
        self.preview_play_button = QPushButton("▶ 미리듣기")
        self.preview_stop_button = QPushButton("■ 정지")

        self.soundtype_combo = QComboBox()
        self.soundtype_combo.addItems(["BGM", "SE"])

        self.sound_play_editor = QWidget()

        self.sound_combo = QComboBox()
        sound_play_layout = QVBoxLayout()

        sound_play_layout.addWidget(QLabel("사운드 종류"))
        sound_play_layout.addWidget(self.soundtype_combo)
        self.soundtype_combo.currentTextChanged.connect(self.change_sound_type)

        sound_play_layout.addWidget(QLabel("사운드 선택"))
        sound_play_layout.addWidget(self.sound_combo)
        self.sound_combo.currentTextChanged.connect(self.change_sound_name)

        sound_play_layout.addWidget(self.preview_play_button)
        self.preview_play_button.clicked.connect(self.preview_sound)
        sound_play_layout.addWidget(self.preview_stop_button)
        self.preview_stop_button.clicked.connect(self.stop_preview_sound)

        self.action_combo = QComboBox()
        self.action_combo.addItems(["Play", "Stop"])
        self.action_combo.currentTextChanged.connect(self.change_sound_action)

        sound_play_layout.addWidget(QLabel("재생 동작"))
        sound_play_layout.addWidget(self.action_combo)
        self.add_sound_button.clicked.connect(self.add_sound_resource)
        
        sound_play_layout.addWidget(self.add_sound_button)
        self.edit_sound_button.clicked.connect(
            self.edit_sound_resource
        )

        sound_play_layout.addWidget(self.edit_sound_button)
        self.delete_sound_button.clicked.connect(
            lambda: self.delete_setting(
                self.sound_combo,
                self.get_sound_setting_key()
            )
        )
        sound_play_layout.addWidget(self.delete_sound_button)


        self.sound_play_editor.setLayout(sound_play_layout)
        self.editor_stack.addWidget(self.sound_play_editor)


        # 메인 창에 붙이기
        left_container = QWidget()
        left_container.setLayout(left_layout)

        right_container = QWidget()
        right_container.setLayout(right_layout)

        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(left_container)
        self.main_splitter.addWidget(right_container)
        self.main_splitter.setSizes([350, 950])

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.main_splitter)

        self.setLayout(main_layout)
        self.resize(1400, 900)
        # self.new_scenario()

    # 새로운 시나리오 만들기
    def new_scenario(self):
        
        if not self.is_modified and self.event_list.count() > 0:
            result = QMessageBox.question(
                self,
                "새 시나리오 작성",
                "현재 시나리오를 닫고 새 시나리오를 만드시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if result == QMessageBox.No:
                return

        if not self.confirm_unsaved_changes():
            return

        self.scenario_data = {
            "ScenarioEvents": []
        }
        self.scenario_events = self.scenario_data["ScenarioEvents"]
        self.event_list.clear()
        self.scenario_preview.clear_background()
        
        self.is_modified = False
        self.setWindowTitle("ProjectSC Scenario Editor")

    def select_event(self, index):
        if index < 0:
            self.editor_stack.hide()
            self.empty_label.show()
            return

        self.editor_stack.show()
        self.empty_label.hide()     
        
        self.current_index = index

        event = self.scenario_events[index]

        background_name = self.find_previous_background(index)

        if background_name is not None:
            self.update_background_preview(background_name)
        else:
            self.scenario_preview.clear_background()

        match event["type"]:
            case "dialogue":
                self.editor_stack.setCurrentIndex(0)

                with (
                    QSignalBlocker(self.speaker_combo),
                    QSignalBlocker(self.expression_combo),
                    QSignalBlocker(self.position_combo),
                    QSignalBlocker(self.dialogue_text_edit),
                ):

                    self.speaker_combo.setCurrentText(event["speaker"])
                    self.expression_combo.setCurrentText(event["expression"])
                    self.position_combo.setCurrentText(event.get("position", "Center"))
                    self.dialogue_text_edit.setPlainText(event["text"])

                self.scenario_preview.set_speaker(speaker = event["speaker"])
                self.scenario_preview.set_dialogue_text(text = event["text"])

            case "narration":
                self.editor_stack.setCurrentIndex(1)

                with QSignalBlocker(self.narration_text_edit):
                    self.narration_text_edit.setPlainText(event["text"])

            case "background":
                self.editor_stack.setCurrentIndex(2)

                with QSignalBlocker(self.background_combo):
                    self.background_combo.setCurrentText(event["background"])

                self.update_background_preview(event["background"])

            case "transition":
                self.editor_stack.setCurrentIndex(3)     

                self.transition_combo.setCurrentText(event["transition_type"]) 

            case "sound":
                self.editor_stack.setCurrentIndex(4)

                self.soundtype_combo.blockSignals(True)
                self.sound_combo.blockSignals(True)
                self.action_combo.blockSignals(True)

                self.soundtype_combo.setCurrentText(event["sound_type"])
                self.update_sound_combo(event["sound_type"])
                self.sound_combo.setCurrentText(event["sound_name"])

                self.action_combo.setCurrentText(event.get("sound_action", "Play"))
                self.action_combo.setEnabled(event["sound_type"] == "BGM")
                self.sound_combo.setEnabled(self.action_combo.currentText() == "Play")  

                self.soundtype_combo.blockSignals(False)
                self.sound_combo.blockSignals(False)
                self.action_combo.blockSignals(False)


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

            if setting_key in ("bgms", "ses"):
                self.audio_player.stop()
                self.audio_player.setSource(QUrl())

            index = combo.currentIndex()
            self.settings[setting_key].pop(index)
            combo.removeItem(index)
            save_settings(self)
    
    # 항목 내용 변경
    def change_speaker(self, value):
        self.scenario_events[self.current_index]["speaker"] = value
        self.update_event_list_item()
        self.scenario_preview.set_speaker(speaker=value)
        self.mark_modified()

    def change_expression(self, value):
        self.scenario_events[self.current_index]["expression"] = value
        self.update_event_list_item()
        self.mark_modified()

    def change_position(self, value):
        self.scenario_events[self.current_index]["position"] = value
        self.update_event_list_item()
        self.mark_modified()

    def change_dialogue_text(self):
        value = self.dialogue_text_edit.toPlainText()

        self.scenario_events[self.current_index]["text"] = value
        self.update_event_list_item()
        self.scenario_preview.set_dialogue_text(text=value)
        self.mark_modified()

    def change_narration_text(self):
        value = self.narration_text_edit.toPlainText()

        self.scenario_events[self.current_index]["text"] = value
        self.update_event_list_item()

        self.mark_modified()

    def change_background(self, value):
        self.scenario_events[self.current_index]["background"] = value
        self.update_event_list_item()
        self.update_background_preview(value)
        self.mark_modified()

    def change_transition_type(self, value):
        self.scenario_events[self.current_index]["transition_type"] = value
        self.update_event_list_item()
        self.mark_modified()

    def change_sound_type(self, value):
        self.scenario_events[self.current_index]["sound_type"] = value

        self.update_sound_combo(value)

        if value == "SE":
            self.action_combo.setCurrentText("Play")

        self.action_combo.setEnabled(value == "BGM")

        self.update_event_list_item()
        self.mark_modified()

    def change_sound_name(self, value):
        self.scenario_events[self.current_index]["sound_name"] = value
        self.update_event_list_item()
        self.mark_modified()

    def change_sound_action(self, value):
        self.scenario_events[self.current_index]["sound_action"] = value
        if value == "Stop":
            self.scenario_events[self.current_index]["sound_name"] = "X"
        else:
            self.scenario_events[self.current_index]["sound_name"] = self.sound_combo.currentText()
        self.sound_combo.setEnabled(value == "Play")
        self.update_event_list_item()
        self.mark_modified()

    # 이벤트 관리
    def add_event_list_item(self):
        event_type, ok = QInputDialog.getItem(
            self,
            "이벤트 추가",
            "이벤트 타입:",
            ["dialogue", "narration", "background", "transition", "sound"],
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
                case "sound":
                    new_event = {
                        "type": "sound",
                        "sound_type": "BGM",
                        "sound_name": self.settings["bgms"][0] if self.settings["bgms"] else "",
                        "sound_action": "Play"
                    }

            self.scenario_events.append(new_event)
            self.refresh_event_list()

            new_index = len(self.scenario_events) - 1
            self.event_list.setCurrentRow(new_index)
            self.mark_modified()

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

            case "sound":
                item.setText(
                    f'{self.current_index} sound '
                    f'{event["sound_type"]} '
                    f'{event["sound_name"]}'
                )

    def delete_event_list_item(self):
        if not 0 <= self.current_index < len(self.scenario_events):
            return
        del self.scenario_events[self.current_index]
        self.event_list.takeItem(self.current_index)
        self.mark_modified()

    def moveup_event_list_item(self):
        if self.current_index <= 0:
            return
        event = self.scenario_events.pop(self.current_index)
        self.scenario_events.insert(self.current_index - 1, event)
        self.event_list.setCurrentRow(self.current_index - 1)
        self.refresh_event_list()
        self.mark_modified()

    def movedown_event_list_item(self):
        if self.current_index >= len(self.scenario_events) - 1:
            return
        event = self.scenario_events.pop(self.current_index)
        self.scenario_events.insert(self.current_index + 1, event)
        self.event_list.setCurrentRow(self.current_index + 1)
        self.refresh_event_list()
        self.mark_modified()

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
                case "sound":
                    sound_type = event["sound_type"]
                    sound_name = event["sound_name"]

                    self.event_list.addItem(
                        f"{index} {event_type} {sound_type} {sound_name}"
                    )
                case _:
                    print("알 수 없는 타입")

    def edit_background_resource(self):
        background_name = self.background_combo.currentText()

        if not background_name:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "교체할 배경 이미지 선택",
            "",
            "이미지 파일 (*.png *.jpg *.jpeg *.webp)"
        )

        if not file_path:
            return

        source = Path(file_path)

        result = QMessageBox.question(
            self,
            "배경 이미지 교체",
            f"'{background_name}' 배경 이미지를 교체하시겠습니까?\n"
            "기존 파일은 덮어쓰거나 삭제되며 복구할 수 없습니다.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        background_dir = BASE_PATH / "backgrounds"

        old_file = None

        for extension in [".png", ".jpg", ".jpeg", ".webp"]:
            candidate = background_dir / f"{background_name}{extension}"

            if candidate.exists():
                old_file = candidate
                break

        if old_file is None:
            QMessageBox.warning(
                self,
                "파일 없음",
                f"'{background_name}' 배경 이미지 파일을 찾을 수 없습니다."
            )
            return

        new_file = background_dir / f"{background_name}{source.suffix.lower()}"

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                dir=background_dir,
                suffix=source.suffix.lower(),
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)

            shutil.copy2(source, temp_path)

            os.replace(temp_path, new_file)
            temp_path = None

            if old_file != new_file:
                old_file.unlink()

            self.update_background_preview(background_name)

            QMessageBox.information(
                self,
                "교체 완료",
                f"'{background_name}' 배경 이미지를 교체했습니다."
            )

        except OSError as error:
            QMessageBox.critical(
                self,
                "교체 실패",
                f"배경 이미지 교체 중 오류가 발생했습니다.\n{error}"
            )

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    def edit_sound_resource(self):
        sound_name = self.sound_combo.currentText()

        if not sound_name:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "교체할 사운드 선택",
            "",
            "사운드 파일 (*.mp3 *.wav *.ogg)"
        )

        if not file_path:
            return

        source = Path(file_path)

        result = QMessageBox.question(
            self,
            "사운드 교체",
            f"'{sound_name}' 사운드를 교체하시겠습니까?\n"
            "기존 파일은 덮어쓰거나 삭제되며 복구할 수 없습니다.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        sound_type = self.soundtype_combo.currentText()

        if sound_type == "BGM":
            sound_dir = BASE_PATH / "sounds" / "bgm"
        else:
            sound_dir = BASE_PATH / "sounds" / "se"

        old_file = None

        for extension in [".mp3", ".wav", ".ogg"]:
            candidate = sound_dir / f"{sound_name}{extension}"

            if candidate.exists():
                old_file = candidate
                break

        if old_file is None:
            QMessageBox.warning(
                self,
                "파일 없음",
                f"'{sound_name}' 사운드 파일을 찾을 수 없습니다."
            )
            return

        new_file = sound_dir / f"{sound_name}{source.suffix.lower()}"

        temp_path = None

        try:
            self.audio_player.stop()
            self.audio_player.setSource(QUrl())
            with tempfile.NamedTemporaryFile(
                dir=sound_dir,
                suffix=source.suffix.lower(),
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)

            shutil.copy2(source, temp_path)

            os.replace(temp_path, new_file)
            temp_path = None

            if old_file != new_file:
                old_file.unlink()

            QMessageBox.information(
                self,
                "교체 완료",
                f"'{sound_name}' 사운드를 교체했습니다."
            )

        except OSError as error:
            QMessageBox.critical(
                self,
                "교체 실패",
                f"사운드 교체 중 오류가 발생했습니다.\n{error}"
            )

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)


    def update_background_preview(self, background_name):
        print(background_name)
        self.background_preview.clear()
        background_dir = BASE_PATH / "backgrounds"

        for extension in [".png", ".jpg", ".jpeg", ".webp"]:
            image_path = background_dir / f"{background_name}{extension}"

            if image_path.exists():
                pixmap = QPixmap(str(image_path))

                self.background_preview.setPixmap(
                    pixmap.scaled(
                        480, 270,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )

                self.scenario_preview.set_background(str(image_path))

                return
            
        # self.background_preview.setText("배경 이미지를 찾을 수 없습니다.")
        self.scenario_preview.clear_background(
            "배경 이미지 파일을 찾을 수 없습니다."
        )

    def find_previous_background(self, index):

        for i in range(index, -1, -1):

            event = self.scenario_events[i]

            if event["type"] == "background":
                return event["background"]

        return None        

    def update_sound_combo(self, sound_type):
        self.sound_combo.clear()

        if sound_type == "BGM":
            self.sound_combo.addItems(self.settings["bgms"])
        elif sound_type == "SE":
            self.sound_combo.addItems(self.settings["ses"])

    def preview_sound(self):
        sound_type = self.soundtype_combo.currentText()
        sound_name = self.sound_combo.currentText()

        if sound_type == "BGM":
            sound_dir = BASE_PATH / "sounds" / "bgm"
        else:
            sound_dir = BASE_PATH / "sounds" / "se"

        for extension in [".mp3", ".wav", ".ogg"]:
            sound_path = sound_dir / f"{sound_name}{extension}"

            if sound_path.exists():
                self.audio_player.setSource(
                    QUrl.fromLocalFile(str(sound_path))
                )
                self.audio_player.play()
                return

        QMessageBox.warning(
            self,
            "파일 없음",
            f"사운드 파일을 찾을 수 없습니다: {sound_name}"
        )

    def stop_preview_sound(self):
        self.audio_player.stop()

    def add_sound_resource(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "오디오 파일 선택",
            "",
            "오디오 파일 (*.mp3 *.wav *.ogg)"
        )

        if not file_path:
            return
    
        source = Path(file_path)
        sound_name = source.stem
        sound_type = self.soundtype_combo.currentText()

        if sound_type == "BGM":
            destination_dir = BASE_PATH / "sounds" / "bgm"
            setting_key = "bgms"
        else:
            destination_dir = BASE_PATH / "sounds" / "se"
            setting_key = "ses"

        if sound_name in self.settings[setting_key]:
            QMessageBox.warning(
                self,
                "중복된 사운드",
                f"'{sound_name}' 사운드는 이미 등록되어 있습니다."
            )
            return
        
        for extension in [".mp3", ".wav", ".ogg"]:
            existing_file = destination_dir / f"{sound_name}{extension}"

            if existing_file.exists():
                QMessageBox.warning(
                    self,
                    "중복된 파일",
                    f"'{sound_name}' 이름의 사운드 파일이 이미 존재합니다."
                )
                return
            
        destination_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination_dir)

        print(f"복사 완료: {destination_dir}")

        self.settings[setting_key].append(sound_name)
        self.sound_combo.addItem(sound_name)

        save_settings(self)

        self.sound_combo.setCurrentText(sound_name)

    def get_sound_setting_key(self):
        sound_type = self.soundtype_combo.currentText()

        if sound_type == "BGM":
            return "bgms"
        else:
            return "ses"

    def open_file(self):
        if not self.confirm_unsaved_changes():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "대본 불러오기",
            "",
            "JSON 파일 (*.json)"
        )

        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                loaded_data = json.load(file)

                if "ScenarioEvents" not in loaded_data:
                    QMessageBox.warning(
                        self,
                        "잘못된 파일",
                        "시나리오 파일이 아닙니다.\n올바른 시나리오 JSON 파일을 선택해주세요."
                    )
                    return                

            self.scenario_data = loaded_data
            self.scenario_events = self.scenario_data["ScenarioEvents"]

            self.event_list.clear()

            self.is_modified = False
            self.setWindowTitle("ProjectSC Scenario Editor")


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

                    case "sound":
                        sound_type = event["sound_type"]
                        sound_name = event["sound_name"]
                        self.event_list.addItem(f"{index} {event_type} {sound_type} {sound_name}")

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
            self.is_modified = False
            self.setWindowTitle("ProjectSC Scenario Editor")

    def add_background_resource(self):
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "배경 이미지 선택",
            "",
            "이미지 파일 (*.png *.jpg *.jpeg *.webp)"
        )

        if not file_path:
            return

        source = Path(file_path)
        background_name = source.stem

        destination_dir = BASE_PATH / "backgrounds"
        destination_dir.mkdir(parents=True, exist_ok=True)

        destination = destination_dir / source.name

        if background_name in self.settings["backgrounds"]:
            QMessageBox.warning(
                self,
                "중복된 배경",
                f"'{background_name}' 배경은 이미 등록되어 있습니다."
            )
            return
        
        for extension in [".png", ".jpg", ".jpeg", ".webp"]:
            existing_file = destination_dir / f"{background_name}{extension}"

            if existing_file.exists():
                QMessageBox.warning(
                    self,
                    "중복된 파일",
                    f"'{background_name}' 이름의 이미지 파일이 이미 존재합니다."
                )
                return



        shutil.copy2(source, destination)

        print(f"복사 완료: {destination}")

        if background_name not in self.settings["backgrounds"]:
            self.settings["backgrounds"].append(background_name)
            self.background_combo.addItem(background_name)

            save_settings(self)
            self.background_combo.setCurrentText(background_name)

    def mark_modified(self):
        self.is_modified = True
        self.setWindowTitle("ProjectSC Scenario Editor *")

    def confirm_unsaved_changes(self):
        if not self.is_modified:
            return True

        result = QMessageBox.question(
            self,
            "저장되지 않은 변경 사항",
            "변경 사항이 저장되지 않았습니다.\n저장하시겠습니까?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )

        if result == QMessageBox.Save:
            self.save_file()
            return not self.is_modified

        elif result == QMessageBox.Discard:
            return True

        else:
            return False

    def closeEvent(self, event):
        if self.confirm_unsaved_changes():
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()


main()