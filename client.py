import socket
import json
from lib.data_process import DataProcess


def receive_single_json_object(server_ip, server_port):
    dp = DataProcess(write_file=True, file_name='test111')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        # Attempt to parse the accumulated data as JSON
        while True:
            try:
                data = s.recv(4096)
                radar_data = json.loads(data.decode())
                # Process the JSON data here
                data = dp.process_cluster(radar_data, thr=30, delay=15)
                # print(f"processed data: {data}\r")
            except json.JSONDecodeError as e:
                print("Failed to decode JSON:", e)
            except KeyboardInterrupt:
                dp.finish_write()
                print("bye")
                break


if __name__ == "__main__":
    import os
    os.makedirs("./output_file", exist_ok=True)
    os.makedirs("./raw_file", exist_ok=True)
    server_ip = 'localhost'  # Change this to your server's IP address
    server_port = 5555  # Change this to your server's port
    receive_single_json_object(server_ip, server_port)
