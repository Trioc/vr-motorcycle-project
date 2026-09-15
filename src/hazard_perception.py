import sys
import os
import csv
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QStyle, QSlider, QFileDialog, QLabel,
    QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl, QTime, QRect
from PyQt6.QtGui import QMouseEvent, QCloseEvent


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # --- 狀態 ---
        self.click_data = []               # (fx, fy, ms)
        self.videoSize = None              # 影片原始解析度
        self.seeking_by_slider = False
        self.accident_ms = 5000
        self.accident_pos = (320, 240)

        # --- 播放器 ---
        self.mediaPlayer = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audioOutput)

        # --- 影片 widget（只有這一個） ---
        self.videoWidget = QVideoWidget()
        self.videoWidget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.videoWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # 點擊事件
        self.videoWidget.mousePressEvent = self.get_click_position  # type: ignore

        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # --- 控制列 ---
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playButton.clicked.connect(self.play_pause)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderPressed.connect(self._on_slider_pressed)
        self.positionSlider.sliderReleased.connect(self._on_slider_released)
        self.positionSlider.sliderMoved.connect(self._on_slider_moved)

        self.timeLabel = QLabel("00:00 / 00:00")

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.timeLabel)

        # 提示文字
        self.infoLabel = QLabel("提示：點擊影片畫面會記錄『影片座標』與時間。")

        # 開檔 & 匯出按鈕
        self.openButton = QPushButton("開啟影片")
        self.openButton.clicked.connect(self.open_file)

        self.exportButton = QPushButton("匯出紀錄")
        self.exportButton.clicked.connect(self.export_clicks)

        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.openButton)
        bottomLayout.addWidget(self.exportButton)
        bottomLayout.addStretch()

        # --- 主版面 ---
        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.infoLabel)
        layout.addLayout(bottomLayout)
        self.setLayout(layout)

        self.controlLayout = controlLayout
        self.mainLayout = layout
        self._sized_once = False

        # --- 信號 ---
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.mediaStatusChanged.connect(self._on_media_status_changed)
        self.mediaPlayer.errorOccurred.connect(self._on_error)

        self.setWindowTitle("防衛性駕駛測驗")

    # ---------- 基本控制 ----------
    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "開啟影片",
            filter="Video Files (*.mp4 *.mov *.mkv *.avi *.wmv);;All Files (*.*)"
        )
        if fileName:
            if not os.path.exists(fileName):
                self.infoLabel.setText("檔案不存在")
                return

            url = QUrl.fromLocalFile(fileName)
            self.mediaPlayer.setSource(url)
            self.playButton.setEnabled(True)
            self.click_data.clear()
            self.videoSize = None
            self._sized_once = False
            self.infoLabel.setText(f"載入中：{fileName}")

            # 先 play 再 pause 讓 backend 讀取 metaData
            self.mediaPlayer.play()
            self.mediaPlayer.pause()

    def play_pause(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def media_state_icon_refresh(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    # ---------- 時間 & Slider ----------
    def position_changed(self, position):
        self.media_state_icon_refresh()

        if not self.seeking_by_slider:
            self.positionSlider.setValue(position)

        duration = self.mediaPlayer.duration()
        current_time = QTime(0, 0, 0).addMSecs(position)
        total_time = QTime(0, 0, 0).addMSecs(duration if duration > 0 else 0)
        fmt = "mm:ss" if duration < 3_600_000 else "hh:mm:ss"
        self.timeLabel.setText(f"{current_time.toString(fmt)} / {total_time.toString(fmt)}")

    def duration_changed(self, duration):
        self.positionSlider.setRange(0, duration)

    def _on_slider_pressed(self):
        self.seeking_by_slider = True

    def _on_slider_moved(self, pos):
        duration = self.mediaPlayer.duration()
        current_time = QTime(0, 0, 0).addMSecs(pos)
        total_time = QTime(0, 0, 0).addMSecs(duration if duration > 0 else 0)
        fmt = "mm:ss" if duration < 3_600_000 else "hh:mm:ss"
        self.timeLabel.setText(f"{current_time.toString(fmt)} / {total_time.toString(fmt)}")

    def _on_slider_released(self):
        self.seeking_by_slider = False
        self.mediaPlayer.setPosition(self.positionSlider.value())

    # ---------- 取得影片原始解析度 ----------
    def _on_media_status_changed(self, status):
        if self.videoSize:
            return

        try:
            md = self.mediaPlayer.metaData()
            for key in ("Resolution", "VideoResolution", "Size"):
                val = md.get(key) if hasattr(md, "get") else None
                if hasattr(val, "width") and val.width() > 0:
                    self.videoSize = val
                    break
                if isinstance(val, (tuple, list)) and len(val) == 2:
                    w, h = map(int, val)
                    if w > 0 and h > 0:
                        self.videoSize = type("Size", (), {
                            "width": lambda: w,
                            "height": lambda: h
                        })()
                        break
        except Exception:
            pass

        if self.videoSize:
            self.infoLabel.setText(
                f"已取得影片解析度：{self.videoSize.width()}x{self.videoSize.height()}"
            )

    # ---------- 算影片在 widget 裡的實際顯示區域（去黑邊） ----------
    def _video_rect_in_widget(self) -> QRect:
        ww, wh = self.videoWidget.width(), self.videoWidget.height()
        if not self.videoSize:
            return QRect(0, 0, ww, wh)

        vw, vh = self.videoSize.width(), self.videoSize.height()
        if vw <= 0 or vh <= 0:
            return QRect(0, 0, ww, wh)

        widget_ratio = ww / wh if wh else 1.0
        video_ratio = vw / vh

        if video_ratio > widget_ratio:
            new_w = ww
            new_h = int(ww / video_ratio)
            x = 0
            y = (wh - new_h) // 2
        else:
            new_h = wh
            new_w = int(wh * video_ratio)
            y = 0
            x = (ww - new_w) // 2

        return QRect(x, y, new_w, new_h)

    def _map_widget_to_video(self, x: int, y: int):
        rect = self._video_rect_in_widget()
        if not rect.contains(x, y):
            return None

        if not self.videoSize:
            # 沒有解析度資訊時，粗略當 1:1
            return (x, y)

        vw, vh = self.videoSize.width(), self.videoSize.height()
        rx = x - rect.left()
        ry = y - rect.top()
        fx = int(rx * vw / rect.width())
        fy = int(ry * vh / rect.height())
        return (fx, fy)

    # ---------- 滑鼠點擊 ----------
    def get_click_position(self, event: QMouseEvent):
        xw, yw = event.pos().x(), event.pos().y()
        mapped = self._map_widget_to_video(xw, yw)
        now_ms = self.mediaPlayer.position()

        if mapped is None:
            print(f"點到黑邊：widget=({xw},{yw}), time={now_ms} ms")
        else:
            fx, fy = mapped
            self.click_data.append((fx, fy, now_ms))
            print(f"影片座標: ({fx},{fy}), 時間: {now_ms} ms")

            # 示範計算誤差
            ax, ay = self.accident_pos
            time_err = abs(now_ms - self.accident_ms) / 1000.0
            dist = ((fx - ax) ** 2 + (fy - ay) ** 2) ** 0.5
            self.infoLabel.setText(
                f"時間差: {time_err:.3f}s | 距離誤差: {dist:.1f}px  (點:{fx},{fy})"
            )

        # 呼叫原本的事件處理（避免吃掉其他行為）
        QVideoWidget.mousePressEvent(self.videoWidget, event)

    # ---------- 匯出紀錄 ----------
    def export_clicks(self):
        if not self.click_data:
            self.infoLabel.setText("尚未有任何點擊紀錄可匯出。")
            return

        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "儲存點擊紀錄",
            "click_log.csv",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*.*)"
        )
        if not fileName:
            return

        try:
            with open(fileName, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["x", "y", "time_ms", "time_sec"])
                for fx, fy, ms in self.click_data:
                    writer.writerow([fx, fy, ms, ms / 1000.0])
        except Exception as e:
            self.infoLabel.setText(f"匯出失敗：{e}")
        else:
            base = os.path.basename(fileName)
            self.infoLabel.setText(f"已匯出 {len(self.click_data)} 筆紀錄到：{base}")

    # ---------- 錯誤處理 ----------
    def _on_error(self, err):
        print("[QMediaPlayer][ERROR]", err, self.mediaPlayer.errorString())
        self.infoLabel.setText(
            f"載入/播放失敗：{self.mediaPlayer.errorString()} (code {int(err)})"
        )

    # ---------- 關閉 ----------
    def closeEvent(self, event: QCloseEvent):
        try:
            self.mediaPlayer.stop()
        except Exception:
            pass
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.resize(900, 600)   # 初始大小，之後可以自己拉
    player.show()
    sys.exit(app.exec())
