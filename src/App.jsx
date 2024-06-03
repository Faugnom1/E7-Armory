// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import UploadUnit from './pages/UploadUnit';
import UnitLookupPage from './pages/UnitLookupPage';
import UnitLookupResultsPage from './pages/UnitLookupResultsPage';
import BuildFinderPage from './pages/BuildFinderPage';
import YourUnitsPage from './pages/YourUnitsPage';
import SignupPage from './pages/SignupPage';
import LoginPage from './pages/LoginPage';
import UserProfile from './pages/UserProfile';
import DisplayUploadedUnit from './pages/DisplayUploadedUnit';
import Logout from './components/Logout';
import TwitchOverlay from './pages/TwitchOverlay';
import { AuthProvider } from './context/AuthContext';
import Sidebar from './sidebar/sidebar';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div>
          <Navbar />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadUnit />} />
            <Route path="/unit_lookup" element={<UnitLookupPage />} />
            <Route path="/unit_details/:unitName" element={<UnitLookupResultsPage />} />
            <Route path="/build_finder" element={<BuildFinderPage />} />
            <Route path="/your_units" element={<YourUnitsPage />} />
            <Route path="/profile" element={<UserProfile />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/user_profile" element={<UserProfile />} />
            <Route path="/display_uploaded_unit" element={<DisplayUploadedUnit />} />
            <Route path="/overlay" element={<TwitchOverlay />} />
            <Route path="/sidebar" element={<Sidebar />} />
            <Route path="/logout" element={<Logout />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
