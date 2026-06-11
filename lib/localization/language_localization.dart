import 'dart:convert';
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'localization_constant.dart';

class LanguageLocalization {
  final Locale locale;

  LanguageLocalization(this.locale);

  static LanguageLocalization? of(BuildContext context) {
    return Localizations.of<LanguageLocalization>(context, LanguageLocalization);
  }

  late Map<String, String> _localizationValue;

  Future<bool> load() async {
    try {
      String jsonStringValue = await rootBundle.loadString(
        'lib/localization/language/${locale.languageCode}.json',
      );
      final Map<String, dynamic> mappedJson = json.decode(jsonStringValue);
      _localizationValue = mappedJson.map(
        (key, value) => MapEntry(key, value?.toString() ?? key),
      );
      return true;
    } catch (e, st) {
      if (kDebugMode) {
        debugPrint('LanguageLocalization load failed for ${locale.languageCode}: $e\n$st');
      }
      _localizationValue = {};
      return false;
    }
  }

  String getTranslateValue(String key) {
    return _localizationValue[key] ?? key;
  }

  static const LocalizationsDelegate<LanguageLocalization> delegate =
      _LanguageLocalizationDelegate();
}

class _LanguageLocalizationDelegate
    extends LocalizationsDelegate<LanguageLocalization> {
  const _LanguageLocalizationDelegate();

  @override
  bool isSupported(Locale locale) {
    return SUPPORTED_LANGUAGE_CODES.contains(locale.languageCode);
  }

  @override
  Future<LanguageLocalization> load(Locale locale) async {
    final LanguageLocalization localization = LanguageLocalization(locale);
    await localization.load();
    return localization;
  }

  @override
  bool shouldReload(_LanguageLocalizationDelegate old) => true;
}
