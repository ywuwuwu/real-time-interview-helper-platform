import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './index.css';
import HomePage from './components/HomePage.jsx';
import InterviewHelperPage from './pages/InterviewHelperPage.jsx';
import InterviewPlannerPage from './pages/InterviewPlannerPage.jsx';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/helper" element={<InterviewHelperPage />} />
        <Route path="/planner" element={<InterviewPlannerPage />} />
      </Routes>
    </Router>
  );
}

export default App;