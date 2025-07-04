import uuid
import pandas as pd

class CRUDHandler:
    def __init__(self, sistem_antrean):
        self.sistem = sistem_antrean
        self.db = sistem_antrean.db
        self.antrean = sistem_antrean.antrean
        self.qr_scanner = sistem_antrean.qr_scanner
        self.qr_generator = sistem_antrean.qr_generator
        self.qr_dir = sistem_antrean.qr_dir
    
    # === CREATE ===
    
    def daftarkan_pasien(self):
        """Create - Mendaftarkan pasien baru"""
        from ui import UI
        
        UI.clear_screen()
        print("=== PENDAFTARAN PASIEN BARU ===\n")
        
        nama = input("Nama Pasien: ")
        no_rekam_medis = input("No. Rekam Medis: ")
        
        id_pasien = str(uuid.uuid4())
        nomor = self.db.get_next_nomor_antrean()
        
        self.db.tambah_pasien(id_pasien, nama, no_rekam_medis, nomor)
        self.antrean.tambah_pasien(id_pasien)
        
        qr_path = self.qr_generator.generate_qr_code(id_pasien, self.qr_dir / f"{id_pasien}.png")
        
        print("\nPasien berhasil didaftarkan!")
        print(f"Nama          : {nama}")
        print(f"No. Antrean   : {nomor}")
        print(f"QR Code tersimpan di: {qr_path}")

        input("\nTekan Enter untuk kembali ke menu...")
    
    # === READ ===
    
    def tampilkan_antrean(self):
        """Read - Menampilkan daftar pasien dalam antrean"""
        from ui import UI
        
        daftar_antrean = []
        
        for id_pasien in self.antrean.antrean_aktif:
            pasien = self.db.cari_pasien(id_pasien)
            if not pasien.empty:
                daftar_antrean.append(pasien.iloc[0])
        
        UI.tampilkan_antrean(daftar_antrean)
        input("\nTekan Enter untuk kembali ke menu...")
    
    def tampilkan_terpanggil(self):
        """Read - Menampilkan daftar pasien yang sudah dipanggil"""
        from ui import UI
        
        daftar_terpanggil = []
        
        for id_pasien in reversed(list(self.antrean.sudah_dipanggil)):
            pasien = self.db.cari_pasien(id_pasien)
            if not pasien.empty:
                daftar_terpanggil.append(pasien.iloc[0])
        
        UI.tampilkan_terpanggil(daftar_terpanggil)
        input("\nTekan Enter untuk kembali ke menu...")
    
    def tampilkan_selesai(self):
        """Read - Menampilkan daftar pasien yang sudah selesai"""
        from ui import UI
        
        UI.clear_screen()
        print("=== DAFTAR PASIEN SELESAI ===\n")
        
        df_hari_ini = self.db.get_pasien_hari_ini()
        selesai = df_hari_ini[df_hari_ini['status'] == 'selesai']
        
        if selesai.empty:
            print("Tidak ada pasien yang sudah selesai hari ini")
        else:
            print("Pasien yang sudah selesai:")
            print("-" * 70)
            print(f"{'No.':<5}{'Nomor Antrean':<15}{'Nama':<30}{'Waktu Selesai':<20}")
            print("-" * 70)
            
            for i, (_, pasien) in enumerate(selesai.iterrows(), 1):
                waktu = pasien['waktu_panggil'] if pd.notna(pasien['waktu_panggil']) else '-'
                print(f"{i:<5}{pasien['nomor_antrean']:<15}{pasien['nama']:<30}{waktu:<20}")
        
        input("\nTekan Enter untuk kembali ke menu...")
    
    def cari_pasien(self):
        from ui import UI
        
        UI.clear_screen()
        print("=== CARI DATA PASIEN ===\n")
        
        print("Cari pasien berdasarkan:")
        print("1. Scan QR Code")
        print("2. Input ID Pasien")
        choice = input("\nPilih metode (1-2): ")
        
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
        else:
            print("\nPilihan tidak valid!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        hasil = self.db.cari_pasien(id_pasien)
        if hasil.empty:
            print("\nPasien tidak ditemukan!")
        else:
            UI.tampilkan_hasil_pencarian(hasil)
    
        input("\nTekan Enter untuk kembali ke menu...")
    
    # === UPDATE ===
    
    def edit_pasien(self):
        from ui import UI
        
        UI.clear_screen()
        print("=== EDIT DATA PASIEN ===\n")
        
        print("Cari pasien berdasarkan:")
        print("1. Scan QR Code")
        print("2. Input ID Pasien")
        choice = input("\nPilih metode (1-2): ")
        
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
        else:
            print("\nPilihan tidak valid!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        hasil = self.db.cari_pasien(id_pasien)
        if hasil.empty:
            print("\nPasien tidak ditemukan!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        pasien = hasil.iloc[0]
        print("\nData pasien saat ini:")
        print("-" * 70)
        print(f"ID           : {pasien['id']}")
        print(f"Nama         : {pasien['nama']}")
        print(f"No. Antrean  : {pasien['nomor_antrean']}")
        print(f"Rekam Medis  : {pasien['no_rekam_medis']}")
        print(f"Status       : {pasien['status']}")
        print("-" * 70)
        
        print("\nMasukkan data baru (kosongkan jika tidak ingin mengubah):")
        nama_baru = input(f"Nama ({pasien['nama']}): ")
        no_rekam_medis_baru = input(f"No. Rekam Medis ({pasien['no_rekam_medis']}): ")
        
        if not nama_baru:
            nama_baru = pasien['nama']
        if not no_rekam_medis_baru:
            no_rekam_medis_baru = pasien['no_rekam_medis']
        
        print("\nData yang akan diupdate:")
        print(f"Nama: {pasien['nama']} -> {nama_baru}")
        print(f"No. Rekam Medis: {pasien['no_rekam_medis']} -> {no_rekam_medis_baru}")
        
        confirm = input("\nApakah Anda yakin ingin mengubah data? (y/n): ")
        if confirm.lower() == 'y':
            if self.db.update_data_pasien(id_pasien, nama_baru, no_rekam_medis_baru):
                print("\nData pasien berhasil diupdate!")
            else:
                print("\nGagal mengupdate data pasien!")
        else:
            print("\nPerubahan dibatalkan.")
        
        input("\nTekan Enter untuk kembali ke menu...")
    
    # === DELETE ===
    
    def hapus_pasien(self):
        from ui import UI
        
        UI.clear_screen()
        print("=== HAPUS DATA PASIEN ===\n")
        
        print("Cari pasien berdasarkan:")
        print("1. Scan QR Code")
        print("2. Input ID Pasien")
        choice = input("\nPilih metode (1-2): ")
        
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
        else:
            print("\nPilihan tidak valid!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        hasil = self.db.cari_pasien(id_pasien)
        if hasil.empty:
            print("\nPasien tidak ditemukan!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        print("\nData pasien yang akan dihapus:")
        print("-" * 70)
        for _, pasien in hasil.iterrows():
            print(f"ID           : {pasien['id']}")
            print(f"Nama         : {pasien['nama']}")
            print(f"No. Antrean  : {pasien['nomor_antrean']}")
            print(f"Rekam Medis  : {pasien['no_rekam_medis']}")
            print(f"Status       : {pasien['status']}")
        print("-" * 70)
        
        confirm = input("\nAnda yakin ingin menghapus data pasien ini? (y/n): ")
        if confirm.lower() == 'y':
            self.hapus_dari_antrean(id_pasien)

            qr_file_path = self.qr_dir / f"{id_pasien}.png"
            try:
                if qr_file_path.exists():
                    qr_file_path.unlink()
                    print(f"\nFile QR code berhasil dihapus: {qr_file_path}")
            except Exception as e:
                print(f"\nGagal menghapus file QR code: {e}")
            
            if self.db.hapus_pasien(id_pasien):
                print("\nData pasien berhasil dihapus!")
            else:
                print("\nGagal menghapus data pasien!")
        else:
            print("\nPenghapusan dibatalkan.")
        
        input("\nTekan Enter untuk kembali ke menu...")
    
    # === HELPER METHODS ===
    
    def hapus_dari_antrean(self, id_pasien):
        """Helper - Menghapus pasien dari antrean aktif atau sudah dipanggil"""
        # Cari di antrean aktif
        if id_pasien in self.antrean.antrean_aktif:
            self.antrean.antrean_aktif.remove(id_pasien)
        
        # Cari di antrean yang sudah dipanggil
        if id_pasien in self.antrean.sudah_dipanggil:
            self.antrean.sudah_dipanggil.remove(id_pasien)