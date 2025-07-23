import pandas as pd
import datetime
import uuid

class Database:
    def __init__(self, excel_path, master_pasien_path):
        self.excel_path = excel_path
        self.master_pasien_path = master_pasien_path
        self.pemeriksaan_path = excel_path.parent / "data_pemeriksaan.xlsx"
        self.data_pasien = self.load_data()
        self.master_pasien = self.load_master_pasien()
        self.data_pemeriksaan = self.load_data_pemeriksaan()
    
    def load_data(self):
        """Memuat data antrean harian dari file Excel"""
        if self.excel_path.exists():
            # Read with dtype to prevent NIK from being converted to scientific notation
            return pd.read_excel(str(self.excel_path), dtype={'nik': str})
        else:
            # Buat dataframe kosong dengan kolom yang sesuai untuk antrean harian
            df = pd.DataFrame(columns=['id', 'nomor_antrean', 'nama', 'nik', 
                                    'tanggal', 'status', 'waktu_daftar', 'waktu_panggil', 'poli'])
            return df
    
    def load_master_pasien(self):
        """Memuat data master pasien dari file Excel"""
        if self.master_pasien_path.exists():
            # Read with dtype to prevent NIK from being converted to scientific notation
            return pd.read_excel(str(self.master_pasien_path), dtype={'nik': str})
        else:
            # Buat dataframe kosong dengan kolom untuk data master pasien
            df = pd.DataFrame(columns=['id_pasien', 'nik', 'nama', 'jenis_kelamin', 'tempat_lahir',
                                    'tanggal_lahir', 'alamat', 'riwayat_penyakit', 'tanggal_daftar_pertama', 'qr_code_path'])
            return df
    
    def load_data_pemeriksaan(self):
        """Memuat data pemeriksaan dari file Excel"""
        if self.pemeriksaan_path.exists():
            return pd.read_excel(str(self.pemeriksaan_path))
        else:
            # Buat dataframe kosong dengan kolom untuk data pemeriksaan
            df = pd.DataFrame(columns=['id_pemeriksaan', 'id_pasien', 'nama_pasien', 'tanggal_pemeriksaan',
                                    'keluhan', 'tekanan_darah', 'nadi', 'suhu', 'diagnosis', 'tindakan', 
                                    'resep', 'catatan', 'waktu_periksa'])
            return df

    def save_data(self):
        """Menyimpan data antrean harian ke file Excel"""
        self.data_pasien.to_excel(str(self.excel_path), index=False)
    
    def save_master_pasien(self):
        """Menyimpan data master pasien ke file Excel"""
        self.master_pasien.to_excel(str(self.master_pasien_path), index=False)
    
    def save_data_pemeriksaan(self):
        """Menyimpan data pemeriksaan ke file Excel"""
        self.data_pemeriksaan.to_excel(str(self.pemeriksaan_path), index=False)
    
    def tambah_pasien_baru_master(self, id_pasien, nik, nama, jenis_kelamin, tempat_lahir, tanggal_lahir, alamat, riwayat_penyakit, qr_code_path):
        """Menambahkan pasien baru ke database master"""
        tanggal_daftar = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        pasien_baru = {
            'id_pasien': id_pasien,
            'nik': nik,
            'nama': nama,
            'jenis_kelamin': jenis_kelamin,
            'tempat_lahir': tempat_lahir,
            'tanggal_lahir': tanggal_lahir,
            'alamat': alamat,
            'riwayat_penyakit': riwayat_penyakit,
            'tanggal_daftar_pertama': tanggal_daftar,
            'qr_code_path': qr_code_path
        }
        
        # Tambahkan ke DataFrame master dan simpan
        self.master_pasien = pd.concat([self.master_pasien, pd.DataFrame([pasien_baru])], ignore_index=True)
        self.save_master_pasien()
        return id_pasien
    
    def tambah_antrean_harian(self, id_pasien, poli, nomor_antrean):
        """Menambahkan pasien ke antrean harian"""
        # Ambil data dari master
        master_data = self.master_pasien[self.master_pasien['id_pasien'] == id_pasien]
        if master_data.empty:
            return False
        
        pasien_master = master_data.iloc[0]
        tanggal_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        waktu_daftar = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        antrean_baru = {
            'id': id_pasien,  # Gunakan ID yang sama dari master
            'nomor_antrean': nomor_antrean,
            'nama': pasien_master['nama'],
            'nik': pasien_master['nik'],
            'tanggal': tanggal_hari_ini,
            'status': 'menunggu',
            'waktu_daftar': waktu_daftar,
            'waktu_panggil': None,
            'poli': poli
        }
        
        # Tambahkan ke DataFrame antrean harian dan simpan
        self.data_pasien = pd.concat([self.data_pasien, pd.DataFrame([antrean_baru])], ignore_index=True)
        self.save_data()
        return True
    
    def update_status_pasien(self, id_pasien, status, waktu_panggil=None):
        """Update status pasien"""
        idx = self.data_pasien[self.data_pasien['id'] == id_pasien].index
        if len(idx) > 0:
            self.data_pasien.at[idx[0], 'status'] = status
            if waktu_panggil:
                self.data_pasien.at[idx[0], 'waktu_panggil'] = waktu_panggil
            self.save_data()
    
    def simpan_data_pemeriksaan(self, data_pemeriksaan):
        """Menyimpan data hasil pemeriksaan dokter"""
        # Generate ID unik untuk pemeriksaan
        id_pemeriksaan = str(uuid.uuid4())[:8]
        
        # Ambil nama pasien dari data master
        master_data = self.master_pasien[self.master_pasien['id_pasien'] == data_pemeriksaan['id_pasien']]
        nama_pasien = master_data.iloc[0]['nama'] if not master_data.empty else 'Unknown'
        
        # Siapkan data pemeriksaan untuk disimpan
        pemeriksaan_baru = {
            'id_pemeriksaan': id_pemeriksaan,
            'id_pasien': data_pemeriksaan['id_pasien'],
            'nama_pasien': nama_pasien,
            'tanggal_pemeriksaan': datetime.date.today().strftime("%Y-%m-%d"),
            'keluhan': data_pemeriksaan.get('keluhan', ''),
            'tekanan_darah': data_pemeriksaan.get('tekanan_darah', ''),
            'nadi': data_pemeriksaan.get('nadi', ''),
            'suhu': data_pemeriksaan.get('suhu', ''),
            'diagnosis': data_pemeriksaan.get('diagnosis', ''),
            'tindakan': data_pemeriksaan.get('tindakan', ''),
            'resep': data_pemeriksaan.get('resep', ''),
            'catatan': data_pemeriksaan.get('catatan', ''),
            'waktu_periksa': data_pemeriksaan.get('waktu_periksa', '')
        }
        
        # Tambahkan ke DataFrame pemeriksaan dan simpan
        self.data_pemeriksaan = pd.concat([self.data_pemeriksaan, pd.DataFrame([pemeriksaan_baru])], ignore_index=True)
        self.save_data_pemeriksaan()
        return id_pemeriksaan
    
    def get_data_pemeriksaan_by_pasien(self, id_pasien):
        """Mendapatkan data pemeriksaan berdasarkan ID pasien"""
        return self.data_pemeriksaan[self.data_pemeriksaan['id_pasien'] == id_pasien]

    def hapus_pasien(self, id_pasien):
        """Menghapus pasien dari database berdasarkan ID"""
        try:
            # Cari pasien yang akan dihapus
            idx = self.data_pasien[self.data_pasien['id'] == id_pasien].index
            if len(idx) > 0:
                # Hapus pasien dari DataFrame
                self.data_pasien = self.data_pasien.drop(idx)
                self.save_data()
                return True
            return False
        except Exception as e:
            print(f"Error saat menghapus pasien: {e}")
            return False
    
    def cari_pasien_master(self, id_pasien=None, nik=None):
        """Cari pasien di database master berdasarkan ID atau NIK"""
        if id_pasien:
            return self.master_pasien[self.master_pasien['id_pasien'] == id_pasien]
        elif nik:
            # Since we're now reading NIK as string, simple comparison should work
            nik_str = str(nik).strip()
            return self.master_pasien[self.master_pasien['nik'].str.strip() == nik_str]
        return pd.DataFrame()
    
    def cari_pasien_by_nik(self, nik):
        """Cari pasien di database master berdasarkan NIK saja"""
        nik_str = str(nik).strip()
        return self.master_pasien[self.master_pasien['nik'].str.strip() == nik_str]
    
    def cari_pasien(self, id_pasien):
        """Cari pasien berdasarkan ID di antrean harian"""
        return self.data_pasien[self.data_pasien['id'] == id_pasien]
    
    def get_pasien_hari_ini(self):
        """Mendapatkan data pasien untuk hari ini"""
        tanggal_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        return self.data_pasien[self.data_pasien['tanggal'] == tanggal_hari_ini]
    
    def get_next_nomor_antrean(self):
        """Mendapatkan nomor antrean berikutnya"""
        tanggal_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        df_hari_ini = self.data_pasien[self.data_pasien['tanggal'] == tanggal_hari_ini]
        
        if df_hari_ini.empty:
            return 1
        return df_hari_ini['nomor_antrean'].max() + 1
    
    def cek_pasien_sudah_antrean_hari_ini(self, id_pasien):
        """Cek apakah pasien sudah mendaftar antrean hari ini"""
        tanggal_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        existing = self.data_pasien[
            (self.data_pasien['id'] == id_pasien) & 
            (self.data_pasien['tanggal'] == tanggal_hari_ini)
        ]
        return not existing.empty
    
    def update_data_pasien(self, id_pasien, nama=None, nik=None):
        """Update data pasien berdasarkan ID"""
        try:
            # Cari pasien yang akan diupdate
            idx = self.data_pasien[self.data_pasien['id'] == id_pasien].index
            if len(idx) > 0:
                # Update nama jika diberikan
                if nama is not None:
                    self.data_pasien.loc[idx, 'nama'] = nama
                
                # Update NIK jika diberikan
                if nik is not None:
                    self.data_pasien.loc[idx, 'nik'] = nik
                
                self.save_data()
                return True
            return False
        except Exception as e:
            print(f"Error saat mengupdate data pasien: {e}")
            return False

    def update_data_master_pasien(self, id_pasien, **kwargs):
        """Update data master pasien berdasarkan ID"""
        try:
            # Cari pasien yang akan diupdate di master
            idx = self.master_pasien[self.master_pasien['id_pasien'] == id_pasien].index
            if len(idx) > 0:
                # Update field yang diberikan
                for field, value in kwargs.items():
                    if field in self.master_pasien.columns and value is not None:
                        self.master_pasien.loc[idx, field] = value
                
                self.save_master_pasien()
                
                # Update juga di antrean harian jika ada perubahan nama atau NIK
                if 'nama' in kwargs or 'nik' in kwargs:
                    self.update_antrean_from_master(id_pasien)
                
                return True
            return False
        except Exception as e:
            print(f"Error saat mengupdate data master pasien: {e}")
            return False
    
    def update_antrean_from_master(self, id_pasien):
        """Update data nama dan NIK di antrean harian berdasarkan master"""
        try:
            # Ambil data terbaru dari master
            master_data = self.master_pasien[self.master_pasien['id_pasien'] == id_pasien]
            if not master_data.empty:
                pasien_master = master_data.iloc[0]
                
                # Update di antrean harian
                antrean_idx = self.data_pasien[self.data_pasien['id'] == id_pasien].index
                if len(antrean_idx) > 0:
                    self.data_pasien.loc[antrean_idx, 'nama'] = pasien_master['nama']
                    self.data_pasien.loc[antrean_idx, 'nik'] = pasien_master['nik']
                    self.save_data()
        except Exception as e:
            print(f"Error saat update antrean from master: {e}")

    def __del__(self):
        """Destruktor untuk memastikan data tersimpan sebelum objek dihapus"""
        try:
            self.save_data()
            self.save_master_pasien()
        except:
            pass