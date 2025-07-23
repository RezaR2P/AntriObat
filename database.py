import pandas as pd
import datetime

class Database:
    def __init__(self, excel_path, master_pasien_path):
        self.excel_path = excel_path
        self.master_pasien_path = master_pasien_path
        self.data_pasien = self.load_data()
        self.master_pasien = self.load_master_pasien()
    
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

    def save_data(self):
        """Menyimpan data antrean harian ke file Excel"""
        self.data_pasien.to_excel(str(self.excel_path), index=False)
    
    def save_master_pasien(self):
        """Menyimpan data master pasien ke file Excel"""
        self.master_pasien.to_excel(str(self.master_pasien_path), index=False)
    
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