# Day 26-30: Buffer & Review

## 🎯 Goal
This period is dedicated to catching up on reading, consolidating knowledge from the first month, and applying LLD concepts by building a small practical tool.

---

## 📚 Reading Catch-up
If you fell behind on **Designing Data-Intensive Applications (DDIA)**, use these days to finish **Chapter 3: Storage and Retrieval**.

### Key Concepts to Review:
1.  **LSM-Trees vs B-Trees**:
    *   **LSM-Trees (Log-Structured Merge-Trees)**: Used in Cassandra, LevelDB. Optimizes for **write throughput**. Appends to a log, merges in background (Compaction).
    *   **B-Trees**: Used in PostgreSQL, MySQL. Optimizes for **read speed**. Updates in-place, breaks data into fixed-size pages.
2.  **Indexing**:
    *   Why putting an index on every column slows down writes.
    *   **Clustered Index**: Data is stored *with* the key (e.g., Primary Key).
    *   **Non-Clustered Index**: Stores key + pointer to data.

---

## 🛠️ Build a CLI Tool
Apply your OOD/LLD knowledge (SOLID, Strategy Pattern) to build a simple Command Line Interface (CLI) tool.

### Project Idea: "File Organizer"
**Goal**: A script that organizes a messy "Downloads" folder into subfolders based on file extension (Images, Docs, Installers).

### Requirements
1.  Scan a target directory.
2.  Identify file types (e.g., `.jpg` -> Images, `.pdf` -> Documents).
3.  Move files to their respective folders.
4.  **Design Constraint**: Use the **Strategy Pattern** for the file handling logic (so you can easily add new rules like "Delete .tmp files" later).

### Code Snippet (Python Strategy Pattern)
```python
from abc import ABC, abstractmethod
import os
import shutil

# Strategy Interface
class FileAction(ABC):
    @abstractmethod
    def execute(self, file_path):
        pass

# Concrete Strategy: Move File
class MoveAction(FileAction):
    def __init__(self, dest_folder):
        self.dest_folder = dest_folder

    def execute(self, file_path):
        if not os.path.exists(self.dest_folder):
            os.makedirs(self.dest_folder)
        shutil.move(file_path, self.dest_folder)
        print(f"Moved {file_path} -> {self.dest_folder}")

# Context
class Organizer:
    def __init__(self):
        self.rules = {} # Extension -> Action

    def add_rule(self, extension, action: FileAction):
        self.rules[extension] = action

    def organize(self, directory):
        for filename in os.listdir(directory):
            ext = os.path.splitext(filename)[1]
            if ext in self.rules:
                full_path = os.path.join(directory, filename)
                self.rules[ext].execute(full_path)

# Usage
# organizer = Organizer()
# organizer.add_rule('.jpg', MoveAction('./Images'))
# organizer.organize('./Downloads')
```

---

## ⚡ Review Checklist
- [ ] Can I explain **SOLID principles** without looking at notes?
- [ ] Do I understand the difference between **Process** and **Thread**?
- [ ] Can I implement a **Singleton** (thread-safe) in my preferred language?
- [ ] Have I read DDIA Chapter 3?

---

## 🧘 Rest
Take a break. The next month (Distributed Systems) is heavy.
