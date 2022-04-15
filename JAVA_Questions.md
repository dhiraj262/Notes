### Java Questions :

##### 1. Why Deque is better than Stack ?
1. <strong>Object oriented design</strong> - Inheritance, abstraction, classes and interfaces: Stack is a class, Deque is an interface. Only one class can be extended, whereas any number of interfaces can be implemented by a single class in Java (multiple inheritance of type). Using the Deque interface removes the dependency on the concrete Stack class and its ancestors and gives you more flexibility, e.g. the freedom to extend a different class or swap out different implementations of Deque (like LinkedList, ArrayDeque).

2. <strong>Inconsistency</strong>- Stack extends the Vector class, which allows you to access element by index. This is inconsistent with what a Stack should actually do, which is why the Deque interface is preferred (it does not allow such operations)--its allowed operations are consistent with what a FIFO or LIFO data structure should allow.

3. <strong>Performance</strong>- The Vector class that Stack extends is basically the "thread-safe" version of an ArrayList. The synchronizations can potentially cause a significant performance hit to your application. Also, extending other classes with unneeded functionality (as mentioned in #2) bloat your objects, potentially costing a lot of extra memory and performance overhead.

```
One more reason to use Deque over Stack is Deque has the ability to use streams convert to list with keeping LIFO concept applied while Stack does not.

Stack<Integer> stack = new Stack<>();
Deque<Integer> deque = new ArrayDeque<>();

stack.push(1);//1 is the top
deque.push(1)//1 is the top
stack.push(2);//2 is the top
deque.push(2);//2 is the top

List<Integer> list1 = stack.stream().collect(Collectors.toList());//[1,2]

List<Integer> list2 = deque.stream().collect(Collectors.toList());//[2,1]

```
