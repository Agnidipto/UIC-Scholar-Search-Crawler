from extractor.pdf_reader import extract_text_from_pdf
from extractor.keyword_extractor import preprocess_text
from extractor.tfidf_computer import compute_tfidf
from db.mongo_client import save_keywords_to_mongo

if __name__ == "__main__":
    pdf_path = "papers/Paper1.pdf"
    print("🔍 Extracting text...")
    text = extract_text_from_pdf(pdf_path)

    print("🧹 Cleaning & tokenizing...")
    tokens = preprocess_text(text)

    print("📊 Computing TF-IDF...")
    tfidf_df = compute_tfidf(tokens)

    print("💾 Saving to MongoDB...")
    save_keywords_to_mongo(tfidf_df)

    print("✅ Done!")