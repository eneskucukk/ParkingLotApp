import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QInputDialog
)
from PyQt5.QtCore import Qt
from datetime import datetime

class ParkingLotApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("2D Gelişmiş Otopark Alanı")
        self.setGeometry(100, 100, 500, 400)
        
        # Otopark yerlerinin durumu (None: boş, {plaka, giriş_zamanı} dolu)
        self.spots = [None] * 6  

        # Ana layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Otopark Bilgisi
        self.capacity_label = QLabel("Toplam Kapasite: 6 | Dolu: 0")
        self.capacity_label.setObjectName("capacityLabel")
        self.main_layout.addWidget(self.capacity_label)

        # Park yeri grid'i
        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.grid_layout)

        # Park yerleri oluşturma
        self.spot_labels = []
        for i in range(6):
            label = QLabel(f"Yer {i+1}")
            label.setAlignment(Qt.AlignCenter)
            label.setObjectName(f"spotLabel{i+1}")
            self.grid_layout.addWidget(label, i // 3, i % 3)  
            self.spot_labels.append(label)

        # Düğmeler
        self.button_layout = QGridLayout()
        self.main_layout.addLayout(self.button_layout)

        for i in range(6):
            park_button = QPushButton(f"Araç Park Et (Yer {i+1})")
            leave_button = QPushButton(f"Parkı Boşalt (Yer {i+1})")

            park_button.clicked.connect(lambda _, idx=i: self.park_car(idx))
            leave_button.clicked.connect(lambda _, idx=i: self.remove_car(idx))

            self.button_layout.addWidget(park_button, i, 0)
            self.button_layout.addWidget(leave_button, i, 1)

        # Stil dosyasını uygula
        self.setStyleSheet(self.get_stylesheet())
        self.update_parking_spots()

    def park_car(self, index):
        if self.spots[index] is None:
            # Plaka bilgisi alma
            plate, ok = QInputDialog.getText(self, "Araç Park Et", "Araç Plaka Numarası:")
            if ok and plate:
                entry_time = datetime.now()
                self.spots[index] = {"plate": plate, "entry_time": entry_time}
                self.update_parking_spots()

    def remove_car(self, index):
        if self.spots[index] is not None:
            # Ücret hesaplama
            entry_time = self.spots[index]['entry_time']
            exit_time = datetime.now()
            duration = exit_time - entry_time
            total_minutes = int(duration.total_seconds() // 60)
            fee = self.calculate_fee(total_minutes)

            plate = self.spots[index]['plate']
            self.spots[index] = None

            # Mesaj göster
            msg = f"Plaka: {plate}\nToplam Park Süresi: {total_minutes} dakika\nÜcret: {fee:.2f} TL"
            QInputDialog.getText(self, "Araç Çıkışı", msg)
            self.update_parking_spots()

            # Ücret bilgilerini JSON dosyasına kaydet
            self.save_fee_to_json(plate, total_minutes, fee)

    def calculate_fee(self, total_minutes):
        # 40 dakikada bir 5 TL ekleyelim
        if total_minutes <= 40:
            return 5.0
        else:
            additional_fee = (total_minutes // 40) * 5
            return 5.0 + additional_fee

    def save_fee_to_json(self, plate, total_minutes, fee):
        data = {
            "plate": plate,
            "duration_minutes": total_minutes,
            "fee": fee,
            "exit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            # Dosyayı aç ve mevcut veriyi yükle
            with open("parking_fees.json", "a") as json_file:
                json.dump(data, json_file)
                json_file.write("\n")  # Her kayıt arasında yeni satır
        except Exception as e:
            print(f"Dosyaya yazarken bir hata oluştu: {e}")

    def update_parking_spots(self):
        occupied_spots = 0
        for i, spot in enumerate(self.spots):
            if spot:
                self.spot_labels[i].setStyleSheet("background-color: red; color: white;")
                self.spot_labels[i].setText(f"Yer {i+1} (Dolu)\n{spot['plate']}\nGiriş: {spot['entry_time'].strftime('%H:%M:%S')}")
                occupied_spots += 1
            else:
                self.spot_labels[i].setStyleSheet("background-color: green; color: white;")
                self.spot_labels[i].setText(f"Yer {i+1} (Boş)")
        
        # Kapasite bilgisi güncelle
        self.capacity_label.setText(f"Toplam Kapasite: 6 | Dolu: {occupied_spots}")

    def get_stylesheet(self):
        return """
        QWidget {
            background-color: #fafafa;
            font-family: Arial, sans-serif;
        }

        #capacityLabel {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }

        QLabel {
            background-color: #3498db;
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton {
            background-color: #2ecc71;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #27ae60;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingLotApp()
    window.show()
    sys.exit(app.exec_())
