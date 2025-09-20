# JWT Token Authentication System

## 📋 Overview

This document describes the comprehensive JWT (JSON Web Token) authentication system implemented for the Mechanic Shop API. The system provides secure user authentication, authorization, and session management.

## 🔧 Implementation Components

### **1. Enhanced Customer Model** (`app/models/customer.py`)
- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Password Methods**: 
  - `set_password(password)`: Hashes and stores password
  - `check_password(password)`: Verifies password against hash
- **Security**: Password hash is never exposed in API responses

### **2. Authentication Utilities** (`app/utils/auth.py`)

#### **`encode_token(customer_id)`**
- Creates JWT tokens with 24-hour expiration
- Includes customer ID as subject (sub) claim
- Uses app's SECRET_KEY for signing
- Returns signed JWT token string

#### **`decode_token(token)`**
- Validates JWT token signature and expiration
- Extracts customer ID from token payload
- Returns customer ID (int) or error message (str)
- Handles expired and invalid tokens gracefully

#### **`@token_required` Decorator**
- Validates Bearer token in Authorization header
- Extracts customer_id and injects into decorated function
- Verifies customer exists in database
- Returns 401 for invalid/missing tokens
- Returns 403 for authorization failures

### **3. Enhanced Customer Schema** (`app/schemas/customer.py`)

#### **CustomerSchema Updates**
- **Password Field**: Added with minimum 6 characters validation
- **Password Hashing**: Automatic password hashing on create/update
- **Security**: Password hash excluded from API responses
- **Validation**: Email format and length validation

#### **LoginSchema**
- **Minimal Schema**: Only email and password fields
- **Validation**: Email format and required field validation
- **Purpose**: Dedicated schema for login endpoints

### **4. Protected Routes** (`app/routes/customers.py`)

#### **Authentication Endpoints**

##### **`POST /customers/login`**
- **Purpose**: Authenticate customer and return JWT token
- **Input**: Email and password (JSON)
- **Output**: JWT token and customer info
- **Security**: Validates credentials before token generation
- **Error Handling**: Returns 401 for invalid credentials

##### **`GET /customers/my-tickets`** 🔒
- **Purpose**: Get service tickets for authenticated customer
- **Authentication**: Requires Bearer token
- **Authorization**: Only returns tickets for token owner
- **Security**: Token automatically provides customer identity

#### **Protected Customer Operations**

##### **`PUT /customers/{id}`** 🔒
- **Authentication**: Requires Bearer token
- **Authorization**: Customers can only update their own information
- **Security**: Prevents unauthorized profile modifications
- **Validation**: Uses CustomerSchema for data validation

##### **`DELETE /customers/{id}`** 🔒
- **Authentication**: Requires Bearer token
- **Authorization**: Customers can only delete their own account
- **Security**: Prevents unauthorized account deletion
- **Safety**: Permanent deletion with confirmation

## 🔐 Security Features

### **Password Security**
- **Hashing Algorithm**: Werkzeug PBKDF2 with salt
- **Storage**: Only password hashes stored, never plain passwords
- **Validation**: Minimum 6 character password requirement
- **API Response**: Password hashes never exposed in responses

### **JWT Token Security**
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 24-hour token lifetime
- **Secret Key**: Uses Flask app's SECRET_KEY for signing
- **Claims**: Standard JWT claims (exp, iat, sub)
- **Validation**: Signature and expiration validation

### **Authorization Controls**
- **Self-Service Only**: Users can only modify their own data
- **Resource Protection**: Critical operations require authentication
- **Error Responses**: Detailed error messages for debugging
- **Access Control**: 403 Forbidden for authorization failures

## 🚀 Usage Examples

### **1. Customer Registration**
```bash
curl -X POST http://127.0.0.1:5000/customers/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "555-0123",
    "password": "securepassword123"
  }'
```

### **2. Customer Login**
```bash
curl -X POST http://127.0.0.1:5000/customers/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "555-0123"
  }
}
```

### **3. Accessing Protected Routes**
```bash
curl -X GET http://127.0.0.1:5000/customers/my-tickets \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### **4. Updating Customer Information**
```bash
curl -X PUT http://127.0.0.1:5000/customers/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "first_name": "Johnny"
  }'
```

## 🔒 Protected Endpoints Summary

| Endpoint | Method | Authentication | Authorization | Purpose |
|----------|--------|----------------|---------------|---------|
| `/customers/login` | POST | ❌ | ❌ | User login |
| `/customers/my-tickets` | GET | ✅ | Self-only | Get own tickets |
| `/customers/{id}` | PUT | ✅ | Self-only | Update own profile |
| `/customers/{id}` | DELETE | ✅ | Self-only | Delete own account |

## 🛡️ Security Testing Results

### **✅ Authentication Tests**
- ✅ Customer registration with password hashing
- ✅ Successful login with correct credentials
- ✅ Login rejection with incorrect credentials
- ✅ JWT token generation and validation
- ✅ Token expiration handling

### **✅ Authorization Tests**
- ✅ Protected routes reject requests without tokens
- ✅ Protected routes accept valid Bearer tokens
- ✅ Users can only access their own data
- ✅ Cross-user access attempts properly blocked
- ✅ Invalid token formats properly rejected

### **✅ Security Features**
- ✅ Password hashing with secure algorithms
- ✅ JWT signature validation
- ✅ Token expiration enforcement
- ✅ Authorization boundary enforcement
- ✅ Error message security (no information leakage)

## 🚨 Security Considerations

### **Production Deployment**
- **SECRET_KEY**: Use strong, random secret key in production
- **HTTPS**: Always use HTTPS in production for token transmission
- **Token Storage**: Client should store tokens securely (httpOnly cookies recommended)
- **Key Rotation**: Implement periodic secret key rotation
- **Rate Limiting**: Already implemented to prevent brute force attacks

### **Token Management**
- **Expiration**: 24-hour tokens balance security and user experience
- **Refresh Tokens**: Consider implementing refresh tokens for longer sessions
- **Blacklisting**: Consider token blacklisting for logout functionality
- **Scope**: Consider adding role-based access control (RBAC)

### **Database Security**
- **Password Hashing**: Using industry-standard PBKDF2 with salt
- **Connection Security**: Use encrypted database connections in production
- **Data Protection**: Sensitive data encrypted at rest and in transit

## 🔄 Future Enhancements

### **Planned Security Features**
- **Role-Based Access Control**: Admin, mechanic, customer roles
- **Two-Factor Authentication**: SMS or TOTP-based 2FA
- **Session Management**: Active session tracking and management
- **Audit Logging**: Security event logging and monitoring
- **OAuth Integration**: Social login with Google, Facebook, etc.

### **Advanced Token Features**
- **Refresh Tokens**: Long-lived tokens for session management
- **Token Blacklisting**: Immediate token revocation capability
- **Scoped Tokens**: Granular permission-based tokens
- **Device Tracking**: Track and manage user devices

This JWT authentication system provides enterprise-grade security for the Mechanic Shop API while maintaining ease of use and developer-friendly integration patterns.