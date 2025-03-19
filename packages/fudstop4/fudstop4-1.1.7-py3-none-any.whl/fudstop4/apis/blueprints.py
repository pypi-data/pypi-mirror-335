import os
from typing import List

# ---------------------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------------------
# Maximum tokens/words per chunk you want to allow before splitting.
# This script uses a simple "split by words" approach for demonstration.
MAX_CHUNK_SIZE = 3000

# Output file name (or provide a full path).
OUTPUT_FILE = "folder_metadata.txt"

# ---------------------------------------------------------------------
# 2. Token/Word Counting (Simplified)
# ---------------------------------------------------------------------
def approximate_token_count(text: str) -> int:
    """
    Very rough approximation of tokens by splitting on whitespace.
    Use an appropriate library for more precise token counts if needed.
    """
    return len(text.split())

def chunk_text_by_limit(text: str, max_size: int) -> List[str]:
    """
    Splits text into chunks that each have fewer than 'max_size' words.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# ---------------------------------------------------------------------
# 3. Process Each File
# ---------------------------------------------------------------------
def process_file(file_path: str) -> List[str]:
    """
    Reads a file as text, breaks it into chunks (if large),
    and returns the list of chunked text segments.
    If the file can't be read as text, returns an empty list.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception as e:
        # If non-text file or read error, skip
        print(f"[WARNING] Could not read file {file_path}: {e}")
        return []

    text = text.strip()
    if not text:
        return []

    token_count = approximate_token_count(text)
    if token_count <= MAX_CHUNK_SIZE:
        # Only one chunk needed
        return [text]
    else:
        # Multiple chunks
        return chunk_text_by_limit(text, MAX_CHUNK_SIZE)

# ---------------------------------------------------------------------
# 4. Gather Metadata for the Entire Folder
# ---------------------------------------------------------------------
def gather_folder_metadata(folder_path: str) -> None:
    """
    Recursively goes through the folder, processes each file, and
    writes the metadata (file name, path, chunked text) to OUTPUT_FILE.
    """
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(f"# Folder Analysis: {folder_path}\n\n")

        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                # Attempt to process file text
                chunks = process_file(file_path)

                if chunks:
                    out.write(f"---\n")
                    out.write(f"File Name: {file_name}\n")
                    out.write(f"File Path: {file_path}\n")
                    out.write(f"Number of Chunks: {len(chunks)}\n\n")

                    for i, chunk in enumerate(chunks, start=1):
                        out.write(f"Chunk {i}:\n")
                        out.write(chunk)
                        out.write("\n\n")
                    out.write(f"---\n\n")

    print(f"[INFO] Metadata has been saved to '{OUTPUT_FILE}'.")

# ---------------------------------------------------------------------
# 5. Main Execution
# ---------------------------------------------------------------------
def main():
    folder_path = input("Enter the path to the folder you want to analyze: ").strip()
    
    if not os.path.exists(folder_path):
        print("[ERROR] Folder path does not exist.")
        return
    
    print(f"\nGathering file metadata for folder: {folder_path} ...\n")
    gather_folder_metadata(folder_path)
    
    print("\n[DONE] You can now upload the output file to an LLM or other tool.")

if __name__ == "__main__":
    main()
