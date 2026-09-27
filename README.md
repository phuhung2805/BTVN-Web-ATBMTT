# BÀI TẬP LỚN LIÊN MÔN: LẬP TRÌNH WEB & AN TOÀN BẢO MẬT THÔNG TIN

Dự án bao gồm trọn bộ mã nguồn, cấu hình hệ thống và tài liệu báo cáo kỹ thuật cho 2 học phần: **Lập Trình Web** và **An Toàn và Bảo Mật Thông Tin (ATBMTT)**.

---

## CẤU TRÚC DỰ ÁN

```text
BTVN-Web-ATBMTT/
├── LapTrinhWeb/
│   ├── docker-compose.yml       # Cấu hình 5 container: Nginx, Node-RED, MariaDB, phpMyAdmin, Cloudflared
│   ├── nodered_flows.json       # Luồng Node-RED cung cấp API /api/tacke
│   ├── nginx/
│   │   └── conf.d/
│   │       └── default.conf     # Virtual Hosts (domain1.local & domain2.local) + Reverse Proxy + CORS
│   ├── web1/
│   │   └── index.html           # Website 1: Giao diện bảng danh sách sinh viên qua fetch() API
│   └── web2/
│       └── index.html           # Website 2: Landing Page chứng minh đa tên miền Nginx
└── ATBMTT/
    ├── aes_demo.py              # Chương trình Python demo AES-CBC (128/256-bit, PKCS#7, IV, Avalanche)
    └── BAOCAO_ATBMTT.md         # Báo cáo kỹ thuật chi tiết DES, AES, RSA và Mô hình Mã hóa lai
```

---

## HƯỚNG DẪN KHỞI CHẠY VÀ THỬ NGHIỆM

### PHẦN 1: MÔN LẬP TRÌNH WEB (DOCKER COMPOSE)

#### 1. Cấu hình tên miền cục bộ (Local Hosts)
Thêm các dòng sau vào tệp tin hosts máy chủ để thử nghiệm Virtual Hosts:
- **Windows:** `C:\Windows\System32\drivers\etc\hosts` (Mở bằng Notepad quyền Run as Administrator)
- **Linux / macOS:** `/etc/hosts`

```text
127.0.0.1   domain1.local
127.0.0.1   domain2.local
```

#### 2. Khởi chạy cụm dịch vụ Docker
Di chuyển vào thư mục `LapTrinhWeb` và chạy:
```bash
cd LapTrinhWeb
docker compose up -d
```

Các dịch vụ sẽ lắng nghe tại:
- **Web 1 (Quản lý SV & API):** [http://domain1.local](http://domain1.local) hoặc [http://localhost](http://localhost)
- **Web 2 (Landing Page Virtual Host):** [http://domain2.local](http://domain2.local)
- **Node-RED Editor:** [http://localhost:1880](http://localhost:1880)
- **phpMyAdmin:** [http://localhost:8080](http://localhost:8080) (User: `root`, Mật khẩu: `root_password_123`)

#### 3. Import Flow vào Node-RED
1. Truy cập [http://localhost:1880](http://localhost:1880).
2. Chọn menu góc trên bên phải $\rightarrow$ **Import**.
3. Chọn tệp `LapTrinhWeb/nodered_flows.json` hoặc dán trực tiếp nội dung JSON $\rightarrow$ Nhấn **Import** $\rightarrow$ Nhấn **Deploy**.
4. Mở [http://domain1.local](http://domain1.local) để xem danh sách sinh viên tự động hiển thị từ API `/api/tacke`.

---

### PHẦN 2: MÔN AN TOÀN VÀ BẢO MẬT THÔNG TIN

#### 1. Cài đặt thư viện yêu cầu (nếu chưa có)
```bash
pip install pycryptodome
```

#### 2. Chạy chương trình demo AES-CBC
```bash
python ATBMTT/aes_demo.py
```
Chương trình sẽ tự động thực thi minh họa chi tiết:
- Độ dài khóa AES-128 và AES-256.
- Quy trình đệm PKCS#7 (giá trị byte đệm, số lượng byte bổ sung).
- Vector khởi tạo ngẫu nhiên (IV 16 bytes).
- Đóng gói bản mã Base64 và Hex.
- Quy trình giải mã, kiểm tra tính toàn vẹn 100%.
- Thử nghiệm hiệu ứng tuyết lở (Avalanche Effect - thay đổi ~50% bit bản mã khi đổi 1 ký tự).

#### 3. Báo cáo kỹ thuật lý thuyết
Nội dung bài báo cáo chi tiết được biên soạn tại [BAOCAO_ATBMTT.md](file:///d:/BTVN-Web-ATBMTT/ATBMTT/BAOCAO_ATBMTT.md) gồm:
1. Chi tiết thuật toán mã hóa khối DES và AES (SubBytes, ShiftRows, MixColumns, AddRoundKey).
2. Nền tảng toán học và các bước sinh cặp khóa RSA (kèm ví dụ số học từng bước).
3. 3 mô hình ứng dụng RSA (Bảo mật cho người nhận, Xác thực/Chữ ký số cho người gửi, và Mô hình kết hợp song hành).
4. So sánh hiệu năng định lượng giữa RSA và AES.
5. Kiến trúc cơ chế Mã hóa lai (Hybrid Encryption / Digital Envelope) trong thực tiễn (HTTPS/TLS, PGP).