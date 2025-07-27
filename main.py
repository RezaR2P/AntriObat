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
        self.last_date_file = self.base_dir / "last_date.txt"
        self.base_dir.mkdir(exist_ok=True)
        self.qr_dir.mkdir(parents=True, exist_ok=True)
        self.db = Database(self.excel_path, self.master_pasien_path)
        self.antrean = AntreanManager()
        self.qr_generator = QRGenerator()
        self.qr_scanner = QRScanner()
        self.audio = AudioManager()
        self.ui = UI()  
        self.crud = CRUDHandler(self)
        self.check_and_auto_reset_daily()
        self.initialize_daily_queue()
    
    def _handle_patient_not_found(self, id_pasien):
        print(f"\nError: Data pasien {id_pasien} tidak ditemukan!")
        input("\nTekan Enter untuk kembali ke menu...")
        return None
    
    def panggil_pasien(self):
        id_pasien = self.antrean.panggil_berikutnya()
        
        if id_pasien is None:
            print("\nTidak ada pasien dalam antrean!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        waktu_panggil = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.update_status_pasien(id_pasien, 'terpanggil', waktu_panggil)

        hasil_pasien = self.db.cari_pasien(id_pasien)
        if hasil_pasien.empty:
            return self._handle_patient_not_found(id_pasien)
            
        pasien = hasil_pasien.iloc[0]
        nama = pasien['nama']
        poli = pasien.get('poli', 'Poli')
        
        self.ui.tampilkan_pemanggilan(pasien['nomor_antrean'], nama, waktu_panggil, poli)
        self.audio.speak(f"Perhatian, nomor antrean {pasien['nomor_antrean']}, atas nama {nama}, silakan ke {poli}")
        
        input("\nTekan Enter untuk kembali ke menu...")
    
    def panggil_ulang(self):
        self.ui.clear_screen()
        print("=== PANGGIL ULANG PASIEN ===\n")

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

        pilihan = input("\nPilih nomor pasien yang akan dipanggil ulang (1-{}): ".format(len(daftar_terpanggil)))
        
        try:
            idx = int(pilihan) - 1
            if 0 <= idx < len(daftar_terpanggil):
                id_pasien = daftar_terpanggil[idx]

                hasil_pasien = self.db.cari_pasien(id_pasien)
                if hasil_pasien.empty:
                    return self._handle_patient_not_found(id_pasien)
                    
                pasien = hasil_pasien.iloc[0]
                nama = pasien['nama']
                nomor = pasien['nomor_antrean']
                poli = pasien.get('poli', 'Poli')
                waktu_panggil = pasien.get('waktu_panggil', 'Tidak tersedia')

                self.ui.tampilkan_pemanggilan(nomor, nama, waktu_panggil, poli, is_ulang=True)
                self.audio.speak(f"Pengulangan panggilan. Nomor antrean {nomor}, atas nama {nama}, silakan ke {poli}")
            else:
                print("\nNomor tidak valid!")
        except ValueError:
            print("\nInput tidak valid!")
    
        input("\nTekan Enter untuk kembali ke menu...")
    
    def proses_pemeriksaan_dokter(self):
        self.ui.clear_screen()
        print("=== PROSES PEMERIKSAAN DOKTER ===\n")

        if not self.antrean.sudah_dipanggil:
            print("\nTidak ada pasien yang telah dipanggil!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        print("Daftar pasien yang telah dipanggil:")
        print("-" * 70)
        print(f"{'No.':<5}{'Waktu Panggil':<25}{'Nama':<30}{'Status':<10}")
        print("-" * 70)
        
        daftar_terpanggil = []
        for i, id_p in enumerate(self.antrean.sudah_dipanggil, 1):
            pasien = self.db.cari_pasien(id_p)
            if not pasien.empty:
                p = pasien.iloc[0]
                waktu_panggil = p.get('waktu_panggil', '-')
                status = p.get('status', 'terpanggil')
                print(f"{i:<5}{waktu_panggil:<25}{p['nama']:<30}{status:<10}")
                daftar_terpanggil.append(p['id'])
        
        try:
            pilihan = input(f"\nPilih nomor pasien yang akan diperiksa (1-{len(daftar_terpanggil)}): ")
            idx = int(pilihan) - 1
            
            if 0 <= idx < len(daftar_terpanggil):
                id_pasien = daftar_terpanggil[idx]
                self._input_hasil_pemeriksaan(id_pasien)
            else:
                print("\nNomor tidak valid!")
        except ValueError:
            print("\nInput tidak valid!")
        
        input("\nTekan Enter untuk kembali ke menu...")
    
    def _input_hasil_pemeriksaan(self, id_pasien):
        hasil_pasien = self.db.cari_pasien(id_pasien)
        if hasil_pasien.empty:
            return self._handle_patient_not_found(id_pasien)
            
        pasien = hasil_pasien.iloc[0]
        
        print(f"\n=== PEMERIKSAAN PASIEN: {pasien['nama']} ===\n")
        keluhan = input("Keluhan utama: ").strip()
        print("\nVital Signs:")
        tekanan_darah = input("Tekanan darah (mmHg): ").strip()
        nadi = input("Nadi (x/menit): ").strip()
        suhu = input("Suhu (°C): ").strip()
        
        print("\nDiagnosis dan Tindakan:")
        diagnosis = input("Diagnosis: ").strip()
        tindakan = input("Tindakan: ").strip()
        resep = input("Resep obat: ").strip()
        catatan = input("Catatan dokter: ").strip()

        waktu_periksa = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.db.update_status_pasien(id_pasien, 'diperiksa', waktu_periksa)

        data_pemeriksaan = {
            'id_pasien': id_pasien,
            'keluhan': keluhan,
            'tekanan_darah': tekanan_darah,
            'nadi': nadi,
            'suhu': suhu,
            'diagnosis': diagnosis,
            'tindakan': tindakan,
            'resep': resep,
            'catatan': catatan,
            'waktu_periksa': waktu_periksa
        }
        
        id_pemeriksaan = self.db.simpan_data_pemeriksaan(data_pemeriksaan)
        
        print(f"\n✓ Pemeriksaan untuk {pasien['nama']} berhasil disimpan")
        print(f"✓ Data pemeriksaan tersimpan dengan ID: {id_pemeriksaan}")
        print(f"Status pasien diubah menjadi: DIPERIKSA")
        
        if resep.strip():
            print(f"\n📋 RESEP OBAT:")
            print(f"{resep}")
            print("\n➡️  Pasien dapat langsung ke bagian farmasi untuk mengambil obat")
    
    def proses_farmasi(self):
        self.ui.clear_screen()
        print("=== PROSES FARMASI ===\n")

        df_hari_ini = self.db.get_pasien_hari_ini()
        pasien_diperiksa = df_hari_ini[df_hari_ini['status'] == 'diperiksa']
        
        if pasien_diperiksa.empty:
            print("\nTidak ada pasien yang sudah diperiksa dokter!")
            input("\nTekan Enter untuk kembali ke menu...")
            return
        
        print("Daftar pasien yang sudah diperiksa dokter:")
        print("-" * 80)
        print(f"{'No.':<5}{'Nama':<25}{'NIK':<20}{'Poli':<15}{'Waktu Periksa':<15}")
        print("-" * 80)
        
        daftar_pasien = []
        for i, (_, pasien) in enumerate(pasien_diperiksa.iterrows(), 1):
            waktu = pasien.get('waktu_panggil', '-')[:16] if pasien.get('waktu_panggil') else '-'
            poli = pasien.get('poli', '-')
            nik = pasien.get('nik', '-')
            print(f"{i:<5}{pasien['nama']:<25}{nik:<20}{poli:<15}{waktu:<15}")
            daftar_pasien.append(pasien['id'])

        try:
            pilihan = input(f"\nPilih nomor pasien untuk proses farmasi (1-{len(daftar_pasien)}): ")
            idx = int(pilihan) - 1
            
            if 0 <= idx < len(daftar_pasien):
                id_pasien = daftar_pasien[idx]
                self._proses_pemberian_obat(id_pasien)
            else:
                print("\nNomor tidak valid!")
        except ValueError:
            print("\nInput tidak valid!")
        
        input("\nTekan Enter untuk kembali ke menu...")
    
    def _proses_pemberian_obat(self, id_pasien):
        hasil_pasien = self.db.cari_pasien(id_pasien)
        if hasil_pasien.empty:
            return self._handle_patient_not_found(id_pasien)
            
        pasien = hasil_pasien.iloc[0]
        
        print(f"\n=== PEMBERIAN OBAT: {pasien['nama']} ===\n")

        data_pemeriksaan = self.db.get_data_pemeriksaan_by_pasien(id_pasien)
        if not data_pemeriksaan.empty:
            pemeriksaan_terakhir = data_pemeriksaan.iloc[-1]
            
            print("📋 DATA PEMERIKSAAN DOKTER:")
            print("-" * 50)
            print(f"Tanggal Pemeriksaan: {pemeriksaan_terakhir.get('tanggal_pemeriksaan', '-')}")
            print(f"Keluhan: {pemeriksaan_terakhir.get('keluhan', '-')}")
            print(f"Diagnosis: {pemeriksaan_terakhir.get('diagnosis', '-')}")
            print(f"Tindakan: {pemeriksaan_terakhir.get('tindakan', '-')}")
            
            resep = pemeriksaan_terakhir.get('resep', '')
            if resep:
                print(f"\n💊 RESEP OBAT:")
                print("-" * 30)
                print(f"{resep}")
            else:
                print(f"\n💊 RESEP OBAT: Tidak ada resep")
            
            catatan_dokter = pemeriksaan_terakhir.get('catatan', '')
            if catatan_dokter:
                print(f"\n📝 CATATAN DOKTER:")
                print(f"{catatan_dokter}")
            print("-" * 50)
        else:
            print("⚠️ Data pemeriksaan tidak ditemukan!")

        print("\nProses Farmasi:")
        obat_tersedia = input("Apakah semua obat tersedia? (y/n): ").lower()
        
        if obat_tersedia == 'y':
            print("\n✓ Semua obat tersedia")

            print("\nEdukasi Pasien:")
            cara_minum = input("Cara minum obat: ").strip()
            efek_samping = input("Peringatan efek samping: ").strip()
            catatan_farmasi = input("Catatan tambahan: ").strip()

            print(f"\n📋 RINGKASAN PEMBERIAN OBAT:")
            print(f"Pasien: {pasien['nama']}")
            if cara_minum:
                print(f"Cara minum: {cara_minum}")
            if efek_samping:
                print(f"Peringatan: {efek_samping}")
            if catatan_farmasi:
                print(f"Catatan: {catatan_farmasi}")

            konfirmasi = input("\nApakah obat sudah diberikan kepada pasien? (y/n): ").lower()
            
            if konfirmasi == 'y':
                waktu_selesai = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.db.update_status_pasien(id_pasien, 'selesai', waktu_selesai)
                self.antrean.hapus_dari_dipanggil(id_pasien)
                
                print(f"\n🎉 PROSES SELESAI!")
                print(f"✓ Obat sudah diberikan kepada {pasien['nama']}")
                print(f"✓ Status pasien otomatis diubah menjadi: SELESAI")
                print(f"✓ Pasien sudah selesai seluruh proses pelayanan")
                
                if cara_minum:
                    print(f"\n💊 CARA MINUM OBAT:")
                    print(f"{cara_minum}")
                
                if efek_samping:
                    print(f"\n⚠️  PERINGATAN:")
                    print(f"{efek_samping}")
                    
                print(f"\n📝 WAKTU SELESAI: {waktu_selesai}")
                
            else:
                waktu_siap = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.db.update_status_pasien(id_pasien, 'siap_ambil_obat', waktu_siap)
                
                print(f"\n⏳ Obat untuk {pasien['nama']} sudah siap")
                print(f"Status pasien: SIAP AMBIL OBAT")
                
        else:
            print("\n⚠️ Ada obat yang tidak tersedia")
            obat_kosong = input("Obat yang kosong: ").strip()
            estimasi = input("Estimasi ketersediaan: ").strip()
            
            waktu_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.update_status_pasien(id_pasien, 'obat_tidak_tersedia', waktu_update)
            
            print(f"\n❌ Obat tidak tersedia: {obat_kosong}")
            if estimasi:
                print(f"Estimasi tersedia: {estimasi}")
            print(f"Status pasien: OBAT TIDAK TERSEDIA")
            print(f"\n📍 INFORMASI UNTUK PASIEN:")
            print(f"Karena obat tidak tersedia di fasilitas ini,")
            print(f"pasien dapat membeli obat di apotek terdekat dengan")
            print(f"membawa resep yang telah diberikan oleh dokter.")
            print(f"\n💊 Pastikan untuk mengikuti aturan minum obat")
            print(f"sesuai dengan petunjuk dokter.")

    def check_and_auto_reset_daily(self):
        """Cek apakah tanggal sudah berganti dan lakukan reset otomatis nomor antrean"""
        tanggal_sekarang = datetime.date.today().strftime("%Y-%m-%d")

        tanggal_terakhir = None
        if self.last_date_file.exists():
            try:
                with open(self.last_date_file, 'r') as f:
                    tanggal_terakhir = f.read().strip()
            except:
                tanggal_terakhir = None

        if tanggal_terakhir != tanggal_sekarang:
            if tanggal_terakhir is not None:  # Jika bukan pertama kali
                print(f"\n🔄 RESET OTOMATIS NOMOR ANTREAN")
                print(f"Tanggal berubah dari {tanggal_terakhir} ke {tanggal_sekarang}")
                print("Nomor antrean akan dimulai dari 1 untuk hari ini...")

                self.antrean.reset()
                
                print("✅ Nomor antrean berhasil direset untuk hari baru!")
                print("📝 Data antrean sebelumnya tetap tersimpan di database")
                print("="*60)

            try:
                with open(self.last_date_file, 'w') as f:
                    f.write(tanggal_sekarang)
            except Exception as e:
                print(f"Warning: Gagal menyimpan tanggal: {e}")

    def initialize_daily_queue(self):
        df_hari_ini = self.db.get_pasien_hari_ini()
        
        menunggu = df_hari_ini[df_hari_ini['status'] == 'menunggu']
        terpanggil = df_hari_ini[df_hari_ini['status'] == 'terpanggil']
        
        self.antrean.initialize_from_data(
            menunggu['id'].tolist(),
            terpanggil['id'].tolist()
        )
    
    def jalankan(self):
        while True:
            self.check_and_auto_reset_daily()
            
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
                self.proses_pemeriksaan_dokter()
            elif choice == '12':
                self.proses_farmasi()
            elif choice == '13':
                self.crud.cari_dan_cetak_ulang_qr()
            elif choice == '0':
                print("\nTerima kasih telah menggunakan Sistem Antrean Pengambilan Obat")
                print("Aplikasi akan ditutup...")
                break
            else:
                print("\nPilihan tidak valid! Silakan pilih menu 0-13")
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