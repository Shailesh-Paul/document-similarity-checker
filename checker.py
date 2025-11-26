from pathlib import Path
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Folders
SUBMISSIONS_DIR = "submissions"
REPORTS_DIR = "reports"

# ----------------------------------------------------
# Risk level labeling
# ----------------------------------------------------
def similarity_risk_level(score: float) -> str:
    """
    score is in PERCENT (0–100)
    """
    if score >= 85:
        return "HIGH RISK 🔴"
    elif score >= 70:
        return "MEDIUM RISK 🟠"
    elif score >= 50:
        return "MILD SIMILARITY 🟡"
    else:
        return "SAFE 🟢"

# ----------------------------------------------------
# Load TXT, PDF, DOCX files from folder
# ----------------------------------------------------
def load_documents(folder_path: str):
    folder = Path(folder_path)
    if not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    files = sorted(folder.glob("*.*"))
    texts = []
    valid_files = []

    for f in files:
        ext = f.suffix.lower()

        # TEXT FILES
        if ext == ".txt":
            text = f.read_text(encoding="utf-8", errors="ignore")

        # PDF FILES
        elif ext == ".pdf":
            import PyPDF2
            text = ""
            with open(f, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text += page.extract_text() or ""

        # DOCX FILES
        elif ext == ".docx":
            from docx import Document
            doc = Document(f)
            text = "\n".join([p.text for p in doc.paragraphs])

        # unsupported
        else:
            print(f"Skipping unsupported file: {f.name}")
            continue

        # Only keep non-empty text
        if text.strip():
            texts.append(text)
            valid_files.append(f)
        else:
            print(f"Warning: {f.name} is empty after extraction, skipping.")

    if not valid_files:
        raise ValueError("No valid TXT/PDF/DOCX files with text found!")

    return valid_files, texts

# ----------------------------------------------------
# Standard TF-IDF similarity (lexical)
# ----------------------------------------------------
def compute_similarity_matrix(texts):
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 3),  # unigrams, bigrams, trigrams
        stop_words=None
    )
    tfidf = vectorizer.fit_transform(texts)
    sim_matrix = cosine_similarity(tfidf)
    return sim_matrix

# ----------------------------------------------------
# Enhanced "semantic-like" similarity (no heavy model)
# ----------------------------------------------------
def compute_semantic_similarity(texts):
    # Still TF-IDF, but larger n-grams for more context
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 5),
        stop_words=None
    )
    tfidf = vectorizer.fit_transform(texts)
    sim_matrix = cosine_similarity(tfidf)
    return sim_matrix

# ----------------------------------------------------
# Report Generation: console + CSV + TXT
# ----------------------------------------------------
def generate_report(files, sim_matrix, threshold: float):
    from openpyxl import Workbook

    Path(REPORTS_DIR).mkdir(exist_ok=True)
    csv_report = Path(REPORTS_DIR) / "similarity_report.csv"
    txt_report = Path(REPORTS_DIR) / "similarity_report.txt"
    excel_report = Path(REPORTS_DIR) / "similarity_report.xlsx"

    results = []
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            score = sim_matrix[i, j] * 100
            results.append((files[i].name, files[j].name, score))

    if not results:
        print("No document pairs to compare.")
        return

    results.sort(key=lambda x: x[2], reverse=True)

    highest = results[0]
    lowest = results[-1]
    avg = sum(r[2] for r in results) / len(results)

    print("\n=== Detailed Similarity Report ===\n")
    print(f"Total Documents       : {len(files)}")
    print(f"Total Comparisons     : {len(results)}")
    print(f"Highest Similarity    : {highest[0]} <--> {highest[1]} = {highest[2]:.2f}%")
    print(f"Lowest Similarity     : {lowest[0]} <--> {lowest[1]} = {lowest[2]:.2f}%")
    print(f"Average Similarity    : {avg:.2f}%\n")

    print("=== Similarity Results (Sorted) ===\n")

    for f1, f2, score in results:
        if score >= threshold * 100:
            risk = similarity_risk_level(score)
            print(f"{f1} <--> {f2} : {score:.2f}%  [{risk}]")

    # CSV
    with csv_report.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File 1", "File 2", "Similarity (%)", "Risk Level"])
        for f1, f2, score in results:
            writer.writerow([f1, f2, f"{score:.2f}%", similarity_risk_level(score)])

    # TXT
    with txt_report.open("w", encoding="utf-8") as txtfile:
        txtfile.write("=== Document Similarity Report ===\n\n")
        txtfile.write(f"Total Documents   : {len(files)}\n")
        txtfile.write(f"Total Comparisons : {len(results)}\n")
        txtfile.write(f"Highest Similarity: {highest[0]} <--> {highest[1]} = {highest[2]:.2f}%\n")
        txtfile.write(f"Lowest Similarity : {lowest[0]} <--> {lowest[1]} = {lowest[2]:.2f}%\n")
        txtfile.write(f"Average Similarity: {avg:.2f}%\n\n")
        txtfile.write("=== Sorted Results ===\n\n")
        for f1, f2, score in results:
            txtfile.write(f"{f1} <--> {f2} : {score:.2f}%  [{similarity_risk_level(score)}]\n")

    # EXCEL
    wb = Workbook()
    ws = wb.active
    ws.title = "Similarity Report"
    ws.append(["File 1", "File 2", "Similarity (%)", "Risk Level"])

    for f1, f2, score in results:
        ws.append([f1, f2, f"{score:.2f}%", similarity_risk_level(score)])

    wb.save(excel_report)

    print(f"\n✅ CSV report saved to: {csv_report}")
    print(f"✅ TXT report saved to: {txt_report}")
    print(f"✅ EXCEL report saved to: {excel_report}")
    print(f"\n🏆 Highest match: {highest[0]} <--> {highest[1]}")


# ----------------------------------------------------
# Main execution
# ----------------------------------------------------
def main():
    print("=== Document Similarity Checker ===")
    print("1 - Standard (TF-IDF)")
    print("2 - Enhanced Semantic Mode (Lightweight)")

    mode = input("Enter 1 or 2: ").strip()

    try:
        threshold_val = float(input("Enter similarity threshold (0–100): ").strip())
        threshold = threshold_val / 100
    except Exception:
        print("Invalid input! Using default threshold = 50%")
        threshold = 0.50

    files, texts = load_documents(SUBMISSIONS_DIR)

    print("\nLoaded documents:")
    for f, t in zip(files, texts):
        print(f"- {f.name}: {len(t)} characters")

    if mode == "2":
        print("\nUsing Enhanced Semantic Similarity...\n")
        sim_matrix = compute_semantic_similarity(texts)
    else:
        print("\nUsing Standard TF-IDF Similarity...\n")
        sim_matrix = compute_similarity_matrix(texts)

    generate_report(files, sim_matrix, threshold)


if __name__ == "__main__":
    main()
