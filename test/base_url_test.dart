import 'dart:io';

import 'package:doctro/retrofit/apis.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test(
    'Check pattern of baseUrl in Apis',
    () {
      // Define the regex pattern for the URL
      var pattern1 = RegExp(r'^https:\/\/.*\/api\/$');
      var pattern2 = RegExp(r'^http:\/\/.*\/api\/$');

      // Check if the baseUrl matches the pattern
      expect(
        ((pattern1.hasMatch(Apis.baseUrl) || pattern2.hasMatch(Apis.baseUrl)) &&
            Apis.baseUrl != "https://ayureze.org/api/"),
        isTrue,
        reason: 'The baseUrl does not match the required pattern',
      );
    },
  );

  test(
    'network_api.g.dart file exists',
    () {
      var filePath = 'lib/retrofit/network_api.g.dart';

      // Check if the file exists
      expect(File(filePath).existsSync(), isTrue,
          reason: 'network_api.g.dart file does not exist/\n'
              'Please run the command: flutter pub run build_runner build --delete-conflicting-outputs');
    },
  );
}
