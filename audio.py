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
        """Mengucapkan teks menggunakan text-to-speech"""
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
        """Destruktor untuk membersihkan resource"""
        try:
            if self.engine:
                pass
        except:
            pass
