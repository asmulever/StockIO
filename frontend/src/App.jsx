import React, { useState, useEffect } from "react";
import { login, getAllProducts, addProduct, predictStock } from "./api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

import DashboardView from './DashboardView';
import ExistenciaView from './ExistenciaView';
import './index.css';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({ name: "", stock: 0 });
  const [loginData, setLoginData] = useState({ username: "", password: "" });
  const [predictionData, setPredictionData] = useState([]);
  const [view, setView] = useState('dashboard');

  useEffect(() => {
    if (token) {
      getAllProducts(token)
        .then((prods) => {
          setProducts(prods);
          // if (prods.length > 0) {
          //   predictStock(prods[0].id, token).then(setPredictionData);
          // }
        })
        .catch(console.error);
    }
  }, [token]);

  function handleLogin(e) {
    e.preventDefault();
    
    login(loginData.username, loginData.password)
      .then((data) => {
        localStorage.setItem("token", data);
        setToken(data);
      })
      .catch((error) => {
        console.error("Error al loguear:", error);
        alert("Login incorrecto");
      });
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setToken(null);
  }

  function handleAddProduct(e) {
    e.preventDefault();
    addProduct(form, token)
      .then((p) => {
        const updated = [...products, p];
        setProducts(updated);
        setForm({ name: "", stock: 0 });
      })
      .catch(() => alert("Error al guardar producto"));
  }

  // LOGIN VIEW
  if (!token) {
    return (
      <div style={{ display: "flex", height: "100vh", justifyContent: "center", alignItems: "center", backgroundColor: "#f9fafb" }}>
        <form onSubmit={handleLogin} style={{ backgroundColor: "white", padding: "30px", borderRadius: "8px", boxShadow: "0 2px 6px rgba(0,0,0,0.15)", width: "300px" }} autoComplete="off">
          <h2 style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "20px", textAlign: "center" }}>Iniciar Sesión</h2>
          <input
            placeholder="Usuario"
            value={loginData.username}
            onChange={(e) =>
              setLoginData({ ...loginData, username: e.target.value })
            }
            style={{ width: "100%", marginBottom: "15px", padding: "10px", borderRadius: "4px", border: "1px solid #ccc" }}
            required
          />
          <input
            type="password"
            placeholder="Clave"
            value={loginData.password}
            onChange={(e) =>
              setLoginData({ ...loginData, password: e.target.value })
            }
            style={{ width: "100%", marginBottom: "20px", padding: "10px", borderRadius: "4px", border: "1px solid #ccc" }}
            required
          />
          <button
            type="submit"
            style={{
              width: "100%",
              backgroundColor: "#2d87f0",
              color: "#fff",
              padding: "10px",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Entrar
          </button>
        </form>
      </div>
    );
  }

  // MAIN APP VIEW
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <aside style={{
        width: '200px',
        backgroundColor: '#f0f4f8',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}>
        <div>
          <h2 style={{ fontWeight: 'bold' }}>STOCK</h2>
          <nav style={{ marginTop: '40px' }}>
            <div
              style={{ marginBottom: '20px', cursor: 'pointer', color: view === 'dashboard' ? '#2d87f0' : '#333' }}
              onClick={() => setView('dashboard')}
            >
              Dashboard
            </div>
            <div
              style={{ cursor: 'pointer', color: view === 'existencia' ? '#2d87f0' : '#333' }}
              onClick={() => setView('existencia')}
            >
              Existencia
            </div>
          </nav>
        </div>
        <button
          onClick={handleLogout}
          style={{
            backgroundColor: '#e74c3c',
            color: '#fff',
            border: 'none',
            padding: '10px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Cerrar sesión
        </button>
      </aside>

      <main style={{ flex: 1, padding: '30px', backgroundColor: '#f9fafb' }}>
        {view === 'dashboard' ? (
          <DashboardView productos={products} prediccion={predictionData} />
        ) : (
          <ExistenciaView
            productos={products}
            form={form}
            setForm={setForm}
            handleAddProduct={handleAddProduct}
          />
        )}
      </main>
    </div>
  );
}
