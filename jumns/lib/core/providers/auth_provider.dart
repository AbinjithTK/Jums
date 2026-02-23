import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_settings.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';
import '../services/revenuecat_service.dart';

/// Manages Cognito auth state for the entire app.
class AuthNotifier extends StateNotifier<AuthState> {
  final AuthService _auth;
  final RevenueCatService _rc;

  AuthNotifier(this._auth, this._rc) : super(const AuthState()) {
    _init();
  }

  Future<void> _init() async {
    state = state.copyWith(isLoading: true);
    try {
      final user = await _auth.restoreSession();
      if (user != null) {
        // Identify user in RevenueCat
        try { await _rc.logIn(user.sub); } catch (_) {}
        state = AuthState(
          status: AuthStatus.authenticated,
          user: user,
        );
      } else {
        state = const AuthState(status: AuthStatus.unauthenticated);
      }
    } catch (_) {
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> signIn({required String email, required String password}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final user = await _auth.signIn(email: email, password: password);
      if (user != null) {
        // Identify user in RevenueCat
        try { await _rc.logIn(user.sub); } catch (_) {}
        state = AuthState(status: AuthStatus.authenticated, user: user);
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'Sign in failed',
        );
      }
    } on CognitoUserNewPasswordRequiredException {
      state = state.copyWith(
        isLoading: false,
        error: 'New password required. Please reset your password.',
      );
    } on CognitoUserMfaRequiredException {
      state = state.copyWith(
        isLoading: false,
        error: 'MFA verification required.',
      );
    } on CognitoUserCustomChallengeException {
      state = state.copyWith(
        isLoading: false,
        error: 'Custom challenge required.',
      );
    } on CognitoUserConfirmationNecessaryException {
      state = state.copyWith(
        isLoading: false,
        error: 'CONFIRM_NEEDED',
      );
    } on CognitoClientException catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.message ?? 'Authentication failed',
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> signUp({
    required String email,
    required String password,
    String? name,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _auth.signUp(email: email, password: password, name: name);
      // Sign up succeeded — user needs to confirm email
      state = state.copyWith(
        isLoading: false,
        error: 'CONFIRM_NEEDED',
      );
    } on CognitoClientException catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.message ?? 'Sign up failed',
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<bool> confirmSignUp({
    required String email,
    required String code,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _auth.confirmSignUp(email: email, code: code);
      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Invalid confirmation code',
      );
      return false;
    }
  }

  Future<void> resendCode({required String email}) async {
    try {
      await _auth.resendConfirmation(email: email);
    } catch (_) {}
  }

  Future<void> signOut() async {
    await _auth.signOut();
    try { await _rc.logOut(); } catch (_) {}
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  Future<void> forgotPassword({required String email}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _auth.forgotPassword(email: email);
      state = state.copyWith(isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<bool> confirmForgotPassword({
    required String email,
    required String code,
    required String newPassword,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _auth.confirmForgotPassword(
        email: email,
        code: code,
        newPassword: newPassword,
      );
      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }
}

final authNotifierProvider =
    StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    ref.watch(authServiceProvider),
    ref.watch(revenueCatServiceProvider),
  );
});

/// Demo mode — bypasses Cognito auth for instant MVP testing.
final demoModeProvider = StateProvider<bool>((ref) => false);

// --- Server-side data providers (use JWT-authenticated API) ---

/// Settings provider that works in BOTH demo and auth modes.
final userSettingsProvider = FutureProvider<UserSettings?>((ref) async {
  final isDemoMode = ref.watch(demoModeProvider);
  final authState = ref.watch(authNotifierProvider);

  // In demo mode OR authenticated — try to fetch settings from backend
  if (isDemoMode || authState.status == AuthStatus.authenticated) {
    try {
      final api = ref.watch(apiClientProvider);
      final json = await api.get('/api/user-settings');
      if (json == null) return null;
      return UserSettings.fromJson(json as Map<String, dynamic>);
    } catch (_) {
      // Backend unreachable — return defaults
      return const UserSettings(id: '', userId: '');
    }
  }
  return null;
});

final subscriptionStatusProvider = FutureProvider<SubscriptionStatus>((ref) async {
  final authState = ref.watch(authNotifierProvider);
  if (authState.status != AuthStatus.authenticated) {
    return const SubscriptionStatus();
  }
  try {
    final api = ref.watch(apiClientProvider);
    final json = await api.get('/api/subscription/status');
    return SubscriptionStatus.fromJson(json as Map<String, dynamic>);
  } catch (_) {
    return const SubscriptionStatus();
  }
});

final accessCodeStatusProvider = FutureProvider<bool>((ref) async {
  final authState = ref.watch(authNotifierProvider);
  if (authState.status != AuthStatus.authenticated) return false;
  try {
    final api = ref.watch(apiClientProvider);
    final json = await api.get('/api/access-code/status');
    return (json as Map<String, dynamic>)['activated'] as bool? ?? false;
  } catch (_) {
    return false;
  }
});
