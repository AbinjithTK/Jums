import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'auth_service.dart';

/// Central API client for the Jumns backend.
///
/// In demo mode (local dev), points at the local FastAPI server.
/// In production, uses Cognito JWT Bearer tokens for authentication.
///
/// Set the backend URL at build time:
///   flutter run --dart-define=API_BASE_URL=https://your-api-gateway-url.amazonaws.com/prod
class ApiClient {
  static const String _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  final http.Client _http;
  final AuthService? _auth;

  ApiClient({AuthService? auth, http.Client? client})
      : _auth = auth,
        _http = client ?? http.Client();

  Future<Map<String, String>> get _headers async {
    final token = _auth != null ? await _auth.getIdToken() : null;
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // --- Generic helpers ---

  Future<dynamic> get(String path, {Map<String, String>? query}) async {
    final uri = Uri.parse('$_baseUrl$path').replace(queryParameters: query);
    final res = await _http.get(uri, headers: await _headers);
    return _handleResponse(res);
  }

  Future<dynamic> post(String path, {Object? body}) async {
    final uri = Uri.parse('$_baseUrl$path');
    final res = await _http.post(uri, headers: await _headers, body: jsonEncode(body));
    return _handleResponse(res);
  }

  Future<dynamic> patch(String path, {Object? body}) async {
    final uri = Uri.parse('$_baseUrl$path');
    final res = await _http.patch(uri, headers: await _headers, body: jsonEncode(body));
    return _handleResponse(res);
  }

  Future<void> delete(String path) async {
    final uri = Uri.parse('$_baseUrl$path');
    final res = await _http.delete(uri, headers: await _headers);
    if (res.statusCode != 204 && res.statusCode != 200) {
      throw ApiException(res.statusCode, res.body);
    }
  }

  dynamic _handleResponse(http.Response res) {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      if (res.body.isEmpty) return null;
      return jsonDecode(res.body);
    }
    throw ApiException(res.statusCode, res.body);
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String body;
  ApiException(this.statusCode, this.body);

  @override
  String toString() => 'ApiException($statusCode): $body';
}

/// In demo mode, create ApiClient without auth (local server doesn't need it).
/// In production, create with AuthService for Cognito JWT tokens.
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});
