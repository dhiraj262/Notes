# Some Design Patterns available in react are :

  1. renderProps :
     - The renderProps is a technique for sharing code between React component using a prop where the prop is a function.

  2. HOC (Higher-order components)
     - A Higher-Order Function takes a function as an argument and/or returns a function.
     - React’s Higher Order Component is a pattern that stems from React’s nature that privileges composition over inheritance.

      Example : 
      
       `withRouter HOC ` - In order to access history, location and match props a component can use withRouter HOC. 
       `connect(mapStateToProps,mapDispatchToProps)` - HOC which returns a component that is connected to the redux store.

  3. Compound Components
     - Compound components is a pattern that helps the components communicate with each other.
     - Think of compound components like the `<select>` and <option> elements in HTML. Apart they don’t do too much, but together they allow you to create the complete experience( Kent C. Dodds).
  
  4. State Reducer 
     - It is a pattern, which helps in managing and controlling the state updates of the child component. 
