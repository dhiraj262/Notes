
### Hash Map fetaures and internal implementation :

  1. HashMap is hashtable based implementation of the map interface.
  2. It is unsynchronized and permits null
  3. There is no order maintained.
  4. Implementation provides O(1) time for get and put operations.
  5. Iteration O(n)
  6. Capacity : Number of buckets in the hashMap
  7. <i>load factor</i> is a measure of how full the hash table is allowed to get before its capacity is automatically increased.
  8. When the number of entries in the hash table exceeds the product of the load factor and the current capacity, the hash table is <i>rehashed</i> (that is, internal data structures are rebuilt) so that the hash table has approximately twice the number of buckets.
  9. The iterators returned by all of this class's "collection view methods" are <i>fail-fast</i>.  Fail-fast iterators throw `ConcurrentModificationException`.
  10. This class is a member of the Java Collections Framework.
  11. HashMap class extends AbstractMap class that implements the Map interface

  ```
  public class HashMap<K,V> extends AbstractMap<K,V>
    implements Map<K,V>, Cloneable, Serializable {
     ....
  ```
  
  12. HashMap uses its static inner class Node<K,V> for storing the entries into the map.
 
  ```
  static class Node<K,V> implements Map.Entry<K,V> {
          final int hash;
          final K key;
          V value;
          Node<K,V> next;

        Node(int hash, K key, V value, Node<K,V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }
        ....
  ```
  
  13. HashMap has multiple buckets or bins which contain a head reference to a singly linked list. That means there would be as many linked lists as there are buckets. Initially, it has a bucket size of 16 which grows to 32 when the number of entries in the map crosses the 75%. (That means after inserting in 12 buckets bucket size becomes 32)
  14. HashMap uses hashCode() and equals() methods on keys for the get and put operations
  ```
  public final int hashCode() {
            return Objects.hashCode(key) ^ Objects.hashCode(value);
        }
        
        
   public final boolean equals(Object o) {
      if (o == this)
          return true;
      if (o instanceof Map.Entry) {
          Map.Entry<?,?> e = (Map.Entry<?,?>)o;
          if (Objects.equals(key, e.getKey()) &&
              Objects.equals(value, e.getValue()))
              return true;
      }
      return false;
  }
  
  
  static final int hash(Object key) {
        int h;
        return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
    }
    
```
##### Internal Working Of hashmap:
 - HashMap uses its static inner class Node<K,V> for storing map entries. That means each entry in hashMap is a Node. Internally HashMap uses a hashCode of the key Object and this hashCode is further used by the hash function to find the index of the bucket where the new entry can be added.
 - HashMap uses multiple buckets and each bucket points to a Singly Linked List where the entries (nodes) are stored.
 - Once the bucket is identified by the hash function using hashcode, then hashCode is used to check if there is already a key with the same hashCode or not in the bucket(singly linked list).
 - If there already exists a key with the same hashCode, then the equals() method is used on the keys. If the equals method returns true, that means there is already a node with the same key and hence the value against that key is overwritten in the entry(node), otherwise, a new node is created and added to this Singly Linked List of that bucket.
 - If there is no key with the same hashCode in the bucket found by the hash function then the new Node is added into the bucket found.

 - Before java 8, singly-linked lists were used for storing the nodes. But this implementation has changed to self-balancing BST after a thresold is crossed ```(static final int TREEIFY_THRESHOLD = 8;)``` The motive behind this change is that HashMap buckets normally use linked lists, but for the linked lists the worst-case time is O(n) for lookup.

##### Re-Hashing :
- Whenever the number of entries in the hashmap crosses the threshold value then the bucket size of the hashmap is doubled and rehashing is performed and all already existing entries(nodes) of the map are copied and new entries are added to this increased hashmap.
 ```
Threshold value = Bucket size * Load factor
```

 - HashMap allows one null key, which is stored at the first location of bucket array e.g., bucket[0] = value. The HashMap doesn't call hashCode() on the null key to avoid a null pointer exception, hence when a user call the get() method with null, then the value of the first index is returned.

##### All Java collections framework interfaces extend Collection interface but Map does not. The reason is that maps do not exactly store single elements as do other collections but rather a collection of key-value pairs. So the generic methods of Collection interface such as add, toArray do not make sense when it comes to Map.

#### Collection Views in HashMap :
  ```
  1. Set<String> keys = map.keySet();   // The set is backed by the map itself. So any change made to the set is reflected in the map:
  2. Collection<String> values = map.values();   
  3. Set<Entry<String, String>> entries = map.entrySet();  //set view of all entries
  
  
  The only allowed structural modification is a remove operation performed through the iterator itself:

public void givenIterator_whenRemoveWorks_thenCorrect() {
    Map<String, String> map = new HashMap<>();
    map.put("name", "baeldung");
    map.put("type", "blog");

    Set<String> keys = map.keySet();
    Iterator<String> it = keys.iterator();

    while (it.hasNext()) {
        it.next();
        it.remove();
    }

    assertEquals(0, map.size());
}

```

#### Collisions in the HashMap :
 -  It is a situation where two or more key objects produce the same final hash value and hence point to the same bucket location or array index.
 -  According to the equals and hashCode contract, two unequal objects in Java can have the same hash code.
 -  It can also happen because of the finite size of the underlying array, that is, before resizing. The smaller this array, the higher the chances of collision.
 -  If the hash codes of any two keys collide, their entries will still be stored in the same bucket.
 -  By default, the implementation uses a linked list as the bucket implementation.

```

public class MyHashMap<K, V> {

	private static int DEFAULT_CAPACITY = 16;

	private Entry<K, V>[] table;
	private int capacity;

	MyHashMap() {
		this(DEFAULT_CAPACITY);
	}

	MyHashMap(int capacity) {
		this.capacity = capacity;
		/**
		 * Initialize "Hash Table" with initial capacity which is nothing but an Array
		 * Each index of an array is called "Hash Bucket"
		 */
		this.table = new Entry[capacity];
	}

	/**
	 * Each Entry stores a key-value pair Each Entry also stores the address of next
	 * Entry in case of "Hash Collision"
	 */
	static class Entry<K, V> {
		K key;
		V value;
		Entry<K, V> next;

		Entry(K key, V value) {
			this.key = key;
			this.value = value;
		}

		Entry(K key, V value, Entry<K, V> next) {
			this.key = key;
			this.value = value;
			this.next = next;
		}
	}

	public void put(K key, V value) {
		if (key == null) {
			return;
		}

		// Create a key-value pair
		Entry<K, V> newEntry = new Entry<>(key, value);

		// Find the right Bucket by hashing the key
		int hash = hash(key);

		// if - Empty Bucket
		if (table[hash] == null) {
			table[hash] = newEntry;
			// else - "Hash Bucket" is not Empty, Known as "Hash Collision"
			// New Entry is created and linked to Previous Node in Same Bucket
		} else {
			Entry<K, V> current = table[hash];
			Entry<K, V> previous = null;
			while (current != null) {
				if (current.key.equals(key)) {
					current.value = newEntry.value;
					return;
				}
				previous = current;
				current = current.next;
			}
			previous.next = newEntry;
		}
	}

	public V get(K key) {
		if (key == null) {
			return null;
		}

		// Find the right Bucket by hashing the key
		int hash = hash(key);

		// if - "Hash Bucket" is Empty, Return null
		if (table[hash] == null) {
			return null;
			// else - "Hash Bucket" is not Empty
			// Traverse through all the linked Nodes in the Bucket
			// Use `equals` method to find the correct key-value pair
		} else {
			Entry<K, V> current = table[hash];
			while (current != null) {
				if (current.key.equals(key)) {
					return current.value;
				}
				current = current.next;
			}
		}
		return null;
	}

	private int hash(K key) {
		// Using modulo "% capacity" to make sure that returned hash in the range of
		// underlying Array size
		return Math.abs(key.hashCode()) % capacity;
	}

	public static void main(String[] args) {
		MyHashMap<String, Integer> likesPerPost = new MyHashMap<String, Integer>();
		likesPerPost.put("Learning Hash Map", 5);
		System.out.println(likesPerPost.get("Learning Hash Map"));
	}
}

```


##### Resources : 
 - https://www.baeldung.com/java-hashmap-advanced
 - https://codingnconcepts.com/java/design-hash-map-in-java/
 - https://www.geeksforgeeks.org/internal-working-of-hashmap-java/
