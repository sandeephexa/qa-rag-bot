def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start = end - overlap  # Overlap for context continuity

    return chunks

# Example
document = """We are delighted that you have decided to join us in learning the system design interviews.
System design interview questions are the most difficult to tackle among all the technical
interviews. The questions require the interviewees to design an architecture for a software
system, which could be a news feed, Google search, chat system, etc. These questions are
intimidating, and there is no certain pattern to follow. The questions are usually very big
scoped and vague. The processes are open-ended and unclear without a standard or correct
answer."""
chunks = chunk_text(document, chunk_size=30, overlap=5)
print(f"Created {len(chunks)} chunks")