---
title: Phongtro VN
emoji: 🏠
colorFrom: orange
colorTo: indigo
sdk: gradio
sdk_version: 6.17.3
app_file: app.py
pinned: false
---

# AI Room Pricing - Hệ thống định giá Phòng trọ Việt Nam

Hệ thống ứng dụng thuật toán Học máy nâng cao nhằm dự báo và ước lượng đơn giá thuê bất động sản cư trú (Phòng trọ, Chung cư mini, Căn hộ dịch vụ, Nhà nguyên căn) theo thời gian thực cho 63 tỉnh/thành phố tại Việt Nam.

Đồ án thực nghiệm phục vụ học phần: **Ứng dụng học máy trong thiết kế** — Chuyên ngành Thiết kế Công nghiệp và Đồ họa, Trường Đại học Công nghệ (VNU-UET).

---

## Tính năng cốt lõi

- **Thu thập & Tối ưu dữ liệu:** Cơ chế cào dữ liệu tự động từ các nền tảng trực tuyến lớn.
- **Kỹ nghệ đặc trưng:** Trích xuất tự động ma trận 8 biến chỉ báo tiện ích nhị phân (`Điều hòa`, `Wifi`, `Thang máy`, `Vệ sinh khép kín`, `Khu bếp riêng`, `An ninh`, `Chỗ để xe`, `Ban công`) từ chuỗi văn bản thô.
- **Phân tầng vĩ mô (Tier Heuristics):** Phân hóa 63 Tỉnh/Thành phố thành 4 phân tầng đô thị (Tier 1 đến Tier 4) để tối ưu hóa trọng số thuật toán.
- **Mô hình cốt lõi:** Kiến trúc cấu trúc cây quyết định tăng cường độ dốc nâng cao (**LightGBM**) được tinh chỉnh siêu tham số tự động bằng framework **Optuna**.
- **Giao diện UI/UX Dashboard:** Ứng dụng giao diện tương tác trực quan cao cấp, tối ưu hóa trải nghiệm người dùng.

---

## Thông số hiệu năng mô hình

Qua tiến trình thực nghiệm nghiêm ngặt trên tập dữ liệu được phân tách độc lập theo tỷ lệ **85% Train : 15% Test**, mô hình đạt được các chỉ số tối ưu:

- **Hệ số xác định ($R^2$):** `0.865` (Mô hình giải thích được 86.5% sự biến động của giá thị trường).
- **Sai số tuyệt đối trung bình (MAE):** `± 0.36` Triệu VNĐ/tháng.

---

## Hướng dẫn cài đặt & Chạy cục bộ (Local Deployment)

1 . Tải mã nguồn về máy tính
```bash
git clone [https://github.com/username/phongtro-vn.git](https://github.com/username/phongtro-vn.git)
cd phongtro-vn
2 . Cài đặt môi trường và các thư viện phụ thuộc
pip install -r requirements.txt
3 . Khởi chạy ứng dụng Web giao diện Gradio
python app.py
Link Deploy ứng dụng lên Hugging Face Spaces
https://huggingface.co/spaces/Quex1/Phongtro-vn2
