import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import pywhatkit
import wikipedia
import requests

# ----------------- ENGINE SETUP -----------------
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    print("JARVIS:", text)
    engine.say(text)
    engine.runAndWait()

# ----------------- LISTEN -----------------
def take_command():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:5
        command = r.recognize_google(audio)
        command = command.lower()
        print("User:", command)
    except:
        return "none"

    return command

# ----------------- WEATHER -----------------
def get_weather(city):
    api_key = "your_api_key"  # optional (OpenWeatherMap)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        data = requests.get(url).json()
        temp = data['main']['temp']
        speak(f"Temperature in {city} is {temp} degree Celsius")
    except:
        speak("Weather info not available")

# ----------------- MAIN BRAIN -----------------
def run_jarvis():

    while True:
        command = take_command()

        if command == "none":
            continue

        # TIME
        elif "time" in command:
            time = datetime.datetime.now().strftime("%I:%M %p")
            speak("Current time is " + time)

        # DATE
        elif "date" in command:
            date = datetime.datetime.now().strftime("%B %d, %Y")
            speak("Today is " + date)

        # YOUTUBE
        elif "play" in command:
            song = command.replace("play", "")
            speak("Playing " + song)
            pywhatkit.playonyt(song)

        # GOOGLE
        elif "search" in command:
            query = command.replace("search", "")
            speak("Searching " + query)
            pywhatkit.search(query)

        # WIKIPEDIA
        elif "who is" in command:
            person = command.replace("who is", "")
            info = wikipedia.summary(person, 1)
            speak(info)

        # OPEN WEBSITES
        elif "open youtube" in command:
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube")

        elif "open google" in command:
            webbrowser.open("https://google.com")
            speak("Opening Google")

        # WEATHER
        elif "weather in" in command:
            city = command.replace("weather in", "")
            get_weather(city)

        # EXIT
        elif "stop" in command:
            speak("Goodbye!")
            break   

        else:
            speak("I did not understand that command")

# ----------------- START -----------------
speak("JARVIS activated")
run_jarvis()