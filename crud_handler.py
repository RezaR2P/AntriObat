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
        
        # Tambahkan UI instance
        self.ui = sistem_antrean.ui
    
    # === CREATE ===
    
    def daftarkan_pasien_baru(self):
        """Create - Mendaftarkan pasien baru ke database master (tanpa antrean)"""
        try:
            # Ambil data dari form UI
            data_pasien = self.ui.form_pendaftaran_pasien_baru()
            
            # Cek apakah NIK sudah ada
            existing = self.db.cari_pasien_master(nik=data_pasien['nik'])
            if not existing.empty:
                print(f"\nNIK {data_pasien['nik']} sudah terdaftar!")
                print("Gunakan menu 'Pendaftaran Antrean (Sudah Punya Kartu)' untuk mendaftar antrean.")
                input("\nTekan Enter untuk kembali ke menu...")
                return
            
            # Generate ID unik untuk pasien
            id_pasien = str(uuid.uuid4())
            
            # Generate QR Code
            qr_filename = f"{id_pasien}.png"
            qr_path = self.qr_generator.generate_qr_code(id_pasien, self.qr_dir / qr_filename)
            
            # Simpan ke database master saja (tidak langsung ke antrean)
            self.db.tambah_pasien_baru_master(
                id_pasien=id_pasien,
                nik=data_pasien['nik'],
                nama=data_pasien['nama'],
                jenis_kelamin=data_pasien['jenis_kelamin'],
                tempat_lahir=data_pasien['tempat_lahir'],
                tanggal_lahir=data_pasien['tanggal_lahir'],
                alamat=data_pasien['alamat'],
                riwayat_penyakit=data_pasien['riwayat_penyakit'],
                qr_code_path=str(qr_path)
            )
            
            # Tampilkan hasil pendaftaran master (tanpa nomor antrean)
            self.ui.tampilkan_pendaftaran_master_berhasil(data_pasien['nama'], str(qr_path))
            
        except Exception as e:
            print(f"\nError saat mendaftarkan pasien: {e}")
        
        input("\nTekan Enter untuk kembali ke menu...")
    
    def daftarkan_antrean_pasien_lama(self):
        """Pendaftaran antrean untuk pasien lama dengan scan QR atau NIK"""
        self.ui.clear_screen()
        print("=== PENDAFTARAN ANTREAN ===\n")
        
        # Pilihan metode pencarian
        print("Cari data pasien dengan:")
        print("1. Scan QR Code")
        print("2. Input NIK")
        choice = input("\nPilih metode (1-2): ")
        
        try:
            id_pasien = None
            pasien_master = None
            
            if choice == '1':
                # Scan QR Code
                print("\nSilakan scan QR Code pada kartu Anda...")
                id_pasien = self.qr_scanner.scan_from_camera()
                if not id_pasien:
                    print("\nQR Code tidak terbaca atau scan dibatalkan!")
                    input("\nTekan Enter untuk kembali ke menu...")
                    return
                    
                # Cari data pasien di master berdasarkan ID
                pasien_master = self.db.cari_pasien_master(id_pasien=id_pasien)
                
            elif choice == '2':
                # Input NIK dengan validasi
                nik = self.ui.input_nik_valid()
                    
                # Cari data pasien di master berdasarkan NIK
                pasien_master = self.db.cari_pasien_master(nik=nik)
                if not pasien_master.empty:
                    id_pasien = pasien_master.iloc[0]['id_pasien']
                    
            else:
                print("\nPilihan tidak valid!")
                input("\nTekan Enter untuk kembali ke menu...")
                return
            
            # Validasi data pasien
            if pasien_master.empty:
                if choice == '1':
                    print("\nData pasien tidak ditemukan!")
                    print("Pastikan QR Code Anda valid atau daftar sebagai pasien baru.")
                else:
                    print(f"\nNIK tidak ditemukan dalam database!")
                    print("Pastikan NIK benar atau daftar sebagai pasien baru.")
                input("\nTekan Enter untuk kembali ke menu...")
                return

            data_pasien = pasien_master.iloc[0]
            
            # Tampilkan data pasien yang ditemukan
            print(f"\n✓ Data pasien ditemukan:")
            print(f"Nama: {data_pasien['nama']}")
            print(f"NIK: {data_pasien['nik']}")
            
            # Cek apakah sudah daftar antrean hari ini
            if self.db.cek_pasien_sudah_antrean_hari_ini(id_pasien):
                # Ambil data antrean hari ini
                antrean_hari_ini = self.db.cari_pasien(id_pasien)
                if not antrean_hari_ini.empty:
                    data_antrean = antrean_hari_ini.iloc[0]
                    self.ui.tampilkan_pasien_sudah_daftar(
                        data_pasien['nama'], 
                        data_antrean['nomor_antrean'], 
                        data_antrean['poli']
                    )
                input("\nTekan Enter untuk kembali ke menu...")
                return
            
            # Pilih poli
            poli = self.ui.pilih_poli()
            nomor_antrean = self.db.get_next_nomor_antrean()
            
            # Tambah ke antrean harian
            success = self.db.tambah_antrean_harian(id_pasien, poli, nomor_antrean)
            if success:
                self.antrean.tambah_pasien(id_pasien)
                self.ui.tampilkan_antrean_lama_berhasil(data_pasien['nama'], nomor_antrean, poli)
            else:
                print("\nGagal mendaftarkan antrean!")
                
        except Exception as e:
            print(f"\nError saat mendaftarkan antrean: {e}")
        
        input("\nTekan Enter untuk kembali ke menu...")
    
    # === READ ===
    
    def tampilkan_antrean(self):
        """Read - Menampilkan daftar pasien dalam antrean"""
        daftar_antrean = []
        
        for id_pasien in self.antrean.antrean_aktif:
            pasien = self.db.cari_pasien(id_pasien)
            if not pasien.empty:
                pasien_data = pasien.iloc[0].to_dict()
                daftar_antrean.append(pasien_data)
        
        self.ui.tampilkan_antrean(daftar_antrean)
        input("\nTekan Enter untuk kembali ke menu...")
    
    def tampilkan_terpanggil(self):
        """Read - Menampilkan daftar pasien yang sudah dipanggil"""
        daftar_terpanggil = []
        
        for id_pasien in reversed(list(self.antrean.sudah_dipanggil)):
            pasien = self.db.cari_pasien(id_pasien)
            if not pasien.empty:
                pasien_data = pasien.iloc[0].to_dict()
                daftar_terpanggil.append(pasien_data)
        
        self.ui.tampilkan_terpanggil(daftar_terpanggil)
        input("\nTekan Enter untuk kembali ke menu...")
    
    def tampilkan_selesai(self):
        """Read - Menampilkan daftar pasien yang sudah selesai"""
        self.ui.clear_screen()
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
        """Cari data pasien di master dan antrean"""
        while True:
            self.ui.clear_screen()
            print("=== CARI DATA PASIEN ===\n")
            
            print("Cari pasien berdasarkan:")
            print("1. Scan QR Code")
            print("2. Input NIK")
            print("0. Kembali ke Menu Utama")
            choice = input("\nPilih metode (0-2): ")
            
            if choice == '0':
                return
            
            id_pasien = None
            if choice == '1':
                print("\nSilakan scan QR code pasien...")
                id_pasien = self.qr_scanner.scan_from_camera()
                if not id_pasien:
                    print("\nTidak ada QR code yang terdeteksi atau scan dibatalkan.")
                    input("\nTekan Enter untuk melanjutkan...")
                    continue
                    
            elif choice == '2':
                nik = self.ui.input_nik_valid()
                
                # Cari berdasarkan NIK di master
                print(f"Mencari pasien dengan NIK: {nik}")
                hasil_master = self.db.cari_pasien_master(nik=nik)
                if hasil_master.empty:
                    print("\nPasien dengan NIK tersebut tidak ditemukan!")
                    print("Pastikan NIK sudah benar dan pasien sudah terdaftar.")
                    input("\nTekan Enter untuk melanjutkan...")
                    continue
                id_pasien = hasil_master.iloc[0]['id_pasien']
                print(f"Pasien ditemukan! ID: {id_pasien}")
                
            else:
                print("\nPilihan tidak valid!")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            # Cari di database master
            hasil_master = self.db.cari_pasien_master(id_pasien=id_pasien)
            if hasil_master.empty:
                print("\nData pasien tidak ditemukan!")
                input("\nTekan Enter untuk melanjutkan...")
                continue
        
            pasien_master = hasil_master.iloc[0].to_dict()
            
            # Cari di antrean hari ini
            hasil_antrean = self.db.cari_pasien(id_pasien)
            pasien_antrean = hasil_antrean.iloc[0].to_dict() if not hasil_antrean.empty else None
            
            # Tampilkan data lengkap
            self.ui.tampilkan_data_pasien_lengkap(pasien_master, pasien_antrean)
            
            input("\nTekan Enter untuk melanjutkan...")
    
    # === UPDATE ===
    
    def edit_pasien(self):
        """Edit data master pasien"""
        while True:
            self.ui.clear_screen()
            print("=== EDIT DATA PASIEN ===\n")
            
            print("Cari pasien berdasarkan:")
            print("1. Scan QR Code")
            print("2. Input NIK")
            print("0. Kembali ke Menu Utama")
            choice = input("\nPilih metode (0-2): ")
            
            if choice == '0':
                return
            
            id_pasien = None
            if choice == '1':
                print("\nSilakan scan QR code pasien...")
                id_pasien = self.qr_scanner.scan_from_camera()
                if not id_pasien:
                    print("\nTidak ada QR code yang terdeteksi atau scan dibatalkan.")
                    input("\nTekan Enter untuk melanjutkan...")
                    continue
                    
            elif choice == '2':
                nik = self.ui.input_nik_valid()
                
                # Cari berdasarkan NIK
                print(f"Mencari pasien dengan NIK: {nik}")
                hasil_master = self.db.cari_pasien_master(nik=nik)
                if hasil_master.empty:
                    print("\nPasien dengan NIK tersebut tidak ditemukan!")
                    print("Pastikan NIK sudah benar dan pasien sudah terdaftar.")
                    input("\nTekan Enter untuk melanjutkan...")
                    continue
                id_pasien = hasil_master.iloc[0]['id_pasien']
                print(f"Pasien ditemukan! ID: {id_pasien}")
                
            else:
                print("\nPilihan tidak valid!")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            # Cari data master pasien
            hasil_master = self.db.cari_pasien_master(id_pasien=id_pasien)
            if hasil_master.empty:
                print("\nData master pasien tidak ditemukan!")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            pasien_master = hasil_master.iloc[0].to_dict()
            
            # Cek apakah ada di antrean hari ini
            hasil_antrean = self.db.cari_pasien(id_pasien)
            pasien_antrean = hasil_antrean.iloc[0].to_dict() if not hasil_antrean.empty else None
            
            # Tampilkan data lengkap
            self.ui.tampilkan_data_pasien_lengkap(pasien_master, pasien_antrean)
            
            # Konfirmasi edit
            lanjut = input("\nApakah Anda ingin mengedit data ini? (y/n): ")
            if lanjut.lower() != 'y':
                print("Edit dibatalkan.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            # Form edit
            data_baru = self.ui.form_edit_pasien(pasien_master)
            
            # Tampilkan perbandingan
            self.ui.tampilkan_perbandingan_data(pasien_master, data_baru)
            
            # Konfirmasi perubahan
            konfirmasi = input("\nApakah Anda yakin ingin menyimpan perubahan? (y/n): ")
            if konfirmasi.lower() == 'y':
                # Cek duplikasi NIK jika NIK diubah
                if data_baru['nik'] != pasien_master['nik']:
                    existing_nik = self.db.cari_pasien_master(nik=data_baru['nik'])
                    if not existing_nik.empty:
                        print(f"\nError: NIK {data_baru['nik']} sudah digunakan oleh pasien lain!")
                        input("\nTekan Enter untuk melanjutkan...")
                        continue
                
                # Update data master
                success = self.db.update_data_master_pasien(id_pasien, **data_baru)
                
                if success:
                    print("\n✅ Data pasien berhasil diupdate!")
                    print("Data di antrean harian (jika ada) juga sudah diupdate.")
                    input("\nTekan Enter untuk melanjutkan...")
                    break
                else:
                    print("\n❌ Gagal mengupdate data pasien!")
                    input("\nTekan Enter untuk melanjutkan...")
                    continue
            else:
                print("\nPerubahan dibatalkan.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
    
    # === DELETE ===
    
    def hapus_pasien(self):
        while True:
            self.ui.clear_screen()
            print("=== HAPUS DATA PASIEN ===\n")
            
            print("Cari pasien berdasarkan:")
            print("1. Scan QR Code")
            print("2. Input NIK")
            print("0. Kembali ke Menu Utama")
            choice = input("\nPilih metode (0-2): ")
            
            if choice == '0':
                return
            
            id_pasien = None
            if choice == '1':
                print("\nSilakan scan QR code pasien...")
                id_pasien = self.qr_scanner.scan_from_camera()
                if not id_pasien:
                    print("\nTidak ada QR code yang terdeteksi atau scan dibatalkan.")
                    input("\nTekan Enter untuk melanjutkan...")
                    continue
                    
            elif choice == '2':
                nik = self.ui.input_nik_valid()
                
                # Cari berdasarkan NIK
                hasil_master = self.db.cari_pasien_master(nik=nik)
                if hasil_master.empty:
                    print("\nPasien dengan NIK tersebut tidak ditemukan!")
                    input("\nTekan Enter untuk melanjutkan...")
                    continue
                id_pasien = hasil_master.iloc[0]['id_pasien']
                
            else:
                print("\nPilihan tidak valid!")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            hasil = self.db.cari_pasien(id_pasien)
            if hasil.empty:
                print("\nPasien tidak ditemukan!")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            
            print("\nData pasien yang akan dihapus:")
            print("-" * 70)
            for _, pasien in hasil.iterrows():
                print(f"ID           : {pasien['id']}")
                print(f"Nama         : {pasien['nama']}")
                print(f"No. Antrean  : {pasien['nomor_antrean']}")
                print(f"NIK          : {pasien.get('nik', '-')}")
                print(f"Poli         : {pasien.get('poli', '-')}")
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
                    input("\nTekan Enter untuk melanjutkan...")
                    break
                else:
                    print("\nGagal menghapus data pasien!")
                    input("\nTekan Enter untuk melanjutkan...")
                    continue
            else:
                print("\nPenghapusan dibatalkan.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
    
    # === HELPER METHODS ===
    
    def hapus_dari_antrean(self, id_pasien):
        """Helper - Menghapus pasien dari antrean aktif atau sudah dipanggil"""
        # Cari di antrean aktif
        self.antrean.hapus_dari_aktif(id_pasien)
        
        # Cari di antrean yang sudah dipanggil
        self.antrean.hapus_dari_dipanggil(id_pasien)
    
    def cari_dan_cetak_ulang_qr(self):
        """Fitur pencarian QR code dengan NIK dan cetak ulang"""
        while True:
            self.ui.clear_screen()
            print("="*60)
            print("           PENCARIAN & CETAK ULANG QR CODE")
            print("="*60)
            print("1. Cari QR dengan NIK")
            print("0. Kembali ke Menu Utama")
            print("-"*60)
            
            pilihan = input("Pilih menu (0-1): ").strip()
            
            if pilihan == "0":
                break
            elif pilihan == "1":
                # Input NIK
                nik = self.ui.input_nik_valid()
                if nik is None:
                    continue
                
                # Cari pasien berdasarkan NIK
                pasien_data = self.db.cari_pasien_master(nik=nik)
                
                if pasien_data.empty:
                    print(f"\nPasien dengan NIK {nik} tidak ditemukan!")
                    input("\nTekan Enter untuk melanjutkan...")
                    continue
                
                # Tampilkan data pasien yang ditemukan
                pasien = pasien_data.iloc[0]
                print("\n✅ Data pasien ditemukan:")
                print("-" * 50)
                print(f"ID Pasien    : {pasien['id_pasien']}")
                print(f"Nama         : {pasien['nama']}")
                print(f"NIK          : {pasien['nik']}")
                print(f"Jenis Kelamin: {pasien.get('jenis_kelamin', '-')}")
                print(f"Tempat Lahir : {pasien.get('tempat_lahir', '-')}")
                print(f"Tanggal Lahir: {pasien.get('tanggal_lahir', '-')}")
                print(f"Alamat       : {pasien.get('alamat', '-')}")
                print("-" * 50)
                
                # Konfirmasi cetak ulang QR
                confirm = input("\nCetak ulang QR code untuk pasien ini? (y/n): ").strip().lower()
                if confirm == 'y':
                    id_pasien = pasien['id_pasien']
                    
                    try:
                        # Generate ulang QR code
                        qr_filename = f"{id_pasien}.png"
                        qr_path = self.qr_generator.generate_qr_code(id_pasien, str(self.qr_dir / qr_filename))
                        
                        print(f"\n✅ QR Code berhasil digenerate ulang!")
                        print(f"📁 Lokasi file: {qr_path}")
                        
                        # Tampilkan QR code jika memungkinkan
                        try:
                            self.qr_generator.show_qr_code(qr_path)
                            print("\n🖼️  QR Code ditampilkan di jendela terpisah.")
                            print("📋 Silakan screenshot atau print QR code tersebut.")
                        except Exception as e:
                            print(f"⚠️  Tidak dapat menampilkan QR code: {e}")
                            print("📁 Silakan buka file QR code secara manual untuk dicetak.")
                        
                        input("\nTekan Enter untuk melanjutkan...")
                    except Exception as e:
                        print(f"\n❌ Error saat generate QR code: {e}")
                        input("\nTekan Enter untuk melanjutkan...")
                else:
                    print("\n❌ Cetak ulang QR dibatalkan.")
                    input("\nTekan Enter untuk melanjutkan...")
            else:
                print(f"\n❌ Pilihan '{pilihan}' tidak valid! Pilih 0 atau 1.")
                input("\nTekan Enter untuk melanjutkan...")