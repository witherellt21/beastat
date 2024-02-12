import './App.css';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from "./pages/Home";
import Matchup from "./pages/Matchup"


function App() {
  return (
    <div className="App">
      <Router>
        <nav className="bg-gray-700 text-white border-gray-200 flex justify-between mx-auto p-4">
          {/* <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4 bg-gray-900"> */}
          <a href="/" className="flex items-center space-x-3 rtl:space-x-reverse">
            <img src="https://flowbite.com/docs/images/logo.svg" className="h-8" alt="Flowbite Logo" />
            <span className="self-center text-2xl font-semibold whitespace-nowrap">NBA Stats</span>
          </a>
          <div className="hidden w-auto md:block" id="navbar-default">
            <ul className="font-medium flex flex-row p-4 border border-gray-100 rounded-lg space-x-8">
              {/* <li>
                <a href="#" class="block text-white rounded" aria-current="page">Home</a>
              </li> */}
              <>
                <Link to="/"> Home Page</Link>
              </>
            </ul>
          </div>
        </nav>
        <Routes>
          <Route path="/" exact Component={Home} />
          <Route path="/matchup/:id" exact Component={Matchup} />
          {/* <Route path="/matchup/:id" exact Component={Matchup} /> */}
        </Routes>
      </Router>
    </div>
  );
}

export default App;
