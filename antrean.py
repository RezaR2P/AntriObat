from collections import deque

class AntreanManager:
    def __init__(self):
        self.antrean_aktif = deque()
        self.sudah_dipanggil = deque()
    
    def tambah_pasien(self, id_pasien):
        """Menambahkan pasien ke antrean (enqueue)"""
        self.antrean_aktif.append(id_pasien)
    
    def panggil_berikutnya(self):
        """Memanggil pasien berikutnya dari antrean (dequeue)"""
        if self.antrean_aktif:
            id_pasien = self.antrean_aktif.popleft()
            self.sudah_dipanggil.append(id_pasien)
            return id_pasien
        return None
    
    def get_terakhir_dipanggil(self):
        """Mendapatkan pasien terakhir yang dipanggil"""
        if self.sudah_dipanggil:
            return self.sudah_dipanggil[-1]
        return None
    
    def reset(self):
        """Reset antrean"""
        self.antrean_aktif.clear()
        self.sudah_dipanggil.clear()
    
    def initialize_from_data(self, menunggu_ids, terpanggil_ids):
        """Inisialisasi antrean dari data yang ada"""
        self.antrean_aktif.clear()
        self.sudah_dipanggil.clear()
        
        for id_pasien in menunggu_ids:
            self.antrean_aktif.append(id_pasien)
            
        for id_pasien in terpanggil_ids:
            self.sudah_dipanggil.append(id_pasien)

    def hapus_dari_dipanggil(self, id_pasien):
        """Menghapus pasien dari daftar sudah dipanggil"""
        # Konversi ke list, hapus, lalu buat deque baru
        if id_pasien in self.sudah_dipanggil:
            temp_list = list(self.sudah_dipanggil)
            temp_list.remove(id_pasien)
            self.sudah_dipanggil = deque(temp_list)
            return True
        return False

    def hapus_dari_aktif(self, id_pasien):
        """Menghapus pasien dari antrean aktif"""
        if id_pasien in self.antrean_aktif:
            # Konversi ke list, hapus, lalu buat deque baru untuk keamanan
            temp_list = list(self.antrean_aktif)
            temp_list.remove(id_pasien)
            self.antrean_aktif = deque(temp_list)
            return True
        return False
