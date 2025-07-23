import os
import platform
import pandas as pd
import datetime

class UI:
    def clear_screen(self):
        """Membersihkan layar terminal"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def tampilkan_banner(self, menunggu, terpanggil):
        """Menampilkan banner aplikasi"""
        self.clear_screen()
        print("="*70)
        print("                SISTEM ANTREAN PUSKESMAS")
        print("="*70)
        
        print(f"Jumlah antrean menunggu : {menunggu}")
        print(f"Jumlah pasien terpanggil: {terpanggil}")
        print("="*70)
    
    def tampilkan_menu(self):
        """Menampilkan menu utama aplikasi"""
        print("\nMENU:")
        print("1. Pendaftaran Pasien Baru (Belum Punya Kartu)")
        print("2. Pendaftaran Antrean (Sudah Punya Kartu - Scan QR)")
        print("3. Lihat Antrean Saat Ini")
        print("4. Lihat Pasien Terpanggil")
        print("5. Lihat Pasien Selesai")
        print("6. Cari Data Pasien") 
        print("7. Edit Data Pasien")
        print("8. Hapus Data Pasien")
        print("9. Panggil Pasien Berikutnya")
        print("10. Panggil Ulang Pasien Terakhir")
        print("11. Tandai Pasien Selesai")
        print("12. Reset Antrean Harian")
        print("0. Keluar")
        
        choice = input("\nPilih menu (0-12): ")
        return choice
    
    def tampilkan_pemanggilan(self, nomor, nama, waktu_panggil, poli=None, is_ulang=False):
        """Menampilkan panel pemanggilan"""
        self.clear_screen()
        print("\n" + "="*70)
        if is_ulang:
            print(f"\n  PENGULANGAN PANGGILAN")
        print(f"  NOMOR ANTREAN {nomor}")
        print(f"  NAMA: {nama}")
        if poli:
            print(f"  SILAKAN KE {poli.upper()}")
        else:
            print(f"  SILAKAN KE LOKET PENDAFTARAN")
        print(f"  WAKTU: {waktu_panggil}\n")
        print("="*70)
    
    def tampilkan_antrean(self, daftar_antrean):
        """Menampilkan daftar antrean"""
        self.clear_screen()
        print("=== ANTREAN SAAT INI ===\n")
        
        if not daftar_antrean:
            print("Tidak ada pasien dalam antrean")
        else:
            print("Pasien yang sedang menunggu:")
            print("-" * 85)
            print(f"{'No.':<5}{'Nomor Antrean':<15}{'Nama':<30}{'NIK':<20}{'Poli':<15}")
            print("-" * 85)
            
            for i, pasien in enumerate(daftar_antrean, 1):
                poli = pasien.get('poli', '-')
                nik = pasien.get('nik', '-')
                print(f"{i:<5}{pasien['nomor_antrean']:<15}{pasien['nama']:<30}{nik:<20}{poli:<15}")
    
    def tampilkan_terpanggil(self, daftar_pasien):
        """Menampilkan daftar pasien yang telah dipanggil"""
        self.clear_screen()
        print("=== DAFTAR PASIEN TERPANGGIL ===\n")
        
        if not daftar_pasien:
            print("Tidak ada pasien yang telah dipanggil!")
            return
        
        print("-" * 105)
        print(f"{'No.':<5}{'Nama':<25}{'Waktu Panggil':<25}{'Status':<20}{'Poli':<30}")
        print("-" * 105)
        
        for i, pasien in enumerate(daftar_pasien, 1):
            waktu_panggil = pasien.get('waktu_panggil', '-') if pasien.get('waktu_panggil') else '-'
            poli = pasien.get('poli', '-')
            print(f"{i:<5}{pasien['nama']:<25}{waktu_panggil:<25}{pasien['status']:<20}{poli:<30}")
    
    def tampilkan_hasil_pencarian(self, hasil):
        """Menampilkan hasil pencarian pasien"""
        if hasil.empty:
            print("\nPasien tidak ditemukan!")
        else:
            print("\nPasien ditemukan!")
            print("-" * 90)
            for _, pasien in hasil.iterrows():
                print(f"ID           : {pasien['id']}")
                print(f"Nama         : {pasien['nama']}")
                print(f"No. Antrean  : {pasien['nomor_antrean']}")
                print(f"NIK          : {pasien.get('nik', '-')}")
                print(f"Poli         : {pasien.get('poli', '-')}")
                print(f"Status       : {pasien['status']}")
                print(f"Waktu Daftar : {pasien['waktu_daftar']}")
                if pasien['waktu_panggil'] and pd.notna(pasien['waktu_panggil']):
                    print(f"Waktu Panggil: {pasien['waktu_panggil']}")
                print("-" * 90)
    
    def form_pendaftaran_pasien_baru(self):
        """Form untuk pendaftaran pasien baru di puskesmas"""
        self.clear_screen()
        print("=== PENDAFTARAN PASIEN BARU PUSKESMAS ===\n")
        print("Silakan lengkapi data berikut:")
        print("-" * 50)
        
        # NIK (wajib dan harus 16 digit)
        while True:
            nik = input("NIK (16 digit): ").strip()
            if len(nik) == 16 and nik.isdigit():
                break
            else:
                print("NIK harus 16 digit angka! Silakan coba lagi.")
        
        # Nama lengkap (wajib)
        nama = input("Nama Lengkap: ").strip()
        while not nama:
            print("Nama tidak boleh kosong!")
            nama = input("Nama Lengkap: ").strip()
        
        # Jenis kelamin
        while True:
            print("\nJenis Kelamin:")
            print("1. Laki-laki")
            print("2. Perempuan")
            pilihan_gender = input("Pilih (1/2): ").strip()
            if pilihan_gender == '1':
                jenis_kelamin = 'Laki-laki'
                break
            elif pilihan_gender == '2':
                jenis_kelamin = 'Perempuan'
                break
            else:
                print("Pilihan tidak valid!")
        
        # Tempat lahir
        tempat_lahir = input("Tempat Lahir: ").strip()
        while not tempat_lahir:
            print("Tempat lahir tidak boleh kosong!")
            tempat_lahir = input("Tempat Lahir: ").strip()
        
        # Tanggal lahir
        while True:
            tanggal_lahir = input("Tanggal Lahir (YYYY-MM-DD): ").strip()
            if tanggal_lahir:
                try:
                    datetime.datetime.strptime(tanggal_lahir, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Format tanggal salah! Gunakan format YYYY-MM-DD")
            else:
                print("Tanggal lahir tidak boleh kosong!")
        
        # Alamat
        alamat = input("Alamat Lengkap: ").strip()
        while not alamat:
            print("Alamat tidak boleh kosong!")
            alamat = input("Alamat Lengkap: ").strip()
        
        # Riwayat penyakit (opsional)
        riwayat_penyakit = input("Riwayat Penyakit (kosongkan jika tidak ada): ").strip()
        if not riwayat_penyakit:
            riwayat_penyakit = "Tidak ada"
        
        return {
            'nik': nik,
            'nama': nama,
            'jenis_kelamin': jenis_kelamin,
            'tempat_lahir': tempat_lahir,
            'tanggal_lahir': tanggal_lahir,
            'alamat': alamat,
            'riwayat_penyakit': riwayat_penyakit
        }
    
    def pilih_poli(self):
        """Menu untuk memilih poli puskesmas"""
        print("\n=== PILIH POLI ===")
        print("1. Poli Umum")
        print("2. Poli Gigi")
        print("3. Poli Lansia")
        
        while True:
            pilihan = input("\nPilih poli (1-3): ").strip()
            poli_map = {
                '1': 'Poli Umum',
                '2': 'Poli Gigi', 
                '3': 'Poli Lansia'
            }
            
            if pilihan in poli_map:
                return poli_map[pilihan]
            else:
                print("Pilihan tidak valid! Silakan pilih 1-3.")
    
    def tampilkan_qr_berhasil(self, nama, no_antrean, poli, qr_path):
        """Menampilkan informasi setelah QR berhasil dibuat"""
        self.clear_screen()
        print("="*70)
        print("           PENDAFTARAN BERHASIL!")
        print("="*70)
        print(f"Nama          : {nama}")
        print(f"No. Antrean   : {no_antrean}")
        print(f"Poli          : {poli}")
        print(f"QR Code       : {qr_path}")
        print("="*70)
        print("\nSIMPAN QR CODE INI UNTUK KUNJUNGAN SELANJUTNYA!")
        print("Anda dapat menggunakan QR Code ini setiap kali datang ke puskesmas.")
        print("QR Code Anda telah tersimpan dan siap digunakan.")
    
    def tampilkan_antrean_lama_berhasil(self, nama, no_antrean, poli):
        """Menampilkan informasi setelah pasien lama berhasil daftar antrean"""
        self.clear_screen()
        print("="*70)
        print("           PENDAFTARAN ANTREAN BERHASIL!")
        print("="*70)
        print(f"Nama          : {nama}")
        print(f"No. Antrean   : {no_antrean}")  
        print(f"Poli          : {poli}")
        print("="*70)
        print("\nSilakan menunggu dipanggil!")
    
    def tampilkan_pasien_sudah_daftar(self, nama, no_antrean, poli):
        """Menampilkan informasi jika pasien sudah daftar hari ini"""
        self.clear_screen()
        print("="*70)
        print("           INFORMASI ANTREAN")
        print("="*70)
        print(f"Nama          : {nama}")
        print(f"No. Antrean   : {no_antrean}")
        print(f"Poli          : {poli}")
        print("="*70)
        print("\nAnda sudah terdaftar dalam antrean hari ini!")
        print("Silakan menunggu dipanggil.")
    
    def tampilkan_data_pasien_lengkap(self, pasien_master, pasien_antrean=None):
        """Menampilkan data lengkap pasien dari master dan antrean"""
        self.clear_screen()
        print("=== DATA LENGKAP PASIEN ===\n")
        
        print("DATA MASTER PASIEN:")
        print("-" * 60)
        print(f"ID Pasien     : {pasien_master.get('id_pasien', '-')}")
        print(f"NIK           : {pasien_master.get('nik', '-')}")
        print(f"Nama          : {pasien_master.get('nama', '-')}")
        print(f"Jenis Kelamin : {pasien_master.get('jenis_kelamin', '-')}")
        print(f"Tempat Lahir  : {pasien_master.get('tempat_lahir', '-')}")
        print(f"Tanggal Lahir : {pasien_master.get('tanggal_lahir', '-')}")
        print(f"Alamat        : {pasien_master.get('alamat', '-')}")
        print(f"Riwayat Penyakit : {pasien_master.get('riwayat_penyakit', '-')}")
        print(f"Tanggal Daftar   : {pasien_master.get('tanggal_daftar_pertama', '-')}")
        print(f"QR Code Path     : {pasien_master.get('qr_code_path', '-')}")
        
        if pasien_antrean is not None:
            print("\nDATA ANTREAN HARI INI:")
            print("-" * 60)
            print(f"Nomor Antrean : {pasien_antrean.get('nomor_antrean', '-')}")
            print(f"Poli          : {pasien_antrean.get('poli', '-')}")
            print(f"Status        : {pasien_antrean.get('status', '-')}")
            print(f"Waktu Daftar  : {pasien_antrean.get('waktu_daftar', '-')}")
            print(f"Waktu Panggil : {pasien_antrean.get('waktu_panggil', '-')}")
        
        print("-" * 60)
    
    def form_edit_pasien(self, pasien_data):
        """Form untuk edit data pasien"""
        print("\n=== EDIT DATA PASIEN ===")
        print("Kosongkan field jika tidak ingin mengubah\n")
        
        # NIK
        nik_lama = pasien_data.get('nik', '')
        while True:
            nik_baru = input(f"NIK ({nik_lama}): ").strip()
            if not nik_baru:  # Tidak diubah
                nik_baru = nik_lama
                break
            elif len(nik_baru) == 16 and nik_baru.isdigit():
                break
            else:
                print("NIK harus 16 digit angka!")
        
        # Nama
        nama_lama = pasien_data.get('nama', '')
        nama_baru = input(f"Nama ({nama_lama}): ").strip()
        if not nama_baru:
            nama_baru = nama_lama
        
        # Jenis Kelamin
        jk_lama = pasien_data.get('jenis_kelamin', '')
        print(f"\nJenis Kelamin sekarang: {jk_lama}")
        print("1. Laki-laki")
        print("2. Perempuan")
        print("3. Tidak diubah")
        pilihan_jk = input("Pilih (1/2/3): ").strip()
        
        if pilihan_jk == '1':
            jk_baru = 'Laki-laki'
        elif pilihan_jk == '2':
            jk_baru = 'Perempuan'
        else:
            jk_baru = jk_lama
        
        # Tempat Lahir
        tempat_lama = pasien_data.get('tempat_lahir', '')
        tempat_baru = input(f"Tempat Lahir ({tempat_lama}): ").strip()
        if not tempat_baru:
            tempat_baru = tempat_lama
        
        # Tanggal Lahir
        tgl_lama = pasien_data.get('tanggal_lahir', '')
        while True:
            tgl_baru = input(f"Tanggal Lahir ({tgl_lama}): ").strip()
            if not tgl_baru:  # Tidak diubah
                tgl_baru = tgl_lama
                break
            else:
                try:
                    datetime.datetime.strptime(tgl_baru, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Format tanggal salah! Gunakan YYYY-MM-DD")
        
        # Alamat
        alamat_lama = pasien_data.get('alamat', '')
        alamat_baru = input(f"Alamat ({alamat_lama}): ").strip()
        if not alamat_baru:
            alamat_baru = alamat_lama
        
        # Riwayat Penyakit
        print(f"Kosongkan field jika tidak ingin mengubah | ganti dengan '-' jika tidak ada riwayat")
        riwayat_lama = pasien_data.get('riwayat_penyakit', '')
        riwayat_baru = input(f"Riwayat Penyakit ({riwayat_lama}): ").strip()
        if not riwayat_baru:
            riwayat_baru = riwayat_lama
        
        return {
            'nik': nik_baru,
            'nama': nama_baru,
            'jenis_kelamin': jk_baru,
            'tempat_lahir': tempat_baru,
            'tanggal_lahir': tgl_baru,
            'alamat': alamat_baru,
            'riwayat_penyakit': riwayat_baru
        }
    
    def tampilkan_perbandingan_data(self, data_lama, data_baru):
        """Tampilkan perbandingan data lama vs baru"""
        print("\n=== PERBANDINGAN DATA ===")
        print("-" * 80)
        print(f"{'Field':<20}{'Data Lama':<30}{'Data Baru':<30}")
        print("-" * 80)
        
        fields = ['nik', 'nama', 'jenis_kelamin', 'tempat_lahir', 'tanggal_lahir', 'alamat', 'riwayat_penyakit']
        
        for field in fields:
            lama = str(data_lama.get(field, '-'))
            baru = str(data_baru.get(field, '-'))
            
            # Tandai jika ada perubahan
            if lama != baru:
                print(f"{field.replace('_', ' ').title():<20}{lama:<30}{baru:<30} *")
            else:
                print(f"{field.replace('_', ' ').title():<20}{lama:<30}{baru:<30}")
        
        print("-" * 80)
        print("* = Ada perubahan")