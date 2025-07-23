import pyttsx3

class AudioManager:
    def __init__(self):
        self.engine = None
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
        except Exception as e:
            print(f"Error inisialisasi text-to-speech: {e}")
    
    def speak(self, text):
        if self.engine:
            try:
                print(f"\nMemanggil dengan suara: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error saat memanggil dengan suara: {e}")
        else:
            print(f"\n[Suara tidak tersedia] {text}")
    
    def __del__(self):
        try:
            if self.engine:
                self.engine.stop()
        except:
            pass
