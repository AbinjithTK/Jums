import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Configuration for AWS Cognito — pass via --dart-define at build time:
///   flutter run \
///     --dart-define=COGNITO_USER_POOL_ID=us-east-1_xxx \
///     --dart-define=COGNITO_CLIENT_ID=xxx \
///     --dart-define=COGNITO_REGION=us-east-1
class CognitoConfig {
  static const String userPoolId = String.fromEnvironment(
    'COGNITO_USER_POOL_ID',
    defaultValue: '',
  );
  static const String clientId = String.fromEnvironment(
    'COGNITO_CLIENT_ID',
    defaultValue: '',
  );
  static const String region = String.fromEnvironment(
    'COGNITO_REGION',
    defaultValue: 'us-east-1',
  );
}

/// Persists Cognito tokens in secure storage so sessions survive app restarts.
class _SecureStorage extends CognitoStorage {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  final String _prefix;

  _SecureStorage({String prefix = 'cognito'}) : _prefix = prefix;

  @override
  Future<String?> getItem(String key) => _storage.read(key: '$_prefix.$key');

  @override
  Future<void> setItem(String key, value) =>
      _storage.write(key: '$_prefix.$key', value: value.toString());

  @override
  Future<void> removeItem(String key) => _storage.delete(key: '$_prefix.$key');

  @override
  Future<void> clear() async {
    final all = await _storage.readAll();
    for (final key in all.keys) {
      if (key.startsWith('$_prefix.')) {
        await _storage.delete(key: key);
      }
    }
  }
}

/// Represents the currently authenticated user.
class AuthUser {
  final String sub;
  final String email;
  final String? name;
  final bool emailVerified;

  const AuthUser({
    required this.sub,
    required this.email,
    this.name,
    this.emailVerified = false,
  });
}

/// Auth state exposed to the UI.
enum AuthStatus { unknown, authenticated, unauthenticated }

class AuthState {
  final AuthStatus status;
  final AuthUser? user;
  final String? error;
  final bool isLoading;

  const AuthState({
    this.status = AuthStatus.unknown,
    this.user,
    this.error,
    this.isLoading = false,
  });

  AuthState copyWith({
    AuthStatus? status,
    AuthUser? user,
    String? error,
    bool? isLoading,
  }) =>
      AuthState(
        status: status ?? this.status,
        user: user ?? this.user,
        error: error,
        isLoading: isLoading ?? this.isLoading,
      );
}

/// Service that wraps AWS Cognito operations.
class AuthService {
  late final CognitoUserPool _userPool;
  late final _SecureStorage _storage;
  CognitoUser? _cognitoUser;
  CognitoUserSession? _session;

  AuthService() {
    _storage = _SecureStorage();
    // If Cognito is not configured, pool will be non-functional but won't crash
    _userPool = CognitoUserPool(
      CognitoConfig.userPoolId.isEmpty ? 'placeholder' : CognitoConfig.userPoolId,
      CognitoConfig.clientId.isEmpty ? 'placeholder' : CognitoConfig.clientId,
      storage: _storage,
    );
  }

  /// Whether Cognito credentials have been configured via --dart-define.
  bool get isConfigured =>
      CognitoConfig.userPoolId.isNotEmpty && CognitoConfig.clientId.isNotEmpty;

  /// Returns the current valid JWT ID token, refreshing if needed.
  Future<String?> getIdToken() async {
    if (_session == null || !_session!.isValid()) {
      await _refreshSession();
    }
    return _session?.getIdToken().getJwtToken();
  }

  /// Returns the current valid JWT access token, refreshing if needed.
  Future<String?> getAccessToken() async {
    if (_session == null || !_session!.isValid()) {
      await _refreshSession();
    }
    return _session?.getAccessToken().getJwtToken();
  }

  /// Try to restore a previous session from secure storage.
  Future<AuthUser?> restoreSession() async {
    if (!isConfigured) return null;
    try {
      // Check if we have a stored username
      const storage = FlutterSecureStorage();
      final username = await storage.read(key: 'cognito.lastUser');
      if (username == null) return null;

      _cognitoUser = CognitoUser(username, _userPool, storage: _storage);
      _session = await _cognitoUser!.getSession();

      if (_session != null && _session!.isValid()) {
        return _getUserFromSession();
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  /// Sign up a new user with email and password.
  Future<bool> signUp({
    required String email,
    required String password,
    String? name,
  }) async {
    final attributes = [
      AttributeArg(name: 'email', value: email),
      if (name != null) AttributeArg(name: 'name', value: name),
    ];

    await _userPool.signUp(email, password, userAttributes: attributes);
    return true; // User created, needs confirmation
  }

  /// Confirm sign up with the verification code sent to email.
  Future<bool> confirmSignUp({
    required String email,
    required String code,
  }) async {
    final user = CognitoUser(email, _userPool, storage: _storage);
    return await user.confirmRegistration(code);
  }

  /// Resend the confirmation code.
  Future<void> resendConfirmation({required String email}) async {
    final user = CognitoUser(email, _userPool, storage: _storage);
    await user.resendConfirmationCode();
  }

  /// Sign in with email and password.
  Future<AuthUser?> signIn({
    required String email,
    required String password,
  }) async {
    _cognitoUser = CognitoUser(email, _userPool, storage: _storage);
    final authDetails = AuthenticationDetails(
      username: email,
      password: password,
    );

    _session = await _cognitoUser!.authenticateUser(authDetails);

    if (_session != null && _session!.isValid()) {
      // Persist the username for session restore
      const storage = FlutterSecureStorage();
      await storage.write(key: 'cognito.lastUser', value: email);
      return _getUserFromSession();
    }
    return null;
  }

  /// Sign out and clear stored tokens.
  Future<void> signOut() async {
    if (_cognitoUser != null) {
      await _cognitoUser!.signOut();
    }
    _session = null;
    _cognitoUser = null;
    await _storage.clear();
    const storage = FlutterSecureStorage();
    await storage.delete(key: 'cognito.lastUser');
  }

  /// Initiate forgot password flow.
  Future<void> forgotPassword({required String email}) async {
    final user = CognitoUser(email, _userPool, storage: _storage);
    await user.forgotPassword();
  }

  /// Confirm new password with the reset code.
  Future<bool> confirmForgotPassword({
    required String email,
    required String code,
    required String newPassword,
  }) async {
    final user = CognitoUser(email, _userPool, storage: _storage);
    return await user.confirmPassword(code, newPassword);
  }

  // --- Private helpers ---

  Future<void> _refreshSession() async {
    if (_cognitoUser == null) return;
    try {
      _session = await _cognitoUser!.getSession();
    } catch (_) {
      _session = null;
    }
  }

  AuthUser? _getUserFromSession() {
    if (_session == null) return null;
    final idToken = _session!.getIdToken();
    final payload = idToken.payload;
    return AuthUser(
      sub: payload['sub'] as String? ?? '',
      email: payload['email'] as String? ?? '',
      name: payload['name'] as String?,
      emailVerified: payload['email_verified'] as bool? ?? false,
    );
  }
}

/// Singleton provider for the auth service.
final authServiceProvider = Provider<AuthService>((ref) => AuthService());
