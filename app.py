import streamlit as st
import pandas as pd
from openai import OpenAI

# ====== GROQ ======
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

st.title("📊 Phân tích 14 Cluster (Chủ đề & Ý nghĩa)")

uploaded_file = st.file_uploader("📂 Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # ====== FIX CLUSTER ======
    df["Cluster_num"] = df["Cluster"].str.extract(r'(\d+)').astype(int)

    st.dataframe(df.head())

    text_column = "Content"

    if st.button("🚀 Phân tích"):

        results = []

        with st.spinner("Đang phân tích chủ đề..."):

            for cluster_id in range(1, 15):

                st.write(f"### 🔹 Cluster {cluster_id}")

                cluster_data = df[df["Cluster_num"] == cluster_id]

                if cluster_data.empty:
                    st.write("⚠️ Không có dữ liệu")
                    continue

                texts = cluster_data[text_column].dropna().astype(str).tolist()
                sample = texts[:5]

                # 🔥 PROMPT CHUẨN TÁCH CHỦ ĐỀ + Ý NGHĨA
                prompt = f"""
                Đây là các câu trả lời khảo sát:
                {sample}

                Hãy phân tích và trả lời CHÍNH XÁC theo format:

                Chủ đề: (viết 3-6 từ, không dài)
                Ý nghĩa: (1 câu giải thích)

                Không viết thêm gì khác.
                """

                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}]
                    )

                    result = response.choices[0].message.content

                except Exception:
                    result = "⚠️ Lỗi API"

                # ====== HIỂN THỊ ======
                st.write(result)

                results.append({
                    "Cluster": cluster_id,
                    "Kết quả": result
                })

        # ====== BẢNG TỔNG ======
        st.subheader("📋 Tổng hợp")
        st.dataframe(pd.DataFrame(results))
