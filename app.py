import streamlit as st
import pandas as pd
from openai import OpenAI

# ====== GROQ ======
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

st.title("📊 Tóm tắt 14 Cluster (Survey)")

uploaded_file = st.file_uploader("📂 Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # ====== FIX CLUSTER (QUAN TRỌNG NHẤT) ======
    df["Cluster_num"] = df["Cluster"].str.extract(r'(\d+)').astype(int)

    st.write("📌 Dữ liệu:")
    st.dataframe(df.head())

    text_column = "Content"  # file của bạn là cột này

    if st.button("🚀 Phân tích"):

        with st.spinner("Đang tóm tắt..."):

            results = []

            # ====== CHẠY 1 → 14 ======
            for cluster_id in range(1, 15):

                st.write(f"### 🔹 Cluster {cluster_id}")

                cluster_data = df[df["Cluster_num"] == cluster_id]

                if cluster_data.empty:
                    st.write("⚠️ Không có dữ liệu")
                    results.append({
                        "Cluster": cluster_id,
                        "Ý nghĩa": "Không có dữ liệu"
                    })
                    continue

                texts = cluster_data[text_column].dropna().astype(str).tolist()

                sample = texts[:3]

                prompt = f"""
                Đây là các câu trả lời survey thuộc Cluster {cluster_id}:
                {sample}

                Hãy tóm tắt ý nghĩa chủ đề chính của cluster này.
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
                    summary = "⚠️ Lỗi API"

                st.write(summary)

                results.append({
                    "Cluster": cluster_id,
                    "Ý nghĩa": summary
                })

            # ====== BẢNG TỔNG ======
            st.subheader("📋 Tổng hợp")
            result_df = pd.DataFrame(results)
            st.dataframe(result_df)

            # ====== DOWNLOAD ======
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Tải file kết quả",
                csv,
                "ket_qua_cluster.csv",
                "text/csv"
            )
