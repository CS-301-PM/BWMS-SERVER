# CBU Central Stores Management System

A blockchain-secured inventory and procurement system for Copperbelt University Central Stores.

## 🚀 Features

- **Multi-Role Authentication** (Stores Manager, Procurement Officer, CFO, Department Dean, Admin)
- **Blockchain-Secured Approvals** - Immutable logging of all decisions
- **3-Step Approval Workflow** - Stores → Procurement → CFO mandatory sequence
- **Real-Time Inventory Tracking** - With low stock alerts
- **QR Code Integration** - Physical item tracking
- **Role-Based Access Control** - Secure permissions system

## 🛠️ Tech Stack

- **Backend:** Django 4.2 + Django REST Framework
- **Database:** SQLite (Development), PostgreSQL (Production)
- **Blockchain:** Web3.py, Ethereum-compatible smart contracts
- **Authentication:** JWT Tokens
- **API:** RESTful architecture

## 📋 System Roles

### Stores Manager
- Approve/Reject department requests
- Initiate restock requests
- Manage inventory levels

### Procurement Officer  
- Execute supplier contracts
- Receive and verify orders
- Forecast demand

### CFO (Finance Manager)
- Final approval authority
- Budget allocation
- Financial oversight

### Department Dean
- Submit resource requests
- Track request status
- View request history

## 🚀 Installation

1. **Clone the repository**
   ```
   git clone https://github.com/your-username/cbu-central-stores-backend.git
   cd cbu-central-stores-backend
   ```

2. **Set up virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```
   python manage.py migrate
   ```

6. **Create superuser**
   ```
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```
   python manage.py runserver
   ```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:

```
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Blockchain (Optional - for simulation mode)
BLOCKCHAIN_RPC_URL=http://localhost:8545
CONTRACT_ADDRESS=0xYourContractAddress
STORE_MANAGER_PRIVATE_KEY=0xYourPrivateKey
```

## 📁 Project Structure

```
cbu-central-stores-backend/
├── authentication/     # User management & JWT auth
├── inventory/         # Product catalog & stock management
├── procurement_requests/  # Department requests
├── approvals/         # 3-step approval workflow
├── blockchain/        # Blockchain integration
├── config/            # Django project settings
├── utils/             # Utilities & helpers
└── manage.py          # Django management script
```

## 🔐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | User registration |
| `/api/auth/login/` | POST | User login |
| `/api/inventory/products/` | GET, POST | Product management |
| `/api/requests/requests/` | GET, POST | Department requests |
| `/api/approvals/approvals/` | GET, PATCH | Approval workflow |
| `/api/blockchain/status/` | GET | Blockchain status |

## 🚧 Development Status

✅ **Completed**
- User authentication & RBAC
- Inventory management API
- Approval workflow system
- Blockchain integration framework
- QR code support
- Data encryption

🔄 **In Progress**
- Offline capability & sync
- Expanded smart contracts
- Real-time WebSocket updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Acknowledgments

- Copperbelt University ICT Department
- Blockchain research team
- Software engineering contributors
```
