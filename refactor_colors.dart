import 'dart:io';

void main() {
  final files = [
    'lib/chat/pages/chat_page.dart',
    'lib/chat/pages/full_photo_page.dart',
    'lib/chat/pages/home_page.dart',
    'lib/chat/widgets/loading_view.dart'
  ];

  for (final path in files) {
    final file = File(path);
    if (!file.existsSync()) continue;
    
    var content = file.readAsStringSync();
    
    // Replace all ColorConstants
    content = content.replaceAll('ColorConstants.greyColor2', 'Theme.of(context).colorScheme.surfaceVariant');
    content = content.replaceAll('ColorConstants.greyColor', 'Theme.of(context).colorScheme.onSurfaceVariant');
    content = content.replaceAll('ColorConstants.themeColor', 'Theme.of(context).colorScheme.primary');
    content = content.replaceAll('ColorConstants.primaryColor', 'Theme.of(context).colorScheme.primary');
    content = content.replaceAll('ColorConstants.black', 'Theme.of(context).colorScheme.onSurface');
    
    // Remove the import if it exists
    content = content.replaceAll("import '../constants/colors.dart';", "");
    content = content.replaceAll("import 'package:doctro/chat/constants/colors.dart';", "");

    file.writeAsStringSync(content);
  }

  // Also modify PaymentGateway and cancel_appointment_backup
  final pgPath = 'lib/screens/paymentScreen/PaymentGateway.dart';
  final pgFile = File(pgPath);
  if (pgFile.existsSync()) {
    var content = pgFile.readAsStringSync();
    content = content.replaceAll(
      'BoxShadow(\n                                    color: Colors.black12,',
      'BoxShadow(\n                                    color: Theme.of(context).shadowColor.withOpacity(0.12),'
    );
    // Since we don't know exact spacing, we'll use a regex for BoxShadow
    content = content.replaceAll(RegExp(r'BoxShadow\(\s*color:\s*Colors\.black12\s*,'), 'BoxShadow(color: Theme.of(context).shadowColor.withOpacity(0.12),');
    content = content.replaceAll('color: Colors.black12', 'color: Theme.of(context).shadowColor.withOpacity(0.12)');
    pgFile.writeAsStringSync(content);
  }

  final cbPath = 'lib/screens/appointment/cancel_appointment_backup.dart';
  final cbFile = File(cbPath);
  if (cbFile.existsSync()) {
    var content = cbFile.readAsStringSync();
    content = content.replaceAll('Colors.white.withOpacity(0.14)', 'Theme.of(context).colorScheme.onSurface.withOpacity(0.14)');
    content = content.replaceAll('color: Colors.white,', 'color: Theme.of(context).colorScheme.onPrimary,');
    cbFile.writeAsStringSync(content);
  }

  // Delete the colors.dart file
  final colorsFile = File('lib/chat/constants/colors.dart');
  if (colorsFile.existsSync()) {
    colorsFile.deleteSync();
    print('lib/chat/constants/colors.dart deleted');
  }
}
