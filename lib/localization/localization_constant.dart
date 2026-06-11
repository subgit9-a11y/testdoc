import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:flutter/material.dart';
import 'language_localization.dart';

String getTranslated(BuildContext context, String key) {
  final localization = LanguageLocalization.of(context);
  if (localization == null) return key;
  return localization.getTranslateValue(key) ?? key;
}

const String ENGLISH = "en";
const String TAMIL = "ta";
const String HINDI = "hi";
const String MALAYALAM = "ml";
const String TELUGU = "te";
const String KANNADA = "kn";

const List<String> SUPPORTED_LANGUAGE_CODES = [
  ENGLISH,
  TAMIL,
  HINDI,
  MALAYALAM,
  TELUGU,
  KANNADA,
];

Future<Locale> setLocale(String languageCode) async {
  await SharedPreferenceHelper.setString(Preferences.current_language_code, languageCode);
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
  if (languageCode.isEmpty || languageCode == 'N_A') {
    return const Locale(ENGLISH, 'US');
  }
  return _locale(languageCode);
}
