# BÀI TẬP LỚN LIÊN MÔN: LẬP TRÌNH WEB & AN TOÀN BẢO MẬT THÔNG TIN

Dự án bao gồm trọn bộ mã nguồn, cấu hình hệ thống và tài liệu báo cáo kỹ thuật cho 2 học phần: **Lập Trình Web** và **An Toàn và Bảo Mật Thông Tin (ATBMTT)**.

---

## CẤU TRÚC DỰ ÁN

```text
BTVN-Web-ATBMTT/
├── LapTrinhWeb/
│   ├── docker-compose.yml          # 5 container: Nginx, Node-RED, MariaDB, phpMyAdmin, Cloudflared
│   ├── .env.example                # Mẫu file .env (không bắt buộc): 2 domain + token Cloudflare
│   ├── nodered_flows.json          # Flow Node-RED: http in -> function (thuật toán) -> http response
│   ├── nodered/
│   │   ├── api_tacke.js            # Mã nguồn thuật toán API (bản dễ đọc của function node)
│   │   ├── build_flows.js          # Sinh lại nodered_flows.json từ api_tacke.js
│   │   └── test_api.js             # Test thuật toán bằng Node.js, không cần Docker
│   ├── nginx/
│   │   └── templates/
│   │       └── default.conf.template  # 2 Virtual Host (DOMAIN1, DOMAIN2) + Reverse Proxy /api/ + CORS
│   ├── web1/index.html             # Website 1: gọi API /api/tacke bằng fetch() và hiển thị kết quả
│   ├── web2/index.html             # Website 2: landing page chứng minh đa tên miền
│   └── docs/images/                # Ảnh chụp minh chứng (xem danh sách bên dưới)
└── ATBMTT/
    ├── aes_demo.py                 # Demo AES-CBC (128/256-bit, PKCS#7, IV, Avalanche)
    └── BAOCAO_ATBMTT.md            # Báo cáo DES, AES, RSA và mã hóa lai
```

---

## PHẦN 1: MÔN LẬP TRÌNH WEB

### Đối chiếu với đề bài

| Đề bài | Đã làm | Ở đâu |
|---|---|---|
| **BT1.1** Giả lập Linux (Hyper-V / VirtualBox / VMware / WSL) | Ubuntu 24.04 trên WSL2 (hoặc máy ảo VMware/VirtualBox) | [Bước 1](#bước-1-giả-lập-linux) |
| **BT1.2** Cài docker compose trên Linux đó | Docker Engine + plugin `docker compose` | [Bước 2](#bước-2-cài-docker-và-docker-compose-trên-ubuntu) |
| **BT1.3** nginx, nodered, mariadb, phpmyadmin, cloudflared | Đủ 5 dịch vụ trong `docker-compose.yml`. Cloudflared mặc định dùng Quick Tunnel (không cần domain), có sẵn chế độ domain thật | [Bước 3](#bước-3-chạy-5-dịch-vụ-bằng-docker-compose), [Bước 4](#bước-4-đưa-web-ra-internet-bằng-cloudflared) |
| **BT1.4** Nginx chạy 2 website với 2 domain khác nhau | 2 `server` block: `web1.localhost` → `web1/`, `web2.localhost` → `web2/` (đổi được sang domain thật) | `nginx/templates/default.conf.template` |
| **BT2.1** Node-RED: http in + http response tạo API | `GET`/`POST /api/tacke` → function → http response | `nodered_flows.json` |
| **BT2.2** Nginx cho web gọi được API, thuật toán tự nghĩ | `location /api/` proxy tới `nodered:1880`; thuật toán chia tiền + chuyển khoản tối thiểu | [Bài tập 2](#bài-tập-2-api-apitacke) |
| **BT2.3** Code JS trong HTML gọi API | `fetch('/api/tacke?...')` trong `web1/index.html` | `web1/index.html` |

---

### Bước 1: Giả lập Linux

**Cách A, WSL2 (khuyên dùng trên Windows 10/11).** WSL2 cần tính năng *Virtual Machine Platform* của Windows và ảo hóa (VT-x) bật trong BIOS. Mở PowerShell bằng quyền **Administrator**:

```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
```

Khởi động lại máy, rồi cài Ubuntu (bỏ qua nếu đã có):

```powershell
wsl --install -d Ubuntu-24.04
```

Mở **Ubuntu** từ Start Menu và tạo user/mật khẩu. Kiểm tra:

```bash
wsl -l -v          # (chạy trong PowerShell) phải thấy Ubuntu, VERSION 2, chạy được không báo lỗi
lsb_release -a     # (chạy trong Ubuntu) Ubuntu 24.04 LTS
```

> Nếu `wsl` báo `HCS_E_SERVICE_NOT_AVAILABLE` / *a required feature is not installed* nghĩa là chưa bật *Virtual Machine Platform*. Chạy 2 lệnh `dism` ở trên rồi khởi động lại.

**Cách B, VMware / VirtualBox / Hyper-V:** tạo máy ảo 2 CPU, 4 GB RAM, 25 GB ổ, cài từ file ISO Ubuntu Server 24.04. Card mạng để chế độ *Bridged* (hoặc NAT và forward cổng 80, 1880, 8080) để máy thật truy cập được.

### Bước 2: Cài Docker và docker compose trên Ubuntu

```bash
sudo apt update && sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER   # đăng xuất / vào lại để dùng docker không cần sudo
docker --version
docker compose version
```

### Bước 3: Chạy 5 dịch vụ bằng docker compose

```bash
git clone https://github.com/phuhung2805/BTVN-Web-ATBMTT.git
cd BTVN-Web-ATBMTT/LapTrinhWeb
docker compose up -d    # không cần file .env, mặc định dùng web1.localhost / web2.localhost
docker compose ps       # nginx, nodered, mariadb, phpmyadmin, cloudflared, cloudflared-web2 đều "running"
```

| Dịch vụ | Địa chỉ |
|---|---|
| Web 1 (gọi API) | `http://web1.localhost` (hoặc `http://localhost`) |
| Web 2 (landing page) | `http://web2.localhost` |
| Node-RED | `http://localhost:1880` |
| phpMyAdmin | `http://localhost:8080` (root / `root_password_123`) |

**Vì sao không cần mua domain, không cần sửa file hosts?** Mọi tên miền đuôi `.localhost` được chuẩn hóa (RFC 6761) để luôn trỏ về chính máy mình. Chrome, Edge, Firefox tự hiểu `web1.localhost`, `web2.localhost` là `127.0.0.1`. Nginx thấy 2 header `Host` khác nhau nên trả về 2 website khác nhau, đúng yêu cầu BT1.4.

**Import flow Node-RED:** mở `http://localhost:1880` → menu ☰ → **Import** → chọn `LapTrinhWeb/nodered_flows.json` → **Import** → **Deploy**.

**Kiểm tra bằng dòng lệnh:**

```bash
curl -H "Host: web1.localhost" http://localhost/        # trả về Web 1
curl -H "Host: web2.localhost" http://localhost/        # trả về Web 2
curl http://localhost/api/tacke                         # JSON {"ok":1,...} từ Node-RED qua Nginx
```

### Bước 4: Đưa web ra Internet bằng cloudflared

**Cách A, Quick Tunnel (mặc định, không cần domain, không cần tài khoản).** Hai container `cloudflared` và `cloudflared-web2` tự tạo 2 địa chỉ public ngẫu nhiên dạng `https://xxxx.trycloudflare.com`:

```bash
docker compose logs cloudflared cloudflared-web2 | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com'
```

Địa chỉ thứ nhất mở ra Web 1, thứ hai mở ra Web 2 (cloudflared gắn header `Host` = `DOMAIN1`/`DOMAIN2` để nginx chọn đúng website). Gửi 2 link này cho thầy là xem được từ bất kỳ đâu. Mỗi lần khởi động lại container thì link đổi.

**Cách B, domain thật (nếu có).**

1. Thêm domain vào **Cloudflare** (Add a site) và chuyển nameserver về Cloudflare.
2. Vào **Cloudflare Zero Trust → Networks → Tunnels → Create a tunnel → Cloudflared**, copy **token**.
3. Trong tab **Public Hostname** của tunnel, thêm 2 dòng `web1.tenmiencuaban.com` và `web2.tenmiencuaban.com`, cả hai là `HTTP` → `nginx:80`.
4. Tạo file `.env` (`cp .env.example .env`), điền `CLOUDFLARE_TUNNEL_TOKEN`, `DOMAIN1=web1.tenmiencuaban.com`, `DOMAIN2=web2.tenmiencuaban.com`, rồi chạy:

```bash
docker compose --profile domain-that up -d
docker compose logs cloudflared-named      # phải có "Registered tunnel connection"
```

---

### Bài tập 2: API `/api/tacke`

**Luồng:** Trình duyệt → `http://web1.localhost/api/tacke` → Nginx (`location /api/`) → `http://nodered:1880/api/tacke` → node **http in** → node **function** (thuật toán) → node **http response**.

**Thuật toán "tách kè" (chia tiền quỹ lớp)**, mã nguồn ở `nodered/api_tacke.js`:

1. Mỗi sinh viên đã chi một số tiền `money`. Tính tổng, trung bình, trung vị, cao nhất, thấp nhất.
2. Tính `chenhlech = money - trung bình`. Số dương là được nhận lại, số âm là phải đóng thêm.
3. Tìm danh sách chuyển khoản để mọi người chi bằng nhau với **ít giao dịch**: thuật toán tham lam ghép người nợ nhiều nhất với người được nhận nhiều nhất, lặp đến khi hết. Số giao dịch luôn ≤ n − 1. Tính toán dùng số nguyên (xu × n) nên không sai số làm tròn.
4. Xếp hạng theo tiền, ai bằng tiền thì đồng hạng (1, 2, 2, 4).
5. Lọc theo tên **không dấu** (`q=nguyen` khớp "Nguyễn"), theo khoảng tiền, sắp xếp, lấy top N.
6. Kiểm tra đầu vào. Dữ liệu sai thì trả HTTP 400 với `{"ok":0,"msg":"<lý do>","dssv":[]}`.

**Tham số:**

| Tham số | Ý nghĩa | Ví dụ |
|---|---|---|
| `sort` | `desc` (mặc định), `asc`, `name` | `?sort=asc` |
| `q` | tìm theo tên, không phân biệt dấu | `?q=nguyen` |
| `min`, `max` | lọc khoảng tiền | `?min=100&max=300` |
| `top` | chỉ lấy N người đầu | `?top=3` |
| `POST` body | tự gửi danh sách | `{"dssv":[{"name":"A","money":100}]}` |

**Phản hồi** (giữ đúng khung đề bài, thêm trường mở rộng):

```json
{
  "ok": 1,
  "msg": "thành công",
  "dssv": [
    {"name": "David", "money": 456, "hang": 2, "chenhlech": 218.5},
    {"name": "Cốp",   "money": 123, "hang": 6, "chenhlech": -114.5}
  ],
  "thongke": {"soluong": 8, "sotrave": 8, "tong": 1900, "trungbinh": 237.5, "trungvi": 210, "caonhat": 512, "thapnhat": 0},
  "chuyenkhoan": [{"tu": "Cốp", "den": "David", "sotien": 107}]
}
```

```bash
curl "http://localhost/api/tacke?top=3"
curl -X POST http://localhost/api/tacke -H "Content-Type: application/json" \
     -d '{"dssv":[{"name":"An","money":100},{"name":"Bình","money":0},{"name":"Châu","money":50}]}'
```

**Test thuật toán không cần Docker:**

```bash
node LapTrinhWeb/nodered/test_api.js
```

Khi sửa `nodered/api_tacke.js`, chạy `node LapTrinhWeb/nodered/build_flows.js` để cập nhật `nodered_flows.json`, rồi import lại vào Node-RED.

---

### Ảnh chụp minh chứng

Lưu ảnh vào `LapTrinhWeb/docs/images/` với đúng tên dưới đây để hiện trong README:

| # | Nội dung cần chụp | Ảnh |
|---|---|---|
| 1 | `wsl -l -v` + `lsb_release -a` (hoặc màn hình máy ảo Ubuntu) | ![](LapTrinhWeb/docs/images/01-linux.png) |
| 2 | `docker --version` + `docker compose version` | ![](LapTrinhWeb/docs/images/02-docker.png) |
| 3 | `docker compose ps`: 5 container đang chạy | ![](LapTrinhWeb/docs/images/03-compose-ps.png) |
| 4 | `docker compose logs` hiện 2 link trycloudflare (hoặc Tunnel *Healthy* nếu dùng domain thật) | ![](LapTrinhWeb/docs/images/04-cloudflare.png) |
| 5 | Trình duyệt mở `http://web1.localhost` / link trycloudflare 1 (Web 1 có dữ liệu API) | ![](LapTrinhWeb/docs/images/05-web1.png) |
| 6 | Trình duyệt mở `http://web2.localhost` / link trycloudflare 2 (Web 2) | ![](LapTrinhWeb/docs/images/06-web2.png) |
| 7 | Flow Node-RED (http in → function → http response) | ![](LapTrinhWeb/docs/images/07-nodered.png) |
| 8 | phpMyAdmin đăng nhập vào MariaDB | ![](LapTrinhWeb/docs/images/08-phpmyadmin.png) |

---

## PHẦN 2: MÔN AN TOÀN VÀ BẢO MẬT THÔNG TIN

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
Nội dung bài báo cáo chi tiết được biên soạn tại [BAOCAO_ATBMTT.md](ATBMTT/BAOCAO_ATBMTT.md) gồm:
1. Chi tiết thuật toán mã hóa khối DES và AES (SubBytes, ShiftRows, MixColumns, AddRoundKey).
2. Nền tảng toán học và các bước sinh cặp khóa RSA (kèm ví dụ số học từng bước).
3. 3 mô hình ứng dụng RSA (Bảo mật cho người nhận, Xác thực/Chữ ký số cho người gửi, và Mô hình kết hợp song hành).
4. So sánh hiệu năng định lượng giữa RSA và AES.
5. Kiến trúc cơ chế Mã hóa lai (Hybrid Encryption / Digital Envelope) trong thực tiễn (HTTPS/TLS, PGP).
