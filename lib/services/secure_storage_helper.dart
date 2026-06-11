import 'package:flutter/foundation.dart' show kDebugMode, debugPrint;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:doctro/constant/prefConstatnt.dart';

class SecureStorageHelper {
  static const _secureStorage = FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock_this_device,
    ),
  );

  static SharedPreferences? _prefs;

  static const Set<String> secureKeys = {
    Preferences.auth_token,
    Preferences.refresh_token,
    Preferences.expiresIn,
    Preferences.doctorId,
    Preferences.user_email,
    Preferences.messageToken,
    Preferences.uniqueId,
    Preferences.is_logged_in,
    Preferences.password,
    Preferences.stripPublicKey,
    Preferences.stripeSecretKey,
    Preferences.razor_key,
    Preferences.agoraAppId,
    Preferences.flutterWave_key,
    Preferences.flutterWave_encryption_key,
    Preferences.payStack_public_key,
    Preferences.payPal_sandbox_key,
    Preferences.payPal_production_key,
    Preferences.paypal_client_key,
    Preferences.paypal_secret_key,
    Preferences.doctorAppId,
  };

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    if (kDebugMode) debugPrint('SecureStorageHelper initialized');
  }

  static bool _isSecureKey(String key) => secureKeys.contains(key);

  static Future<void> _ensurePrefs() async {
    _prefs ??= await SharedPreferences.getInstance();
  }

  // ========== SETTERS ==========
  static Future<bool> setBoolean(String key, bool value) async {
    if (_isSecureKey(key)) {
      await _secureStorage.write(key: key, value: value.toString());
      return true;
    }
    await _ensurePrefs();
    return await _prefs!.setBool(key, value);
  }

  static Future<bool> setDouble(String key, double value) async {
    if (_isSecureKey(key)) {
      await _secureStorage.write(key: key, value: value.toString());
      return true;
    }
    await _ensurePrefs();
    return await _prefs!.setDouble(key, value);
  }

  static Future<bool> setInt(String key, int value) async {
    if (_isSecureKey(key)) {
      await _secureStorage.write(key: key, value: value.toString());
      return true;
    }
    await _ensurePrefs();
    return await _prefs!.setInt(key, value);
  }

  static Future<bool> setString(String key, String value) async {
    if (_isSecureKey(key)) {
      await _secureStorage.write(key: key, value: value);
      return true;
    }
    await _ensurePrefs();
    return await _prefs!.setString(key, value);
  }

  static Future<bool> setStringList(String key, List<String> value) async {
    if (_isSecureKey(key)) {
      await _secureStorage.write(key: key, value: value.join(','));
      return true;
    }
    await _ensurePrefs();
    return await _prefs!.setStringList(key, value);
  }

  // ========== GETTERS ==========
  static Future<bool> getBoolean(String key) async {
    if (_isSecureKey(key)) {
      final value = await _secureStorage.read(key: key);
      return value?.toLowerCase() == 'true';
    }
    await _ensurePrefs();
    return _prefs!.getBool(key) ?? false;
  }

  static Future<double> getDouble(String key) async {
    if (_isSecureKey(key)) {
      final value = await _secureStorage.read(key: key);
      return double.tryParse(value ?? '') ?? 0.0;
    }
    await _ensurePrefs();
    return _prefs!.getDouble(key) ?? 0.0;
  }

  static Future<int> getInt(String key) async {
    if (_isSecureKey(key)) {
      final value = await _secureStorage.read(key: key);
      return int.tryParse(value ?? '') ?? 0;
    }
    await _ensurePrefs();
    return _prefs!.getInt(key) ?? 0;
  }

  static Future<String> getString(String key) async {
    if (_isSecureKey(key)) {
      final value = await _secureStorage.read(key: key);
      return value ?? 'N_A';
    }
    await _ensurePrefs();
    return _prefs!.getString(key) ?? 'N_A';
  }

  static Future<List<String>> getStringList(String key) async {
    if (_isSecureKey(key)) {
      final value = await _secureStorage.read(key: key);
      return value?.split(',') ?? [];
    }
    await _ensurePrefs();
    return _prefs!.getStringList(key) ?? [];
  }

  // ========== DELETES ==========
  static Future<bool> remove(String key) async {
    if (_isSecureKey(key)) {
      await _secureStorage.delete(key: key);
      return true;
    }
    await _ensurePrefs();
    return await _prefs!.remove(key);
  }

  static Future<void> clearPref() async {
    await _secureStorage.deleteAll();
    await _ensurePrefs();
    await _prefs!.clear();
  }

  static Future<void> clearSecureOnly() async {
    for (final key in secureKeys) {
      await _secureStorage.delete(key: key);
    }
  }
}
