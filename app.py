import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from openai import OpenAI

# ====== SET API KEY ======
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("📊 AI Survey Cluster Summarizer")

# ====== UPLOAD FILE ======
uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.write("📌 Dữ liệu:")
    st.dataframe(df.head())

    # ====== CHỌN CỘT TEXT ======
    text_column = st.selectbox("Chọn cột chứa câu trả lời", df.columns)

    if st.button("🚀 Phân tích"):
        texts = df[text_column].dropna().astype(str)

        # ====== VECTORIZE ======
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(texts)

        # ====== CLUSTER ======
        k = st.slider("Số cluster", 2, 10, 3)
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(X)

        df["Cluster"] = labels

        st.success("✅ Đã phân cụm!")

        # ====== HIỂN THỊ ======
        st.dataframe(df)

        # ====== TÓM TẮT BẰNG AI ======
        st.subheader("🧠 Tóm tắt từng Cluster")

        for cluster_id in range(k):
            st.write(f"### 🔹 Cluster {cluster_id}")

            cluster_texts = df[df["Cluster"] == cluster_id][text_column].tolist()

            sample = cluster_texts[:20]  # tránh quá dài

            prompt = f"""
            Dưới đây là các câu trả lời khảo sát:
            {sample}

            Hãy tóm tắt ý nghĩa chung của nhóm này bằng 1-2 câu ngắn.
            """

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            summary = response.choices[0].message.content

            st.write("👉 Tóm tắt:", summary)
