import streamlit as st
import pandas as pd
from openai import OpenAI

# ====== CONFIG GROQ ======
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

    # ====== CHỌN 14 CỘT ======
    columns = st.multiselect("Chọn 14 cột chủ đề", df.columns)

    if st.button("🚀 Phân tích"):

        if len(columns) == 0:
            st.warning("⚠️ Bạn phải chọn ít nhất 1 cột")
        else:
            with st.spinner("Đang phân tích từng chủ đề..."):

                results = []

                # ====== XỬ LÝ TỪNG CHỦ ĐỀ (KHÔNG GỘP) ======
                for col in columns:
                    texts = df[col].dropna().astype(str).tolist()

                    # giảm dữ liệu tránh rate limit
                    sample = texts[:3]

                    prompt = f"""
                    Đây là câu trả lời khảo sát cho 1 chủ đề:
                    {sample}

                    Hãy tóm tắt ý nghĩa chính của chủ đề này trong 1-2 câu.
                    Trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu.
                    """

                    try:
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}]
                        )

                        summary = response.choices[0].message.content

                    except Exception as e:
                        summary = "⚠️ Lỗi API (có thể do rate limit)"

                    results.append({
                        "Chủ đề": col,
                        "Tóm tắt": summary
                    })

                # ====== HIỂN THỊ ======
                st.success("✅ Hoàn thành!")

                result_df = pd.DataFrame(results)

                st.subheader("🧠 Kết quả tóm tắt 14 chủ đề:")
                st.dataframe(result_df)

                # ====== DOWNLOAD FILE ======
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Tải kết quả",
                    csv,
                    "ket_qua_tom_tat.csv",
                    "text/csv"
                )
