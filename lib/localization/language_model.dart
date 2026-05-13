class Language {
  final int id;
  final String name;
  final String flag;
  final String languageCode;

  Language(this.id, this.name, this.flag, this.languageCode);

  static List<Language> languageList() {
    return <Language>[
      Language(1, 'English', '🇺🇸', 'en'),
      Language(2, 'Tamil', '🇮🇳', 'ta'),
      Language(3, 'Hindi', '🇮🇳', 'hi'),
      Language(4, 'Malayalam', '🇮🇳', 'ml'),
      Language(5, 'Telugu', '🇮🇳', 'te'),
      Language(6, 'Kannada', '🇮🇳', 'kn'),
    ];
  }
}
