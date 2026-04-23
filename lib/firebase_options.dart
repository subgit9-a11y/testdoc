import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      case TargetPlatform.macOS:
        return macos;
      case TargetPlatform.windows:
        return windows;
      case TargetPlatform.linux:
        return linux;
      default:
        throw UnsupportedError(
          'DefaultFirebaseOptions are not supported for this platform.',
        );
    }
  }

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyDbeOvU5nkgLkYCc8CFMnlrK5duMQySKf0',
    appId: '1:298839588168:android:ae85ad77aedf34a5a1c77d',
    messagingSenderId: '298839588168',
    projectId: 'ayurease-healthcare',
    storageBucket: 'ayurease-healthcare.firebasestorage.app',
  );

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyDbeOvU5nkgLkYCc8CFMnlrK5duMQySKf0',
    appId: '1:298839588168:web:ae85ad77aedf34a5a1c77d',
    messagingSenderId: '298839588168',
    projectId: 'ayurease-healthcare',
    storageBucket: 'ayurease-healthcare.firebasestorage.app',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'AIzaSyDbeOvU5nkgLkYCc8CFMnlrK5duMQySKf0',
    appId: '1:298839588168:ios:ae85ad77aedf34a5a1c77d',
    messagingSenderId: '298839588168',
    projectId: 'ayurease-healthcare',
    storageBucket: 'ayurease-healthcare.firebasestorage.app',
    iosBundleId: 'app.ayureze.patient',
  );

  static const FirebaseOptions macos = FirebaseOptions(
    apiKey: 'AIzaSyDbeOvU5nkgLkYCc8CFMnlrK5duMQySKf0',
    appId: '1:298839588168:macos:ae85ad77aedf34a5a1c77d',
    messagingSenderId: '298839588168',
    projectId: 'ayurease-healthcare',
    storageBucket: 'ayurease-healthcare.firebasestorage.app',
    iosBundleId: 'app.ayureze.patient',
  );

  static const FirebaseOptions windows = FirebaseOptions(
    apiKey: 'AIzaSyDbeOvU5nkgLkYCc8CFMnlrK5duMQySKf0',
    appId: '1:298839588168:windows:ae85ad77aedf34a5a1c77d',
    messagingSenderId: '298839588168',
    projectId: 'ayurease-healthcare',
    storageBucket: 'ayurease-healthcare.firebasestorage.app',
  );

  static const FirebaseOptions linux = FirebaseOptions(
    apiKey: 'AIzaSyDbeOvU5nkgLkYCc8CFMnlrK5duMQySKf0',
    appId: '1:298839588168:linux:ae85ad77aedf34a5a1c77d',
    messagingSenderId: '298839588168',
    projectId: 'ayurease-healthcare',
    storageBucket: 'ayurease-healthcare.firebasestorage.app',
  );
}
