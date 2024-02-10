import './App.css';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from "./pages/Home";

function App() {
  return (
    <div className="App">
      <Router>
        <div className='w-full bg-red-400'>THIS IS A DIV
          <div className='flex'>
            <>
              <Link to="/"> Home Page</Link>
            </>
          </div>
        </div>
        <Routes>
          <Route path="/" exact Component={Home} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
