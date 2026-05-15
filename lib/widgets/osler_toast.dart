import 'package:flutter/material.dart';
import 'package:doctro/theme/ayureze_theme.dart';

enum OslerToastType { success, error, warning, info }

class OslerToast {
  static void show({
    required BuildContext context,
    required String message,
    OslerToastType type = OslerToastType.info,
    Duration duration = const Duration(seconds: 3),
  }) {
    final Color backgroundColor;
    final Color textColor;
    final IconData icon;

    switch (type) {
      case OslerToastType.success:
        backgroundColor = AyurezeTheme.healingGreen100;
        textColor = Colors.white;
        icon = Icons.check_circle_outline;
        break;
      case OslerToastType.error:
        backgroundColor = AyurezeTheme.remoteRed100;
        textColor = Colors.white;
        icon = Icons.error_outline;
        break;
      case OslerToastType.warning:
        backgroundColor = AyurezeTheme.sunshineYellow100;
        textColor = Colors.black87;
        icon = Icons.warning_amber_outlined;
        break;
      case OslerToastType.info:
        backgroundColor = AyurezeTheme.connectivityBlue100;
        textColor = Colors.white;
        icon = Icons.info_outline;
        break;
    }

    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(icon, color: textColor, size: 20),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: TextStyle(
                  color: textColor,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
        backgroundColor: backgroundColor,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        duration: duration,
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  static void success(BuildContext context, String message) {
    show(context: context, message: message, type: OslerToastType.success);
  }

  static void error(BuildContext context, String message) {
    show(context: context, message: message, type: OslerToastType.error);
  }

  static void warning(BuildContext context, String message) {
    show(context: context, message: message, type: OslerToastType.warning);
  }

  static void info(BuildContext context, String message) {
    show(context: context, message: message, type: OslerToastType.info);
  }
}