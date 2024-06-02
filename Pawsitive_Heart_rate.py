import asyncio
import numpy as np
from bleak import BleakClient
from datetime import datetime
import pyrebase
import signal

# Firebase configuration
config = {
    "apiKey": "AIzaSyCc5UcrsiyYfwE2gnfK_yHRYg1dtl7cF8",
    "authDomain": "pawsitude-2bab7.firebaseapp.com",
    "databaseURL": "https://pawsitude-2bab7-default-rtdb.firebaseio.com",
    "storageBucket": "pawsitude-2bab7.appspot.com"
}  

firebase = pyrebase.initialize_app(config)
db = firebase.database()

HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
DEVICE_ADDRESS = "DF:0C:AA:B4:B2:12"

rr_intervals = []

def dfa(signal, nvals=None):
    """
    Detrended Fluctuation Analysis (DFA) for calculating long-range correlations
    in a time series.

    Args:
        signal (np.array): Array of time series values.
        nvals (list of int, optional): List of window sizes. Defaults to None.

    Returns:
        float: The DFA alpha value.
    """
    L = len(signal)
    if nvals is None:
        nvals = np.floor(np.logspace(0.5, np.log10(L/4), 20)).astype(int)

    signal_mean = np.mean(signal)
    y_n = np.cumsum(signal - signal_mean)

    F_n = []
    for n in nvals:
        y_n_n = y_n[:L//n*n].reshape((L//n, n))
        y_n_n = y_n_n - y_n_n.mean(axis=1, keepdims=True)
        F_n.append(np.sqrt((y_n_n**2).mean()))

    F_n = np.array(F_n)
    nvals = np.array(nvals)

    coeffs = np.polyfit(np.log10(nvals), np.log10(F_n), 1)
    return coeffs[0]

async def run_heart_rate_monitor(address, interval=0.3):
    """
    Connects to the Bluetooth device and monitors heart rate data.

    Args:
        address (str): The MAC address of the Bluetooth device.
        interval (float): The interval in seconds to wait between checks.
    """
    print(f"Connecting to device at {address}...")
    try:
        async with BleakClient(address) as client:
            if await client.is_connected():
                print(f"Connected to device at {address}")
                running = True

                def handle_stop_signals(signum, frame):
                    nonlocal running
                    print("\nStopping heart rate monitor...")
                    running = False

                # Register signal handlers for graceful shutdown
                signal.signal(signal.SIGINT, handle_stop_signals)
                signal.signal(signal.SIGTERM, handle_stop_signals)

                def callback(sender, data):
                    if running:
                        try:
                            heart_rate = int.from_bytes(data[1:2], byteorder='little')
                            now = datetime.now()
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            print(f"Timestamp: {formatted_time}, Heart Rate: {heart_rate} BPM")
                            
                            # Simulating RR intervals from heart rate data
                            rr_interval = 60000 / heart_rate  # in ms
                            rr_intervals.append(rr_interval)
                            
                            if len(rr_intervals) > 1:
                                diff_rr_intervals = np.diff(rr_intervals)
                                sd1 = np.sqrt(np.var(diff_rr_intervals) / 2)
                                sd2 = np.sqrt(2 * sd1 ** 2 + np.var(rr_intervals))
                                dfa_alpha = dfa(rr_intervals)
                                
                                print(f"SD1: {sd1}, SD2: {sd2}, DFA: {dfa_alpha}")
                                
                                # Update Firebase with the latest heart rate and DFA alpha data
                                data_to_update = {
                                    "Timestamp": formatted_time,
                                    "Heart Rate": heart_rate,
                                    "DFA": dfa_alpha
                                }
                                db.child("heart_rate_data").set(data_to_update)
                        except Exception as e:
                            print(f"An error occurred: {e}")

                await client.start_notify(HEART_RATE_UUID, callback)
                print("Started receiving heart rate data...")

                # Loop until stopped by signal
                while running:
                    await asyncio.sleep(interval)

                await client.stop_notify(HEART_RATE_UUID)
                print("Stopped heart rate monitor.")
            else:
                print("Failed to connect.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_heart_rate_monitor(DEVICE_ADDRESS))
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
