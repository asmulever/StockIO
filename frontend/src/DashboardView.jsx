import React, { useRef, useEffect, useState, useMemo } from "react";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { login, getAllProducts, addProduct, predictStock, getAllstockMoves,getPredicion } from "./api";
import "./index.css";

/* ──────────────────────────────────────────────────────────── */
/* 🔧 Función utilitaria: agrupa cantidades por mes‑año         */
/* ──────────────────────────────────────────────────────────── */
function agruparPorMes(movimientos) {  
  if (!movimientos || movimientos.length === 0) return [];
  
  const acumulado = movimientos.reduce((acc, movs) => {
    // Asegúrate que estos campos coincidan con tu API real
    const fecha = new Date(movs.date);
    if (isNaN(fecha.getTime())) return acc; // Fecha inválida
    
    const key = `${fecha.getUTCFullYear()}-${String(fecha.getUTCMonth() + 1).padStart(2, "0")}`;
    const cantidad = movs.quantity ?? 0;
    acc[key] = (acc[key] || 0) + cantidad;
    return acc;
  }, {});

  return Object.entries(acumulado)
    .map(([key, existencia]) => {
      const [y, m] = key.split("-").map(Number);
      const mesNombre = new Date(y, m - 1, 1)
        .toLocaleString("es", { month: "short" })
        .replace(/^\w/, (c) => c.toUpperCase());
      return { mes: mesNombre, existencia };
    })
    .sort((a, b) => a.mes.localeCompare(b.mes, "es"));
}

/* ──────────────────────────────────────────────────────────── */
/* 🧩 Componente principal                                      */
/* ──────────────────────────────────────────────────────────── */
export default function DashboardView() {
  const [existenciaPorMes, setExistenciaPorMes] = useState([]);  
  const [productos, setProductos] = useState([]); // Datos transformados para tabla
  const [prediccion, setPrediccion] = useState([]);      
  const loaded = useRef(false);  

  useEffect(() => {
    if (loaded.current) return;
    loaded.current = true;

    // ──────── 1.  Cargar productos reales ────────────────────────────────   
    async function fetchProductos() {
      try {
        const token = localStorage.getItem("token"); // o tu gestor de auth
        const products = await getAllProducts(token); // GET /api/products
        
        const MovStock = await getAllstockMoves(token);

        const Predict = await getPredicion(token);
        setPrediccion(Predict);

        const agrupado = agruparPorMes(MovStock);        
        setExistenciaPorMes(agrupado);       

        const rows = products.map((p) => ({
          id: p.product_id,
          nombre: p.product_name,
          cantidad: p.stk_qty ?? 0,
          categoria: p.category,
        }));

        setProductos(rows);
      } catch (err) {
        console.log("Error al cargar productos", err);
      }
    }

    fetchProductos();  
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>

      <section style={{ marginBottom: "40px" }}>
        <h2>Productos en Existencia</h2>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #ddd" }}>
              <th style={{ textAlign: "left", padding: "8px" }}>ID</th>
              <th style={{ textAlign: "left", padding: "8px" }}>Nombre</th>
              <th style={{ textAlign: "right", padding: "8px" }}>Cantidad</th>
              <th style={{ textAlign: "right", padding: "8px" }}>Categoria</th>
            </tr>
          </thead>
          <tbody>
            {productos.map((p) => (
              <tr key={p.id} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: "8px" }}>{p.id}</td>
                <td style={{ padding: "8px" }}>{p.nombre}</td>
                <td style={{ padding: "8px", textAlign: "right" }}>
                  {p.cantidad}
                </td>
                <td style={{ padding: "8px", textAlign: "right" }}>
                  {p.categoria}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

     <section style={{ display: 'flex', gap: '40px' }}>
        <div>
          <h3>Total de Productos en Existencia por Mes</h3>
          <BarChart width={400} height={300} data={existenciaPorMes}>
            <CartesianGrid stroke="#ccc" />
            <XAxis dataKey="mes" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="existencia" fill="#8884d8" />
          </BarChart>
        </div>
      
        <div>
          <h3>Predicción de compras de Producto</h3>
          <LineChart width={400} height={300} data={prediccion}>
            <CartesianGrid stroke="#ccc" />
            <XAxis dataKey="producto" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="prediccion" stroke="#82ca9d" />
          </LineChart>
        </div>
      </section>
    </div>
  );
}
