import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:flutter/material.dart';
import 'language_localization.dart';

String? getTranslated(BuildContext context, String key) {
  return LanguageLocalization.of(context)!.getTranslateValue(key);
}

const String ENGLISH = "en";
const String TAMIL = "ta";
const String HINDI = "hi";
const String MALAYALAM = "ml";
const String TELUGU = "te";
const String KANNADA = "kn";

Future<Locale> setLocale(String languageCode) async {
  SharedPreferenceHelper.setString(Preferences.current_language_code, languageCode);
  return _locale(languageCode);
}

Locale _locale(String languageCode) {
  Locale _temp;
  switch (languageCode) {
    case ENGLISH:
      _temp = Locale(languageCode, 'US');
      break;
    case TAMIL:
      _temp = Locale(languageCode, 'IN');
      break;
    case HINDI:
      _temp = Locale(languageCode, 'IN');
      break;
    case MALAYALAM:
      _temp = Locale(languageCode, 'IN');
      break;
    case TELUGU:
      _temp = Locale(languageCode, 'IN');
      break;
    case KANNADA:
      _temp = Locale(languageCode, 'IN');
      break;
    default:
      _temp = Locale(ENGLISH, 'US');
  }
  return _temp;
}

Future<Locale> getLocale() async {
  String languageCode = SharedPreferenceHelper.getString(Preferences.current_language_code);
  return _locale(languageCode);
}
