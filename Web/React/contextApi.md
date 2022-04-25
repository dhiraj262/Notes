### Context Api is used to share state within a compoenent tree easily.
 - https://reactjs.org/docs/context.html
 
 - Context provides a way to pass data through the component tree without having to pass props down manually at every level. 
 
 1. Create a context object.
 2. create Provider to make the context available to all the components.
 3. The components can consume the context using Consumer or using static property 'contextType'.
 
 - useContext() hook is used to consume context within functional components.
 - In order to consume the context in any component, the component needs to be wrapped in context provider class.

```
FileName : CourseList.js
-------------------------
import React,{useContext} from 'react';
import { ThemeContext } from '../Context/ThemeContext';


const CourseList =()=> {

        const {isLightTheme,light,dark} = useContext(ThemeContext);
        const theme = isLightTheme? light:dark;
        return (
           <div className='course-list' style={{color:theme.color,background:theme.bg}}>
               <ul>
                   <li style={{background:theme.ui}}>Computer Scienc</li>
                   <li style={{background:theme.ui}}>Electrical</li>
                   <li style={{background:theme.ui}}>Mechanical</li>
                   <li style={{background:theme.ui}}>Civil</li>
               </ul>
           </div>
        );
    }

export default CourseList;

////////////////////
FileName : Navbar.js
-------------------

import React from 'react';
import { ThemeContext } from '../Context/ThemeContext';

class Navbar extends React.Component {
    render(){
        return(
            <ThemeContext.Consumer>
                {(context)=>{
                    const {isLightTheme,light,dark} = context;
                    const theme = isLightTheme ? light:dark;

                    return(
                        <nav style={{background:theme.ui,color:theme.color}}>
                            <h2>Context API Demo</h2>
                            <ul>
                                <li>Home</li>
                                <li>About</li>
                                <li>Contact</li>
                            </ul>
                        </nav>
                    )
                }}
            </ThemeContext.Consumer>
        )
    }
}

export default Navbar;


//////////////////////////
FileName : ThemeToggle.js
------------------------------
import React from 'react';
import { ThemeContext } from '../Context/ThemeContext';


class ThemeToggle extends React.Component {
    static contextType = ThemeContext;

    render(){
        const {toggleTheme} = this.context;
        return (
           <button onClick={toggleTheme}>Toggle theme</button>
        );
    }
}

export default ThemeToggle;


//////////////////////////////////
FileName : ThemeContext.js

---------------------------------
import React,{createContext} from 'react';

export const ThemeContext = createContext();

class ThemeContextProvider extends React.Component {
    constructor () {
        super();
        this.state= {
            isLightTheme:true,
            light:{color:'#555',ui:'#ddd',bg:'#eee'},
            dark:{color:'#ddd',ui:'#333',bg:'#555'}
        }
    }
    toggleTheme=()=>{
        this.setState({isLightTheme:!this.state.isLightTheme})
    }
    render(){
        return (
            <ThemeContext.Provider value={{...this.state,toggleTheme:this.toggleTheme}}>
                {this.props.children}
            </ThemeContext.Provider>
        )
    }
}

export default ThemeContextProvider;


//////////////////////////////////////////
FileName : App.js
------------------------------------

import './App.css';
import CourseList from './Components/CourseList';
import Navbar from './Components/Navbar';
import ThemeToggle from './Components/ThemeToggle';
import ThemeContextProvider from './Context/ThemeContext';

function App() {
  return (
    <div className="App">
      <ThemeContextProvider>
        <Navbar/>
        <CourseList/>
        <ThemeToggle/>
      </ThemeContextProvider>
    </div>
  );
}

export default App;

```
