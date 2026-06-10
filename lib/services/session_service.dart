import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/main.dart';
import 'package:doctro/services/secure_shared_preference_helper.dart';
import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:flutter/material.dart';

class SessionService {
  static bool _isLoggingOut = false;

  static bool get isLoggingOut => _isLoggingOut;

  static Future<void> handleSessionExpired({String? reason}) async {
    if (_isLoggingOut) return;
    _isLoggingOut = true;

    try {
      await SecureSharedPreferenceHelper.setBoolean(Preferences.is_logged_in, false);
      await SecureSharedPreferenceHelper.clearPref();
    } catch (e) {
      if (kDebugMode) debugPrint('SessionService clearPref failed: $e');
    }

    final nav = navigatorKey.currentState;
    if (nav != null) {
      final currentName = ModalRoute.of(nav.context)?.settings.name;
      if (currentName != 'SignIn') {
        nav.pushNamedAndRemoveUntil('SignIn', (route) => false);
      }
    }

    Future.delayed(const Duration(seconds: 2), () {
      _isLoggingOut = false;
    });
  }

  static Future<void> logout() async {
    await handleSessionExpired();
  }
}
