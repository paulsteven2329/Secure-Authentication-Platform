# Secure Authentication Platform – Full-Stack Project Walkthrough  
**December 2025**

## Project Overview
A **production-grade secure authentication and authorization platform** built from scratch. This full-stack application provides a complete user authentication system suitable for real-world applications such as banking, e-commerce, or SaaS products.

**Key Features**:
- Email/password registration & login
- JWT with access + refresh tokens
- Token revocation & session management
- Role-Based Access Control (RBAC)
- OAuth2 login (Google & GitHub)
- Rate limiting to prevent brute-force attacks
- Secure token storage on mobile
- Auto token refresh

## Tech Stack

### Backend (FastAPI – Python)
- **Framework**: FastAPI (high performance, async-ready)
- **Database**: PostgreSQL (SQLAlchemy ORM + Alembic migrations)
- **Cache/Blacklist**: Redis (token revocation & rate limiting)
- **Authentication**: PyJWT, passlib (bcrypt), Authlib (OAuth2)
- **Rate Limiting**: fastapi-limiter
- **Containerization**: Docker Compose (PostgreSQL + Redis)

### Frontend (Flutter – Cross-Platform Mobile)
- **Framework**: Flutter (Android & iOS)
- **State Management**: flutter_bloc + equatable
- **HTTP Client**: Dio (with interceptors for auto-refresh)
- **Secure Storage**: flutter_secure_storage (Keychain/Keystore)
- **OAuth Providers**: google_sign_in, oauth2_client (GitHub)
- **Architecture**: Clean BLoC pattern with Repository layer

## Architecture & Module Flow

### Backend Modules
- **Core Security**: JWT creation, refresh tokens, revocation using Redis blacklist
- **Dependencies**: Centralized `get_current_user`, `get_db`, rate limiters
- **Routers**:
  - `/auth/register`, `/auth/login` (with rate limiting)
  - `/auth/refresh`, `/auth/logout`
  - `/auth/google`, `/auth/github` (OAuth2 flows)
  - `/protected/me`, `/protected/admin` (RBAC protected)
- **Database**: `users` table (email, hashed_password, role, etc.)
- **Migrations**: Alembic for schema management

### Frontend Modules
- **BLoC Layer**: AuthBloc managing states (Loading, Authenticated, Error, etc.)
- **Repository**: AuthRepository handling all API calls and secure token storage
- **Interceptors**: Auto-add Bearer token + auto-refresh on 401
- **Screens**:
  - LoginScreen: Email/password + Google/GitHub buttons
  - HomeScreen: Displays user info + logout
- **Secure Storage**: Tokens stored in device Keychain/Keystore
- **Auto Login**: On app start, checks stored token and validates

## Key Security Features
- Short-lived access tokens (15 min) + long-lived refresh tokens (7 days)
- Token revocation via Redis blacklist
- Rate limiting on login (5 attempts/min)
- Password hashing with bcrypt
- Secure token storage on mobile
- Auto token refresh on expiry
- RBAC ready (admin routes protected)
- OAuth2 with Google & GitHub

## Testing & Validation
- **Backend**: Tested via Swagger UI (`/docs`)
  - Registration, login, protected routes, rate limiting, logout
- **Database**: Verified records in PostgreSQL container
- **Frontend**: Full flow tested on Android device
  - Register → Login → Auto-login → Logout
  - Google & GitHub sign-in (with deep linking)

## Deployment Setup
- Docker Compose for PostgreSQL + Redis
- Backend runs on Uvicorn
- Frontend builds to APK (ready for Android)

## What I Learned
- Deep dive into JWT, refresh tokens, and revocation strategies
- Secure mobile token handling and auto-refresh
- OAuth2 flows for mobile apps
- Clean architecture with BLoC and Repository pattern
- Handling real-world dependency issues (Python 3.12, bcrypt, AGP 8+)

**Tech Stack Summary**:  
Flutter • FastAPI • PostgreSQL • Redis • JWT • OAuth2 • Docker • BLoC • Dio

GitHub repo and demo APK available on request!

#FullStack #Flutter #FastAPI #Authentication #CyberSecurity #MobileDevelopment #Backend #OAuth2 #JWT #Redis #PostgreSQL #Docker #SoftwareEngineering