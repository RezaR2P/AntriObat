import qrcode
import cv2
from pyzbar.pyzbar import decode
import numpy as np

class QRGenerator:
    def generate_qr_code(self, data, save_path):
        """Membuat QR code dari data"""
        img = qrcode.make(data)
        img.save(save_path)
        return save_path

class QRScanner:
    def scan_from_camera(self):
        """Scan QR code menggunakan kamera laptop"""
        print("\nMembuka kamera untuk scan QR code...")
        print("Tekan 'q' untuk keluar dari mode scan\n")
        
        # Inisialisasi kamera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Tidak dapat membuka kamera!")
            return None
        
        qr_data = None
        
        try:
            while True:
                # Baca frame dari kamera
                ret, frame = cap.read()
                if not ret:
                    print("Error: Tidak dapat membaca frame dari kamera!")
                    break
                
                # Decode QR code dari frame
                decoded_objects = decode(frame)
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    print(f"QR Code terdeteksi: {qr_data}")
                    
                    # Gambar kotak di sekitar QR code
                    points = obj.polygon
                    if len(points) > 4:
                        hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                        cv2.polylines(frame, [hull], True, (0, 255, 0), 3)
                    else:
                        for j in range(4):
                            cv2.line(frame, points[j], points[(j+1) % 4], (0, 255, 0), 3)
                
                # Tambahkan teks petunjuk
                cv2.putText(frame, "Arahkan QR Code ke kamera", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, "Tekan 'q' untuk keluar", (10, 70), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Tampilkan frame
                cv2.imshow("QR Code Scanner", frame)
                
                # Keluar dari loop jika QR code terdeteksi atau pengguna menekan 'q'
                if qr_data or cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        finally:
            # Tutup kamera dan jendela
            cap.release()
            cv2.destroyAllWindows()
            
        return qr_data