import 'package:flutter/foundation.dart';

class ApiConfig {
  const ApiConfig._();

  static const defaultBaseUrl =
      'https://labelsetu-backend.onrender.com';

  static String get baseUrl => const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: defaultBaseUrl,
      ).replaceAll(RegExp(r'/$'), '');

  static String get apiUrl => baseUrl.endsWith('/api/v1')
      ? baseUrl
      : '$baseUrl/api/v1';

  static bool get isConfigured => baseUrl.isNotEmpty &&
      (Uri.tryParse(baseUrl)?.hasScheme ?? false) &&
      (Uri.tryParse(baseUrl)?.host.isNotEmpty ?? false);
}

@visibleForTesting
String apiBaseUrlForTesting() => ApiConfig.baseUrl;
