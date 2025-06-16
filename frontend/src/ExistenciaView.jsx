import React, { useState } from "react";

export default function ExistenciaView({ productos, form, setForm, handleAddProduct }) {
  const [salida, setSalida] = useState({ id: "", cantidad: 0 });

  function registrarSalida(e) {
    e.preventDefault();
    const producto = productos.find(p => p.product_id === salida.id);
    if (!producto) return alert("Producto no encontrado");
    if (salida.cantidad <= 0) return alert("Cantidad inválida");

    producto.stock = (producto.stock || 0) - salida.cantidad; // Simulación local
    alert(`Salida registrada para "${producto.product_name}"`);
    setSalida({ id: "", cantidad: 0 });
  }

  const inputStyle = {
    width: "100%",
    marginBottom: "10px",
    padding: "8px",
    borderRadius: "4px",
    border: "1px solid #ccc"
  };

  const buttonStyle = {
    backgroundColor: "#2d87f0",
    color: "#fff",
    border: "none",
    padding: "10px",
    borderRadius: "4px",
    cursor: "pointer",
    width: "100%"
  };

  return (
    <div>
      <h2 style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "20px" }}>
        Gestión de Existencias
      </h2>

      {/* Alta de producto */}
      <form onSubmit={handleAddProduct} autoComplete="off" style={{
        backgroundColor: "#fff",
        padding: "20px",
        borderRadius: "8px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
        marginBottom: "30px",
        maxWidth: "400px"
      }}>
        <h3 style={{ marginBottom: "10px" }}>Agregar nuevo producto</h3>

        <input placeholder="Nombre del producto" value={form.product_name} onChange={(e) => setForm({ ...form, product_name: e.target.value })} required style={inputStyle} />

        <input placeholder="SKU" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} required style={inputStyle} />

        <input placeholder="Unidad de medida" value={form.unit_of_measure} onChange={(e) => setForm({ ...form, unit_of_measure: e.target.value })} required style={inputStyle} />

        <input type="number" placeholder="Costo" value={form.cost} onChange={(e) => setForm({ ...form, cost: parseFloat(e.target.value) || 0 })} required style={inputStyle} />

        <input type="number" placeholder="Precio de venta" value={form.sale_price} onChange={(e) => setForm({ ...form, sale_price: parseFloat(e.target.value) || 0 })} required style={inputStyle} />

        <input placeholder="Categoría" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required style={inputStyle} />

        <input placeholder="Ubicación" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} required style={inputStyle} />

        <button type="submit" style={buttonStyle}>Agregar producto</button>
      </form>

      {/* Salida de producto */}
      <form onSubmit={registrarSalida} autoComplete="off" style={{
        backgroundColor: "#fff",
        padding: "20px",
        borderRadius: "8px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
        maxWidth: "400px"
      }}>
        <h3 style={{ marginBottom: "10px" }}>Registrar salida</h3>
        <select
          value={salida.id}
          onChange={(e) => setSalida({ ...salida, id: e.target.value })}
          required
          style={inputStyle}
        >
          <option value="">Seleccione un producto</option>
          {productos.map(p => (
            <option key={p.product_id} value={p.product_id}>
              {p.product_name} (Stock: {p.stock ?? 0})
            </option>
          ))}
        </select>
        <input
          type="number"
          placeholder="Cantidad a descontar"
          value={salida.cantidad}
          onChange={(e) => setSalida({ ...salida, cantidad: parseInt(e.target.value) || 0 })}
          required
          style={inputStyle}
        />
        <button type="submit" style={{
          backgroundColor: "#e67e22",
          color: "#fff",
          border: "none",
          padding: "10px",
          borderRadius: "4px",
          cursor: "pointer",
          width: "100%"
        }}>
          Registrar salida
        </button>
      </form>
    </div>
  );
}
