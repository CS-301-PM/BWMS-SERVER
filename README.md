


# Central Stores Blockchain System - Backend API

![Django](https://img.shields.io/badge/Django-4.2-brightgreen)
![DRF](https://img.shields.io/badge/DRF-3.14-blue)
![Web3.py](https://img.shields.io/badge/Web3.py-6.0-orange)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)

## 📌 API Base URL
```
http://localhost:8000/api/
```

## 🔐 Authentication
All endpoints require JWT authentication. Include the token in headers:
```
Authorization: Token YOUR_TOKEN_HERE
```

## 🧑‍💻 Test Accounts
| Role              | Username  | Password | Department   | Permissions |
|-------------------|-----------|----------|--------------|-------------|
| Admin             | `admin`   | `admin123` | -            | Full Acess to the System   |
| Manager           | `manager1`| `pass123` | -            | Approve/ Verify |
| Central Staff     | `staff1`  | `pass123` | Warehouse    | Move Stock / Report Damage |
| Department Staff  | `dept1`   | `pass123` | Engineering  | Create Requests |
| Supplier          | `supplier1`| `pass123` | -          | Submit Deliveries |

**Get Token:**
```
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "dept1", "password": "pass123"}'
```

## 📡 Key Endpoints

### Inventory Management
| Endpoint                | Method | Auth       | Description                     |
|-------------------------|--------|------------|---------------------------------|
| `/stock-items/`         | GET    | All        | List all inventory items        |
| `/stock-items/`         | POST   | Staff+     | Add new stock item              |
| `/stock-requests/`      | GET    | All        | List requests                   |
| `/department-requests/` | POST   | Dept Staff | Create new request              |

### Blockchain Actions
| Endpoint                | Method | Auth       | Description                     |
|-------------------------|--------|------------|---------------------------------|
| `/stock-movements/`     | POST   | Staff      | Log stock movement (blockchain) |
| `/supplier-deliveries/` | POST   | Supplier   | Submit delivery                 |

## 🛠️ Frontend Integration Guide

### 1. Install Dependencies
```
npm install axios jwt-decode
```

### 2. API Service Example (TypeScript)
```
// src/services/api.ts
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export const fetchStockItems = async () => {
  const response = await api.get('/stock-items/');
  return response.data;
};

export const createRequest = async (data: {
  item_id: number;
  quantity: number;
  urgent: boolean;
}) => {
  return await api.post('/department-requests/', data);
};
```

### 3. Vite Environment Variables
Create `.env.development`:
```
VITE_API_URL=http://localhost:8000/api
```

## 🧪 Testing the API
### Using cURL:
```
# Get stock items
curl http://localhost:8000/api/stock-items/ \
  -H "Authorization: Token YOUR_TOKEN"

# Create request (Dept Staff)
curl -X POST http://localhost:8000/api/department-requests/ \
  -H "Authorization: Token DEPT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "quantity": 5, "urgent": false}'
```

## 🔗 Response Format
All responses follow this structure:
```
interface ApiResponse<T> {
  data: T;
  status: number;
}

// Example response
interface StockItem {
  id: number;
  name: string;
  quantity: number;
  location: string;
}
```

## 🚀 Running the Backend
```
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## 📚 Full API Documentation
[View Swagger Docs](http://localhost:8000/swagger/) (After enabling DRF Spectacular)
```
