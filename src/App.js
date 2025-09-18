import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginSignup1 from './component/LoginSignup/LoginSignup1';
import Homepage1 from './component/LoginSignup/Homepage1'; 

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginSignup1 />} />
        <Route path="/home" element={<Homepage1 />} />
      </Routes>
    </Router>
  );
}

export default App;
