import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage.jsx';
import InterviewHelper from './App.jsx';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/helper" element={<InterviewHelper />} />
      </Routes>
    </Router>
  );
}

export default App;