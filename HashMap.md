
### Hash Map fetaures and internal implementation :

  1. HashMap is hashtable based implementation of the map interface.
  2. It is unsynchronized and permits null
  3. There is no order maintained.
  4. Implementation provides O(1) time for get and put operations.
  5. Iteration O(n)
  6. Capacity : Number of buckets in the hashMap
  7. <i>load factor</i> is a measure of how full the hash table is allowed to get before its capacity is automatically increased.
  8. When the number of entries in the hash table exceeds the product of the load factor and the current capacity, the hash table is <i>rehashed</i> (that is, internal data structures are rebuilt) so that the hash table has approximately twice the number of buckets.
  9. The iterators returned by all of this class's "collection view methods" re <i>fail-fast</i>.  Fail-fast iterators throw `ConcurrentModificationException`.
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

