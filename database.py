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
            return pd.read_excel(str(self.excel_path), dtype={'nik': str})
        else:
            df = pd.DataFrame(columns=['id', 'nomor_antrean', 'nama', 'nik', 
                                    'tanggal', 'status', 'waktu_daftar', 'waktu_panggil', 'poli'])
            return df
    
    def load_master_pasien(self):
        """Memuat data master pasien dari file Excel"""
        if self.master_pasien_path.exists():
            return pd.read_excel(str(self.master_pasien_path), dtype={'nik': str})
        else:
            df = pd.DataFrame(columns=['id_pasien', 'nik', 'nama', 'jenis_kelamin', 'tempat_lahir',
                                    'tanggal_lahir', 'alamat', 'riwayat_penyakit', 'tanggal_daftar_pertama', 'qr_code_path'])
            return df
    
    def load_data_pemeriksaan(self):
        if self.pemeriksaan_path.exists():
            return pd.read_excel(str(self.pemeriksaan_path))
        else:
            df = pd.DataFrame(columns=['id_pemeriksaan', 'id_pasien', 'nama_pasien', 'tanggal_pemeriksaan',
                                    'keluhan', 'tekanan_darah', 'nadi', 'suhu', 'diagnosis', 'tindakan', 
                                    'resep', 'catatan', 'waktu_periksa'])
            return df

    def save_data(self):
        self.data_pasien.to_excel(str(self.excel_path), index=False)
    
    def save_master_pasien(self):
        self.master_pasien.to_excel(str(self.master_pasien_path), index=False)
    
    def save_data_pemeriksaan(self):
        self.data_pemeriksaan.to_excel(str(self.pemeriksaan_path), index=False)
    
    def tambah_pasien_baru_master(self, id_pasien, nik, nama, jenis_kelamin, tempat_lahir, tanggal_lahir, alamat, riwayat_penyakit, qr_code_path):
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
        
        self.master_pasien = pd.concat([self.master_pasien, pd.DataFrame([pasien_baru])], ignore_index=True)
        self.save_master_pasien()
        return id_pasien
    
    def tambah_antrean_harian(self, id_pasien, poli, nomor_antrean):
        master_data = self.master_pasien[self.master_pasien['id_pasien'] == id_pasien]
        if master_data.empty:
            return False
        
        pasien_master = master_data.iloc[0]
        tanggal_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        waktu_daftar = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        antrean_baru = {
            'id': id_pasien,
            'nomor_antrean': nomor_antrean,
            'nama': pasien_master['nama'],
            'nik': pasien_master['nik'],
            'tanggal': tanggal_hari_ini,
            'status': 'menunggu',
            'waktu_daftar': waktu_daftar,
            'waktu_panggil': None,
            'poli': poli
        }
        
        self.data_pasien = pd.concat([self.data_pasien, pd.DataFrame([antrean_baru])], ignore_index=True)
        self.save_data()
        return True
    
    def update_status_pasien(self, id_pasien, status, waktu_panggil=None):
        idx = self.data_pasien[self.data_pasien['id'] == id_pasien].index
        if len(idx) > 0:
            self.data_pasien.at[idx[0], 'status'] = status
            if waktu_panggil:
                self.data_pasien.at[idx[0], 'waktu_panggil'] = waktu_panggil
            self.save_data()
    
    def simpan_data_pemeriksaan(self, data_pemeriksaan):
        id_pemeriksaan = str(uuid.uuid4())[:8]
        master_data = self.master_pasien[self.master_pasien['id_pasien'] == data_pemeriksaan['id_pasien']]
        nama_pasien = master_data.iloc[0]['nama'] if not master_data.empty else 'Unknown'
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
        
        self.data_pemeriksaan = pd.concat([self.data_pemeriksaan, pd.DataFrame([pemeriksaan_baru])], ignore_index=True)
        self.save_data_pemeriksaan()
        return id_pemeriksaan
    
    def get_data_pemeriksaan_by_pasien(self, id_pasien):
        return self.data_pemeriksaan[self.data_pemeriksaan['id_pasien'] == id_pasien]

    def hapus_pasien(self, id_pasien):
        try:
            idx = self.data_pasien[self.data_pasien['id'] == id_pasien].index
            if len(idx) > 0:
                self.data_pasien = self.data_pasien.drop(idx)
                self.save_data()
                return True
            return False
        except Exception as e:
            print(f"Error saat menghapus pasien: {e}")
            return False
    
    def cari_pasien_master(self, id_pasien=None, nik=None):
        if id_pasien:
            return self.master_pasien[self.master_pasien['id_pasien'] == id_pasien]
        elif nik:
            nik_str = str(nik).strip()
            return self.master_pasien[self.master_pasien['nik'].str.strip() == nik_str]
        return pd.DataFrame()
    
    def cari_pasien_by_nik(self, nik):
        nik_str = str(nik).strip()
        return self.master_pasien[self.master_pasien['nik'].str.strip() == nik_str]
    
    def cari_pasien(self, id_pasien):
        return self.data_pasien[self.data_pasien['id'] == id_pasien]
    
    def get_pasien_hari_ini(self):
        tanggal_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        return self.data_pasien[self.data_pasien['tanggal'] == tanggal_hari_ini]
    
    def get_next_nomor_antrean(self):
        tanggal_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        df_hari_ini = self.data_pasien[self.data_pasien['tanggal'] == tanggal_hari_ini]
        
        if df_hari_ini.empty:
            return 1
        return df_hari_ini['nomor_antrean'].max() + 1
    
    def cek_pasien_sudah_antrean_hari_ini(self, id_pasien):
        tanggal_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        existing = self.data_pasien[
            (self.data_pasien['id'] == id_pasien) & 
            (self.data_pasien['tanggal'] == tanggal_hari_ini)
        ]
        return not existing.empty
    
    def update_data_pasien(self, id_pasien, nama=None, nik=None):
        try:
            idx = self.data_pasien[self.data_pasien['id'] == id_pasien].index
            if len(idx) > 0:
                if nama is not None:
                    self.data_pasien.loc[idx, 'nama'] = nama
                if nik is not None:
                    self.data_pasien.loc[idx, 'nik'] = nik
                self.save_data()
                return True
            return False
        except Exception as e:
            print(f"Error saat mengupdate data pasien: {e}")
            return False

    def update_data_master_pasien(self, id_pasien, **kwargs):
        try:
            idx = self.master_pasien[self.master_pasien['id_pasien'] == id_pasien].index
            if len(idx) > 0:
                for field, value in kwargs.items():
                    if field in self.master_pasien.columns and value is not None:
                        self.master_pasien.loc[idx, field] = value
                
                self.save_master_pasien()
                
                if 'nama' in kwargs or 'nik' in kwargs:
                    self.update_antrean_from_master(id_pasien)
                
                return True
            return False
        except Exception as e:
            print(f"Error saat mengupdate data master pasien: {e}")
            return False
    
    def update_antrean_from_master(self, id_pasien):
        try:
            master_data = self.master_pasien[self.master_pasien['id_pasien'] == id_pasien]
            if not master_data.empty:
                pasien_master = master_data.iloc[0]
                
                antrean_idx = self.data_pasien[self.data_pasien['id'] == id_pasien].index
                if len(antrean_idx) > 0:
                    self.data_pasien.loc[antrean_idx, 'nama'] = pasien_master['nama']
                    self.data_pasien.loc[antrean_idx, 'nik'] = pasien_master['nik']
                    self.save_data()
        except Exception as e:
            print(f"Error saat update antrean from master: {e}")

    def hapus_master_pasien(self, id_pasien):
        try:
            idx = self.master_pasien[self.master_pasien['id_pasien'] == id_pasien].index
            if len(idx) > 0:
                self.master_pasien = self.master_pasien.drop(idx)
                self.save_master_pasien()
                return True
            return False
        except Exception as e:
            print(f"Error saat menghapus master pasien: {e}")
            return False

    def hapus_data_pemeriksaan_pasien(self, id_pasien):
        try:
            idx = self.data_pemeriksaan[self.data_pemeriksaan['id_pasien'] == id_pasien].index
            if len(idx) > 0:
                self.data_pemeriksaan = self.data_pemeriksaan.drop(idx)
                self.save_data_pemeriksaan()
                return True
            return False
        except Exception as e:
            print(f"Error saat menghapus data pemeriksaan: {e}")
            return False

    def __del__(self):
        try:
            if hasattr(self, 'data_pasien') and self.data_pasien is not None:
                self.save_data()
            if hasattr(self, 'master_pasien') and self.master_pasien is not None:
                self.save_master_pasien()
            if hasattr(self, 'data_pemeriksaan') and self.data_pemeriksaan is not None:
                self.save_data_pemeriksaan()
        except Exception:
            pass