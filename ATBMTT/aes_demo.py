#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
CHƯƠNG TRÌNH DEMO THUẬT TOÁN MÃ HÓA KHỐI AES (CHẾ ĐỘ CBC)
Môn học: An toàn và Bảo mật Thông tin (ATBMTT)
Thư viện sử dụng: PyCryptodome (Crypto)
Các tính năng chính:
  1. Hỗ trợ độ dài khóa: AES-128 (16 bytes) và AES-256 (32 bytes)
  2. Cơ chế đệm dữ liệu: PKCS#7 (PKCS7 Padding) theo chuẩn RFC 5652
  3. Chế độ hoạt động: CBC (Cipher Block Chaining) với Vector khởi tạo (IV) ngẫu nhiên
  4. Trực quan hóa chi tiết từng bước: Khóa -> IV -> Padding -> Mã hóa -> Giải mã -> Unpadding
================================================================================
"""

import sys
import os
import base64
from typing import Tuple, Dict, Any

# Đảm bảo console Windows in chuẩn tiếng Việt UTF-8
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Đảm bảo tự động nạp thư viện PyCryptodome trên mọi môi trường
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    from Crypto.Util.Padding import pad, unpad
except ImportError:
    for fallback_path in [
        r"D:\msys64\mingw64\lib\python3.14\site-packages",
        r"D:\msys64\mingw64\lib\python3.12\site-packages"
    ]:
        if os.path.exists(fallback_path) and fallback_path not in sys.path:
            sys.path.append(fallback_path)
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    from Crypto.Util.Padding import pad, unpad


class AESCipherCBC:
    """
    Lớp xử lý Mã hóa và Giải mã AES chế độ CBC (Cipher Block Chaining)
    """

    def __init__(self, key: bytes):
        """
        Khởi tạo đối tượng AESCipherCBC với khóa bí mật.
        Độ dài khóa hợp lệ: 16 bytes (128-bit), 24 bytes (192-bit), 32 bytes (256-bit).
        """
        if len(key) not in (16, 24, 32):
            raise ValueError(f"Độ dài khóa không hợp lệ: {len(key)} bytes. Phải là 16 (128-bit) hoặc 32 (256-bit).")
        self.key = key
        self.key_size_bits = len(key) * 8
        self.block_size = AES.block_size  # Luôn là 16 bytes (128-bit) đối với thuật toán AES

    @staticmethod
    def generate_random_key(key_size_bits: int = 256) -> bytes:
        """
        Sinh khóa đối xứng giả ngẫu nhiên an toàn mật mã (CSPRNG)
        """
        if key_size_bits not in (128, 192, 256):
            raise ValueError("Kích thước khóa chỉ hỗ trợ 128, 192 hoặc 256 bits.")
        return get_random_bytes(key_size_bits // 8)

    def encrypt(self, plaintext: str) -> Dict[str, Any]:
        """
        Quy trình mã hóa văn bản gốc (Plaintext):
          Bước 1: Chuyển đổi chuỗi văn bản UTF-8 sang mảng byte.
          Bước 2: Thực hiện đệm (Padding) theo chuẩn PKCS#7 để độ dài dữ liệu là bội số của 16 bytes.
          Bước 3: Sinh Vector khởi tạo ngẫu nhiên (IV - Initialization Vector, 16 bytes).
          Bước 4: Khởi tạo bộ mã AES ở chế độ CBC với Key và IV.
          Bước 5: Thực hiện mã hóa (XOR từng khối với khối mã trước đó rồi qua hàm biến đổi AES).
          Bước 6: Trả về kết quả và định dạng hiển thị (Hex, Base64).
        """
        # Bước 1: Encode chuỗi sang UTF-8 bytes
        plaintext_bytes = plaintext.encode('utf-8')
        raw_length = len(plaintext_bytes)

        # Bước 2: PKCS#7 Padding
        padded_bytes = pad(plaintext_bytes, self.block_size, style='pkcs7')
        padded_length = len(padded_bytes)
        pad_bytes_count = padded_length - raw_length
        pad_byte_value = padded_bytes[-1]

        # Bước 3: Sinh IV ngẫu nhiên 16 bytes
        iv = get_random_bytes(self.block_size)

        # Bước 4: Khởi tạo Cipher
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        # Bước 5: Tiến hành mã hóa
        ciphertext = cipher.encrypt(padded_bytes)

        # Đóng gói kết quả
        return {
            "key_bytes": self.key,
            "key_hex": self.key.hex(),
            "key_b64": base64.b64encode(self.key).decode('ascii'),
            "iv_bytes": iv,
            "iv_hex": iv.hex(),
            "iv_b64": base64.b64encode(iv).decode('ascii'),
            "raw_length": raw_length,
            "padded_length": padded_length,
            "pad_bytes_count": pad_bytes_count,
            "pad_byte_value": pad_byte_value,
            "padded_hex": padded_bytes.hex(),
            "ciphertext_bytes": ciphertext,
            "ciphertext_hex": ciphertext.hex(),
            "ciphertext_b64": base64.b64encode(ciphertext).decode('ascii'),
            # Gói tin kết hợp phổ biến trong thực tế: IV ghép đầu bản mã
            "combined_b64": base64.b64encode(iv + ciphertext).decode('ascii')
        }

    def decrypt(self, ciphertext: bytes, iv: bytes) -> str:
        """
        Quy trình giải mã văn bản mã hóa (Ciphertext):
          Bước 1: Khởi tạo bộ giải mã AES chế độ CBC với cùng Key và IV ban đầu.
          Bước 2: Giải mã bản mã để thu được mảng byte đã đệm (Padded Bytes).
          Bước 3: Loại bỏ đệm PKCS#7 (Unpad) để khôi phục chính xác dữ liệu gốc.
          Bước 4: Giải mã UTF-8 mảng byte thành chuỗi ký tự ban đầu.
        """
        if len(iv) != self.block_size:
            raise ValueError(f"Độ dài IV không đúng chuẩn ({len(iv)} != {self.block_size} bytes)")

        # Bước 1: Khởi tạo bộ giải mã
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        # Bước 2: Giải mã CBC
        decrypted_padded_bytes = cipher.decrypt(ciphertext)

        # Bước 3: Unpad PKCS#7
        unpadded_bytes = unpad(decrypted_padded_bytes, self.block_size, style='pkcs7')

        # Bước 4: Decode UTF-8
        return unpadded_bytes.decode('utf-8')

    def decrypt_from_b64(self, ciphertext_b64: str, iv_b64: str) -> str:
        """Giải mã từ chuỗi định dạng Base64"""
        ciphertext = base64.b64decode(ciphertext_b64)
        iv = base64.b64decode(iv_b64)
        return self.decrypt(ciphertext, iv)

    def decrypt_combined_b64(self, combined_b64: str) -> str:
        """Giải mã từ chuỗi đóng gói (IV 16 bytes + Ciphertext) định dạng Base64"""
        combined = base64.b64decode(combined_b64)
        iv = combined[:self.block_size]
        ciphertext = combined[self.block_size:]
        return self.decrypt(ciphertext, iv)


def print_banner(title: str):
    line = "=" * 80
    print(f"\n{line}")
    print(f" {title.center(78)}")
    print(f"{line}")


def run_demonstration(key_size_bits: int, message: str):
    """
    Hàm thực thi minh họa trực quan quy trình mã hóa và giải mã
    """
    print_banner(f"MINH HỌA MÃ HÓA & GIẢI MÃ AES-{key_size_bits}-CBC")

    # 1. Sinh khóa
    key = AESCipherCBC.generate_random_key(key_size_bits)
    cipher = AESCipherCBC(key)

    print(f"[*] Cấu hình:")
    print(f"  - Thuật toán:       AES (Advanced Encryption Standard)")
    print(f"  - Chế độ mã hóa:    CBC (Cipher Block Chaining)")
    print(f"  - Kích thước khối:  {cipher.block_size} bytes (128 bits)")
    print(f"  - Độ dài khóa:      {cipher.key_size_bits} bits ({len(key)} bytes)")
    print(f"  - Khóa bí mật (Hex): {cipher.key.hex()}")
    print(f"  - Khóa bí mật (B64): {base64.b64encode(cipher.key).decode()}")

    # 2. Thông tin thông điệp gốc
    print(f"\n[1] Thông điệp gốc (Plaintext):")
    print(f"  - Nội dung:         \"{message}\"")
    raw_bytes = message.encode('utf-8')
    print(f"  - Độ dài byte gốc:  {len(raw_bytes)} bytes")
    print(f"  - Dạng Hex gốc:     {raw_bytes.hex()}")

    # 3. Quá trình mã hóa
    result = cipher.encrypt(message)

    print(f"\n[2] Quy trình Đệm (PKCS#7 Padding):")
    print(f"  - Kích thước khối yêu cầu:     16 bytes")
    print(f"  - Số byte đệm cần bổ sung:     {result['pad_bytes_count']} bytes")
    print(f"  - Giá trị mỗi byte đệm:        0x{result['pad_byte_value']:02x} ({result['pad_byte_value']} decimal)")
    print(f"  - Chiều dài sau khi đệm:       {result['padded_length']} bytes (chia hết cho 16)")
    print(f"  - Dữ liệu sau khi đệm (Hex):   {result['padded_hex']}")

    print(f"\n[3] Vector khởi tạo ngẫu nhiên (IV):")
    print(f"  - IV (16 bytes Hex):           {result['iv_hex']}")
    print(f"  - IV (Base64):                 {result['iv_b64']}")
    print(f"  * Vai trò: Đảm bảo cùng 1 bản rõ khi mã hóa nhiều lần sẽ sinh ra các bản mã hoàn toàn khác nhau.")

    print(f"\n[4] Kết quả Mã Hóa (Ciphertext):")
    print(f"  - Bản mã (Hex):                {result['ciphertext_hex']}")
    print(f"  - Bản mã (Base64):             {result['ciphertext_b64']}")
    print(f"  - Đóng gói chuẩn [IV + Cipher] (Base64):")
    print(f"    {result['combined_b64']}")

    # 4. Quá trình giải mã
    print(f"\n[5] Quy trình Giải Mã (Decryption):")
    decrypted_text = cipher.decrypt(result["ciphertext_bytes"], result["iv_bytes"])
    print(f"  - Thực hiện: AES-CBC Decrypt -> Kiểm tra & Bỏ đệm PKCS#7 -> Decode UTF-8")
    print(f"  - Kết quả giải mã:             \"{decrypted_text}\"")

    # 5. Kiểm tra tính toàn vẹn (Verification)
    is_matched = (message == decrypted_text)
    print(f"\n[6] Kiểm chứng tính đúng đắn:")
    print(f"  - Plaintext ban đầu == Decrypted text ? -> {is_matched}")
    if is_matched:
        print("  => KẾT QUẢ: THÀNH CÔNG! Dữ liệu được khôi phục nguyên vẹn 100%.")
    else:
        print("  => KẾT QUẢ: THẤT BẠI! Dữ liệu giải mã bị sai lệch.")

    # 6. Thử nghiệm tính chất hiệu ứng tuyết lở (Avalanche Effect)
    print(f"\n[7] Thử nghiệm tính chất chống phân tích mật mã (Avalanche Effect):")
    alt_message = message[:-1] + ("." if message[-1] != "." else "!")
    alt_result = cipher.encrypt(alt_message)
    print(f"  - Thay đổi chỉ 1 ký tự cuối:   \"{alt_message}\"")
    print(f"  - Bản mã mới (Hex):             {alt_result['ciphertext_hex']}")
    # So sánh số bit khác biệt
    xor_diff = int(result['ciphertext_hex'], 16) ^ int(alt_result['ciphertext_hex'], 16)
    diff_bits = bin(xor_diff).count('1')
    total_bits = len(result['ciphertext_bytes']) * 8
    print(f"  - Số bit bị thay đổi trong bản mã: {diff_bits}/{total_bits} bit ({diff_bits / total_bits * 100:.1f}%)")
    print(f"  => Hiệu ứng tuyết lở hoạt động tối ưu: Thay đổi nhỏ ở bản rõ làm thay đổi ~50% bản mã.")


def main():
    print("""
################################################################################
#                   BÀI TẬP LỚN AN TOÀN VÀ BẢO MẬT THÔNG TIN                   #
#                   DEMO THUẬT TOÁN MÃ HÓA KHỐI AES-CBC                       #
################################################################################
""")

    # Demo 1: AES-128 với chuỗi tiếng Việt có dấu
    sample_text_1 = "Học viện Công nghệ Bưu chính Viễn thông - PTIT. Môn An toàn và Bảo mật thông tin!"
    run_demonstration(key_size_bits=128, message=sample_text_1)

    # Demo 2: AES-256 với chuỗi cấu trúc dữ liệu JSON
    sample_text_2 = '{"student_id": "B21DCCN001", "fullname": "Nguyễn Văn A", "status": "Passed"}'
    run_demonstration(key_size_bits=256, message=sample_text_2)

    print("\n" + "=" * 80)
    print(" HOÀN TẤT DEMO MÃ HÓA AES-CBC".center(80))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
