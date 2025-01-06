from flask import Flask, render_template, request  # Import necessary Flask modules for app creation, rendering templates, and handling requests.
import requests  # Import the requests library to make HTTP requests to external APIs.
from datetime import datetime  # Import datetime to handle date and time formatting.
import pytz  # Import pytz for handling timezones (to correctly display local times).
import os  # Import os for environment variable handling (to store sensitive data securely, such as the API key).

app = Flask(__name__)  # Initialize a Flask web application.

# Fetch the API Key from an environment variable for security purposes (ensure the key is not hardcoded in production).
API_Key = os.environ.get("API_KEY", "7f0fd63ad0a8859cb91057af6acd7bda")  # If the environment variable is not found, use a default key (for testing).

@app.route("/", methods=["GET", "POST"])  # Define the route for the home page, which accepts both GET (default) and POST requests.
def weather():
    weather_info = None  # Initialize a variable to store weather data or error messages.
    
    # If the request method is POST (i.e., form submission with city name)
    if request.method == "POST":
        city = request.form["city"].strip()  # Get the city name from the form, and remove any extra spaces (strip leading/trailing spaces).
        
        # If no city name is provided, set an error message
        if not city:
            weather_info = {"error": "Please enter a valid city name."}
        
        else:
            # If the city name length is too long, return an error
            if len(city) > 100:
                weather_info = {"error": "City name is too long. Please enter a valid city name."}
            else:
                # Construct the URL to call the OpenWeatherMap API, embedding the API key and the city name.
                base_url = f"http://api.openweathermap.org/data/2.5/weather?appid={API_Key}&q={city}&units=metric"

                # Try to fetch the weather data from the OpenWeatherMap API
                try:
                    response = requests.get(base_url)  # Make the GET request to fetch data from the API.
                    response.raise_for_status()  # Raise an HTTPError if the response code is not 200 (successful).
                    weather_data = response.json()  # Parse the response as JSON and store it in weather_data.

                    # If the 'cod' key in the response is 200, the city was found and the data is valid.
                    if weather_data.get('cod') == 200:
                        # Extract city and country from the response
                        city_name = weather_data['name']
                        country = weather_data['sys']['country']

                        # Extract the weather data: temperature, feels like, humidity, weather description, etc.
                        temperature = weather_data['main']['temp']  # Current temperature.
                        feels_like = weather_data['main']['feels_like']  # Feels like temperature.
                        humidity = weather_data['main']['humidity']  # Humidity level.
                        weather_desc = weather_data['weather'][0]['description']  # Weather description (e.g., clear sky, rain).
                        wind_speed = weather_data['wind'].get('speed', 'N/A')  # Wind speed, defaulting to 'N/A' if not available.
                        wind_deg = weather_data['wind'].get('deg', 'N/A')  # Wind direction (in degrees), defaulting to 'N/A'.

                        # Extract and convert sunrise and sunset times using the timezone offset
                        timezone_offset = weather_data['timezone']  # Get the timezone offset from the API response (in seconds).
                        
                        # Convert the timezone offset to a pytz timezone format (e.g., Etc/GMT+2).
                        local_timezone = pytz.timezone(f"Etc/GMT{'+' if timezone_offset < 0 else ''}{-timezone_offset // 3600}")
                        
                        # Get the current local time using the timezone offset
                        current_time = datetime.now(local_timezone)
                        day = current_time.strftime('%A')  # Get the day of the week (e.g., Monday).
                        date = current_time.strftime('%d %B %Y')  # Get the full date (e.g., 29 December 2024).
                        
                        # Convert the sunrise and sunset timestamps into the local time zone and format them
                        sunrise_time = datetime.fromtimestamp(weather_data['sys']['sunrise'], local_timezone).strftime('%H:%M:%S')
                        sunset_time = datetime.fromtimestamp(weather_data['sys']['sunset'], local_timezone).strftime('%H:%M:%S')

                        # Store all the extracted data in the weather_info dictionary for use in the template
                        weather_info = {
                            "city": f"{city_name}, {country}",  # City and country (e.g., New York, US).
                            "day": day,  # The day of the week (e.g., Monday).
                            "date": date,  # The current date (e.g., 29 December 2024).
                            "temperature": f"{temperature:.2f}°C",  # Temperature, rounded to 2 decimal places.
                            "feels_like": f"{feels_like:.2f}°C",  # Feels-like temperature, rounded to 2 decimal places.
                            "humidity": f"{humidity}%",  # Humidity percentage.
                            "description": weather_desc.capitalize(),  # Weather description with the first letter capitalized.
                            "wind_speed": f"{wind_speed} m/s",  # Wind speed (in meters per second).
                            "wind_deg": f"{wind_deg}°",  # Wind direction (in degrees).
                            "sunrise": sunrise_time,  # Sunrise time in the local timezone.
                            "sunset": sunset_time  # Sunset time in the local timezone.
                        }
                    else:
                        # If the city was not found (response code is not 200), set an error message
                        weather_info = {"error": "City not found. Please check the city name."}

                # Catch any errors that occur during the API call
                except requests.exceptions.RequestException as e:
                    weather_info = {"error": f"An error occurred while fetching weather data: {e}"}
    
    # Render the weather_info dictionary (or error message) in the weather.html template
    return render_template("weather.html", weather_info=weather_info)

# Start the Flask application in debug mode if it's the main module being run
if __name__ == "__main__":
    # The app will run with debug mode enabled if the FLASK_DEBUG environment variable is set to "True"
    app.run(debug=os.environ.get("FLASK_DEBUG", "False") == "True")
