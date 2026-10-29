from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QPen, QFont, QPixmap
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem


class ScenarioPreview(QGraphicsView):

    PREVIEW_WIDTH = 1600
    PREVIEW_HEIGHT = 900

    DIALOGUE_HEIGHT_RATIO = 0.30

    def __init__(self, parent=None):
        super().__init__(parent)

        # 미리보기 장면 생성
        self.preview_scene = QGraphicsScene(self)
        self.preview_scene.setSceneRect(
            0, 0,
            self.PREVIEW_WIDTH,
            self.PREVIEW_HEIGHT
        )

        self.setScene(self.preview_scene)

        # 스크롤바 숨기기
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 미리보기 화면 구성
        self.setup_preview()

    def setup_preview(self):

        # # 배경 (임시 색상)
        # self.preview_scene.addRect(
        #     0, 0,
        #     self.PREVIEW_WIDTH,
        #     self.PREVIEW_HEIGHT,
        #     QPen(Qt.NoPen),
        #     QBrush(QColor(45, 45, 55))
        # )

        # 미리보기 화면에 이미지 추가
        self.background_item = self.preview_scene.addPixmap(QPixmap())

        self.background_placeholder = self.preview_scene.addText(
            "배경이 설정되지 않았습니다.",
            QFont("Malgun Gothic", 32)
        )

        self.background_placeholder.setDefaultTextColor(
            QColor(180, 180, 180)
        )

        text_rect = self.background_placeholder.boundingRect()

        x = (self.PREVIEW_WIDTH - text_rect.width()) / 2
        y = (self.PREVIEW_HEIGHT - text_rect.height()) / 2

        self.background_placeholder.setPos(x, y)

        self.clear_background()

        # 대사창 크기 계산
        dialogue_height = (
            self.PREVIEW_HEIGHT * self.DIALOGUE_HEIGHT_RATIO
        )

        dialogue_y = self.PREVIEW_HEIGHT - dialogue_height

        # 반투명 대사창
        self.preview_scene.addRect(
            0,
            dialogue_y,
            self.PREVIEW_WIDTH,
            dialogue_height,
            QPen(Qt.NoPen),
            QBrush(QColor(0, 0, 0, 160))
        )

        # 화자 이름
        self.speaker_text = self.preview_scene.addText(
            "화자 이름",
            QFont("Malgun Gothic", 32, QFont.Bold)
        )

        self.speaker_text.setDefaultTextColor(QColor(255, 255, 255))
        self.speaker_text.setPos(60, dialogue_y + 20)


        # 대사 내용
        self.dialogue_text = self.preview_scene.addText(
            "여기에 대사가 표시됩니다.",
            QFont("Malgun Gothic", 28)
        )

        self.dialogue_text.setDefaultTextColor(QColor(255, 255, 255))
        self.dialogue_text.setPos(60, dialogue_y + 85)

        # 대사창 너비에 맞춰 자동 줄바꿈
        self.dialogue_text.setTextWidth(self.PREVIEW_WIDTH - 120)

    def set_dialogue_text(self, text):
        self.dialogue_text.setPlainText(text)

    def set_speaker(self, speaker):
        self.speaker_text.setPlainText(speaker)

    def set_background(self, image_path):
        # 배경 이미지 불러오기
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print(f"배경 이미지를 불러올 수 없습니다: {image_path}")
            return

        # 이미지를 1600x900 크기로 조정
        pixmap = pixmap.scaled(
            self.PREVIEW_WIDTH,
            self.PREVIEW_HEIGHT,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.background_item.setPixmap(pixmap)
        self.background_placeholder.hide()

    def clear_background(self, message="배경이 설정되지 않았습니다."):
        self.background_item.setPixmap(QPixmap())
        self.preview_scene.setBackgroundBrush(QColor(0, 0, 0))
        self.background_placeholder.setPlainText(message)
        self.background_placeholder.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # 위젯 크기에 맞춰 16:9 비율 유지
        self.fitInView(
            self.preview_scene.sceneRect(),
            Qt.KeepAspectRatio
        )

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    preview = ScenarioPreview()

    preview.set_speaker("시헌")
    preview.set_dialogue_text(
        "그건 말이 좀 심하시네요...\n정말 그렇게 생각하세요?"
    )
    preview.set_background("testfiles/TEST_BG02.jpg")
    preview.clear_background()
    preview.clear_background("배경 이미지 파일을 찾을 수 없습니다.")

    preview.resize(960, 540)
    preview.show()

    sys.exit(app.exec())