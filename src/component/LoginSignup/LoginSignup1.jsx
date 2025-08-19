import { useNavigate } from 'react-router-dom';
import React, { useState } from "react";
import "./LoginSignup.css";

function LoginSignup1() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: ""
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

const navigate = useNavigate(); 

const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const url = isSignUp
      ? "http://127.0.0.1:5000/signup"
      : "http://127.0.0.1:5000/login";

    const response = await fetch(url, {
      method: "POST", 
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.message || "Upload failed");
      return;
    }

    alert(data.message);
    setFormData({ name: "", email: "", password: "" });
    navigate('/home'); 
  } catch (err) {
    console.error(err);
    alert("Upload failed");
  }
};

  return (
    <div className="form-container">
      <h2>{isSignUp ? "Sign Up" : "Login"}</h2>
      <form onSubmit={handleSubmit}>
        {isSignUp && (
          <input
            type="text"
            name="name"
            placeholder="Full Name"
            value={formData.name}
            onChange={handleChange}
          />
        )}
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
        />
        <button type="submit">{isSignUp ? "Sign Up" : "Login"}</button>
      </form>
      <p
        onClick={() => setIsSignUp(!isSignUp)}
        style={{ cursor: "pointer", color: "blue", textDecoration: "underline" }}
      >
        {isSignUp
          ? "Already have an account? Login"
          : "Don't have an account? Sign Up"}
      </p>
    </div>
  );
}

export default LoginSignup1;
