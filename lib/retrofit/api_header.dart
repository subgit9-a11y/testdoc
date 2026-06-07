import 'package:dio/dio.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/services/session_service.dart';
import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import '../helpers/logger.dart';

class RetroApi {
  Future<Dio> dioData(BuildContext context) async {
    final dio = Dio();
    dio.options.headers["Accept"] = "application/json";
    dio.options.headers["Content-Type"] = "application/x-www-form-urlencoded";
    dio.options.followRedirects = false;
    dio.options.connectTimeout = const Duration(seconds: 30);
    dio.options.receiveTimeout = const Duration(seconds: 30);

    final token = SharedPreferenceHelper.getString(Preferences.auth_token);
    final refreshToken =
        SharedPreferenceHelper.getString(Preferences.refresh_token);
    final expiresIn = SharedPreferenceHelper.getInt(Preferences.expiresIn);
    final savedAt = SharedPreferenceHelper.getInt('token_saved_at');
    if (kDebugMode) {
      logger.w('token present: ${token != 'N_A' && token.isNotEmpty}, expiresIn: $expiresIn, savedAt: $savedAt');
    }

    final isLoggedIn = SharedPreferenceHelper.getBoolean(Preferences.is_logged_in);

    if (token != 'N_A' && token.isNotEmpty) {
      dio.options.headers["Authorization"] = "Bearer $token";
    }
    dio.options.headers["Accept"] = "application/json";

    dio.interceptors.add(
      InterceptorsWrapper(
        onError: (DioException e, ErrorInterceptorHandler handler) async {
          if (SessionService.isLoggingOut) {
            return handler.next(e);
          }

          final requestOptions = e.requestOptions;
          final status = e.response?.statusCode;
          final isAuthPath = requestOptions.path.contains('refresh') ||
              requestOptions.path.contains('register') ||
              requestOptions.path.contains('login') ||
              requestOptions.path.contains('setting');

          if (status == 401 && isLoggedIn && !isAuthPath) {
            try {
              final savedRefreshToken =
                  SharedPreferenceHelper.getString(Preferences.refresh_token);

              if (savedRefreshToken == 'N_A' || savedRefreshToken.isEmpty) {
                await SessionService.handleSessionExpired();
                return handler.reject(e);
              }

              final newToken = await refreshFirebaseToken(savedRefreshToken);

              if (newToken != null) {
                final clonedRequest = await dio.request(
                  requestOptions.path,
                  data: requestOptions.data,
                  queryParameters: requestOptions.queryParameters,
                  options: Options(
                    method: requestOptions.method,
                    headers: {
                      ...requestOptions.headers,
                      'Authorization': 'Bearer $newToken',
                    },
                  ),
                );
                return handler.resolve(clonedRequest);
              } else {
                await SessionService.handleSessionExpired();
                return handler.reject(e);
              }
            } catch (err) {
              logger.w('Token refresh error: $err');
              await SessionService.handleSessionExpired();
              return handler.reject(e);
            }
          }

          return handler.next(e);
        },
      ),
    );
    return dio;
  }

  Future<String?> refreshFirebaseToken(String refreshToken) async {
    try {
      String? apiKey;
      try {
        apiKey = dotenv.maybeGet('FIREBASE_API_KEY');
      } catch (_) {
        apiKey = null;
      }
      apiKey ??= const String.fromEnvironment('FIREBASE_API_KEY');
      if (apiKey.isEmpty) {
        return null;
      }
      final response = await Dio().post(
        'https://securetoken.googleapis.com/v1/token?key=$apiKey',
        data: {
          'grant_type': 'refresh_token',
          'refresh_token': refreshToken,
        },
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );

      if (response.statusCode == 200) {
        final data = response.data;
        final newIdToken = data['id_token'];
        final newRefreshToken = data['refresh_token'];
        final newExpiresIn = int.parse(data['expires_in']);

        await SharedPreferenceHelper.setString(
            Preferences.auth_token, newIdToken);
        await SharedPreferenceHelper.setString(
            Preferences.refresh_token, newRefreshToken);
        await SharedPreferenceHelper.setInt(
            Preferences.expiresIn, newExpiresIn);
        await SharedPreferenceHelper.setInt(
            'token_saved_at', DateTime.now().millisecondsSinceEpoch);

        return newIdToken;
      } else {
        return null;
      }
    } catch (e) {
      logger.e('Firebase token refresh failed: $e');
      return null;
    }
  }
}

class RetroApi2 {
  Dio dioData2() {
    final dio = Dio();
    dio.options.headers["Accept"] = "application/json";
    dio.options.followRedirects = false;
    dio.options.connectTimeout = const Duration(seconds: 30);
    dio.options.receiveTimeout = const Duration(seconds: 30);
    return dio;
  }
}
