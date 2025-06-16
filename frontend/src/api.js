const API_BASE_URL = 'http://localhost:5000/api';

async function handleResponse(response) {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({
            message: response.statusText
        }));
        throw new Error(errorData.error || errorData.message || 'Request failed');
    }
    return response.json();
}

export async function login(username, password) {
    const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    return handleResponse(response);
}

export async function getAllProducts(token) {  
    const response = await fetch(`${API_BASE_URL}/get_products`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        }
    });    
    return handleResponse(response);
}

export async function getAllstockMoves(token) {  
    const response = await fetch(`${API_BASE_URL}/get_stocks`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        }
    });    
    return handleResponse(response);
}

export async function getPredicion(token){
    
    const response = await fetch(`${API_BASE_URL}/get_prediction`, {
         method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        }
    });    
    return handleResponse(response);
}

export async function addProduct(product, token) {
    
    const response = await fetch(`${API_BASE_URL}/product`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(product)
    });
    return handleResponse(response);
}

export async function updateProduct(productId, updates, token) {
    const response = await fetch(`${API_BASE_URL}/product/${productId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(updates)
    });
    return handleResponse(response);
}

export async function predictStock(productId, token) {
  const res = await fetch(`${API_BASE_URL}/${productId}`, {
    credentials: 'include',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) throw new Error('Error en predicción');
  return res.json(); // [{ mes: "Ene", valor: 10 }, ...]
}