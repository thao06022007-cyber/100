import streamlit as st
import pandas as pd
from openai import OpenAI

# ====== GROQ ======
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

st.title("📊 AI Tóm tắt 14 Cluster")

uploaded_file = st.file_uploader("📂 Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.write("📌 Dữ liệu:")
    st.dataframe(df.head())

    # ====== CHỌN CỘT TEXT ======
    text_column = st.selectbox("Chọn cột chứa nội dung", df.columns)

    if st.button("🚀 Phân tích"):
        with st.spinner("Đang phân tích từng cluster..."):

            results = []

            # ====== LẤY DANH SÁCH CLUSTER ======
            clusters = sorted(df["Cluster"].dropna().unique())

            for cluster_id in clusters:
                st.write(f"### 🔹 Cluster {cluster_id}")

                cluster_texts = df[df["Cluster"] == cluster_id][text_column].astype(str).tolist()

                # giảm dữ liệu tránh rate limit
                sample = cluster_texts[:3]

                prompt = f"""
                Đây là các câu trả lời thuộc Cluster {cluster_id}:
                {sample}

                Hãy tóm tắt ý nghĩa chung của cluster này trong 1-2 câu.
                Viết bằng tiếng Việt, ngắn gọn.
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
                    "Tóm tắt": summary
                })

            # ====== BẢNG KẾT QUẢ ======
            st.subheader("📋 Tổng hợp")
            st.dataframe(pd.DataFrame(results))
