import datetime
from pathlib import Path

from database import Database
from qr_handler import QRGenerator, QRScanner
from audio import AudioManager
from ui import UI
from antrean import AntreanManager
from crud_handler import CRUDHandler

class SistemAntreanObat:
    def __init__(self):
        self.base_dir = Path("data")
        self.qr_dir = self.base_dir / "qr_codes"
        self.excel_path = self.base_dir / "antrean_harian.xlsx"
        self.master_pasien_path = self.base_dir / "master_pasien.xlsx"
        
        self.base_dir.mkdir(exist_ok=True)
        self.qr_dir.mkdir(parents=True, exist_ok=True)
        
        self.db = Database(self.excel_path, self.master_pasien_path)
        self.antrean = AntreanManager()
        self.qr_generator = QRGenerator()
        self.qr_scanner = QRScanner()
        self.audio = AudioManager()
        
        # Buat instance UI
        self.ui = UI()
        
        self.crud = CRUDHandler(self)
        
        self.initialize_daily_queue()
    
    def panggil_pasien(self):
        id_pasien = self.antrean.panggil_berikutnya()
        
        if id_pasien is None:
            print("\nTidak ada pasien dalam antrean!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        waktu_panggil = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.update_status_pasien(id_pasien, 'terpanggil', waktu_panggil)
        
        pasien = self.db.cari_pasien(id_pasien).iloc[0]
        nama = pasien['nama']
        poli = pasien.get('poli', 'Poli')
        
        self.ui.tampilkan_pemanggilan(pasien['nomor_antrean'], nama, waktu_panggil, poli)
        
        self.audio.speak(f"Perhatian, nomor antrean {pasien['nomor_antrean']}, atas nama {nama}, silakan ke {poli}")
        
        input("\nTekan Enter untuk kembali ke menu...")
    
    def panggil_ulang(self):
        """Memanggil ulang pasien yang telah dipanggil sebelumnya"""
        self.ui.clear_screen()
        print("=== PANGGIL ULANG PASIEN ===\n")
        
        # Cek apakah ada pasien yang sudah dipanggil
        if not self.antrean.sudah_dipanggil:
            print("\nBelum ada pasien yang dipanggil!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        print("\nDaftar pasien yang telah dipanggil:")
        print("-" * 70)
        print(f"{'No.':<5}{'Waktu Panggil':<25}{'Nama':<45}")
        print("-" * 70)
        
        daftar_terpanggil = []
        for i, id_p in enumerate(self.antrean.sudah_dipanggil, 1):
            pasien = self.db.cari_pasien(id_p)
            if not pasien.empty:
                p = pasien.iloc[0]
                waktu_panggil = p['waktu_panggil'] if 'waktu_panggil' in p else '-'
                print(f"{i:<5}{waktu_panggil:<25}{p['nama']:<30}")  
                daftar_terpanggil.append(p['id'])
        
        # Pilih pasien untuk dipanggil ulang
        pilihan = input("\nPilih nomor pasien yang akan dipanggil ulang (1-{}): ".format(len(daftar_terpanggil)))
        
        try:
            idx = int(pilihan) - 1
            if 0 <= idx < len(daftar_terpanggil):
                id_pasien = daftar_terpanggil[idx]
                
                # Ambil data pasien
                pasien = self.db.cari_pasien(id_pasien).iloc[0]
                nama = pasien['nama']
                nomor = pasien['nomor_antrean']
                poli = pasien.get('poli', 'Poli')
                waktu_panggil = pasien.get('waktu_panggil', 'Tidak tersedia')
                
                # Tampilkan pemanggilan dan suara
                self.ui.tampilkan_pemanggilan(nomor, nama, waktu_panggil, poli, is_ulang=True)
                self.audio.speak(f"Pengulangan panggilan. Nomor antrean {nomor}, atas nama {nama}, silakan ke {poli}")
            else:
                print("\nNomor tidak valid!")
        except ValueError:
            print("\nInput tidak valid!")
    
        input("\nTekan Enter untuk kembali ke menu...")
    
    def reset_antrean(self):
        confirm = input("Anda yakin ingin mereset antrean harian? (y/n): ")
        if confirm.lower() == 'y':
            self.antrean.reset()
            print("\nAntrean harian berhasil direset!")
        else:
            print("\nReset antrean dibatalkan.")
        
        input("\nTekan Enter untuk kembali ke menu...")

    def initialize_daily_queue(self):
        df_hari_ini = self.db.get_pasien_hari_ini()
        
        menunggu = df_hari_ini[df_hari_ini['status'] == 'menunggu']
        terpanggil = df_hari_ini[df_hari_ini['status'] == 'terpanggil']
        
        self.antrean.initialize_from_data(
            menunggu['id'].tolist(),
            terpanggil['id'].tolist()
        )
    
    def tandai_selesai(self):
        """Menandai pasien sebagai selesai setelah mengambil obat"""
        self.ui.clear_screen()
        print("=== TANDAI PASIEN SELESAI ===\n")
        
        # Metode pencarian
        print("Cari pasien berdasarkan:")
        print("1. Scan QR Code")
        print("2. Input ID Pasien")
        print("3. Pilih dari Daftar Terpanggil")
        choice = input("\nPilih metode (1-3): ")
        
        id_pasien = None
        if choice == '1':
            print("\nSilakan scan QR code pasien...")
            id_pasien = self.qr_scanner.scan_from_camera()
            if not id_pasien:
                print("\nTidak ada QR code yang terdeteksi atau scan dibatalkan.")
                input("\nTekan Enter untuk kembali ke menu...")
                return
        elif choice == '2':
            id_pasien = input("\nMasukkan ID pasien: ")
        elif choice == '3':
            # Tampilkan daftar pasien terpanggil
            if not self.antrean.sudah_dipanggil:
                print("\nTidak ada pasien yang telah dipanggil!")
                input("\nTekan Enter untuk kembali ke menu...")
                return
                
            print("\nDaftar pasien yang telah dipanggil:")
            print("-" * 70)
            print(f"{'No.':<5}{'Waktu Panggil':<25}{'Nama':<45}")
            print("-" * 70)
            
            daftar_terpanggil = []
            for i, id_p in enumerate(self.antrean.sudah_dipanggil, 1):
                pasien = self.db.cari_pasien(id_p)
                if not pasien.empty:
                    p = pasien.iloc[0]
                    waktu_panggil = p['waktu_panggil'] if 'waktu_panggil' in p else '-'
                    print(f"{i:<5}{waktu_panggil:<25}{p['nama']:<30}")
                    daftar_terpanggil.append(p['id'])
            
            pilihan = input("\nPilih nomor pasien (1-{}): ".format(len(daftar_terpanggil)))
            try:
                idx = int(pilihan) - 1
                if 0 <= idx < len(daftar_terpanggil):
                    id_pasien = daftar_terpanggil[idx]
                else:
                    print("\nNomor tidak valid!")
                    input("\nTekan Enter untuk kembali ke menu...")
                    return
            except ValueError:
                print("\nInput tidak valid!")
                input("\nTekan Enter untuk kembali ke menu...")
                return
        else:
            print("\nPilihan tidak valid!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        # Cari dan tampilkan data pasien
        hasil = self.db.cari_pasien(id_pasien)
        if hasil.empty:
            print("\nPasien tidak ditemukan!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        pasien = hasil.iloc[0]
        
        # Validasi status
        if pasien['status'] == 'selesai':
            print("\nPasien ini sudah ditandai selesai sebelumnya!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
            
        if pasien['status'] == 'menunggu':
            print("\nPasien ini belum dipanggil! Tandai sebagai terpanggil terlebih dahulu.")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        # Tampilkan data pasien
        print("\nData pasien:")
        print("-" * 70)
        print(f"ID           : {pasien['id']}")
        print(f"Nama         : {pasien['nama']}")
        print(f"No. Antrean  : {pasien['nomor_antrean']}")
        print(f"NIK          : {pasien.get('nik', '-')}")
        print(f"Poli         : {pasien.get('poli', '-')}")
        print(f"Status       : {pasien['status']}")
        print("-" * 70)
        
        # Konfirmasi
        confirm = input("\nAnda yakin ingin menandai pasien ini sebagai SELESAI? (y/n): ")
        if confirm.lower() == 'y':
            # Update status
            waktu_selesai = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.update_status_pasien(id_pasien, 'selesai', waktu_selesai)
            
            # Hapus dari antrean sudah_dipanggil jika ada
            if id_pasien in self.antrean.sudah_dipanggil:
                self.antrean.sudah_dipanggil.remove(id_pasien)
            
            print(f"\nPasien {pasien['nama']} berhasil ditandai SELESAI")
        else:
            print("\nPenandaan selesai dibatalkan.")
        
        input("\nTekan Enter untuk kembali ke menu...")

    
    def jalankan(self):
        while True:
            self.ui.tampilkan_banner(
                len(self.antrean.antrean_aktif),
                len(self.antrean.sudah_dipanggil)
            )
            
            choice = self.ui.tampilkan_menu()
            
            if choice == '1':
                self.crud.daftarkan_pasien_baru()     
            elif choice == '2':
                self.crud.daftarkan_antrean_pasien_lama()    
            elif choice == '3':
                self.crud.tampilkan_antrean()    
            elif choice == '4':
                self.crud.tampilkan_terpanggil() 
            elif choice == '5':
                self.crud.tampilkan_selesai()    
            elif choice == '6':
                self.crud.cari_pasien()          
            elif choice == '7':
                self.crud.edit_pasien()          
            elif choice == '8':
                self.crud.hapus_pasien()         
            elif choice == '9':
                self.panggil_pasien()            
            elif choice == '10':
                self.panggil_ulang()             
            elif choice == '11':
                self.tandai_selesai()            
            elif choice == '12':
                self.reset_antrean()             
            elif choice == '0':
                print("\nTerima kasih telah menggunakan Sistem Antrean Pengambilan Obat")
                print("Aplikasi akan ditutup...")
                break
            else:
                print("\nPilihan tidak valid! Silakan pilih menu 0-12")
                input("\nTekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    try:
        sistem_antrean = SistemAntreanObat()
        sistem_antrean.jalankan()
    except ModuleNotFoundError as e:
        print(f"Error: {e}")
        print("\nPastikan semua library terinstal dengan menjalankan:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"Error tak terduga: {e}")