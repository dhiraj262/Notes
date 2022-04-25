### Context Api is used to share state within a compoenent tree easily.
 - https://reactjs.org/docs/context.html
 
 - Context provides a way to pass data through the component tree without having to pass props down manually at every level. 
 
 1. Create a context object.
 2. create Provider to make the context available to all the components.
 3. The components can consume the context using Consumer or using static property 'contextType'.
 
 - useContext() hook is used to consume context within functional components.
 - In order to consume the context in any component, the component needs to be wrapped in context provider class.
