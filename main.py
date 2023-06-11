import pprint
import time
import traceback

from lib.radar import Radar
from serial import SerialException
import matplotlib.pyplot as plt

CLI_BAUD = 115200
DATA_BAUD = 921600


if __name__ == '__main__':
    radar = Radar("rangedoppler.cfg", CLI_BAUD, DATA_BAUD)
    while True:
        try:
            dataOK, frameNumber, range_doppler, range_profile = radar.parse_data()
            if dataOK:
                radar.plot_range_doppler(range_doppler, alpha=0.7, threshold=200)
                radar.write_to_json(range_doppler)
                # time.sleep(1/30)

        except KeyboardInterrupt or SerialException:
            # if ^C pressed
            radar.close_connection()
            print("\nPeace")
            break

        except Exception as e:
            radar.close_connection()
            print(f"\nShit code: {e} - ", end='')
            traceback.print_exc()
            break
