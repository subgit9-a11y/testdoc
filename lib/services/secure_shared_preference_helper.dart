import 'package:flutter/foundation.dart' show kDebugMode, debugPrint;
import 'package:doctro/services/secure_storage_helper.dart';
import 'package:doctro/constant/preferences.dart';

/// Async drop-in replacement for SharedPreferenceHelper that uses
/// flutter_secure_storage for sensitive keys and SharedPreferences for others.
/// For secure keys, writes to BOTH storages so synchronous reads still work.
class SecureSharedPreferenceHelper {
  static const Set<String> _secureKeys = SecureStorageHelper.secureKeys;

  static Future<void> init() async {
    await SecureStorageHelper.init();
    if (kDebugMode) debugPrint('SecureSharedPreferenceHelper initialized');
  }

  static bool _isSecureKey(String key) => _secureKeys.contains(key);

  // ========== SETTERS ==========
  static Future<bool> setBoolean(String key, bool value) async {
    if (_isSecureKey(key)) {
      await SecureStorageHelper.setBoolean(key, value);
      return await SharedPreferenceHelper.setBoolean(key, value);
    }
    return await SharedPreferenceHelper.setBoolean(key, value);
  }

  static Future<bool> setDouble(String key, double value) async {
    if (_isSecureKey(key)) {
      await SecureStorageHelper.setDouble(key, value);
      return await SharedPreferenceHelper.setDouble(key, value);
    }
    return await SharedPreferenceHelper.setDouble(key, value);
  }

  static Future<bool> setInt(String key, int value) async {
    if (_isSecureKey(key)) {
      await SecureStorageHelper.setInt(key, value);
      return await SharedPreferenceHelper.setInt(key, value);
    }
    return await SharedPreferenceHelper.setInt(key, value);
  }

  static Future<bool> setString(String key, String value) async {
    if (_isSecureKey(key)) {
      await SecureStorageHelper.setString(key, value);
      return await SharedPreferenceHelper.setString(key, value);
    }
    return await SharedPreferenceHelper.setString(key, value);
  }

  static Future<bool> setStringList(String key, List<String> value) async {
    if (_isSecureKey(key)) {
      await SecureStorageHelper.setStringList(key, value);
      return await SharedPreferenceHelper.setStringList(key, value);
    }
    return await SharedPreferenceHelper.setStringList(key, value);
  }

  // ========== GETTERS (async) ==========
  static Future<bool> getBoolean(String key) async {
    if (_isSecureKey(key)) {
      return await SecureStorageHelper.getBoolean(key);
    }
    return SharedPreferenceHelper.getBoolean(key);
  }

  static Future<double> getDouble(String key) async {
    if (_isSecureKey(key)) {
      return await SecureStorageHelper.getDouble(key);
    }
    return SharedPreferenceHelper.getDouble(key).toDouble();
  }

  static Future<int> getInt(String key) async {
    if (_isSecureKey(key)) {
      return await SecureStorageHelper.getInt(key);
    }
    return SharedPreferenceHelper.getInt(key);
  }

  static Future<String> getString(String key) async {
    if (_isSecureKey(key)) {
      return await SecureStorageHelper.getString(key);
    }
    return SharedPreferenceHelper.getString(key);
  }

  static Future<List<String>> getStringList(String key) async {
    if (_isSecureKey(key)) {
      return await SecureStorageHelper.getStringList(key);
    }
    return SharedPreferenceHelper.getStringList(key);
  }

  // ========== DELETES ==========
  static Future<bool> remove(String key) async {
    if (_isSecureKey(key)) {
      await SecureStorageHelper.remove(key);
      return await SharedPreferenceHelper.remove(key);
    }
    return await SharedPreferenceHelper.remove(key);
  }

  static Future<void> clearPref() async {
    await SecureStorageHelper.clearPref();
  }

  static Future<void> clearSecureOnly() async {
    await SecureStorageHelper.clearSecureOnly();
  }
}
