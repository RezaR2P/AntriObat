import os
import platform
import pandas as pd

class UI:
    def clear_screen(self):
        """Membersihkan layar terminal"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def tampilkan_banner(self, menunggu, terpanggil):
        """Menampilkan banner aplikasi"""
        self.clear_screen()
        print("="*70)
        print("                SISTEM ANTREAN PENGAMBILAN OBAT")
        print("="*70)
        
        print(f"Jumlah antrean menunggu : {menunggu}")
        print(f"Jumlah pasien terpanggil: {terpanggil}")
        print("="*70)
    
    def tampilkan_menu(self):
        """Menampilkan menu utama aplikasi"""
        print("\nMENU:")
        print("1. Daftarkan Pasien Baru")
        print("2. Lihat Antrean Saat Ini")
        print("3. Lihat Pasien Terpanggil")
        print("4. Lihat Pasien Selesai")
        print("5. Cari Data Pasien") 
        print("6. Edit Data Pasien")
        print("7. Hapus Data Pasien")
        print("8. Panggil Pasien Berikutnya")
        print("9. Panggil Ulang Pasien Terakhir")
        print("10. Tandai Pasien Selesai")
        print("11. Reset Antrean Harian")
        print("0. Keluar")
        
        choice = input("\nPilih menu (0-11): ")
        return choice
    
    def tampilkan_pemanggilan(self, nomor, nama, is_ulang=False):
        """Menampilkan panel pemanggilan"""
        self.clear_screen()
        print("\n" + "="*70)
        if is_ulang:
            print(f"\n  PENGULANGAN PANGGILAN")
        print(f"  NOMOR ANTREAN {nomor}")
        print(f"  NAMA: {nama}")
        print(f"  SILAKAN KE LOKET PENGAMBILAN OBAT\n")
        print("="*70)
    
    def tampilkan_antrean(self, daftar_antrean):
        """Menampilkan daftar antrean"""
        self.clear_screen()
        print("=== ANTREAN SAAT INI ===\n")
        
        if not daftar_antrean:
            print("Tidak ada pasien dalam antrean")
        else:
            print("Pasien yang sedang menunggu:")
            print("-" * 70)
            print(f"{'No.':<5}{'Nomor Antrean':<15}{'Nama':<30}{'No. Rekam Medis':<20}")
            print("-" * 70)
            
            for i, pasien in enumerate(daftar_antrean, 1):
                print(f"{i:<5}{pasien['nomor_antrean']:<15}{pasien['nama']:<30}{pasien['no_rekam_medis']:<20}")
    
    def tampilkan_terpanggil(self, daftar_pasien):
        """Menampilkan daftar pasien yang telah dipanggil"""
        self.clear_screen()
        print("=== DAFTAR PASIEN TERPANGGIL ===\n")
        
        if not daftar_pasien:
            print("Tidak ada pasien yang telah dipanggil!")
            return
        
        print("-" * 80)
        print(f"{'No.':<5}{'Nama':<30}{'Waktu Panggil':<25}{'Status':<20}")
        print("-" * 80)
        
        for i, pasien in enumerate(daftar_pasien, 1):
            waktu_panggil = pasien['waktu_panggil'] if 'waktu_panggil' in pasien else '-'
            print(f"{i:<5}{pasien['nama']:<30}{waktu_panggil:<25}{pasien['status']:<20}")
    
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
                print(f"Rekam Medis  : {pasien['no_rekam_medis']}")
                print(f"Status       : {pasien['status']}")
                print(f"Waktu Daftar : {pasien['waktu_daftar']}")
                if pasien['waktu_panggil'] and pd.notna(pasien['waktu_panggil']):
                    print(f"Waktu Panggil: {pasien['waktu_panggil']}")
                print("-" * 90)