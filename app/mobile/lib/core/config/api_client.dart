import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'api_config.dart';

class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class AuthTokens {
  const AuthTokens({required this.accessToken, required this.refreshToken});

  final String accessToken;
  final String refreshToken;
}

class ApiClient {
  ApiClient({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage(),
        _dio = Dio(BaseOptions(
          baseUrl: ApiConfig.apiUrl,
          connectTimeout: const Duration(seconds: 20),
          sendTimeout: const Duration(minutes: 2),
          receiveTimeout: const Duration(seconds: 30),
          headers: {'Accept': 'application/json'},
        )) {
    _dio.interceptors.add(QueuedInterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: _accessTokenKey);
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        if (kDebugMode) {
          debugPrint('LabelSetu API ${options.method} ${options.path}');
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (kDebugMode) {
          debugPrint(
            'LabelSetu API error ${error.response?.statusCode ?? 'network'} '
            '${error.requestOptions.method} ${error.requestOptions.path}',
          );
        }
        if (error.response?.statusCode == 401 &&
            error.requestOptions.extra['retried'] != true &&
            await _refresh()) {
          final request = error.requestOptions;
          request.extra['retried'] = true;
          try {
            final response = await _dio.fetch<dynamic>(request);
            handler.resolve(response);
            return;
          } on DioException catch (retryError) {
            handler.next(retryError);
            return;
          }
        }
        handler.next(error);
      },
    ));
  }

  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  final FlutterSecureStorage _storage;
  final Dio _dio;

  Future<AuthTokens> login(String email, String password) async {
    final response = await _request(() => _dio.post<Map<String, dynamic>>(
          '/auth/login',
          data: {'email': email, 'password': password},
        ));
    final data = response.data!;
    final tokens = AuthTokens(
      accessToken: data['access_token'] as String,
      refreshToken: data['refresh_token'] as String,
    );
    await _saveTokens(tokens);
    return tokens;
  }

  Future<Map<String, dynamic>> loginAndVerify(
    String email,
    String password,
  ) async {
    await login(email, password);
    try {
      return await currentUser();
    } on ApiException {
      await logout();
      rethrow;
    }
  }

  Future<Map<String, dynamic>> currentUser() async {
    final response = await _request(() => _dio.get<Map<String, dynamic>>('/auth/me'));
    return response.data!;
  }

  Future<void> logout() => _storage.deleteAll();

  Future<Map<String, dynamic>> createInspection(
    Map<String, dynamic> payload,
  ) async {
    final response = await _request(() => _dio.post<Map<String, dynamic>>(
          '/inspections',
          data: payload,
        ));
    return response.data!;
  }

  Future<Map<String, dynamic>> uploadInspectionImage(
    String inspectionId,
    String imagePath, {
    double? latitude,
    double? longitude,
  }) async {
    final form = FormData.fromMap({
      'file': await MultipartFile.fromFile(imagePath),
      if (latitude != null) 'gps_latitude': latitude,
      if (longitude != null) 'gps_longitude': longitude,
    });
    final response = await _request(() => _dio.post<Map<String, dynamic>>(
          '/inspections/$inspectionId/images/direct-upload',
          data: form,
        ));
    return response.data ?? <String, dynamic>{};
  }

  Future<Map<String, dynamic>> createSession(
    Map<String, dynamic> payload,
  ) async {
    final response = await _request(() => _dio.post<Map<String, dynamic>>(
          '/inspection-sessions',
          data: payload,
        ));
    return response.data!;
  }

  Future<Map<String, dynamic>> uploadSessionImage(
    String sessionId,
    String imagePath, {
    double? latitude,
    double? longitude,
  }) async {
    final form = FormData.fromMap({
      'file': await MultipartFile.fromFile(imagePath),
      if (latitude != null) 'gps_latitude': latitude,
      if (longitude != null) 'gps_longitude': longitude,
    });
    final response = await _request(() => _dio.post<Map<String, dynamic>>(
          '/inspection-sessions/$sessionId/images/direct-upload',
          data: form,
        ));
    return response.data ?? <String, dynamic>{};
  }

  Future<Map<String, dynamic>> session(String sessionId) async {
    final response = await _request(() => _dio.get<Map<String, dynamic>>(
          '/inspection-sessions/$sessionId',
        ));
    return response.data!;
  }

  Future<List<Map<String, dynamic>>> sessionProducts(String sessionId) async {
    final response = await _request(() => _dio.get<Map<String, dynamic>>(
          '/inspection-sessions/$sessionId/products',
        ));
    final products = response.data?['products'];
    return products is List
        ? products.whereType<Map<String, dynamic>>().toList()
        : <Map<String, dynamic>>[];
  }

  Future<List<Map<String, dynamic>>> sessionRecapture(String sessionId) async {
    final response = await _request(() => _dio.get<Map<String, dynamic>>(
          '/inspection-sessions/$sessionId/recapture',
        ));
    final items = response.data?['items'];
    return items is List
        ? items.whereType<Map<String, dynamic>>().toList()
        : <Map<String, dynamic>>[];
  }

  Future<Map<String, dynamic>> uploadProductRecapture(
    String sessionId,
    String productId,
    String imagePath,
  ) async {
    final form = FormData.fromMap({
      'file': await MultipartFile.fromFile(imagePath),
    });
    final response = await _request(() => _dio.post<Map<String, dynamic>>(
          '/inspection-sessions/$sessionId/products/$productId/recapture',
          data: form,
        ));
    return response.data!;
  }

  Future<Map<String, dynamic>> job(String jobId) async {
    final response = await _request(() => _dio.get<Map<String, dynamic>>('/jobs/$jobId'));
    return response.data!;
  }

  Future<List<Map<String, dynamic>>> inspections() async {
    final response = await _request(() => _dio.get<List<dynamic>>('/inspections'));
    return response.data!
        .whereType<Map<String, dynamic>>()
        .toList(growable: false);
  }

  Future<bool> _refresh() async {
    final refreshToken = await _storage.read(key: _refreshTokenKey);
    if (refreshToken == null || refreshToken.isEmpty) return false;
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );
      final data = response.data!;
      await _saveTokens(AuthTokens(
        accessToken: data['access_token'] as String,
        refreshToken: data['refresh_token'] as String,
      ));
      return true;
    } on DioException {
      await logout();
      return false;
    }
  }

  Future<void> _saveTokens(AuthTokens tokens) async {
    await _storage.write(key: _accessTokenKey, value: tokens.accessToken);
    await _storage.write(key: _refreshTokenKey, value: tokens.refreshToken);
  }

  Future<Response<T>> _request<T>(Future<Response<T>> Function() request) async {
    try {
      return await request();
    } on DioException catch (error) {
      final detail = error.response?.data;
        final message = detail is Map && detail['detail'] is String
          ? detail['detail'] as String
          : error.response?.statusCode == 403
            ? 'Your account is not permitted to use this application.'
            : error.response?.statusCode == 422
              ? 'Please check the email and password format.'
              : error.response?.statusCode == 429
                ? 'Too many attempts. Please wait and try again.'
                : (error.response?.statusCode ?? 0) >= 500
                  ? 'LabelSetu is temporarily unavailable.'
                  : error.type == DioExceptionType.connectionError
                    ? 'Unable to connect to LabelSetu.'
                    : error.type == DioExceptionType.receiveTimeout ||
                        error.type == DioExceptionType.sendTimeout
                      ? 'The request timed out. Please try again.'
                      : 'The server returned an unexpected response.';
      throw ApiException(message, statusCode: error.response?.statusCode);
    }
  }
}
