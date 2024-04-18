import asyncio
import csv
from bleak import BleakClient
from datetime import datetime
import pyrebase
import signal
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Firebase configuration
config = {
    "apiKey": "AIzaSyCc5UcrsiyYfwE2gnfK_yHRYg1dtl7cFf8",
    "authDomain": "pawsitude-2bab7.firebaseapp.com",
    "databaseURL": "https://pawsitude-2bab7-default-rtdb.firebaseio.com",
    "storageBucket": "pawsitude-2bab7.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
DEVICE_ADDRESS = "DF:0C:AA:B4:B2:12"
csv_file = 'heart_rate_data.csv'

async def run_heart_rate_monitor(address, interval=0.3):
    print(f"Connecting to device at {address}...")
    async with BleakClient(address) as client:
        if await client.is_connected():
            print(f"Connected to device at {address}")
            running = True

            with open(csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Heart Rate (BPM)"])

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
                            formatted_time = now.strftime("%H:%M:%S")
                            print(f"Timestamp: {formatted_time}, Heart Rate: {heart_rate} BPM")
                            writer.writerow([now.strftime("%Y-%m-%d %H:%M:%S"), heart_rate])
                            
                            # Update Firebase with the new data
                            data_to_update = {formatted_time: f"Heart rate: {heart_rate}"}
                            db.child("heart_rate_data").child(now.strftime("%Y%m%d%H")).update(data_to_update)
                        except Exception as e:
                            print(f"An error occurred: {e}")

                await client.start_notify(HEART_RATE_UUID, callback)
                print("Started receiving heart rate data...")

                # Loop until stopped by signal
                while running:
                    await asyncio.sleep(interval)

                await client.stop_notify(HEART_RATE_UUID)
                print("CSV file has been saved.")
        else:
            print("Failed to connect.")

def plot_heart_rate_data(csv_file_path):
    timestamps = []
    heart_rates = []

    with open(csv_file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header
        for row in csvreader:
            timestamps.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
            heart_rates.append(int(row[1]))

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, heart_rates, marker='o')
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gcf().autofmt_xdate()

    plt.xlabel('Time (hours:minutes)')
    plt.ylabel('Heart Rate (BPM)')
    plt.title('Heart Rate Over Time')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    try:
        asyncio.run(run_heart_rate_monitor(DEVICE_ADDRESS))
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Preparing to plot data.")
    finally:
        plot_heart_rate_data(csv_file)