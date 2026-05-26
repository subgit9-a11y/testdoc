import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AyurezeTheme {
  // Osler UI Kit Colors
  static const Color oslerGray100 = Color(0xFF111A14);
  static const Color oslerGray50 = Color(0xFF849087);
  static const Color oslerGray10 = Color(0xFFF5F5F5);

  static const Color healingGreen100 = Color(0xFF0F2916); // Deep Botanical Forest Green
  static const Color healingGreen50 = Color(0xFF10B981);  // Premium Healing Emerald Green
  static const Color healingGreen10 = Color(0xFFE6F7F0);  // Soft Sage Mint Accent

  static const Color remoteRed100 = Color(0xFF4C050B);
  static const Color remoteRed50 = Color(0xFFF43F5E);
  static const Color remoteRed10 = Color(0xFFFFE4E7);

  static const Color sunshineYellow100 = Color(0xFF422006);
  static const Color sunshineYellow50 = Color(0xFFF59E0B);
  static const Color sunshineYellow10 = Color(0xFFFEF9C3);

  static const Color caringViolet100 = Color(0xFF311065);
  static const Color caringViolet50 = Color(0xFF8B5CF6);
  static const Color caringViolet10 = Color(0xFFEDE9FE);

  static const Color connectivityBlue100 = Color(0xFF172554);
  static const Color connectivityBlue50 = Color(0xFF3B82F6);
  static const Color connectivityBlue10 = Color(0xFFEFF6FF);

  // Private state for dynamic theme support
  static bool _isDark = false;
  static void updateThemeMode(bool value) => _isDark = value;

  // Semantic Colors - Light Definitions
  static const Color lightCanvas = Color(0xFFE9EEE4);
  static const Color lightSurface = Color(0xFFF7F8F2);
  static const Color lightSurfaceMuted = Color(0xFFEFF3EA);
  static const Color lightBorder = Color(0xFFD4DDCC);
  static const Color lightTextPrimary = Color(0xFF203126);
  static const Color lightTextSecondary = Color(0xFF607063);

  // Semantic Colors - Dark Definitions
  static const Color darkCanvas = Color(0xFF1A1A1A);
  static const Color darkSurface = Color(0xFF2D2D2D);
  static const Color darkSurfaceMuted = Color(0xFF3D3D3D);
  static const Color darkBorder = Color(0xFF4D4D4D);
  static const Color darkTextPrimary = Color(0xFFE0E0E0);
  static const Color darkTextSecondary = Color(0xFFA0A0A0);

  // Dynamic Getters
  static Color get canvas => _isDark ? darkCanvas : lightCanvas;
  static Color get surface => _isDark ? darkSurface : lightSurface;
  static Color get surfaceMuted => _isDark ? darkSurfaceMuted : lightSurfaceMuted;
  static Color get border => _isDark ? darkBorder : lightBorder;
  static Color get textPrimary => _isDark ? darkTextPrimary : lightTextPrimary;
  static Color get textSecondary => _isDark ? darkTextSecondary : lightTextSecondary;
  
  // Aliases for backwards compatibility
  static const Color forestDeep = healingGreen100;
  static const Color forest = healingGreen50;
  static const Color moss = oslerGray50;
  static const Color lightGreen = healingGreen50;
  static const Color lightGreenSoft = healingGreen10;
  static const Color danger = remoteRed50;
  static const Color warning = sunshineYellow50;
  static const Color purple = caringViolet50;
  
  // Additional semantic getters
  static Color get surfaceDark => darkSurface;
  static Color get textMuted => darkTextSecondary;
  static Color get borderMuted => border;
  static Color get shadow => _isDark ? const Color(0x66000000) : const Color(0x26000000);
  
  // Dynamic Icon/SVG Colors - ensures visibility in both modes
  static Color get iconPrimary => _isDark ? Colors.white : healingGreen100;
  static Color get iconSecondary => _isDark ? darkTextSecondary : oslerGray50;
  static Color get iconOnDark => _isDark ? Colors.white : Colors.white;
  static Color get iconOnLight => _isDark ? Colors.white : Colors.white;
  static Color get logoColor => _isDark ? Colors.white : Colors.white;
  
  // Action button colors for dark/light mode
  static Color get actionButtonPrimary => _isDark ? healingGreen50 : healingGreen100;
  static Color get actionButtonSecondary => _isDark ? oslerGray50 : healingGreen50;

  static const EdgeInsets screenPadding = EdgeInsets.symmetric(
    horizontal: 20,
    vertical: 16,
  );

  static ThemeData theme({bool isDarkMode = false}) {
    if (isDarkMode) {
      return darkTheme();
    }
    return lightTheme();
  }

  static ThemeData lightTheme() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: healingGreen100,
      brightness: Brightness.light,
      primary: healingGreen50,
      secondary: oslerGray50,
      surface: lightSurface,
    ).copyWith(
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onSurface: lightTextPrimary,
      error: remoteRed50,
      onError: Colors.white,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: lightCanvas,
      cardColor: lightSurface,
      dividerColor: lightBorder,
      shadowColor: const Color(0x16000000),
      textTheme: GoogleFonts.nunitoTextTheme(
        ThemeData.light().textTheme,
      ).copyWith(
        headlineLarge: const TextStyle(
          fontSize: 32,
          height: 1.05,
          fontWeight: FontWeight.w800,
          color: lightTextPrimary,
        ),
        headlineMedium: const TextStyle(
          fontSize: 24,
          height: 1.15,
          fontWeight: FontWeight.w800,
          color: lightTextPrimary,
        ),
        titleLarge: const TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: lightTextPrimary,
        ),
        titleMedium: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w700,
          color: lightTextPrimary,
        ),
        bodyLarge: const TextStyle(
          fontSize: 15,
          height: 1.4,
          color: lightTextPrimary,
        ),
        bodyMedium: const TextStyle(
          fontSize: 14,
          height: 1.35,
          color: lightTextSecondary,
        ),
        labelLarge: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.2,
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: lightCanvas,
        surfaceTintColor: Colors.transparent,
        foregroundColor: lightTextPrimary,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.w800,
          color: lightTextPrimary,
        ),
      ),
      cardTheme: CardThemeData(
        color: lightSurface,
        elevation: 0,
        margin: EdgeInsets.zero,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(28),
          side: const BorderSide(color: lightBorder),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: healingGreen100,
          foregroundColor: Colors.white,
          minimumSize: const Size.fromHeight(56),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
          textStyle: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          backgroundColor: lightSurface,
          foregroundColor: lightTextPrimary,
          minimumSize: const Size.fromHeight(56),
          side: const BorderSide(color: lightBorder),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          textStyle: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: lightSurface,
        hintStyle: const TextStyle(color: lightTextSecondary),
        labelStyle: const TextStyle(color: lightTextSecondary),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 18,
          vertical: 18,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: const BorderSide(color: lightBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: const BorderSide(color: healingGreen100, width: 1.4),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: const BorderSide(color: remoteRed50),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: const BorderSide(color: remoteRed50, width: 1.4),
        ),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: healingGreen10,
        disabledColor: lightSurfaceMuted,
        selectedColor: healingGreen50,
        secondarySelectedColor: healingGreen50,
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        labelStyle: const TextStyle(
          color: healingGreen100,
          fontWeight: FontWeight.w700,
        ),
        secondaryLabelStyle: const TextStyle(
          color: healingGreen100,
          fontWeight: FontWeight.w700,
        ),
        brightness: Brightness.light,
        side: BorderSide.none,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(999),
        ),
      ),
    );
  }

  static BoxDecoration heroDecoration() {
    return BoxDecoration(
      borderRadius: BorderRadius.circular(32),
      gradient: const LinearGradient(
        colors: [healingGreen50, healingGreen100],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      boxShadow: const [
        BoxShadow(
          color: Color(0x22000000),
          blurRadius: 24,
          offset: Offset(0, 16),
        ),
      ],
    );
  }

  static BoxDecoration panelDecoration() {
    return BoxDecoration(
      color: surface,
      borderRadius: BorderRadius.circular(28),
      border: Border.all(color: border),
      boxShadow: const [
        BoxShadow(
          color: Color(0x10000000),
          blurRadius: 18,
          offset: Offset(0, 10),
        ),
      ],
    );
  }

  static BoxDecoration mutedPanelDecoration() {
    return BoxDecoration(
      color: surfaceMuted,
      borderRadius: BorderRadius.circular(24),
      border: Border.all(color: border),
    );
  }

  static ThemeData darkTheme() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: healingGreen100,
      brightness: Brightness.dark,
      primary: healingGreen50,
      secondary: oslerGray50,
      surface: darkSurface,
    ).copyWith(
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onSurface: darkTextPrimary,
      error: remoteRed50,
      onError: Colors.white,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: darkCanvas,
      cardColor: darkSurface,
      dividerColor: darkBorder,
      shadowColor: const Color(0x40000000),
      textTheme: GoogleFonts.nunitoTextTheme(
        ThemeData.dark().textTheme,
      ).copyWith(
        headlineLarge: const TextStyle(
          fontSize: 32,
          height: 1.05,
          fontWeight: FontWeight.w800,
          color: darkTextPrimary,
        ),
        headlineMedium: const TextStyle(
          fontSize: 24,
          height: 1.15,
          fontWeight: FontWeight.w800,
          color: darkTextPrimary,
        ),
        titleLarge: const TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: darkTextPrimary,
        ),
        titleMedium: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w700,
          color: darkTextPrimary,
        ),
        bodyLarge: const TextStyle(
          fontSize: 15,
          height: 1.4,
          color: darkTextPrimary,
        ),
        bodyMedium: const TextStyle(
          fontSize: 14,
          height: 1.35,
          color: darkTextSecondary,
        ),
        labelLarge: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w700,
          color: darkTextPrimary,
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: darkSurface,
        foregroundColor: darkTextPrimary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: darkTextPrimary,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: healingGreen50,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: healingGreen50,
          side: const BorderSide(color: healingGreen50, width: 1.5),
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: darkSurfaceMuted,
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: darkBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: healingGreen50, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: remoteRed50),
        ),
        hintStyle: const TextStyle(color: darkTextSecondary),
      ),
      cardTheme: CardThemeData(
        color: darkSurface,
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20), side: const BorderSide(color: darkBorder)),
      ),
      iconTheme: const IconThemeData(color: darkTextPrimary),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: darkSurface,
        selectedItemColor: healingGreen50,
        unselectedItemColor: darkTextSecondary,
      ),
      drawerTheme: const DrawerThemeData(backgroundColor: darkSurface),
      dialogTheme: DialogThemeData(backgroundColor: darkSurface, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24))),
      floatingActionButtonTheme: const FloatingActionButtonThemeData(backgroundColor: healingGreen50, foregroundColor: Colors.white),
      chipTheme: ChipThemeData(backgroundColor: darkSurfaceMuted, labelStyle: const TextStyle(color: darkTextPrimary)),
      tabBarTheme: TabBarThemeData(labelColor: healingGreen50, unselectedLabelColor: darkTextSecondary),
    );
  }

  static BoxDecoration darkPanelDecoration() {
    return BoxDecoration(
      color: const Color(0xFF2D2D2D),
      borderRadius: BorderRadius.circular(28),
      border: Border.all(color: const Color(0xFF4D4D4D)),
      boxShadow: const [
        BoxShadow(
          color: Color(0x30000000),
          blurRadius: 18,
          offset: Offset(0, 10),
        ),
      ],
    );
  }
  static InputDecoration textFieldDecoration({String? labelText, String? hintText}) {
    return InputDecoration(
      labelText: labelText,
      hintText: hintText,
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(20),
        borderSide: BorderSide(color: border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(20),
        borderSide: BorderSide(color: border),
      ),      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(20),
        borderSide: BorderSide(color: healingGreen100, width: 2),
      ),
      filled: true,
      fillColor: surface,
      labelStyle: TextStyle(color: textSecondary, fontSize: 14),
      hintStyle: TextStyle(color: textSecondary.withOpacity(0.6), fontSize: 14),
    );
  }

}
