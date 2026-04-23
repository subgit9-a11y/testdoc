import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart' show NotificationResponse;

class NotificationHandler {
  static final ValueNotifier<NotificationResponse?> notificationResponse = ValueNotifier(null);

  static void handle(NotificationResponse response) {
    notificationResponse.value = response;
  }
}
