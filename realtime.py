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


def collect_data(model, host="localhost", port=5555):
    dp = DataProcess()
    pp = Preprocess()
    prev = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        while True:
            try:
                data = s.recv(16384)
                if not data:
                    break
                now = time.time()
                fps = str(round(1 / (now-prev), 2)) + ' '
                if len(fps) < 6:
                    fps += (6-len(fps))*'='
                prev = now
                radar_data = json.loads(data.decode())
                velocity = radar_data["tracking_object"].get("v", [])
                _, groups, _, vectors, _ = dp.process_cluster(radar_data, thr=10, delay=15)
                print(f"\r=================== fps: {fps}===================", end='')
                if any([item[-1] < -(0.8/np.sqrt(2)) for item in velocity]) and len(groups) >= 1:
                    print("\nDrop Detected")
                    data = pp.load_group_by_subject(groups, vectors)
                    input_data = np.expand_dims(data, axis=0)
                    prediction = (model.predict(input_data) > 0.5).astype(int)[0][0]
                    if prediction == 1:
                        os.makedirs("./false_positive", exist_ok=True)
                        with open(f"./false_positive/{str(time.time()).split('.')}.json", "a") as fp:
                            fp.write(f"[{time.time()}, {radar_data}],\n")
                        print("Prediction: Fall")
                        beep()
                    else:
                        print("Prediction: Not Fall")

            except Exception as e:
                break


def main():
    model = load_model("./res/TPR0.90_TNR0.97.h5")
    radar = initialize_radar()
    radar.start()
    while True:
        try:
            collect_data(model)
        except KeyboardInterrupt:
            radar.stop()
            break

        except:
            pass


if __name__ == '__main__':
    main()
