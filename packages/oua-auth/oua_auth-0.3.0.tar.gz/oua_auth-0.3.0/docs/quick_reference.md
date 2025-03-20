# OUA Authentication Quick Reference Guide

This quick reference provides concise examples for common tasks when working with the OUA Authentication system.

## Installation

```bash
pip install oua-auth
```

## Configuration

### Minimal Configuration

```python
# settings.py
OUA_SSO_URL = 'https://sso.example.com'
OUA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----"""
OUA_CLIENT_ID = 'your-client-id'

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'oua_auth',
]

# Add middleware
MIDDLEWARE = [
    # ... other middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oua_auth.OUAAuthMiddleware',
    # ... other middleware
]

# Add authentication backend
AUTHENTICATION_BACKENDS = [
    'oua_auth.OUAAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

### Django REST Framework Configuration

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oua_auth.OUAJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## Usage Examples

### Protect a Django View

```python
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def protected_view(request):
    return JsonResponse({
        'message': 'This is protected content',
        'user': request.user.username,
    })
```

### Protect a Django REST Framework API

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'This is protected API content',
            'user': request.user.username,
        })
```

### Access Token Claims

```python
def view_with_token_data(request):
    # Access the original token claims
    token_claims = request.token_claims

    # Example: check if user has specific role
    if 'roles' in token_claims and 'admin' in token_claims['roles']:
        # Do admin-specific things
        pass

    # Proceed with normal view logic
    return JsonResponse({'message': 'Success'})
```

### Use Internal Token

```python
from oua_auth.utils import create_internal_token

def service_to_service_call():
    # Create an internal token for service-to-service communication
    token = create_internal_token(
        user_id='service-account',
        additional_claims={'scope': 'read:data'}
    )

    # Use the token to call another service
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('https://api.example.com/data', headers=headers)
    return response.json()
```

### Blacklist a Token

```python
from oua_auth.models import BlacklistedToken

def logout_view(request):
    # Get the token from the request
    token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')

    if token:
        # Blacklist the token
        BlacklistedToken.add_token_to_blacklist(
            token=token,
            blacklisted_by=request.user.username,
            reason='User logout'
        )

    # Proceed with normal logout
    return JsonResponse({'message': 'Successfully logged out'})
```

## Frontend Integration

### React Example

```javascript
// api.js - API service configuration
import axios from "axios";

// Create axios instance
const api = axios.create({
  baseURL: "https://api.example.com",
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for handling auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Redirect to login or refresh token
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Authentication Hook (React)

```javascript
// useAuth.js - React hook for authentication
import { useState, useEffect, createContext, useContext } from "react";
import api from "./api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem("auth_token");
    if (token) {
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await api.get("/api/user/profile");
      setUser(response.data);
    } catch (error) {
      console.error("Failed to fetch user profile:", error);
      localStorage.removeItem("auth_token");
    } finally {
      setLoading(false);
    }
  };

  const login = (token) => {
    localStorage.setItem("auth_token", token);
    fetchUserProfile();
  };

  const logout = async () => {
    try {
      await api.post("/api/auth/logout");
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      localStorage.removeItem("auth_token");
      setUser(null);
      window.location.href = "/login";
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

## Mobile Integration

### Android (Kotlin) Example

```kotlin
// ApiService.kt
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.Interceptor

class TokenInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val token = SessionManager.getToken()
        val request = chain.request().newBuilder()

        if (token != null) {
            request.addHeader("Authorization", "Bearer $token")
        }

        return chain.proceed(request.build())
    }
}

object ApiClient {
    private const val BASE_URL = "https://api.example.com/"

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(TokenInterceptor())
        .build()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
}

// Usage in Repository
interface ApiService {
    @GET("protected/data")
    suspend fun getProtectedData(): Response<DataModel>
}

class Repository {
    private val apiService = ApiClient.retrofit.create(ApiService::class.java)

    suspend fun getProtectedData(): Result<DataModel> {
        return try {
            val response = apiService.getProtectedData()
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("API call failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### iOS (Swift) Example

```swift
// NetworkManager.swift
import Foundation

class NetworkManager {
    static let shared = NetworkManager()
    private let baseURL = "https://api.example.com"

    func request<T: Decodable>(
        endpoint: String,
        method: String = "GET",
        parameters: [String: Any]? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        guard let url = URL(string: baseURL + endpoint) else {
            completion(.failure(NSError(domain: "Invalid URL", code: -1, userInfo: nil)))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = method

        // Add token if available
        if let token = UserDefaults.standard.string(forKey: "authToken") {
            request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        // Add parameters for POST requests
        if let parameters = parameters, method == "POST" {
            do {
                request.httpBody = try JSONSerialization.data(withJSONObject: parameters)
                request.addValue("application/json", forHTTPHeaderField: "Content-Type")
            } catch {
                completion(.failure(error))
                return
            }
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -2, userInfo: nil)))
                return
            }

            do {
                let decodedResponse = try JSONDecoder().decode(T.self, from: data)
                completion(.success(decodedResponse))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}

// Usage in ViewModel
class UserViewModel {
    func fetchProtectedData(completion: @escaping (Result<DataModel, Error>) -> Void) {
        NetworkManager.shared.request(endpoint: "/protected/data", completion: completion)
    }

    func login(username: String, password: String, completion: @escaping (Bool) -> Void) {
        NetworkManager.shared.request(
            endpoint: "/auth/login",
            method: "POST",
            parameters: ["username": username, "password": password]
        ) { (result: Result<AuthResponse, Error>) in
            switch result {
            case .success(let response):
                UserDefaults.standard.set(response.token, forKey: "authToken")
                completion(true)
            case .failure:
                completion(false)
            }
        }
    }
}
```

## Common Patterns

### Custom Permission Based on Token Claims

```python
from rest_framework.permissions import BasePermission

class HasAdminRole(BasePermission):
    """
    Permission class to check if user has an admin role in their token.
    """
    def has_permission(self, request, view):
        # Check if request has token_claims attribute
        if not hasattr(request, 'token_claims'):
            return False

        # Check if roles claim exists and contains admin
        roles = request.token_claims.get('roles', [])
        return 'admin' in roles
```

### Custom User Creation from Token

```python
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def create_user_from_token(token_claims):
    """
    Custom function to create a user from token claims.
    """
    with transaction.atomic():
        # Extract data using configured field mappings
        email = token_claims.get(settings.OUA_USER_FIELD_MAPPINGS.get('email', 'email'))
        username = token_claims.get(settings.OUA_USER_FIELD_MAPPINGS.get('username', 'preferred_username'), email)

        # Create or update user
        user, created = User.objects.update_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': token_claims.get(settings.OUA_USER_FIELD_MAPPINGS.get('first_name', 'given_name'), ''),
                'last_name': token_claims.get(settings.OUA_USER_FIELD_MAPPINGS.get('last_name', 'family_name'), ''),
                'is_active': True,
            }
        )

        # Set admin status based on domain
        if '@admin.example.com' in email:
            user.is_staff = True
            user.is_superuser = True
            user.save()

        return user
```

### Rate Limiting Helper

```python
from django.core.cache import cache
from django.conf import settings
import time

def check_rate_limit(key, max_attempts=None, window=None):
    """
    Check if a rate limit has been exceeded.
    Returns (is_allowed, attempts, reset_time)
    """
    # Use settings or defaults
    max_attempts = max_attempts or getattr(settings, 'OUA_MAX_AUTH_FAILURES', 5)
    window = window or getattr(settings, 'OUA_AUTH_FAILURE_WINDOW', 300)  # 5 minutes

    cache_key = f"rate_limit:{key}"
    now = int(time.time())

    # Get current rate limit data or initialize
    rate_data = cache.get(cache_key)
    if not rate_data:
        rate_data = {
            'attempts': 0,
            'reset_at': now + window
        }

    # Check if window expired and reset if needed
    if now > rate_data['reset_at']:
        rate_data = {
            'attempts': 0,
            'reset_at': now + window
        }

    # Increment attempt counter
    rate_data['attempts'] += 1

    # Store updated data
    cache.set(cache_key, rate_data, window)

    # Return rate limit status
    is_allowed = rate_data['attempts'] <= max_attempts
    return is_allowed, rate_data['attempts'], rate_data['reset_at']
```

### Debugging Token Helper

```python
import base64
import json

def debug_token(token):
    """
    Inspect a JWT token without validation.
    Helps debugging token-related issues.
    """
    try:
        # Split token into header, payload, signature
        parts = token.split('.')
        if len(parts) != 3:
            return {'error': 'Invalid token format'}

        # Decode header
        header_data = parts[0] + '=' * (4 - len(parts[0]) % 4)  # Add padding
        header_bytes = base64.urlsafe_b64decode(header_data)
        header = json.loads(header_bytes)

        # Decode payload
        payload_data = parts[1] + '=' * (4 - len(parts[1]) % 4)  # Add padding
        payload_bytes = base64.urlsafe_b64decode(payload_data)
        payload = json.loads(payload_bytes)

        return {
            'header': header,
            'payload': payload,
            'signature_present': bool(parts[2])
        }
    except Exception as e:
        return {'error': str(e)}
```

## Useful URLs and Endpoints

### Common Admin URLs

- Admin Interface: `/admin/`
- Token Management: `/admin/oua_auth/blacklistedtoken/`
- User Management: `/admin/auth/user/`

### Common API Endpoints

- Protected API: `/api/protected/`
- User Profile: `/api/user/profile/`
- Logout: `/api/auth/logout/`

## Security Headers Reference

```python
# settings.py - Security Headers Configuration
OUA_SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Content-Security-Policy': "default-src 'self'; script-src 'self'; object-src 'none';",
    'Permissions-Policy': 'geolocation=(), camera=(), microphone=()',
    'Cache-Control': 'no-store, max-age=0',
}

# Enable HSTS (HTTPS Strict Transport Security)
OUA_ENABLE_HSTS = True
OUA_HSTS_SECONDS = 31536000  # 1 year
OUA_HSTS_INCLUDE_SUBDOMAINS = True
OUA_HSTS_PRELOAD = True
```
