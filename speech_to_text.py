import speech_recognition as sr

def voice_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            return r.recognize_google(audio)
        except sr.WaitTimeoutError:
            return "No speech detected (Timeout)."
        except sr.UnknownValueError:
            return "Could not understand the audio clearly."
        except Exception as e:
            return f"Audio hardware error: {str(e)}"