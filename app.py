"""
Dự đoán giá phòng trọ Việt Nam — Hugging Face Spaces
Compatible với Gradio 6.x (HF default)
"""

import numpy as np
import pandas as pd
import gradio as gr
import joblib
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# 63 TỈNH/TP
# ─────────────────────────────────────────────────────────────────────────────
PROVINCES = {
    "Hà Nội":             {"tier": 1, "base": 4.2},
    "TP. Hồ Chí Minh":   {"tier": 1, "base": 4.6},
    "Đà Nẵng":            {"tier": 2, "base": 3.2},
    "Hải Phòng":          {"tier": 2, "base": 2.8},
    "Cần Thơ":            {"tier": 2, "base": 2.5},
    "Bình Dương":         {"tier": 2, "base": 3.0},
    "Đồng Nai":           {"tier": 2, "base": 2.6},
    "Khánh Hòa":          {"tier": 2, "base": 2.8},
    "Thừa Thiên Huế":     {"tier": 2, "base": 2.3},
    "Quảng Nam":          {"tier": 2, "base": 2.2},
    "Lâm Đồng":           {"tier": 2, "base": 2.4},
    "Bà Rịa - Vũng Tàu": {"tier": 2, "base": 2.7},
    "Long An":            {"tier": 2, "base": 2.2},
    "Bình Thuận":         {"tier": 2, "base": 2.1},
    "Nghệ An":            {"tier": 3, "base": 1.8},
    "Thanh Hóa":          {"tier": 3, "base": 1.7},
    "Hà Tĩnh":            {"tier": 3, "base": 1.6},
    "Quảng Bình":         {"tier": 3, "base": 1.5},
    "Quảng Trị":          {"tier": 3, "base": 1.5},
    "Quảng Ngãi":         {"tier": 3, "base": 1.6},
    "Bình Định":          {"tier": 3, "base": 1.8},
    "Phú Yên":            {"tier": 3, "base": 1.6},
    "Ninh Thuận":         {"tier": 3, "base": 1.5},
    "Đắk Lắk":            {"tier": 3, "base": 1.7},
    "Đắk Nông":           {"tier": 3, "base": 1.5},
    "Gia Lai":            {"tier": 3, "base": 1.6},
    "Kon Tum":            {"tier": 3, "base": 1.4},
    "Bình Phước":         {"tier": 3, "base": 1.7},
    "Tây Ninh":           {"tier": 3, "base": 1.8},
    "Tiền Giang":         {"tier": 3, "base": 1.9},
    "Bến Tre":            {"tier": 3, "base": 1.6},
    "Vĩnh Long":          {"tier": 3, "base": 1.7},
    "Trà Vinh":           {"tier": 3, "base": 1.5},
    "Đồng Tháp":          {"tier": 3, "base": 1.7},
    "An Giang":           {"tier": 3, "base": 1.7},
    "Hậu Giang":          {"tier": 3, "base": 1.5},
    "Sóc Trăng":          {"tier": 3, "base": 1.5},
    "Bạc Liêu":           {"tier": 3, "base": 1.5},
    "Cà Mau":             {"tier": 3, "base": 1.5},
    "Kiên Giang":         {"tier": 3, "base": 1.8},
    "Hải Dương":          {"tier": 3, "base": 2.0},
    "Hưng Yên":           {"tier": 3, "base": 2.0},
    "Bắc Ninh":           {"tier": 3, "base": 2.2},
    "Vĩnh Phúc":          {"tier": 3, "base": 2.0},
    "Thái Nguyên":        {"tier": 3, "base": 1.8},
    "Nam Định":           {"tier": 3, "base": 1.7},
    "Ninh Bình":          {"tier": 3, "base": 1.7},
    "Hà Nam":             {"tier": 3, "base": 1.8},
    "Thái Bình":          {"tier": 3, "base": 1.6},
    "Lào Cai":            {"tier": 4, "base": 1.4},
    "Yên Bái":            {"tier": 4, "base": 1.3},
    "Phú Thọ":            {"tier": 4, "base": 1.5},
    "Tuyên Quang":        {"tier": 4, "base": 1.3},
    "Hà Giang":           {"tier": 4, "base": 1.2},
    "Cao Bằng":           {"tier": 4, "base": 1.2},
    "Bắc Kạn":            {"tier": 4, "base": 1.2},
    "Lạng Sơn":           {"tier": 4, "base": 1.3},
    "Quảng Ninh":         {"tier": 4, "base": 2.0},
    "Bắc Giang":          {"tier": 4, "base": 1.8},
    "Sơn La":             {"tier": 4, "base": 1.3},
    "Hòa Bình":           {"tier": 4, "base": 1.4},
    "Điện Biên":          {"tier": 4, "base": 1.2},
    "Lai Châu":           {"tier": 4, "base": 1.1},
}

PROVINCE_LIST = sorted(PROVINCES.keys())
CATEGORY_LIST = ["Phòng trọ", "Chung cư mini", "Căn hộ", "Nhà nguyên căn"]
BOOL_COLS = ["has_ac","has_wifi","has_parking","has_security",
             "has_wc_rieng","has_kitchen","has_balcony","has_elevator"]
FEATURE_COLS = [
    "area_m2","log_area","city_tier","amenity_count","area_x_tier","category_enc",
    "has_ac","has_wifi","has_parking","has_security",
    "has_wc_rieng","has_kitchen","has_balcony","has_elevator",
]
CAT_MAP = {"Phòng trọ":1,"Chung cư mini":2,"Căn hộ":3,"Nhà nguyên căn":4}
TIER_LABEL = {1:"Đô thị đặc biệt",2:"Đô thị lớn",3:"Tỉnh trung bình",4:"Miền núi/xa"}

# ── Load ML model nếu có ──────────────────────────────────────────────────────
MODEL, FEAT_NAMES = None, None
if Path("best_model.pkl").exists():
    try:
        pkg = joblib.load("best_model.pkl")
        MODEL, FEAT_NAMES = pkg["model"], pkg["features"]
        print(" Loaded ML model")
    except Exception as e:
        print(f"⚠️ Cannot load model: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# PREDICT
# ─────────────────────────────────────────────────────────────────────────────
def predict(province, category, area,
            has_ac, has_wifi, has_parking, has_security,
            has_wc_rieng, has_kitchen, has_balcony, has_elevator):

    bools = [int(b) for b in [has_ac, has_wifi, has_parking, has_security,
                                has_wc_rieng, has_kitchen, has_balcony, has_elevator]]
    info  = PROVINCES.get(province, {"tier": 3, "base": 1.8})
    tier  = info["tier"]

    if MODEL and FEAT_NAMES:
        row = {
            "area_m2": area, "log_area": np.log1p(area),
            "city_tier": tier, "amenity_count": sum(bools),
            "area_x_tier": area * tier, "category_enc": CAT_MAP.get(category, 2),
            "has_ac": bools[0], "has_wifi": bools[1], "has_parking": bools[2],
            "has_security": bools[3], "has_wc_rieng": bools[4],
            "has_kitchen": bools[5], "has_balcony": bools[6], "has_elevator": bools[7],
        }
        X = pd.DataFrame([row])[FEAT_NAMES].fillna(0)
        price  = float(np.expm1(MODEL.predict(X)[0]))
        method = " ML Model (XGBoost/LightGBM)"
    else:
        cat_mult = {"Phòng trọ":0.70,"Chung cư mini":1.00,"Căn hộ":1.65,"Nhà nguyên căn":2.20}
        amenity_bonus = (bools[0]*0.25 + bools[1]*0.10 + bools[2]*0.15 + bools[3]*0.10 +
                         bools[4]*0.20 + bools[5]*0.12 + bools[6]*0.15 + bools[7]*0.30)
        price  = max(0.3, info["base"] * cat_mult.get(category, 1.0)
                         + (area - 25) * 0.045 + amenity_bonus)
        method = " Heuristic (chưa có model)"

    price = round(price, 2)
    lo, hi = round(price * 0.85, 2), round(price * 1.15, 2)

    return f"""##  {price:.2f} triệu VNĐ / tháng
**Khoảng dao động:** {lo:.2f} – {hi:.2f} triệu/tháng
---
| Thông tin | Chi tiết |
|-----------|----------|
| Tỉnh/TP | {province} |
| Tier đô thị | Tier {tier} — {TIER_LABEL[tier]} |
| Loại hình | {category} |
| Diện tích | {area} m² |
| Tiện ích | {sum(bools)}/8 |
| Phương pháp | {method} |
"""


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────
with gr.Blocks(title="Dự đoán giá phòng trọ VN") as demo:
    gr.Markdown("""
# 🏠 Dự đoán giá phòng trọ Việt Nam
Ước tính giá thuê hàng tháng cho **63 tỉnh/thành phố**. Kết quả mang tính tham khảo (±15%).
""")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📍 Vị trí & loại hình")
            province = gr.Dropdown(choices=PROVINCE_LIST, value="Hà Nội",
                                   label="Tỉnh/Thành phố")
            category = gr.Dropdown(choices=CATEGORY_LIST, value="Phòng trọ",
                                   label="Loại hình")
            area     = gr.Slider(minimum=8, maximum=200, value=25, step=1,
                                 label="Diện tích (m²)")

            gr.Markdown("### ✅ Tiện ích")
            with gr.Row():
                has_ac       = gr.Checkbox(label=" Điều hoà",  value=False)
                has_wifi     = gr.Checkbox(label=" Wifi",       value=True)
            with gr.Row():
                has_parking  = gr.Checkbox(label=" Đỗ xe",     value=False)
                has_security = gr.Checkbox(label=" Bảo vệ",    value=False)
            with gr.Row():
                has_wc_rieng = gr.Checkbox(label=" WC riêng",  value=True)
                has_kitchen  = gr.Checkbox(label=" Bếp",       value=False)
            with gr.Row():
                has_balcony  = gr.Checkbox(label=" Ban công",   value=False)
                has_elevator = gr.Checkbox(label=" Thang máy",  value=False)

            btn = gr.Button("🔍 Dự đoán giá", variant="primary")

        with gr.Column():
            gr.Markdown("###  Kết quả")
            output = gr.Markdown(value="*Điền thông tin rồi nhấn **Dự đoán giá***")

            gr.Examples(
                examples=[
                    ["Hà Nội",          "Phòng trọ",     20, True,  True,  False, False, True,  True,  False, False],
                    ["TP. Hồ Chí Minh", "Chung cư mini", 35, True,  True,  True,  True,  True,  True,  False, False],
                    ["Đà Nẵng",         "Căn hộ",        60, True,  True,  True,  True,  True,  True,  True,  True ],
                    ["Thái Nguyên",     "Phòng trọ",     22, False, True,  False, False, False, True,  False, False],
                    ["Lai Châu",        "Phòng trọ",     15, False, False, False, False, False, False, False, False],
                ],
                inputs=[province, category, area,
                        has_ac, has_wifi, has_parking, has_security,
                        has_wc_rieng, has_kitchen, has_balcony, has_elevator],
                outputs=output,
                fn=predict,
                label="Ví dụ mẫu — click để thử",
            )

    gr.Markdown("""
---
| Tier | Khu vực | Giá tham khảo |
|------|---------|---------------|
|  Tier 1 | Hà Nội, TP. HCM | 3.5 – 8+ triệu/tháng |
|  Tier 2 | Đà Nẵng, Hải Phòng, Bình Dương… | 2.0 – 4.5 triệu/tháng |
|  Tier 3 | Các tỉnh đồng bằng | 1.3 – 2.5 triệu/tháng |
|  Tier 4 | Miền núi, biên giới | 0.8 – 1.6 triệu/tháng |
""")

    inputs = [province, category, area,
              has_ac, has_wifi, has_parking, has_security,
              has_wc_rieng, has_kitchen, has_balcony, has_elevator]

    btn.click(fn=predict, inputs=inputs, outputs=output)
    for inp in inputs:
        inp.change(fn=predict, inputs=inputs, outputs=output)


if __name__ == "__main__":
    demo.launch()
