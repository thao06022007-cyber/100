import streamlit as st
import pandas as pd
from openai import OpenAI

# ====== CONFIG GROQ ======
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

st.title("📊 Tóm tắt ý nghĩa 14 Cluster (Chủ đề)")

# ====== UPLOAD FILE ======
uploaded_file = st.file_uploader("📂 Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # ====== FIX KIỂU DỮ LIỆU CLUSTER ======
    df["Cluster"] = pd.to_numeric(df["Cluster"], errors="coerce")

    st.write("📌 Dữ liệu:")
    st.dataframe(df.head())

    # ====== CHỌN CỘT NỘI DUNG ======
    text_column = st.selectbox("Chọn cột nội dung khảo sát", df.columns)

    if st.button("🚀 Phân tích"):

        with st.spinner("Đang tóm tắt từng cluster..."):

            results = []

            # ====== CHẠY ĐÚNG THỨ TỰ 1 → 14 ======
            for cluster_id in range(1, 15):

                st.write(f"### 🔹 Cluster {cluster_id}")

                cluster_data = df[df["Cluster"] == cluster_id]

                if cluster_data.empty:
                    st.write("⚠️ Không có dữ liệu")
                    results.append({
                        "Cluster": cluster_id,
                        "Ý nghĩa": "Không có dữ liệu"
                    })
                    continue

                texts = cluster_data[text_column].astype(str).tolist()

                # giảm dữ liệu tránh rate limit
                sample = texts[:3]

                prompt = f"""
                Đây là các câu trả lời thuộc Cluster {cluster_id}:
                {sample}

                Hãy tóm tắt ý nghĩa nội dung của cluster này.
                - 1-2 câu
                - Ngắn gọn
                - Rõ ràng
                - Tiếng Việt
                """

                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}]
                    )

                    summary = response.choices[0].message.content

                except Exception:
                    summary = "⚠️ Lỗi API (có thể do rate limit)"

                st.write(summary)

                results.append({
                    "Cluster": cluster_id,
                    "Ý nghĩa": summary
                })

            # ====== BẢNG TỔNG ======
            st.subheader("📋 Tổng hợp 14 chủ đề")
            result_df = pd.DataFrame(results)
            st.dataframe(result_df)

            # ====== DOWNLOAD ======
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Tải kết quả",
                csv,
                "ket_qua_14_cluster.csv",
                "text/csv"
            )
