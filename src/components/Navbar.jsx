// src/components/Navbar.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';


const Navbar = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="navbar navbar-expand">
      <Link className="navbar-brand" to="/">E7 Armory</Link>
      <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span className="navbar-toggler-icon"></span>
      </button>
      <div className="collapse navbar-collapse" id="navbarNav">
        <ul className="navbar-nav">
          {isAuthenticated ? (
            <>
              <li className="nav-item"><Link className="nav-link" to="/upload">Upload Image</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/unit_lookup">Unit Look Up</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/build_finder">Build Finder</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/your_units">Your Units</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/profile">User Profile</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/overlay">Twitch Overlay Setup</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/sidebar">Sidebar</Link></li>
              <li className="nav-item"><Link className="nav-link" onClick={logout}>Log Out</Link></li>
            </>
          ) : (
            <>
              <li className="nav-item"><Link className="nav-link" to="/signup">Sign Up</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/login">Log In</Link></li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
