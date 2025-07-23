# 🏥 AntriObat - Sistem Antrean Puskesmas

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/RezaR2P/AntriObat)

Sistem manajemen antrean digital untuk Puskesmas dengan fitur QR Code, pemeriksaan dokter, dan farmasi terintegrasi.

## 📖 Daftar Isi

- [Fitur Utama](#-fitur-utama)
- [Teknologi](#️-teknologi)
- [Instalasi](#-instalasi)
- [Penggunaan](#-penggunaan)
- [Struktur Project](#-struktur-project)
- [Workflow Sistem](#-workflow-sistem)
- [Screenshot](#-screenshot)
- [Troubleshooting](#-troubleshooting)
- [Kontribusi](#-kontribusi)
- [Lisensi](#-lisensi)

## 🚀 Fitur Utama

### 📋 Manajemen Pasien
- **Pendaftaran Pasien Baru** - Registrasi dengan data lengkap dan generate QR Code
- **Database Master Pasien** - Penyimpanan data permanen di Excel
- **Pencarian Pasien** - Cari berdasarkan NIK atau scan QR Code
- **Edit/Hapus Data** - Update informasi pasien

### 🎯 Sistem Antrean
- **Antrean Digital** - Nomor antrean otomatis per hari
- **Reset Harian Otomatis** - Nomor antrean reset setiap ganti hari
- **Multi Poli** - Support Poli Umum, Gigi, dan Lansia
- **Status Tracking** - Monitor status pasien real-time

### 🔊 Audio & Visual
- **Text-to-Speech** - Pemanggilan pasien dengan suara
- **QR Code Generator** - Generate dan cetak ulang QR Code
- **Interface Console** - UI terminal yang user-friendly

### 🏥 Workflow Medis Lengkap
- **Pemeriksaan Dokter** - Input hasil pemeriksaan, diagnosis, resep
- **Farmasi Terintegrasi** - Proses pemberian obat dengan resep dari dokter
- **Status Otomatis** - Update status dari menunggu → terpanggil → diperiksa → selesai

### 📊 Data Management
- **Excel Integration** - Penyimpanan data di file Excel
- **Data Pemeriksaan** - Riwayat lengkap pemeriksaan pasien
- **Backup Otomatis** - Data tersimpan otomatis setiap transaksi

## 🛠️ Teknologi

| Kategori | Teknologi | Fungsi |
|----------|-----------|---------|
| **Backend** | Python 3.7+ | Core application |
| **Database** | Excel (.xlsx) | Data storage |
| **QR Code** | qrcode, pyzbar | Generate & scan QR |
| **Computer Vision** | OpenCV | Camera QR scanning |
| **Audio** | pyttsx3 | Text-to-speech |
| **Data Processing** | pandas, openpyxl | Excel manipulation |
| **UI** | Console/Terminal | User interface |

## 🔧 Instalasi

### Prerequisites
- Python 3.7 atau lebih baru
- Webcam (untuk scan QR Code)
- Windows/Linux/macOS

### 1. Clone Repository
```bash
git clone https://github.com/RezaR2P/AntriObat.git
cd AntriObat
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi
```bash
python main.py
```

## 📱 Penggunaan

### 🏃‍♂️ Quick Start

1. **Daftar Pasien Baru** (Menu 1)
   - Input data lengkap pasien
   - Sistem generate QR Code otomatis
   - Simpan QR Code untuk kunjungan berikutnya

2. **Daftar Antrean** (Menu 2)
   - Scan QR Code atau input NIK
   - Pilih poli tujuan
   - Dapatkan nomor antrean

3. **Panggil Pasien** (Menu 9)
   - Panggil pasien berikutnya
   - Suara otomatis memanggil nama

4. **Pemeriksaan Dokter** (Menu 11)
   - Input hasil pemeriksaan
   - Tulis resep obat
   - Update status ke "diperiksa"

5. **Proses Farmasi** (Menu 12)
   - Lihat resep dari dokter
   - Berikan obat ke pasien
   - Status otomatis "selesai"

### 📋 Menu Lengkap

| Menu | Fungsi | Pengguna |
|------|--------|----------|
| 1 | Pendaftaran Pasien Baru | Staff Pendaftaran |
| 2 | Pendaftaran Antrean | Staff Pendaftaran |
| 3 | Lihat Antrean Saat Ini | Semua Staff |
| 4 | Lihat Pasien Terpanggil | Semua Staff |
| 5 | Lihat Pasien Selesai | Semua Staff |
| 6 | Cari Data Pasien | Staff Pendaftaran |
| 7 | Edit Data Pasien | Staff Pendaftaran |
| 8 | Hapus Data Pasien | Staff Pendaftaran |
| 9 | Panggil Pasien Berikutnya | Staff Loket |
| 10 | Panggil Ulang Pasien | Staff Loket |
| 11 | Proses Pemeriksaan Dokter | Dokter |
| 12 | Proses Farmasi | Staff Farmasi |
| 13 | Cetak Ulang QR Code | Staff Pendaftaran |

## 📁 Struktur Project

```
AntriObat/
├── main.py                 # Entry point aplikasi
├── antrean.py             # Queue management system
├── audio.py               # Text-to-speech handler
├── crud_handler.py        # CRUD operations
├── database.py            # Excel database operations
├── qr_handler.py          # QR Code generator & scanner
├── ui.py                  # User interface console
├── requirements.txt       # Python dependencies
├── README.md             # Dokumentasi
└── data/                 # Data directory
    ├── master_pasien.xlsx     # Database master pasien
    ├── antrean_harian.xlsx    # Database antrean harian
    ├── data_pemeriksaan.xlsx  # Database pemeriksaan
    ├── last_date.txt          # File tracking tanggal
    └── qr_codes/              # Folder QR Code pasien
        ├── patient1.png
        ├── patient2.png
        └── ...
```

## 🔄 Workflow Sistem

### 1. 👤 Pasien Baru
```
Datang ke Puskesmas → Daftar Pasien Baru → Generate QR Code → Simpan QR Code
```

### 2. 🎯 Daftar Antrean
```
Scan QR Code → Pilih Poli → Dapat Nomor Antrean → Tunggu Dipanggil
```

### 3. 🏥 Proses Pelayanan
```
Dipanggil → Pemeriksaan Dokter → Dapat Resep → Farmasi → Selesai
```

### 4. 📊 Status Tracking
```
menunggu → terpanggil → diperiksa → selesai
```

## 🎨 Screenshot

### Dashboard Utama
```
======================================================================
                SISTEM ANTREAN PUSKESMAS
======================================================================
Jumlah antrean menunggu : 5
Jumlah pasien terpanggil: 3
======================================================================

MENU:
1. Pendaftaran Pasien Baru (Buat Akun & QR Code)
2. Pendaftaran Antrean (Scan QR / Input NIK)
3. Lihat Antrean Saat Ini
...
```

### Pemanggilan Pasien
```
======================================================================
  🔊 PEMANGGILAN PASIEN
  NOMOR ANTREAN 5
  NAMA: John Doe
  POLI: Poli Umum
  WAKTU: 2025-07-24 10:30:15

======================================================================
```

## 🔧 Troubleshooting

### ❌ Error: Kamera tidak bisa dibuka
**Solusi:**
- Pastikan webcam terhubung
- Tutup aplikasi lain yang menggunakan kamera
- Restart aplikasi

### ❌ Error: File Excel tidak bisa dibuka
**Solusi:**
- Tutup file Excel yang terbuka
- Pastikan folder `data/` ada dan writeable
- Check permissions folder

### ❌ Error: Text-to-speech tidak bekerja
**Solusi:**
- Install audio driver
- Check volume sistem
- Restart aplikasi

### ❌ Error: ModuleNotFoundError
**Solusi:**
```bash
pip install -r requirements.txt
```

## 🔄 Auto Reset Harian

Sistem memiliki fitur **auto-reset nomor antrean** setiap hari:

- **File Tracking**: `data/last_date.txt` menyimpan tanggal terakhir
- **Deteksi Otomatis**: Sistem cek tanggal saat aplikasi dibuka
- **Reset Otomatis**: Jika ganti hari, nomor antrean reset ke 1
- **Data Aman**: Data lama tetap tersimpan di database

## 📈 Fitur Mendatang

- [ ] Web interface
- [ ] SMS notification
- [ ] Laporan analitik
- [ ] Multi-branch support
- [ ] Database MySQL/PostgreSQL
- [ ] Mobile app
- [ ] Appointment booking

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan:

1. Fork repository ini
2. Buat branch fitur (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📞 Support

Jika ada pertanyaan atau masalah:

- **Issues**: [GitHub Issues](https://github.com/RezaR2P/AntriObat/issues)
- **Email**: [your-email@example.com]
- **Documentation**: README.md ini

## 📄 Lisensi

Distributed under the MIT License. See `LICENSE` for more information.

## 👨‍💻 Author

**RezaR2P**
- GitHub: [@RezaR2P](https://github.com/RezaR2P)
- Project Link: [https://github.com/RezaR2P/AntriObat](https://github.com/RezaR2P/AntriObat)

## 🙏 Acknowledgments

- [Python](https://python.org) - Programming language
- [OpenCV](https://opencv.org) - Computer vision library
- [pandas](https://pandas.pydata.org) - Data manipulation
- [qrcode](https://pypi.org/project/qrcode/) - QR Code generation
- [pyttsx3](https://pypi.org/project/pyttsx3/) - Text-to-speech

---

⭐ **Jika project ini bermanfaat, berikan star di GitHub!** ⭐