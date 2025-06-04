// File: src/pages/Login.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Footer from "./Footer.jsx";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = () => {
    if (username === "admin" && password === "admin") {
      localStorage.setItem("loggedInUser", username);
      navigate("/dashboard");
    } else {
      alert("Invalid credentials");
    }
  };

  return (
    <div className="min-h-screen relative bg-white flex items-center justify-center">
      <div className="w-full max-w-md p-10 rounded-lg shadow-lg border border-orange-500 bg-white">
        <h2 className="text-center text-3xl font-bold text-orange-600 mb-8 tracking-wide">
          FaceAttend Login
        </h2>
        <input
          type="text"
          id="username"
          name="username"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-3 mb-6 rounded-md border border-orange-400 placeholder-orange-500 text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-700 transition"
          autoComplete="username"
        />
        <input
          type="password"
          id="password"
          name="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-3 mb-8 rounded-md border border-orange-400 placeholder-orange-500 text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-700 transition"
          autoComplete="current-password"
        />
        <button
          onClick={handleLogin}
          className="w-full bg-orange-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-md shadow-md transition"
        >
          Login
        </button>
      </div>
      <Footer />
    </div>
  );
}

export default Login;
