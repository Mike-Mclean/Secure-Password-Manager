import { Routes, Route } from 'react-router'
import { useState } from 'react'
import Header from './components/Header'
import Home from './pages/Home'
import Login from './pages/Login'
import MFAChallege from './pages/MFAChallenge.jsx'
import MFAInput from './pages/MFAInput.jsx'
import MFATOTPInput from './pages/MFATOTPInput.jsx'
import Logout from './pages/Logout'
import Register from './pages/Register'
import RegConfirm from './pages/RegConfirm'
import Account from './pages/Account'
import Guide from './pages/Guide'
import Dashboard from './pages/Dashboard.jsx'
import AddCredential from './pages/AddCredential.jsx'
import MFASetupPage from './pages/TOTPEnroll.jsx'
import EditCredential from './pages/EditCredential.jsx'
import ConfirmDelete from './pages/ConfirmDelete.jsx'

import './App.css'

const currUser = window.__USER__;
if (currUser) {
  console.log("Logged in as:", currUser.username);
  // You can use currentUser.id to fetch user-specific data
  // Example: fetch(`/api/users/${currentUser.id}/vault/`)
}

function App() {

  // isLoggedIn used to display appropriate links in navbar
  let status = false;
  if (window.__USER__.username != 'None') {
    status = true;
  }
  const[isLoggedIn, setIsLoggedIn] = useState(status);

  const triggerLoginChange = (status) => {
    setIsLoggedIn(status);
  };

  // Login message
  const [loginMessage, setLoginMessage] = useState('');

  const triggerLoginMessage = (message) => {
    setLoginMessage(message);
  };

  return (
    <div>
      <Header isLoggedIn={isLoggedIn} />
      <main>
        <div className="body-container">
          <Routes>
            {isLoggedIn ? 
              <Route path="/" element={<Dashboard />} />
            :
              <Route path="/" element={<Home />} />
            }
            <Route path="/login" element={<Login onLoginChange={triggerLoginChange} onMessageChange={triggerLoginMessage} message={loginMessage}/>} />
            <Route path="/mfa-challenge" element={<MFAChallege />} />
            <Route path="/mfa-input" element={<MFAInput onLoginChange={triggerLoginChange} />} />
            <Route path="/logout" element={<Logout onLoginChange={triggerLoginChange} />} />
            <Route path="/register" element={<Register onLoginChange={triggerLoginChange} onMessageChange={triggerLoginMessage} message={loginMessage} />} />
            <Route path="/reg-confirm" element={<RegConfirm />} />
            <Route path="/account" element={<Account onLoginChange={triggerLoginChange} />} />
            <Route path="/guide" element={<Guide />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/add-credential" element={<AddCredential />} />

            {/* // just an example to test out rendering the QR code */}
            <Route path="/totp-enroll" element={<MFASetupPage />} />
            <Route path="/mfa-totp-input" element={<MFATOTPInput onLoginChange={triggerLoginChange} />} />

            <Route path="/delete-credential" element={<ConfirmDelete />} />
            <Route path="/edit-credential" element={<EditCredential />} />

          </Routes>
        </div>
       {/* <h2> user --- {currentUser.username}</h2> */}
      </main>
    </div>
  );
}

export default App
