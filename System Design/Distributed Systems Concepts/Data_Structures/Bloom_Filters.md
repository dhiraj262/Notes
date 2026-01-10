# 🌸 Deep Dive: Bloom Filters

> **Category**: Data Structures
> **Core Concept**: Probabilistic Data Structure for set membership.
> **Key Characteristic**: "Definitely No" or "Maybe Yes".

---

## 1. The Concept

A **Bloom Filter** is a space-efficient probabilistic data structure that is used to test whether an element is a member of a set.

*   **False Positive Matches**: Possible. (The filter says "Yes", but the element is not in the set).
*   **False Negatives**: Impossible. (The filter says "No", the element is definitely not in the set).

### How It Works
1.  **Bit Array**: Initialize an array of $m$ bits to 0.
2.  **Hash Functions**: Use $k$ different independent hash functions.
3.  **Add(item)**: Hash the item $k$ times. Set the bits at indices $h_1(item), h_2(item), \dots, h_k(item)$ to 1.
4.  **Check(item)**: Hash the item $k$ times. If **ALL** bits at the corresponding indices are 1, return **True** (Maybe). If **ANY** bit is 0, return **False** (Definitely No).

---

## 2. Interview Post-Mortem: "The Certainty Trap"

### 🛑 The Trap
**Scenario**: You are designing a Username Availability Service.
**Candidate**: *"I'll store all taken usernames in a Bloom Filter. When a user types a name, I check the Bloom Filter. If it says 'Taken', I reject it."*

**The Failure**: Bloom Filters have **False Positives**. You might tell a user "JohnDoe" is taken when it's actually free (because of a hash collision). This degrades UX.

### ✅ The Solution
Use the Bloom Filter as a **First Line of Defense** (Cache) to save expensive database lookups.
1.  Check Bloom Filter.
2.  If **"No"** $\rightarrow$ Return "Available" (Certain). **Optimization!** DB never touched.
3.  If **"Yes"** $\rightarrow$ Check the Database (Source of Truth) to confirm.

---

## 3. Real World Use Cases
1.  **Cassandra / HBase**: To check if an SSTable (disk file) contains a row. Avoids reading the file if the Bloom Filter says "No".
2.  **Google Chrome**: Checking against a list of malicious URLs.
3.  **CDN**: To check if an object is cached before querying the origin.

---

## 4. Implementation (Python)

```python
import hashlib

class BloomFilter:
    def __init__(self, size=1000, num_hashes=3):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size

    def _hashes(self, item):
        """Generates k hash indices for the item"""
        indices = []
        for i in range(self.num_hashes):
            # Simulate k hash functions using MD5 with salt
            # In prod, use MurmurHash or FNV
            digest = hashlib.md5(f"{item}{i}".encode()).hexdigest()
            index = int(digest, 16) % self.size
            indices.append(index)
        return indices

    def add(self, item):
        for index in self._hashes(item):
            self.bit_array[index] = 1

    def check(self, item):
        for index in self._hashes(item):
            if self.bit_array[index] == 0:
                return False # Definitely No
        return True # Maybe Yes

# --- Test ---
bf = BloomFilter(size=20, num_hashes=3)
bf.add("user@example.com")
bf.add("admin@system.com")

print(f"Check 'user@example.com': {bf.check('user@example.com')}") # True
print(f"Check 'random@guy.com': {bf.check('random@guy.com')}")     # False
```

---

## 5. Mathematical Nuances

*   **Optimal Hash Functions ($k$)**: $k = (m/n) \ln 2$
    *   $m$ = bits, $n$ = expected elements.
*   **Space Efficiency**: A Bloom Filter with 1% false positive rate requires about **9.6 bits per element**, regardless of the element's size (String, Blob, etc.).

## ⚡ Flashcards
1.  **Q: Can you delete items from a Bloom Filter?**
    *   *A: No (mostly). Removing a bit might affect other items that map to the same bit (Counting Bloom Filters are an exception).*
2.  **Q: Why use MurmurHash instead of MD5?**
    *   *A: MurmurHash is non-cryptographic, much faster, and has good distribution properties.*
