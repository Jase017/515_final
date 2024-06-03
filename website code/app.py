import streamlit as st
import requests
from datetime import datetime
import time
import base64

# Constants for API
WEATHER_API_KEY = 'bb75a58b0c1df1a9a5cd689e1ea9d145'
WEATHER_BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?'
IPINFO_API_KEY = '497433d3776dfd'
IPINFO_URL = f"https://ipinfo.io?token={IPINFO_API_KEY}"
TIME_API_URL = 'http://worldtimeapi.org/api/timezone/America/Los_Angeles'
FIREBASE_URL = 'https://pawsitude-2bab7-default-rtdb.firebaseio.com/'

def get_location():
    """Fetch the location based on IP address"""
    response = requests.get(IPINFO_URL)
    data = response.json()
    return data['city']

def get_weather(city):
    """Fetch weather data for a specified city"""
    response = requests.get(f"{WEATHER_BASE_URL}q={city}&appid={WEATHER_API_KEY}&units=metric")
    data = response.json()
    return data

def get_time():
    """Fetch current time from WorldTimeAPI"""
    response = requests.get(TIME_API_URL)
    data = response.json()
    datetime_str = data['datetime']
    return datetime_str.split('T')[1].split('.')[0]  # Extract time in HH:MM:SS format

def get_date():
    """Fetch current date"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d")

def load_image_to_base64(image_path):
    """Convert image to base64 to use as a background"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

def get_firebase_data(path):
    """Fetch data from Firebase"""
    url = f"{FIREBASE_URL}{path}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_weather_icon(description):
    """Get weather icon based on description"""
    icons = {
        'clear sky': '☀️',
        'few clouds': '🌤',
        'scattered clouds': '☁️',
        'broken clouds': '☁️',
        'shower rain': '🌧',
        'rain': '🌧',
        'thunderstorm': '⛈',
        'snow': '❄️',
        'mist': '🌫'
    }
    return icons.get(description, '☁️')

def main():
    # Convert logo image to base64
    logo_base64 = load_image_to_base64("pawsitive.png")  # Path to the uploaded image
    active_base64 = load_image_to_base64("active.gif")  # Replace with the path to your GIF image
    relaxing_base64 = load_image_to_base64("relaxing.gif")  # Replace with the path to your relaxed GIF image
    overload_base64 = load_image_to_base64("overload.gif")  # Replace with the path to your overload GIF image
    other_base64 = load_image_to_base64("otherstage.gif")  # Replace with the path to your overload GIF image

    # Add custom styles
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #FAF3E0;  /* Sets the background color to off-white */
            color: black;  /* Sets text color to black */
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; /* Improves font appearance */
            padding: 20px; /* Adds padding around the entire app */
        }}
        .time {{
            position: fixed;
            top: 60px;  
            left: 20px;  
            font-size: 24px;
            font-weight: bold;
            color: black; /* Sets text color to black */
        }}
        .weather {{
            position: fixed;
            top: 60px;  
            right: 20px;  
            font-size: 24px;
            font-weight: bold;
            color: black; /* Sets text color to black */
        }}
        .logo {{
            position: fixed;
            bottom: 20px;  
            right: 20px;  
            width: 150px;  
            height: 150px;  
        }}
        .date {{
            position: fixed;
            bottom: 20px;  
            left: 20px;  
            font-size: 24px;
            font-weight: bold;
            color: black; /* Sets text color to black */
        }}
        h1 {{
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: black; /* Sets text color to black */
            margin-top: 20px; /* Adds margin on top */
        }}
        h2 {{
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: black; /* Sets text color to black */
            margin-top: 20px; /* Adds margin on top */
        }}
        p {{
            text-align: center;
            font-size: 20px;
            color: black; /* Sets text color to black */
            margin-top: 20px; /* Adds margin on top */
        }}
        .data-container {{
            white-space: pre-wrap;  /* Allows content to wrap */
            color: black; /* Sets text color to black */
            margin-top: 20px; /* Adds margin on top */
        }}
        </style>
        <div>
            <img src="data:image/png;base64,{logo_base64}" class="logo">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Time container
    st.markdown("<div class='time' id='time-container'></div>", unsafe_allow_html=True)
    time_container = st.empty()

    # Weather container
    st.markdown("<div class='weather' id='weather-container'></div>", unsafe_allow_html=True)
    weather_container = st.empty()

    # Date container
    st.markdown(f"<div class='date'><b>Date:</b> {get_date()}</div>", unsafe_allow_html=True)

    heartrate_container = st.empty()
    barking_container = st.empty()
    stage_container = st.empty()
    gif_container = st.empty()

    # Initialize previous barking count
    previous_barking_count = None

    # Continuously update time, weather, and Firebase data
    while True:
        current_time = get_time()
        time_container.markdown(f"<div class='time'>{current_time}</div>", unsafe_allow_html=True)

        try:
            city = get_location()
            weather_data = get_weather(city)
            if 'main' in weather_data:
                temperature = f"{weather_data['main']['temp']} °C"
                description = weather_data['weather'][0]['description']
                icon = get_weather_icon(description)
                weather_info = f"<div class='weather'><b>{city}</b><br>{temperature},<br>{description} {icon}</div>"
            else:
                weather_info = "<div class='weather'>Weather data not available</div>"
        except Exception as e:
            weather_info = f"<div class='weather'>Error fetching weather data: {e}</div>"

        weather_container.markdown(weather_info, unsafe_allow_html=True)

        try:
            heartrate = get_firebase_data('heart_rate_data/Heart Rate')
            current_barking_count = get_firebase_data('Barking/count')
            stage = get_firebase_data('predictions/prediction')

            if stage:
                if stage == "active":
                    stage_message = "Your dog is active!"
                    gif_base64 = active_base64
                elif stage == "relaxing":
                    stage_message = "Your dog is relaxing!"
                    gif_base64 = relaxing_base64
                elif stage == "stress":
                    stage_message = "Your dog is overload!"
                    gif_base64 = overload_base64
                else:
                    stage_message = "Your dog is in an unknown state!"
                    gif_base64 = other_base64  # Default to active GIF
            else:
                stage_message = "No stage data available!"
                gif_base64 = other_base64  # Default to active GIF

            # Check if barking count has changed
            if previous_barking_count is not None and current_barking_count != previous_barking_count:
                barking_message = "🐕‍🦺Your dog is barking!🐕‍🦺"
            else:
                barking_message = "Your dog is quiet"

            previous_barking_count = current_barking_count

            heartrate_container.markdown(f"<p class='data-container'><b>Heartrate:</b>{heartrate}</p>", unsafe_allow_html=True)
            barking_container.markdown(f"<p class='data-container'><b>{barking_message}</b></p>", unsafe_allow_html=True)
            stage_container.markdown(f"<h2>{stage_message}</h2>", unsafe_allow_html=True)
            gif_container.markdown(
                f"""
                <div style='text-align: center;'>
                    <img src="data:image/gif;base64,{gif_base64}" width="300" height="200" />
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error fetching Firebase data: {e}")

        time.sleep(1)  # Update every 1 second

if __name__ == "__main__":
    main()
