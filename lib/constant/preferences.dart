import 'package:shared_preferences/shared_preferences.dart';

class SharedPreferenceHelper {
  static Future<SharedPreferences> get _instance async => _preferences ??= await SharedPreferences.getInstance();

  static SharedPreferences? _preferences;

  // call this method from iniState() function of mainApp().
  static Future<SharedPreferences?> init() async {
    _preferences = await _instance;
    return _preferences;
  }

  //sets
  static Future<bool> setBoolean(String key, bool value) async => await (_preferences ??= await _instance).setBool(key, value);

  static Future<bool> setDouble(String key, double value) async => await (_preferences ??= await _instance).setDouble(key, value);

  static Future<bool> setInt(String key, int value) async => await (_preferences ??= await _instance).setInt(key, value);

  static Future<bool> setString(String key, String value) async => await (_preferences ??= await _instance).setString(key, value);

  static Future<bool> setStringList(String key, List<String> value) async => await (_preferences ??= await _instance).setStringList(key, value);

  //gets

  static bool getBoolean(String key) => _preferences?.getBool(key) ?? false;

  static double getDouble(String key) => _preferences?.getDouble(key) ?? 0.0;

  static int getInt(String key) => _preferences?.getInt(key) ?? 0;

  static String getString(String key) => _preferences?.getString(key) ?? 'N_A';

  static List<String> getStringList(String key) => _preferences?.getStringList(key) ?? [];

  //deletes..
  static Future<bool> remove(String key) async {
    if (_preferences == null) {
      _preferences = await _instance;
    }
    return await _preferences!.remove(key);
  }

  static void clearPref() {
    _preferences?.clear();
  }
}
