import multiprocessing
import time
import json
import os
import socket
import sys
import traceback
import matplotlib.pyplot as plt

import numpy as np
from tensorflow.keras.models import load_model
from lib.thread_radar import RadarThread
from lib.data_process import DataProcess
from lib.preprocess import Preprocess


ev = multiprocessing.Event()

CLI_BAUD = 115200
DATA_BAUD = 921600


def initialize_radar(name=None):
    os.makedirs("./output_file", exist_ok=True)
    os.makedirs("./raw_file", exist_ok=True)
    return RadarThread("area_scanner_68xx_ODS.cfg", CLI_BAUD, DATA_BAUD)


def beep():
    file = "./res/beep.mp3"
    if sys.platform == "win32" or sys.platform == "cygwin":
        import playsound
        playsound.playsound(file, True)

    elif sys.platform == "linux":
        os.system("mpg123 " + file)

    return


def collect_data(host="localhost", port=5555):
    model = load_model("./res/TPR0.93_TNR0.96.h5")
    dp = DataProcess()
    pp = Preprocess()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        while True:
            try:
                data = s.recv(16384)
                if not data:
                    break

                radar_data = json.loads(data.decode())
                _, groups, _, vectors = dp.process_cluster(radar_data, thr=10, delay=15)
                data = pp.load_group_by_subject(groups, vectors)
                input_data = np.expand_dims(data, axis=0)
                prediction = (model.predict(input_data) > 0.5).astype(int)[0][0]
                if prediction == 0:
                    print("Prediction: Not Fall")
                else:
                    print("Prediction: Fall")
                    beep()

            except Exception as e:
                break


def main():
    radar = initialize_radar()
    radar.start()
    while True:
        try:
            collect_data()
        except KeyboardInterrupt:
            radar.stop()
            break

        except:
            pass


if __name__ == '__main__':
    main()