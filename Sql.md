# Sql Interview Questions :

  ### 1. Find duplicate rows in sql : 
   
   ```
      SELECT OrderID, COUNT(OrderID) FROM Orders GROUP BY OrderID HAVING COUNT(OrderID) > 1;
   ```
  
   ### 2. Find Nth Highest salary : 
   
   ```
   1 . Using Co-related subqueries.
        - This is a special type of subquery where the subquery depends upon the main query and execute for every row returned by the main query.
   
      SELECT name, salary FROM Employee e1 WHERE N-1 = (SELECT COUNT(DISTINCT salary) FROM Employee e2 WHERE e2.salary > e1.salary);
   ```
   
   ```
   2. Using LIMIT keyword, which provides pagination capability.
   
     SELECT salary FROM Employee ORDER BY salary DESC LIMIT N-1, 1

   ```
   ### 3. find the second highest salary of Employee :
   
   ```
   SELECT MAX(Salary) FROM Employee WHERE Salary NOT IN (select MAX(Salary) from Employee );

   ```
   
   ### 4. Find the number of employees according to gender whose DOB is between 01/01/1960 to 31/12/1975.
  ```
  SELECT COUNT(*), gender FROM Employees WHERE DOB BETWEEN '01/01/1960' AND '31/12/1975' GROUP BY gender;
  ```
  
   ### 5. Delete Duplicate rows from SQL table.
   ```
   DELETE FROM [Employee]
    WHERE ID NOT IN
    (
        SELECT MAX(ID) AS MaxID
        FROM [Employee]
        GROUP BY [FirstName],  
                 [Country]
    );
   ```
  
  
  ## Resources :
  - https://www.java67.com/2013/04/10-frequently-asked-sql-query-interview-questions-answers-database.html
