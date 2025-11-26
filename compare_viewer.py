from pathlib import Path

SUBMISSIONS_DIR = "submissions"

# Load two files and print side by side
def show_side_by_side(file1, file2):
    text1 = Path(SUBMISSIONS_DIR, file1).read_text(encoding="utf-8", errors="ignore").splitlines()
    text2 = Path(SUBMISSIONS_DIR, file2).read_text(encoding="utf-8", errors="ignore").splitlines()

    max_len = max(len(text1), len(text2))

    print("\n=== Side-by-Side Document Comparison ===\n")
    print(f"{file1:<60} | {file2}")

    print("-" * 130)

    for i in range(max_len):
        line1 = text1[i] if i < len(text1) else ""
        line2 = text2[i] if i < len(text2) else ""
        print(f"{line1:<60} | {line2}")

    print("\n✅ Comparison Complete\n")

# Ask filenames
f1 = input("Enter first file name: ").strip()
f2 = input("Enter second file name: ").strip()

show_side_by_side(f1, f2)

