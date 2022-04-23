#### MDN  : https://developer.mozilla.org/en-US/docs/Web/JavaScript for every concept

1. Chrome : V8 Engine - Just in time compilation


#### Data Types :
1. Primitive types
    ```
    String- represents sequence of characters e.g. var str="ram";
    Number-   represents numeric values eg var num =25;
    BigInt  - represent whole numbers larger than 2^53 - 1
    Boolean - represents boolean value either false or true eg var b=true;
    Undefined - represents undefined value
    Null - represents null i.e. no value at all
    Symbol- Symbols are often used to add unique property keys to an object
    ```

2.  Non - primitive types
    ```
    Object - instance through which we can access members.
    eg: var man={name:"john",age:50,height:5.6}

    Arrays - represents group of similar values
    eg var arr=[1,2,3,4,5];
    ```

##### Hoisting : Accessing the variables and functions before declaration.

##### Operators :
  1. Arithmatic Operators
  ```
  +	Addition (Also works with strings)
  -	Subtraction
  *	Multiplication
  **	Exponentiation (ES2016)
  /	Division
  %	Modulus (Division Remainder)
  ++	Increment
  --	Decrement
  ```
  
  2. Assignment Operators :
  ```
  =	x = y	x = y
  +=	x += y	x = x + y
  -=	x -= y	x = x - y
  *=	x *= y	x = x * y
  /=	x /= y	x = x / y
  %=	x %= y	x = x % y
  <<=	x <<= y	x = x << y
  >>=	x >>= y	x = x >> y
  >>>=	x >>>= y	x = x >>> y
  &=	x &= y	x = x & y
  ^=	x ^= y	x = x ^ y
  |=	x |= y	x = x | y
  **=	x **= y	x = x ** y
  ```
  
  3. Bitwise Operators :
  ```
  &	AND	
  |	OR
  ~	NOT
  ^	XOR
  <<	Zero fill left shift
  >>	Signed right shift
  >>>	Zero fill right shift
  ```
  
  4. Comparision Operators :
  ```
  ==	equal to
  ===	equal value and equal type
  !=	not equal
  !==	not equal value or not equal type
  >	greater than
  <	less than
  >=	greater than or equal to
  <=	less than or equal to
  ?	ternary operator
  ```
  
  5. Logical Operators :
  ```
  &&	logical and
  ||	logical or
  !	logical not
  ```
  
  6. Rest :
  ```
  
? Description
The rest parameter syntax allows a function to accept an 
indefinite number of arguments as an array,

? Uses
Commonly used in server side functions where unknown arguments like
configurations need to be passed.

function myFun(a, b, ...manyMoreArgs) {
    console.log("a", a);
    console.log("b", b);
    console.log("manyMoreArgs", manyMoreArgs); // [ 'three', 'four', 'five', 'six' ]
  }
  
  myFun("one", "two", "three", "four", "five", "six");
  ```
  
   7. Spread :
   ```
// Used to spread the state in react app to avoid mutation.

let numberStore = [0, 1, 2];
let newNumber = 12;
let newNumberStore = [...numberStore, newNumber];

console.log(newNumberStore); // [ 0, 1, 2, 12 ]
   ```
   
   8. Type :
```
? Type Operators

typeof - Returns the type of a variable.
typeof supports two forms of syntax:
1. As an operator: typeof x
2. As a function: typeof(x)
In other words typeof operator works with both parentheses and without parentheses, giving the same result.

instanceof - The instanceof operator tests to see if the prototype 
property of a constructor appears anywhere in the prototype chain of 
an object. The return value is a boolean value. 

// Examples for typeof
console.log(typeof "abc"); // string
console.log(typeof 123); // number
console.log(typeof function () {}); // function
console.log(typeof {}); // object
console.log(typeof 10n); // "bigint"
console.log(typeof null); // object
console.log(typeof NaN); // number
console.log(typeof undefined); // undefined
console.log(typeof true); // boolean
console.log(typeof $); // undefined (function in browser console)

// Example for instanceof
function Car(make, model, year) {
  this.make = make;
  this.model = model;
  this.year = year;
}

const auto = new Car("Honda", "Accord", 1998);

console.log(auto instanceof Car);
// expected output: true

console.log(auto instanceof Object);
// expected output: true
```
