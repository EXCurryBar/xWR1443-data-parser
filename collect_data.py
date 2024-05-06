import multiprocessing
import time
import json
import os
import socket
import sys
from lib.thread_radar import RadarThread
from lib.data_process import DataProcess


ev = multiprocessing.Event()

CLI_BAUD = 115200
DATA_BAUD = 921600
# "light_fall_lr", "light_fall_rl", "light_fall_fw", "light_fall_bw", 
# "sit", "squat", "pick_thing", "walk_pass_fw", "walk_pass_bw", "walk_pass_lr", "walk_pass_rl", "making_bed",
#          "swing", "step_still", "rotate_hand", "raise_hand"
ACTION = ["light_fall_lr", "light_fall_rl", "light_fall_fw", "light_fall_bw", "walk_fall_lr", "walk_fall_rl", "walk_fall_fw", "walk_fall_bw"]
SET = 3


def initialize_radar(name=None):
    os.makedirs("./output_file", exist_ok=True)
    os.makedirs("./raw_file", exist_ok=True)
    return RadarThread("area_scanner_68xx_ODS.cfg", CLI_BAUD, DATA_BAUD)


def beep():
    file = "./res/beep.mp3"
    if sys.platform == "win32" or sys.platform == "cygwin":
        import playsound
        time.sleep(3)
        playsound.playsound(file, True)

        time.sleep(5)
        playsound.playsound(file, True)

    elif sys.platform == "linux":
        os.system("mpg123 " + file)
        time.sleep(3)
        os.system("mpg123 " + file)

        time.sleep(5)
        os.system("mpg123 " + file)

    return


def collect_data(file_name, host="localhost", port=5555):
    dp = DataProcess(write_file=True, file_name=file_name)
    th = multiprocessing.Process(target=beep, args=())
    th.start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        while th.is_alive():
            try:
                data = s.recv(4096)
                radar_data = json.loads(data.decode())
                dp.process_cluster(radar_data, thr=10, delay=15)
            except json.JSONDecodeError as e:
                print("failed to decode json", e)
        dp.finish_write()
    return


def main():
    radar = initialize_radar()
    radar.start()
    subject = input("Enter subject name: ")
    for i, action in enumerate(ACTION):
        if radar.is_running:
            for j in range(SET):
                input(f"\n\nenter to start collecting {subject}'s {action} no.{j}:")
                file_name = f"{subject}_{action}_{j}.json"
                t1 = multiprocessing.Process(target=collect_data, args=(f"{subject}_{action}_{j}",))
                t1.start()

                ev.set()
                t1.join()
                ev.clear()
        else:
            print("Radar UART not UARTing")
            radar.join()
            radar = initialize_radar()
            radar.start()


if __name__ == '__main__':
    main()
