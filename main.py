import sys
import numpy as np
import pyaudio
import librosa
import librosa.display
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QRect
from PyQt5 import uic
from datetime import datetime

 
from tensorflow.keras.models import load_model
from tensorflow.keras import models
from tensorflow.keras.losses import categorical_crossentropy
import cv2
import os

form_class = uic.loadUiType("gui_1.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.title = '구멍가공 모니터링'
        self.setupUi(self)
        
        self.class_indices = ['초반', '중반', '후반']
        self.model = load_model('model/model_1.h5',compile = False)
        self.initUI()


    def initUI(self):
        self.setWindowTitle(self.title)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.setDisabled(True)
        self.stop_button.clicked.connect(self.stop_recording)
        
        self.figure, self.ax = plt.subplots(figsize = (10,10))
        self.canvas = FigureCanvas(self.figure)
        self.graph_verticalLayout.addWidget(self.canvas)

        self.elapsed_timer = QTimer(self)
        self.elapsed_timer.timeout.connect(self.update_elapsed_time)

        self.show()

    def update_plot(self, data):
        self.ax.clear()
        plt.gca().xaxis.set_visible(False)
        plt.gca().yaxis.set_visible(False)
        plt.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        img = librosa.display.specshow(data, sr=32000, x_axis='time', y_axis='linear', ax=self.ax, cmap='plasma',vmin = -5, vmax = 5)
        self.canvas.draw()
        self.figure.savefig('stft_image.png')
        self.predict_cnn('stft_image.png')


    def update_time(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.current_time_label.setText(f'현재 시간: {current_time}')


    def update_elapsed_time(self):
        elapsed_time = datetime.now() - self.start_time
        elapsed_seconds = elapsed_time.total_seconds()
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.elapsed_time_label.setText(f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}')

    def start_recording(self):
        self.start_time = datetime.now()
        self.elapsed_timer.start(1000)
        self.audio_thread = AudioThread()
        self.audio_thread.audio_signal.connect(self.update_plot)
        self.audio_thread.start()
        self.start_button.setDisabled(True)
        self.stop_button.setDisabled(False)


    def stop_recording(self):
        self.audio_thread.stop()
        self.start_button.setDisabled(False)
        self.stop_button.setDisabled(True)
        self.elapsed_timer.stop()

    def predict_cnn(self,image_path):
        
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        img = img/255.0
        img = cv2.resize(img,(500,500))
        
        img = img.reshape(1,500,500,3)
        prediction = self.model.predict(img)
        self.current_state_label.setText(f'{self.class_indices[np.argmax(prediction)]} 구간 가공 중입니다...')


class AudioThread(QThread):
    audio_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        sampling_rate = 32000
        chunk_size = 1024
        seconds = 5
        num_chunks = int(sampling_rate / chunk_size * seconds)
        audio_buffer = np.zeros(sampling_rate * seconds)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=sampling_rate,
                        input=True,
                        frames_per_buffer=chunk_size)

        while self.running:
            for i in range(num_chunks):
                if not self.running:
                    break
                data = np.frombuffer(stream.read(chunk_size), dtype=np.int16).astype(np.float32)
                audio_buffer = np.roll(audio_buffer, -chunk_size)
                audio_buffer[-chunk_size:] = data

            if self.running:
                stft = librosa.stft(audio_buffer, n_fft=2048, hop_length=512)
                db_stft = librosa.amplitude_to_db(np.abs(stft), ref=np.max)
                self.audio_signal.emit(db_stft)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self.running = False
        self.wait()


        



if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()