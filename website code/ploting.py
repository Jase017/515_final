import streamlit as st
import pyrebase
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time

# Firebase configuration
config = {
    "apiKey": "AIzaSyCc5UcrsiyYfwE2gnfK_yHRYg1dtl7cFf8",
    "authDomain": "pawsitude-2bab7.firebaseapp.com",
    "databaseURL": "https://pawsitude-2bab7-default-rtdb.firebaseio.com",
    "storageBucket": "pawsitude-2bab7.appspot.com"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Streamlit application title
st.title('Real-time Heart Rate Monitor')

# Real-time data fetching function
def fetch_data():
    data = db.child('heart_rate_data').get().val()
    if data:
        timestamp = data.get('timestamp')
        heart_rate = data.get('heart_rate')
        return timestamp, heart_rate
    return None, None

# Set up the initial plot
fig, ax = plt.subplots(figsize=(10, 6))
line, = ax.plot([], [], color='blue', marker='o', markersize=5, linestyle='-', linewidth=2, label='Heart Rate (BPM)')

# Configure plot appearance
ax.set_xlabel('Time', fontsize=14)
ax.set_ylabel('Heart Rate (BPM)', fontsize=14)
ax.set_title('Heart Rate Over Time', fontsize=16)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
fig.autofmt_xdate()

# Add grid
ax.grid(True, linestyle='--', alpha=0.5)

# Add legend
ax.legend(loc='upper left', fontsize=12)

# Set background color
ax.set_facecolor('#f0f0f0')

# Placeholder for the chart
chart = st.empty()

# Initialize data lists
timestamps = []
heart_rates = []

# Real-time data fetching and plotting
while True:
    timestamp, heart_rate = fetch_data()
    if timestamp and heart_rate:
        timestamps.append(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"))
        heart_rates.append(heart_rate)
        
        # Update plot data
        line.set_xdata(timestamps)
        line.set_ydata(heart_rates)
        ax.relim()
        ax.autoscale_view()

        # Update chart in Streamlit
        with chart.container():
            st.pyplot(fig)
    
    # Sleep for a short duration before fetching data again
    time.sleep(1)
