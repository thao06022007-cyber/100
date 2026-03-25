import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from openai import OpenAI

# ====== CONFIG GROQ ======
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

st.title("📊 AI Survey Cluster Summarizer")

# ====== UPLOAD ======
uploaded_file = st.file_uploader("📂 Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.write("📌 Dữ liệu:")
    st.dataframe(df.head())

    # ====== CHỌN CỘT ======
    text_column = st.selectbox("Chọn cột chứa câu trả lời", df.columns)

    if st.button("🚀 Phân tích"):
        with st.spinner("Đang xử lý..."):

            texts = df[text_column].dropna().astype(str)

            # ====== VECTORIZE ======
            vectorizer = TfidfVectorizer()
            X = vectorizer.fit_transform(texts)

            # ====== CLUSTER ======
            k = st.slider("Số cluster", 2, 6, 3)
            kmeans = KMeans(n_clusters=k, random_state=42)
            labels = kmeans.fit_predict(X)

            df["Cluster"] = labels

            st.success("✅ Đã phân cụm!")
            st.dataframe(df)

            # ====== GỘP TEXT (TRÁNH RATE LIMIT) ======
            all_clusters_text = ""

            for cluster_id in range(k):
                cluster_texts = df[df["Cluster"] == cluster_id][text_column].tolist()
                sample = cluster_texts[:3]

                all_clusters_text += f"\nCluster {cluster_id}:\n{sample}\n"

            # ====== AI TÓM TẮT (CHỈ 1 LẦN GỌI API) ======
            prompt = f"""
            Dưới đây là các nhóm câu trả lời khảo sát:

            {all_clusters_text}

            Hãy tóm tắt ý nghĩa từng cluster (mỗi cluster 1-2 câu, viết ngắn gọn).
            """

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            st.subheader("🧠 Kết quả tóm tắt:")
            st.write(response.choices[0].message.content)
