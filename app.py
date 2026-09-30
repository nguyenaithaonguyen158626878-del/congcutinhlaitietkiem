
import streamlit as st
import pandas as pd

# =========================
# CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="Tính lãi gửi tiết kiệm",
    page_icon="🏦",
    layout="centered"
)

st.title("🏦 CÔNG CỤ TÍNH LÃI TIẾT KIỆM")
st.caption("Tính lãi đơn và lãi kép theo kỳ hạn gửi")

# =========================
# HÀM ĐỊNH DẠNG TIỀN
# =========================
def vnd(number):
    return f"{number:,.0f} VNĐ".replace(",", ".")

# =========================
# NHẬP THÔNG TIN
# =========================
st.subheader("1. Thông tin tiền gửi")

with st.form("deposit_form"):
    principal = st.number_input(
        "Số tiền gửi (VNĐ)",
        min_value=0,
        value=100_000_000,
        step=10_000_000,
        format="%d"
    )

    col1, col2 = st.columns(2)

    with col1:
        term = st.number_input(
            "Kỳ hạn gửi (tháng)",
            min_value=1,
            max_value=600,
            value=12,
            step=1
        )

    with col2:
        rate = st.number_input(
            "Lãi suất (%/năm)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.1,
            format="%.2f"
        )

    interest_type = st.selectbox(
        "Hình thức tính lãi",
        ["Lãi đơn", "Lãi kép"]
    )

    payout = st.selectbox(
        "Hình thức nhận lãi",
        [
            "Lãnh lãi theo tháng",
            "Lãnh lãi theo quý",
            "Lãnh lãi cuối kỳ"
        ]
    )

    submitted = st.form_submit_button(
        "🧮 TÍNH TIỀN LÃI",
        type="primary",
        use_container_width=True
    )

# =========================
# TÍNH TOÁN
# =========================
if submitted:
    if principal <= 0:
        st.error("Vui lòng nhập số tiền gửi lớn hơn 0.")
    else:
        r = rate / 100
        months = int(term)

        # Xác định chu kỳ trả lãi / ghép lãi
        if payout == "Lãnh lãi theo tháng":
            period_months = 1
        elif payout == "Lãnh lãi theo quý":
            period_months = 3
        else:
            period_months = months

        # Các mốc trả lãi trong kỳ hạn
        dates = list(range(period_months, months + 1, period_months))
        if not dates or dates[-1] != months:
            dates.append(months)

        # Tính lãi từng kỳ
        balance = float(principal)
        total_interest = 0.0
        rows = []
        previous_month = 0

        for month in dates:
            duration = month - previous_month
            period_rate = r * duration / 12

            if interest_type == "Lãi đơn":
                interest = principal * period_rate
            else:
                interest = balance * (
                    (1 + r / 12) ** duration - 1
                )

            total_interest += interest

            # Lãi kép: tái đầu tư lãi sau mỗi kỳ,
            # trừ kỳ cuối khi nhận lãi và tất toán.
            if interest_type == "Lãi kép" and month < months:
                balance += interest

            rows.append({
                "Tháng": month,
                "Số tháng kỳ này": duration,
                "Tiền lãi kỳ này": interest,
                "Lãi lũy kế": total_interest,
                "Số dư gốc + lãi": (
                    balance if month < months else
                    principal + total_interest
                    if interest_type == "Lãi đơn"
                    else balance + interest
                )
            })

            previous_month = month

        # Tổng kết
        final_interest = total_interest
        final_amount = principal + final_interest

        st.divider()
        st.subheader("2. Kết quả tính toán")

        c1, c2 = st.columns(2)
        with c1:
            st.metric(
                "Tổng tiền lãi",
                vnd(final_interest)
            )
        with c2:
            st.metric(
                "Tổng gốc và lãi",
                vnd(final_amount)
            )

        # Tiền lãi định kỳ: hiển thị kỳ đầu tiên
        first_interest = rows[0]["Tiền lãi kỳ này"]
        st.info(
            f"**Tiền lãi kỳ đầu tiên:** {vnd(first_interest)}"
        )

        st.write("**Thông tin khoản gửi**")
        st.write(f"- Số tiền gốc: {vnd(principal)}")
        st.write(f"- Kỳ hạn: {months} tháng")
        st.write(f"- Lãi suất: {rate:.2f}%/năm")
        st.write(f"- Cách tính: {interest_type}")
        st.write(f"- Nhận lãi: {payout}")

        # Bảng chi tiết
        st.subheader("3. Chi tiết lãi theo kỳ")

        df = pd.DataFrame(rows)
        df_display = df.copy()

        for col in [
            "Tiền lãi kỳ này",
            "Lãi lũy kế",
            "Số dư gốc + lãi"
        ]:
            df_display[col] = df_display[col].apply(vnd)

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )

        # Giải thích
        with st.expander("Cách tính"):
            st.markdown("""
            **1. Lãi đơn**

            Tiền lãi = Gốc × Lãi suất năm × Số tháng / 12

            Lãi được tính trên số vốn gốc ban đầu.

            **2. Lãi kép**

            Lãi được nhập vào vốn sau mỗi kỳ ghép lãi,
            rồi tiếp tục sinh lãi ở các kỳ tiếp theo.

            **3. Lưu ý**

            - Lãi suất được giả định không đổi trong suốt kỳ hạn.
            - Với lãi kép, lãi được tái đầu tư sau mỗi kỳ
              tháng hoặc quý nếu còn thời gian gửi.
            - Với lãnh lãi cuối kỳ, lãi kép được ghép
              theo tháng trong phép tính này và thanh toán
              toàn bộ khi đáo hạn.
            - Kết quả chưa tính thuế, phí hoặc quy định
              làm tròn của ngân hàng.
            """)

else:
    st.info(
        "Nhập thông tin khoản gửi và nhấn "
        "**TÍNH TIỀN LÃI** để xem kết quả."
    )
