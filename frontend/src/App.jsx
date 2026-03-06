import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Search from './pages/Search';
import AdminDashboard from './pages/AdminDashboard';
import Settings from './pages/Settings';
import ProtectedRoute from './components/ProtectedRoute';
import CreateSubAdmin from './pages/CreateSubAdmin';
import SubAdminsList from './pages/SubAdminsList';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute adminOnly={true}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/create-sub-admin"
              element={
                <ProtectedRoute adminOnly={true}>
                  <CreateSubAdmin />
                </ProtectedRoute>
              }
            />
            <Route
              path="/sub-admins"
              element={
                <ProtectedRoute adminOnly={true}>
                  <SubAdminsList />
                </ProtectedRoute>
              }
            />
            <Route path="/search" element={<Search />} />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
