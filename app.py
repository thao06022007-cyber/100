import streamlit as st
import pandas as pd
from openai import OpenAI

# ====== GROQ ======
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

st.title("📊 AI Tóm tắt 14 chủ đề khảo sát")

# ====== UPLOAD FILE ======
uploaded_file = st.file_uploader("📂 Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.write("📌 Dữ liệu:")
    st.dataframe(df.head())

    # ====== CHỌN CÁC CỘT CHỦ ĐỀ ======
    columns = st.multiselect(
        "Chọn các cột (14 chủ đề)",
        df.columns
    )

    if st.button("🚀 Phân tích") and columns:
        with st.spinner("Đang phân tích..."):

            all_text = ""

            # ====== GỘP TEXT 14 CHỦ ĐỀ ======
            for col in columns:
                texts = df[col].dropna().astype(str).tolist()
                sample = texts[:5]   # giảm để tránh rate limit

                all_text += f"\nChủ đề: {col}\n{sample}\n"

            # ====== PROMPT ======
            prompt = f"""
            Dưới đây là dữ liệu khảo sát theo từng chủ đề:

            {all_text}

            Hãy:
            - Tóm tắt ý nghĩa từng chủ đề
            - Mỗi chủ đề 1-2 câu
            - Viết rõ ràng, dễ hiểu, bằng tiếng Việt
            """

            # ====== CALL API 1 LẦN ======
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            st.subheader("🧠 Kết quả tóm tắt:")
result = response.choices[0].message.content

for i, col in enumerate(columns):
    st.write(f"### 🔹 {col}")
    
    try:
        st.write(result.split(f"Chủ đề {i+1}:")[1].split("Chủ đề")[0])
    except:
        st.write("⚠️ Không tách được nội dung")
