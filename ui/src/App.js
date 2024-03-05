import './App.css';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from "./pages/Home";
import Matchup from "./pages/Matchup"
import Props from './pages/Props';


function App() {
  return (
    <div className="App">
      <Router>
        <nav className="bg-gray-700 text-white border-gray-200 flex justify-between items-center mx-auto p-4">
          {/* <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4 bg-gray-900"> */}
          <a href="/" className="flex items-center space-x-6 rtl:space-x-reverse">
            <div className='flex bg-white'>
              <img
                src="https://1000logos.net/wp-content/uploads/2017/04/Logo-NBA.png"
                className="h-20 w-32"
                alt="NBA Logo"
              />
            </div>
            <span className="self-center text-2xl font-semibold whitespace-nowrap">NBA Prop Analyzer</span>
          </a>
          <div className="hidden w-auto md:block" id="navbar-default">
            <ul className="font-medium flex flex-row p-4 border border-gray-100 rounded-lg space-x-8">
              {/* <li>
                <a href="#" class="block text-white rounded" aria-current="page">Home</a>
              </li> */}
              <>
                <Link to="/"> Games</Link>
                <Link to="/props"> Props</Link>
              </>
            </ul>
          </div>
        </nav>
        <Routes>
          <Route path="/" exact Component={Home} />
          <Route path="/matchup/:id" exact Component={Matchup} />
          <Route path="/props" exact Component={Props} />
          {/* <Route path="/matchup/:id" exact Component={Matchup} /> */}
        </Routes>
      </Router>
    </div>
  );
}

export default App;
