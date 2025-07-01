import pandas as pd
from pathlib import Path
import datetime

class Database:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.data_pasien = self.load_data()
    
    def load_data(self):
        """Memuat data pasien dari file Excel"""
        if self.excel_path.exists():
            return pd.read_excel(str(self.excel_path))
        else:
            # Buat dataframe kosong dengan kolom yang sesuai
            df = pd.DataFrame(columns=['id', 'nomor_antrean', 'nama', 'no_rekam_medis', 
                                     'tanggal', 'status', 'waktu_daftar', 'waktu_panggil'])
            return df

    def save_data(self):
        """Menyimpan data pasien ke file Excel"""
        self.data_pasien.to_excel(str(self.excel_path), index=False)
    
    def tambah_pasien(self, id_pasien, nama, no_rekam_medis, nomor_antrean):
        """Menambahkan pasien baru ke database"""
        tanggal_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        waktu_daftar = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        pasien_baru = {
            'id': id_pasien,
            'nomor_antrean': nomor_antrean,
            'nama': nama,
            'no_rekam_medis': no_rekam_medis,
            'tanggal': tanggal_hari_ini,
            'status': 'menunggu',
            'waktu_daftar': waktu_daftar,
            'waktu_panggil': None
        }
        
        # Tambahkan ke DataFrame dan simpan ke Excel
        self.data_pasien = pd.concat([self.data_pasien, pd.DataFrame([pasien_baru])], ignore_index=True)
        self.save_data()
    
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
    
    def cari_pasien(self, id_pasien):
        """Cari pasien berdasarkan ID"""
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
    
    def update_data_pasien(self, id_pasien, nama=None, no_rekam_medis=None):
        """Update data pasien berdasarkan ID"""
        try:
            # Cari pasien yang akan diupdate
            idx = self.data_pasien[self.data_pasien['id'] == id_pasien].index
            if len(idx) > 0:
                # Update nama jika diberikan
                if nama is not None:
                    self.data_pasien.loc[idx, 'nama'] = nama
                
                # Update no_rekam_medis jika diberikan
                if no_rekam_medis is not None:
                    self.data_pasien.loc[idx, 'no_rekam_medis'] = no_rekam_medis
                
                self.save_data()
                return True
            return False
        except Exception as e:
            print(f"Error saat mengupdate data pasien: {e}")
            return False

    def __del__(self):
        """Destruktor untuk memastikan data tersimpan sebelum objek dihapus"""
        try:
            self.save_data()
        except:
            pass