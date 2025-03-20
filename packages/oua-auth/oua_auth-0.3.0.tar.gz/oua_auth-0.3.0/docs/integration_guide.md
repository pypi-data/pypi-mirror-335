# Integration Guide for OUA Authentication

This guide provides detailed information on integrating the Organization Unified Access Authentication (OUA Auth) system with various types of applications. Follow these steps to incorporate OUA Auth into your project.

## Basic Django Integration

### Step 1: Installation

Install the OUA Auth package using pip:

```bash
pip install oua-auth
```

Add it to your `requirements.txt` or `pyproject.toml` for future installations:

```
oua-auth==1.0.0  # Replace with actual version
```

### Step 2: Configure Settings

Add the required settings to your Django `settings.py` file:

```python
# OUA SSO Settings
OUA_SSO_URL = 'https://your-sso-server.com'
OUA_PUBLIC_KEY = '''
-----BEGIN PUBLIC KEY-----
Your SSO public key here
-----END PUBLIC KEY-----
'''
OUA_CLIENT_ID = 'your-client-id'

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'oua_auth',
]

# Add the middleware
MIDDLEWARE = [
    # ... existing middleware ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Required before OUA middleware
    'oua_auth.OUAAuthMiddleware',
    'oua_auth.OUAUserMiddleware',  # Optional: For user data sync
]

# Add the authentication backend
AUTHENTICATION_BACKENDS = [
    'oua_auth.OUAAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

### Step 3: Apply Migrations

Apply the database migrations for the OUA Auth models:

```bash
python manage.py migrate oua_auth
```

### Step 4: Protect Views

Use Django's standard authentication decorators to protect your views:

```python
from django.contrib.auth.decorators import login_required

@login_required
def protected_view(request):
    return render(request, 'protected_page.html', {'user': request.user})
```

For class-based views:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class ProtectedView(LoginRequiredMixin, TemplateView):
    template_name = 'protected_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
```

### Step 5: Access Token Data

Access the token claims from the request object:

```python
def my_view(request):
    if request.user.is_authenticated:
        # Access token claims
        user_roles = request.oua_claims.get('roles', [])
        user_groups = request.oua_claims.get('groups', [])

        # Check for specific permissions
        is_admin = 'admin' in user_roles

        # Access the raw token if needed
        raw_token = request.oua_token

        return render(request, 'my_template.html', {
            'user': request.user,
            'roles': user_roles,
            'is_admin': is_admin,
        })
```

## Django REST Framework Integration

### Step 1: Configure DRF Settings

Add the OUA JWT Authentication class to your REST Framework settings:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oua_auth.OUAJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Optional: Fallback
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Step 2: Create Protected API Views

Create API views that require authentication:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': f'Hello, {request.user.email}!',
            'roles': request.oua_claims.get('roles', []),
        })
```

Using viewsets:

```python
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from myapp.models import MyModel
from myapp.serializers import MyModelSerializer

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_info(self, request):
        return Response({
            'user': request.user.email,
            'claims': request.oua_claims,
        })
```

### Step 3: Custom Permissions Based on Token Claims

Create custom permissions based on token claims:

```python
from rest_framework import permissions

class HasAdminRole(permissions.BasePermission):
    """
    Permission to check if user has admin role in token claims.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        roles = request.oua_claims.get('roles', [])
        return 'admin' in roles

class InAllowedGroups(permissions.BasePermission):
    """
    Permission to check if user belongs to specific groups.
    """
    def __init__(self, allowed_groups):
        self.allowed_groups = allowed_groups

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        user_groups = request.oua_claims.get('groups', [])
        return any(group in self.allowed_groups for group in user_groups)
```

Usage:

```python
class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated, HasAdminRole]

    def get(self, request):
        return Response({'message': 'Admin access granted'})

class GroupRestrictedView(APIView):
    permission_classes = [IsAuthenticated, InAllowedGroups(['developers', 'managers'])]

    def get(self, request):
        return Response({'message': 'Group access granted'})
```

## Frontend Integration

### Step 1: Configure Frontend Authentication

Use a library compatible with your frontend framework for JWT authentication:

#### React Example with `react-auth-kit`:

```bash
npm install react-auth-kit
```

```jsx
// src/App.js
import React from "react";
import { AuthProvider, useAuthHeader } from "react-auth-kit";
import axios from "axios";

// Configure axios to use the token
const authAxios = axios.create();
authAxios.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

function App() {
  return (
    <AuthProvider
      authType="localstorage"
      authName="auth_token"
      cookieDomain={window.location.hostname}
      cookieSecure={window.location.protocol === "https:"}
    >
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <RequireAuth loginPath="/login">
                <Dashboard />
              </RequireAuth>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

// Login component
function LoginPage() {
  const login = useSignIn();

  const handleLogin = async (credentials) => {
    try {
      // Get token from your SSO server
      const response = await axios.post(
        "https://your-sso-server.com/token",
        credentials
      );
      const { token, expiresIn } = response.data;

      // Store the token
      login({
        token,
        expiresIn,
        tokenType: "Bearer",
        authState: { email: credentials.email },
      });

      // Redirect to dashboard
      navigate("/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        handleLogin({
          email: e.target.email.value,
          password: e.target.password.value,
        });
      }}
    >
      <input name="email" type="email" placeholder="Email" />
      <input name="password" type="password" placeholder="Password" />
      <button type="submit">Login</button>
    </form>
  );
}

// Protected component
function Dashboard() {
  const [data, setData] = useState(null);
  const authHeader = useAuthHeader();

  useEffect(() => {
    // Call your Django API with the token
    const fetchData = async () => {
      try {
        const response = await axios.get("https://your-api.com/api/dashboard", {
          headers: {
            Authorization: authHeader(),
          },
        });
        setData(response.data);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
    };

    fetchData();
  }, [authHeader]);

  return (
    <div>
      <h1>Dashboard</h1>
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}
```

#### Vue.js Example:

```bash
npm install axios vue-jwt-decode
```

```javascript
// src/auth.js
import axios from "axios";
import router from "./router";

const AUTH_TOKEN_KEY = "auth_token";

export default {
  getToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  },

  saveToken(token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  },

  removeToken() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
  },

  isAuthenticated() {
    const token = this.getToken();
    return token !== null && token !== undefined;
  },

  setupInterceptors() {
    axios.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers["Authorization"] = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    axios.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        if (error.response.status === 401) {
          this.removeToken();
          router.push("/login");
        }
        return Promise.reject(error);
      }
    );
  },
};
```

### Step 2: Configure API Calls

Ensure all API calls include the authentication token:

```javascript
// api.js
import axios from "axios";

const API_URL = "https://your-api.com/api";

export default {
  getUserProfile() {
    return axios.get(`${API_URL}/user/profile`);
  },

  getProtectedData() {
    return axios.get(`${API_URL}/protected-data`);
  },

  updateUserProfile(profileData) {
    return axios.put(`${API_URL}/user/profile`, profileData);
  },
};
```

## Mobile App Integration

### Step 1: Obtain and Store JWT Token

#### Android (Kotlin) Example:

```kotlin
import android.content.Context
import android.content.SharedPreferences
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

// TokenManager for storing and retrieving the token
class TokenManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("AuthPrefs", Context.MODE_PRIVATE)
    private val tokenKey = "auth_token"

    fun saveToken(token: String) {
        prefs.edit().putString(tokenKey, token).apply()
    }

    fun getToken(): String? {
        return prefs.getString(tokenKey, null)
    }

    fun clearToken() {
        prefs.edit().remove(tokenKey).apply()
    }
}

// AuthInterceptor to add token to requests
class AuthInterceptor(private val tokenManager: TokenManager) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val originalRequest = chain.request()
        val token = tokenManager.getToken()

        if (token.isNullOrEmpty()) {
            return chain.proceed(originalRequest)
        }

        val newRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .build()

        return chain.proceed(newRequest)
    }
}

// API service setup with Retrofit
interface ApiService {
    @GET("user/profile")
    suspend fun getUserProfile(): Response<UserProfile>

    @GET("protected-data")
    suspend fun getProtectedData(): Response<ProtectedData>
}

// Setup Retrofit with authentication
fun createApiService(context: Context): ApiService {
    val tokenManager = TokenManager(context)
    val authInterceptor = AuthInterceptor(tokenManager)

    val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .build()

    val retrofit = Retrofit.Builder()
        .baseUrl("https://your-api.com/api/")
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    return retrofit.create(ApiService::class.java)
}
```

#### iOS (Swift) Example:

```swift
import Foundation

// TokenManager for storing and retrieving the token
class TokenManager {
    private let tokenKey = "auth_token"
    private let userDefaults = UserDefaults.standard

    func saveToken(_ token: String) {
        userDefaults.set(token, forKey: tokenKey)
    }

    func getToken() -> String? {
        return userDefaults.string(forKey: tokenKey)
    }

    func clearToken() {
        userDefaults.removeObject(forKey: tokenKey)
    }
}

// APIClient to make authenticated requests
class APIClient {
    private let baseURL = "https://your-api.com/api"
    private let tokenManager = TokenManager()

    func request<T: Decodable>(endpoint: String, method: String = "GET", body: Data? = nil, completion: @escaping (Result<T, Error>) -> Void) {
        guard let url = URL(string: baseURL + endpoint) else {
            completion(.failure(NSError(domain: "Invalid URL", code: -1, userInfo: nil)))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = method

        if let token = tokenManager.getToken() {
            request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = body
            request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let httpResponse = response as? HTTPURLResponse else {
                completion(.failure(NSError(domain: "Invalid response", code: -1, userInfo: nil)))
                return
            }

            if httpResponse.statusCode == 401 {
                // Token expired or invalid
                self.tokenManager.clearToken()
                completion(.failure(NSError(domain: "Authentication failed", code: 401, userInfo: nil)))
                return
            }

            guard let data = data else {
                completion(.failure(NSError(domain: "No data received", code: -1, userInfo: nil)))
                return
            }

            do {
                let decoder = JSONDecoder()
                let result = try decoder.decode(T.self, from: data)
                completion(.success(result))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }

    func getUserProfile(completion: @escaping (Result<UserProfile, Error>) -> Void) {
        request(endpoint: "/user/profile", completion: completion)
    }

    func getProtectedData(completion: @escaping (Result<ProtectedData, Error>) -> Void) {
        request(endpoint: "/protected-data", completion: completion)
    }
}
```

## Platform-specific Integration Examples

### Multi-server Microservices

When integrating OUA Auth with a microservices architecture:

1. **Configure Shared Token Verification**:

```python
# settings.py for each microservice
OUA_SSO_URL = 'https://your-sso-server.com'
OUA_PUBLIC_KEY = '''
-----BEGIN PUBLIC KEY-----
Your SSO public key here
-----END PUBLIC KEY-----
'''
OUA_CLIENT_ID = 'your-client-id'
```

2. **Centralized User Management**: Use a dedicated service for user management.

3. **Token Propagation**: Pass tokens between services:

```python
def call_other_service(request, service_url, method='GET', data=None):
    """Call another microservice while propagating the auth token."""
    headers = {}

    # Propagate the original token or use internal token
    if hasattr(request, 'oua_token'):
        headers['Authorization'] = f'Bearer {request.oua_token}'
    elif hasattr(request, 'internal_token'):
        headers['Authorization'] = f'Bearer {request.internal_token}'

    response = requests.request(
        method=method,
        url=service_url,
        headers=headers,
        json=data
    )

    return response
```

4. **Distributed Token Blacklisting**: Ensure blacklisted tokens are synchronized across services:

```python
# Use Redis for shared token blacklist
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

# Use shared database for BlacklistedToken model
DATABASES = {
    'default': {...},
    'auth_db': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'auth_db',
        'USER': 'auth_user',
        'PASSWORD': '****',
        'HOST': 'auth-db.your-domain.com',
    }
}

DATABASE_ROUTERS = ['your_project.routers.AuthRouter']

# In routers.py
class AuthRouter:
    """
    A router to control database operations for auth models.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'oua_auth':
            return 'auth_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'oua_auth':
            return 'auth_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'oua_auth':
            return db == 'auth_db'
        return None
```

### Single-page Applications (SPAs)

For SPAs, configure these additional settings:

```python
# settings.py
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://your-spa-domain.com",
]

# Additional middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware ...
]
```

### Third-party API Integration

When integrating with third-party APIs that need authentication:

```python
from oua_auth import OUAJWTAuthentication

def call_third_party_api(request, api_url):
    """Call a third-party API with your internal token."""
    # Generate an internal token for the third-party API
    internal_token = OUAJWTAuthentication.generate_internal_token(
        email=request.user.email,
        user_id=request.user.id,
        extra_claims={
            'scope': 'third-party-api',
            'roles': request.oua_claims.get('roles', [])
        }
    )

    headers = {
        'Authorization': f'Bearer {internal_token}',
        'Content-Type': 'application/json',
    }

    response = requests.get(api_url, headers=headers)
    return response
```

## Troubleshooting Common Integration Issues

### 1. Token Validation Failures

If token validation fails:

- Check that the public key format is correct and includes BEGIN/END markers
- Verify that the token is being passed correctly in the Authorization header
- Ensure the token hasn't expired
- Check for clock skew between servers

### 2. Cross-Origin (CORS) Issues

If you're experiencing CORS issues:

- Add the correct CORS configuration:

  ```python
  INSTALLED_APPS = [
      # ...
      'corsheaders',
  ]

  MIDDLEWARE = [
      'corsheaders.middleware.CorsMiddleware',
      # Must be placed before other middleware that can generate responses
      # ...
  ]

  CORS_ALLOWED_ORIGINS = [
      "https://example.com",
      "https://sub.example.com",
  ]
  ```

### 3. User Synchronization Problems

If user data isn't synchronizing properly:

- Ensure `OUAUserMiddleware` is properly configured
- Check token claims for required user fields
- Verify database permissions for user creation/updates

### 4. Integration Testing

Add integration tests for your authentication flow:

```python
from django.test import TestCase, Client
from unittest.mock import patch
import jwt
import datetime

class AuthIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.valid_token_payload = {
            'sub': '123',
            'email': 'test@example.com',
            'name': 'Test User',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }

    @patch('oua_auth.authentication.jwt.decode')
    def test_protected_view_with_valid_token(self, mock_decode):
        # Mock JWT decode to return a valid payload
        mock_decode.return_value = self.valid_token_payload

        # Make request with a fake token
        response = self.client.get(
            '/protected-view/',
            HTTP_AUTHORIZATION='Bearer fake.jwt.token'
        )

        # Check that the view is accessible
        self.assertEqual(response.status_code, 200)

    @patch('oua_auth.authentication.jwt.decode')
    def test_api_view_with_valid_token(self, mock_decode):
        # Mock JWT decode to return a valid payload
        mock_decode.return_value = self.valid_token_payload

        # Make request with a fake token
        response = self.client.get(
            '/api/protected-data/',
            HTTP_AUTHORIZATION='Bearer fake.jwt.token'
        )

        # Check that the API is accessible
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'email': 'test@example.com', 'name': 'Test User'}
        )
```

## Advanced Integration Scenarios

### Internal Services Communication

For secure service-to-service communication:

```python
from oua_auth import OUAJWTAuthentication

def service_call(service_name, endpoint, method='GET', data=None):
    """Make a secure service-to-service call."""
    # Generate a service-specific token
    service_token = OUAJWTAuthentication.generate_internal_token(
        email=f'{service_name}@internal',
        user_id=None,
        extra_claims={
            'service': service_name,
            'scope': 'internal',
        }
    )

    headers = {
        'Authorization': f'Bearer {service_token}',
        'Content-Type': 'application/json',
    }

    service_url = f"https://{service_name}.internal/{endpoint}"
    response = requests.request(
        method=method,
        url=service_url,
        headers=headers,
        json=data
    )

    return response
```

### Hybrid Authentication

Supporting both token and session authentication:

```python
# settings.py
AUTHENTICATION_BACKENDS = [
    'oua_auth.OUAAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    # ... other middleware ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oua_auth.OUAAuthMiddleware',
    # ... other middleware ...
]
```

In your view:

```python
def hybrid_auth_view(request):
    """View that supports both session and token authentication."""
    if request.user.is_authenticated:
        # User is authenticated via either method
        auth_method = 'token' if hasattr(request, 'oua_token') else 'session'

        return JsonResponse({
            'authenticated': True,
            'user': request.user.email,
            'method': auth_method
        })

    return JsonResponse({
        'authenticated': False
    }, status=401)
```

### Customizing User Creation

To customize how users are created or updated from token claims:

```python
# Create a custom middleware
from oua_auth.OUAUserMiddleware import OUAUserMiddleware

class CustomUserMiddleware(OUAUserMiddleware):
    def _create_or_update_user(self, email, claims):
        """Custom user creation/update logic."""
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            # Update existing user
            user.first_name = claims.get('given_name', '')
            user.last_name = claims.get('family_name', '')

            # Custom field updates
            if hasattr(user, 'department'):
                user.department = claims.get('department', '')

            if hasattr(user, 'employee_id'):
                user.employee_id = claims.get('employee_id', '')

            # Handle roles/permissions
            if 'admin' in claims.get('roles', []):
                user.is_staff = True

            user.save()
            return user

        except User.DoesNotExist:
            # Create new user with custom fields
            user = User.objects.create_user(
                email=email,
                username=claims.get('preferred_username', email),
                first_name=claims.get('given_name', ''),
                last_name=claims.get('family_name', ''),
            )

            # Set custom user profile data if available
            if hasattr(user, 'profile'):
                user.profile.department = claims.get('department', '')
                user.profile.phone = claims.get('phone', '')
                user.profile.save()

            return user
```

Register your custom middleware in settings.py:

```python
MIDDLEWARE = [
    # ... other middleware ...
    'your_app.middleware.CustomUserMiddleware',
    # ... other middleware ...
]
```

## Integration Examples by Framework

### Django Channels (WebSockets)

Authenticate WebSocket connections:

```python
# Authentication middleware for Django Channels
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from jose import jwt, JWTError
from django.conf import settings
from django.contrib.auth import get_user_model

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            # Authenticate the token
            user = await self.authenticate(token)
            if user:
                # Add the user to the scope
                scope['user'] = user

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def authenticate(self, token):
        try:
            # Verify the token
            payload = jwt.decode(
                token,
                settings.OUA_PUBLIC_KEY,
                algorithms=['RS256'],
                audience=settings.OUA_CLIENT_ID
            )

            # Get the user from the database
            User = get_user_model()
            user = User.objects.get(email=payload['email'])
            return user

        except (JWTError, User.DoesNotExist):
            return None
```

Configure in your `asgi.py`:

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from your_app.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    'websocket': JWTAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                your_app.routing.websocket_urlpatterns
            )
        )
    ),
})
```

### Flask Integration

For Flask applications:

```python
from flask import Flask, request, jsonify
from functools import wraps
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['OUA_PUBLIC_KEY'] = '''
-----BEGIN PUBLIC KEY-----
Your SSO public key here
-----END PUBLIC KEY-----
'''
app.config['OUA_CLIENT_ID'] = 'your-client-id'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check for token in headers
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Decode and verify the token
            payload = jwt.decode(
                token,
                app.config['OUA_PUBLIC_KEY'],
                algorithms=['RS256'],
                audience=app.config['OUA_CLIENT_ID']
            )

            # Add user info to request
            request.user = payload

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/protected')
@token_required
def protected():
    return jsonify({
        'message': 'This is a protected endpoint',
        'user': request.user['email']
    })

if __name__ == '__main__':
    app.run(debug=True)
```
