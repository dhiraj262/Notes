### Hooks in functional components :
  #### 1. useRef :
          1. Refs are use to refer to the DOM elements.
          //
          let countRef = useRef(0);
          //
          
          2. The countRef ref object returned is mutable and will persist for the full lifetime of the compoent.
          3. Using refs we can gain focus to the elements.
          4. Modifying the current property of the ref does not cause the compponent to re-render.
          
          const InputText = ()=>{
              const inputText = useRef(null);
              const focusText=() =>{
                inputText.current.focus();
              }
              
              return (
                <div>
                  Name:<input type="text" ref={inputText}/>
                  <button onClick={focusText}>Focus the text </button>
                </div>
              )
          }
          export default InputText;
          
      Note : React.forwardref method is used within the child component to get the ref passed from parent component.
      
          
#### 2. useMemo and useCallback: Both are use to avoid unnecessary re-renders.
      1. Both useMemo and useCallback hooks accepts callback function and array of dependencies as arguments.
      2. The return value of both useMemo and useCallback function changes only if one of the specified dependencies changes, otherwise memorized value will be returned.
      3. Passing the empty array dependencies will cause the hook to execute only once but if we do not pass the second argument, then the hook will return a new value on every call.
      
          newValue = useMemo(()=>{
          },[dependencies])

           newValue = useCallback(()=>{
          },[dependencies])
          
 #### 3. useLayoutEffect : 
        1. useLayoutEffect is involked synchronously after all the DOM mutations but before the browser paints the changes.
          - It is suggested to use when we wnat to read computed styles after the DOM has been mutated but before the browser has painted the new layout like when we need the scroll position or other style of an element.
         
          - useLayoutEffect is synchronous a.k.a. blocking a.k.a. the app won’t visually update until your effect finishes running… it could cause performance issues like stuttering if you have slow code in your effect.
          
          
        Order of execution : 
          1. An event is triggered which causes the component to re-render.
          2. React invokes the render method of the component.
          3. The the useLayoutEffect method runs and react waits for it to finish.
          4. The view on the browser is updated.
          5. Then the useEffect method runs.
          
          useLayoutEffect(() => {
            // do side effects
            return () => /* cleanup */
          }, [dependency, array]);

 #### 3. useReducer : 
 
      1. Alternative for useState.
      2. when next state depends on the previous state.
      3. useReducer is pre-built in React and not with redux.
      4. It is used for only local state managment and not for global state managment.
      5. To achieve global state managment we can use useContext with useReducer.
      
      Arguments : 
        1. first argument is the reducer function that takes current state and action object and returns the new modified state.
        2. The second argument is the initial state. 
        
        import React, { useReducer } from 'react';

          function Counter() {
            // First render will create the state, and it will
            // persist through future renders
            const [sum, dispatch] = useReducer((state, action) => {
              return state + action;
            }, 0);  // initial state is 0.

            return (
              <>
                {sum}

                <button onClick={() => dispatch(1)}>
                  Add 1
                </button>
              </>
            );
          }
