#### JAVA 7 Features :

 - Some Features provided by Java 7 :
    1. String literals in switch statements.
    2. Diamond operator in Collection and Generic instance creation.  :  ` List<String> list = new ArrayList<>();` 
    3. Handling multiple exceptions with a single catch block.
        ```
          try {
          } catch (NullPointerException | StringIndexOutOfBoundsException e) {
            System.out.println(e.getMessage());
          }
        ```
    4. Try with resource block.
        ```
          - Before Java 7, we used to close the non-java resources such as streams and JDBC connections inside the finally block.
          - Try-with-resource block :
            - reduced coding and efficient managment of resources.
            - Resources are opened at the start of the try block and closed automatically when the try block ends. (ARM - automatic resource managment)
          
          try ( Connection connection = DriverManager.getConnection("url")) {
            //DB Operations
            } catch ( SQLException e){
              System.out.println(e);
            } 
        ```
   
#### JAVA 8 Features : 
##### 1. Default nad Static Methods in Interfaces :  
- Prior to Java SE 8, interfaces were expected to have abstract methods only. And, the classes implementing the interfaces had to override all those abstract methods. 
- However, Java SE 8 has made it possible to hold method definitions in an interface using default methods which will make sure avoiding the need for breaking the existing implementations unnecessarily.
- The default methods of interfaces have definitions that need not be redefined always
- `For example, forEach() is a default method in the List interface whose inclusion does not force the existing implementations like ArrayList to be modified.`
- Default Methods help in removing the base implementation classes. The interface provides the default implementation and the classes can choose which one to override.
- A default method cannot override methods from java.lang.Object
- Default methods also help in avoiding utility classes. For example, all Collections class methods provide default methods in the Collection interface
- The major reason for presenting default methods was to improve the Collections API to have a support for lambda expressions.
```
Class/Interface	 | New Methods 

Map	             | getOrDefault, forEach, compute, computeIfAbsent, computeIfPresent, merge, putIfAbsent, remove, replace, replaceAll 
Iterable	       | forEach, spliterator
Iterator	       | forEachRemaining
Collection	     | removeIf, stream, parallelStream
List	           | replaceAll, sort
BitSet	         | stream
```

```
Example : List sort before java 8 :
  
  List<Employee> empList = new ArrayList<>();
// Code to add employees to empList
// Sorting empList using a comparator
 
Collections.sort(empList, new EmployeeComparator());


After java 8:
List<Employee> empList = new ArrayList<>();
// Code to add employees to empList
// Sorting empList using a comparator
 
empList.sort(new EmployeeComparator());


// comparator class
public class EmployeeComparator implements Comparator<Employee> {
    public int compare(Employee employee1, Employee employee2) {
        return employee1.getEmpNo().compareTo(employee2.getEmpNo());
    }
}

Note : lists can now be sorted using their own sort() method instead of the one from the Collections class.

```
##### Rules for default methods :
  1. Classes always win. A method defined in the class or its superclass takes precedence over the default method definition that is available in the interface.
  2. Otherwise, sub-interfaces win: the method with the exact signature in the most specific default-functionality providing interface will be selected.
  3. If the choice continues to be ambiguous, the class that inherits multiple interfaces should explicitly select the default method implementation to be used just by overriding it and the overridden method should have an explicit call to the desired default behavior.
 
```
interface Greeting{
    default void hello() {
	System.out.println(" hello from A");
    }
}

interface GreetingExtn extends Greeting{
    default void hello() {
	System.out.println(" hello from Greeting");
     }
}

class Greet {   //comment and uncomment this class to try more possibilities
    public void hello()  {
        System.out.println("hello from Greet");
    }
}

class DefaultStarter extends Greet implements Greeting, GreetingExtn{
   public static void main(String[] args) {
	    new DefaultStarter().hello();
   }
}

OUTPUT : hello from greet
```

##### Static Methods :
 - When we have common behaviors for all the implementations of an interface, making them static inside the interface will make them part of the interface itself. No external utility class would be required in such a case.
 - Just like the static methods of a class, the static methods of an interface belong to the interface, and not specific to any instance of its implementing classes.
 - These methods can only be invoked using the interface name.
 - Static methods in interfaces help to provide utility methods. For example, null check, collection sorting, etc
 - Methods of java.lang.Object can never be defined as static methods in interfaces
 - The Comparator interface of Java 8 is a perfect example in which the static methods have been included: comparingInt(), comparingDouble(), comparingLong(), naturalOrder(), nullsFirst(), nullsLast() and reverseOrder() 
```
 List<String> countrylst = Arrays.asList("India", "America", "Japan", "Brazil");
        countrylst.sort(Comparator.naturalOrder()); // will sort in String natural sorting order
        
```

##### Lambda Expressions :
 - Lambda expressions provide implementation logic for functional interfaces (interfaces with only one abstract method)
 - Lambda expressions add the essence of functional programming in Java. They are functional constructs without classes, which can be passed like objects and executed as required. 
 - They also make the modifiers, return type, and parameter types completely optional.
```


//Example :
Comparator<Employee> comparator = (Employee employee1, Employee employee2) -> employee1.getCountry().compareTo(employee2.getCountry());
empList.sort(comparator);

```

##### Functional Interface :
 - Functional interfaces strictly have abstract methods of count one. However, they are allowed to have any number of static or default methods. In addition, they can override some methods from java.lang.Object.
 - Hence, lambda expressions can appear only in places where functional interfaces are used.
 - <strong>@FunctionalInterface</strong> annotation helps designing an interface as a functional interface.
 - ```java.util.Comparator interface is example with 	int compare(T objectt1, T objectt2) as the abstract method```
  
