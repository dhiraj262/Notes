# Day 26-30: Buffer & Review - Month 1

## 🎯 Goal
Consolidate knowledge from Month 1 (LLD, Concurrency, Database Internals). Catch up on reading and build a small project.

---

## 📅 Schedule

### Day 26: The "Design Data-Intensive Applications" Catch-up
*   **Focus**: Read **Chapter 3 (Storage and Retrieval)** and **Chapter 4 (Encoding and Evolution)** of DDIA.
*   **Key Concepts**:
    *   LSM-Trees vs B-Trees.
    *   SSTables and Compaction.
    *   Avro/Protobuf vs JSON/XML.

### Day 27: Concurrency Review
*   **Task**: Revisit the **Elevator System** or **Parking Lot** code you wrote.
*   **Challenge**: Introduce threading.
    *   Can two elevators move simultaneously?
    *   What happens if two users try to book the last spot at the exact same microsecond?
*   **Action**: Write a small Python script proving a race condition, then fix it with a Lock.

### Day 28: Project - Build a CLI Tool
*   **Idea**: Build a simple command-line tool called `file-analyzer`.
*   **Features**:
    *   Read a large text file.
    *   Count frequency of words.
    *   Output top 10 words.
*   **Requirement**: Use **Streams** (or Generators in Python) so it doesn't crash on a 10GB file. This tests your understanding of memory management (Day 8).

### Day 29: Design Patterns Refactoring
*   **Task**: Take an old project (or a messy script).
*   **Action**: Apply 2 Design Patterns.
    *   Use **Strategy Pattern** for something that has multiple `if-else` conditions.
    *   Use **Builder Pattern** for a class with a huge constructor.

### Day 30: Rest & Reflection
*   **Activity**: Write down 3 things you struggled with this month.
*   **Plan**: How will you attack them in Month 2?
*   **Flashcards**: Review your Anki deck.

---

## 🛠️ Mini-Project: Stream Processing CLI (Day 28)

Here is a starting point for the CLI tool.

```python
import sys
import collections
import re

def stream_file(filepath):
    """Generator that reads a file line by line to be memory efficient."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                yield line
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return

def count_words(filepath):
    counter = collections.Counter()

    # Process stream
    for line in stream_file(filepath):
        # Simple tokenization
        words = re.findall(r'\w+', line.lower())
        counter.update(words)

    return counter.most_common(10)

if __name__ == "__main__":
    # Create a dummy file for testing
    with open("test_large_file.txt", "w") as f:
        f.write("system design system design interview system lld hld " * 1000)

    print("Analyzing file...")
    top_words = count_words("test_large_file.txt")

    print("--- Top 10 Words ---")
    for word, count in top_words:
        print(f"{word}: {count}")

    import os
    os.remove("test_large_file.txt")
```
