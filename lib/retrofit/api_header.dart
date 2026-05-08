import 'package:dio/dio.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import '../helpers/logger.dart';

class RetroApi {
  Future<Dio> dioData(BuildContext context) async {
    final dio = Dio();
    dio.options.headers["Accept"] =
        "application/json"; // config your dio headers globally
    // dio.options.headers["Authorization"] = "Bearer" +
    //     " " +
    //     SharedPreferenceHelper.getString(
    //         Preferences.auth_token); // config your dio headers globally
    dio.options.headers["Content-Type"] = "application/x-www-form-urlencoded";
    dio.options.followRedirects = false;
    dio.options.connectTimeout = Duration(seconds: 30);
    dio.options.receiveTimeout = Duration(seconds: 30);

    final token = SharedPreferenceHelper.getString(Preferences.auth_token);
    final refreshToken =
        SharedPreferenceHelper.getString(Preferences.refresh_token);
    final expiresIn = SharedPreferenceHelper.getInt(Preferences.expiresIn);
    final savedAt = SharedPreferenceHelper.getInt('token_saved_at');
    logger.w('token: $token, refreshToken: $refreshToken, expiresIn: $expiresIn, savedAt: $savedAt');
    
    final isLoggedIn = SharedPreferenceHelper.getBoolean(Preferences.is_logged_in);

    if (token != 'N_A' && token.isNotEmpty) {
      dio.options.headers["Authorization"] = "Bearer $token";
    }
    dio.options.headers["Accept"] = "application/json";

    // Interceptor
    dio.interceptors.add(
      InterceptorsWrapper(
        onError: (DioException e, ErrorInterceptorHandler handler) async {
          final requestOptions = e.requestOptions;

          if (e.response?.statusCode == 401 &&
              isLoggedIn &&
              !requestOptions.path.contains('refresh') &&
              !requestOptions.path.contains('register') &&
              !requestOptions.path.contains('login') &&
              !requestOptions.path.contains('setting')) {
            try {
              final refreshToken =
                  SharedPreferenceHelper.getString(Preferences.refresh_token);

              if (refreshToken == 'N_A' || refreshToken.isEmpty) {
                SharedPreferenceHelper.clearPref();
                final navigator = Navigator.of(context);
                final current = ModalRoute.of(context)?.settings.name;
                if (navigator.canPop() && current != 'SignIn') {
                  navigator.pushNamedAndRemoveUntil('SignIn', (route) => false);
                }
                return handler.reject(e);
              }

              final newToken = await refreshFirebaseToken(refreshToken);

              if (newToken != null) {
                // Retry request with new token
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
                // Refresh failed, force logout
                SharedPreferenceHelper.clearPref();

                final navigator = Navigator.of(context);
                final current = ModalRoute.of(context)?.settings.name;
                if (navigator.canPop() && current != 'SignIn') {
                  navigator.pushNamedAndRemoveUntil('SignIn', (route) => false);
                }
                return handler.reject(e);
              }
            } catch (err) {
              logger.w('Token refresh error: $err');
              SharedPreferenceHelper.clearPref();
              final navigator = Navigator.of(context);
              final current = ModalRoute.of(context)?.settings.name;
              if (navigator.canPop() && current != 'SignIn') {
                navigator.pushNamedAndRemoveUntil('SignIn', (route) => false);
              }
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

        // Save updated tokens
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
    dio.options.connectTimeout = Duration(seconds: 30);
    dio.options.receiveTimeout = Duration(seconds: 30);
    return dio;
  }
}
