import 'dart:convert';
import 'dart:developer';
import 'dart:io';
import 'package:flutter/foundation.dart' show kDebugMode, debugPrint;

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:doctro/chat/pages/chat_page.dart' show ChatPage;
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/helpers/logger.dart';
import 'package:doctro/helpers/notification.dart' show NotificationHandler;
import 'package:doctro/localization/language_localization.dart';
import 'package:doctro/model/setting.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/auth/SignIn.dart';
import 'package:doctro/screens/auth/forgotpassword.dart';
import 'package:doctro/screens/notification/ViewAllNotification.dart';
import 'package:doctro/screens/paymentScreen/PaymentGateway.dart';
import 'package:doctro/screens/schedule/ScheduleTimings.dart';
import 'package:doctro/screens/setting/ChangePassword.dart';
import 'package:doctro/screens/setting/Setting.dart';
import 'package:doctro/screens/setting/changeLanguage.dart';
import 'package:doctro/screens/subscription/Subscription.dart';
import 'package:doctro/screens/subscription/SubscriptionHistory.dart';
import 'package:doctro/screens/videoCall/videocallhistory.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'theme/ayureze_theme.dart';
import 'theme/theme_provider.dart';
import 'VideoCall/overlay_handler.dart';
import 'chat/pages/home_page.dart';
import 'chat/providers/auth_provider.dart' as provider;
import 'chat/providers/chat_provider.dart';
import 'chat/providers/home_provider.dart';
import 'constant/prefConstatnt.dart';
import 'firebase_options.dart';
import 'localization/localization_constant.dart';
import 'screens/appointment/appointment_history.dart';
import 'screens/appointment/cancel_appointment.dart';
import 'screens/auth/phoneverification.dart';
import 'screens/auth/signup.dart';
import 'screens/home page/login_home.dart';
import 'screens/home page/patient_information.dart';
import 'screens/notification/notifications.dart';
import 'screens/paymentScreen/payment.dart';
import 'screens/profile/profile.dart' hide Container;
import 'screens/review/rate&review.dart';
import 'screens/videoCall/video_Call.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  bool firebaseInitialized = false;

  try {
    await dotenv.load(fileName: ".env");
  } catch (e) {
    debugPrint(".env not found, using compile-time environment values.");
  }

  String? getEnvSafe(String key) {
    try {
      return dotenv.maybeGet(key);
    } catch (_) {
      return null;
    }
  }

  final String supabaseUrl =
      getEnvSafe('SUPABASE_URL') ?? const String.fromEnvironment('SUPABASE_URL');
  final String supabaseAnonKey =
      getEnvSafe('SUPABASE_ANON_KEY') ?? const String.fromEnvironment('SUPABASE_ANON_KEY');

  if (supabaseUrl.isNotEmpty && supabaseAnonKey.isNotEmpty) {
    try {
      await Supabase.initialize(
        url: supabaseUrl,
        anonKey: supabaseAnonKey,
      );
    } catch (e) {
      debugPrint("Supabase initialization failed: $e");
    }
  } else {
    debugPrint("Supabase not initialized: missing SUPABASE_URL or SUPABASE_ANON_KEY.");
  }
  
  // Use a safer initialization sequence
  SharedPreferences? _prefs;
  try {
    _prefs = await SharedPreferences.getInstance();
    await SharedPreferenceHelper.init();
  } catch (e) {
    debugPrint("Failed to initialize preferences: $e");
  }

  // Initialize Firebase but don't let it hang the whole app
  try {
    await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
    firebaseInitialized = true;
    
    // Subscribe to topic in background, don't await it
    FirebaseMessaging.instance.subscribeToTopic("all").catchError((e) {
      debugPrint("Failed to subscribe to topic: $e");
    });
  } catch (e) {
    debugPrint("Firebase initialization failed: $e");
  }

  if (kDebugMode) {
    HttpOverrides.global = new MyHttpOverrides();
  }
  
  if (Platform.isAndroid && _prefs != null) {
    try {
      await SharedPreferenceHelper.setString(Preferences.device_platform, "Android");
    } catch (e) {
      debugPrint("Failed to store device platform: $e");
    }
  }

  if (_prefs == null) {
    debugPrint("CRITICAL: SharedPreferences failed to initialize. Starting with empty prefs.");
    // Ideally we should show an error screen, but for now we'll try to continue
    _prefs = await SharedPreferences.getInstance(); 
  }

  runApp(MyApp(prefs: _prefs!, firebaseInitialized: firebaseInitialized));
}

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();
const AndroidNotificationChannel channel = AndroidNotificationChannel(
    'high_importance_channel', // id
    'High Importance Notifications', // title
    importance: Importance.max,
    showBadge: true,
    playSound: true,
    enableVibration: true);

class MyHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..badCertificateCallback =
          (X509Certificate cert, String host, int port) => true;
  }
}

class MyApp extends StatefulWidget {
  final SharedPreferences prefs;
  final bool firebaseInitialized;
  const MyApp({Key? key, required this.prefs, required this.firebaseInitialized}) : super(key: key);

  _MyAppState createState() => _MyAppState();

  static void setLocale(BuildContext context, Locale newLocale) {
    final _MyAppState? state = context.findAncestorStateOfType<_MyAppState>();
    if (state == null) {
      if (kDebugMode) debugPrint('MyApp.setLocale: ancestor state not found');
      return;
    }
    state.setLocale(newLocale);
  }
}

class _MyAppState extends State<MyApp> {
  Locale? _locale = const Locale('en', 'US');
  String messageImage = '';
  String messageName = '';
  String messageId = '';
  String userToken = '';

  void initState() {
    super.initState();
    if (widget.firebaseInitialized) {
      initApp();
    }
    // settingRequest();
  }

  String msgId = "";
  String msgName = "";
  String msgImage = "";
  String doctorToken = "";

  Future<void> initApp() async {
    Future.delayed(const Duration(seconds: 2), () {
      FirebaseMessaging.instance
          .getInitialMessage()
          .then((RemoteMessage? message) {
        if (message != null) {
          final Map<String, dynamic> dataValue = message.data;
          msgImage = dataValue['doctorImage'].toString();
          msgName = dataValue['doctorName'].toString();
          msgId = dataValue['doctorId'].toString();
          doctorToken = dataValue['doctorToken'].toString();
          if (SharedPreferenceHelper.getBoolean(Preferences.is_logged_in) ==
              true) {
            Navigator.of(context).pushReplacement(MaterialPageRoute(
              builder: (context) => ChatPage(
                peerId: dataValue['doctorId'].toString(),
                peerAvatar: dataValue['doctorImage'].toString(),
                peerNickname: dataValue['doctorName'].toString(),
                token: dataValue['doctorToken'].toString(),
                isNavigate: "",
              ),
            ));
          } else {
            Navigator.of(context).pushReplacement(MaterialPageRoute(
              builder: (context) => SignIn(),
            ));
          }
        }
      });

      NotificationHandler.notificationResponse.addListener(() {
        final response = NotificationHandler.notificationResponse.value;
        if (response != null) {
          _processNotificationResponse(response);
          NotificationHandler.notificationResponse.value = null; // reset
        }
      });
    });

    const initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    const initializationSettingsIOS = DarwinInitializationSettings();
    const initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
    );

    flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: onSelectNotification,
      onDidReceiveBackgroundNotificationResponse: notificationTapBackground,
    );

    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      // final RemoteNotification? notification = message.notification;
      // final AndroidNotification? android = message.notification?.android;
      // final Map<String, dynamic> dataValue = message.data;
      // final String screen = dataValue['screen'].toString();
      final data = message.data;

      logger.i(data);
      flutterLocalNotificationsPlugin.show(
        DateTime.now().millisecondsSinceEpoch ~/ 1000,
        data['title'],
        data['body'],
        NotificationDetails(
          android: AndroidNotificationDetails(
            channel.id,
            channel.name,
            icon: "@mipmap/ic_launcher",
            importance: Importance.max,
            priority: Priority.high,
            actions: data['action_type'] == 'call_notification'
                ? <AndroidNotificationAction>[
                    AndroidNotificationAction(
                      'accept_action',
                      'Accept',
                      showsUserInterface: true,
                      cancelNotification: true,
                    ),
                    AndroidNotificationAction(
                      'decline_action',
                      'Decline',
                      showsUserInterface: true,
                      cancelNotification: true,
                    ),
                  ]
                : null,
          ),
        ),
        payload: jsonEncode(data),
      );
    });

    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      logger.i("Notification tapped: ${message.data}");
      // Map<String, dynamic> data = message.data;
      // logger.e(data);
      // ScaffoldMessenger.of(context).showSnackBar(
      //   SnackBar(
      //     content: Text('$data'),
      //     duration: Duration(seconds: 10),
      //   ),
      // );
      // String? actionId = data['actionId'];
      // String? doctorId = data['id'];
      //
      // if (actionId == "decline_action") {
      //   if (doctorId != null)
      //     Navigator.push(
      //       context,
      //       MaterialPageRoute(
      //         builder: (context) => VideoCall(
      //           id: int.tryParse('$doctorId'),
      //           flag: "Cut",
      //           callEnd: true,
      //         ),
      //       ),
      //     );
      // }
      // else if (actionId == "accept_action") {
      //   logger.i('accept id = $doctorId');
      //   if (doctorId != null)
      //     Navigator.pushReplacement(
      //       context,
      //       MaterialPageRoute(
      //         builder: (context) => VideoCall(
      //           id: int.parse('${doctorId}'),
      //           flag: "InComming",
      //           callEnd: false,
      //         ),
      //       ),
      //     );
      // }
      // else {
      //   Navigator.pushReplacement(
      //     context,
      //     MaterialPageRoute(
      //       builder: (context) => PhoneScreen(data),
      //     ),
      //   );
      // }

      // final RemoteNotification? notification = message.notification;
      // final AndroidNotification? android = message.notification?.android;
      // if (notification != null && android != null) {
      //   Navigator.of(context).pushReplacement(MaterialPageRoute(
      //     builder: (context) => ChatPage(
      //       peerId: msgId,
      //       peerAvatar: msgImage,
      //       peerNickname: msgName,
      //       doctorToken: doctorToken,
      //       where: "",
      //     ),
      //   ));
      // }
    });
    if (Platform.isAndroid) {
      final permission = await Permission.notification.request();
      if (permission.isGranted) {
      }
    }
  }

  void _processNotificationResponse(NotificationResponse payload) async {
    final actionId = payload.actionId;
    final doctorId = jsonDecode(payload.payload ?? '{}')['id'];
    if (doctorId == null) return;

    if (actionId == 'accept_action') {
      // Handle accept
      if (doctorId != null)
        navigatorKey.currentState?.pushReplacement(
          MaterialPageRoute(
            builder: (context) => VideoCall(
              id: int.parse('${doctorId}'),
              flag: "InComming",
              callEnd: false,
            ),
          ),
        );
      // Navigate or call accept logic
      return;
    } else if (actionId == 'decline_action') {
      // Handle decline
      if (doctorId != null)
        navigatorKey.currentState?.pushReplacement(
          MaterialPageRoute(
            builder: (context) => VideoCall(
              id: int.tryParse('$doctorId'),
              flag: "Cut",
              callEnd: true,
            ),
          ),
        );
      return;
    } /*else if (jsonDecode('${payload.payload}')['screen'] != null) {
      if (messageId.isNotEmpty &&
          msgName.isNotEmpty &&
          msgImage.isNotEmpty &&
          SharedPreferenceHelper.getBoolean(Preferences.is_logged_in) == true) {
        Navigator.of(context).pushReplacement(MaterialPageRoute(
          builder: (context) => ChatPage(
            peerId: messageId,
            peerAvatar: msgImage,
            peerNickname: msgName,
            token: doctorToken,
            isNavigate: "",
          ),
        ));
      }
    }*/
  }

  Future<void> onSelectNotification(NotificationResponse payload) async {
    if (payload.payload == null) return;
    NotificationHandler.handle(payload);
    logger.w('Inside payload ${jsonDecode('${payload.payload}')}');
    logger.w('Inside ${payload.input}');
    logger.w('Inside ${payload.actionId}');
    logger.w('Inside ${payload.id}');
    logger.w('Inside ${payload.notificationResponseType.name}');
  }

  Future<BaseModel<Setting>> settingRequest() async {
    Setting response;

    try {
      response =
          await RestClient(await RetroApi2().dioData2()).settingRequest();
      log("Data = ${response.data?.toJson()} ");
      if (SharedPreferenceHelper.getBoolean(Preferences.is_logged_in) == true) {
        if (response.data!.stripeSecretKey != null) {
          SharedPreferenceHelper.setString(
              Preferences.stripeSecretKey, response.data!.stripeSecretKey!);
        }

        if (response.data!.stripePublicKey != null) {
          SharedPreferenceHelper.setString(
              Preferences.stripPublicKey, response.data!.stripePublicKey!);
        }

        if (response.data!.flutterwaveEncryptionKey != null) {
          SharedPreferenceHelper.setString(
              Preferences.flutterWave_encryption_key,
              response.data!.flutterwaveEncryptionKey!);
        }

        if (response.data!.flutterwaveKey != null) {
          SharedPreferenceHelper.setString(
              Preferences.flutterWave_key, response.data!.flutterwaveKey!);
        }

        if (response.data!.paystackPublicKey != null) {
          SharedPreferenceHelper.setString(Preferences.payStack_public_key,
              response.data!.paystackPublicKey!);
        }

        if (response.data!.razorKey != null) {
          SharedPreferenceHelper.setString(
              Preferences.razor_key, response.data!.razorKey!);
        }

        if (response.data!.paypalProducationKey != null) {
          SharedPreferenceHelper.setString(Preferences.payPal_production_key,
              response.data!.paypalProducationKey!);
        }

        if (response.data!.paypalSandboxKey != null) {
          SharedPreferenceHelper.setString(
              Preferences.payPal_sandbox_key, response.data!.paypalSandboxKey!);
        }

        if (response.data!.paypalClientId != null) {
          SharedPreferenceHelper.setString(
              Preferences.paypal_client_key, response.data!.paypalClientId!);
        }

        if (response.data!.paypalSecretKey != null) {
          SharedPreferenceHelper.setString(
              Preferences.paypal_secret_key, response.data!.paypalSecretKey!);
        }

        if (response.data!.currencySymbol != null) {
          SharedPreferenceHelper.setString(
              Preferences.currency_symbol, response.data!.currencySymbol!);
        }

        if (response.data!.currencyCode != null) {
          SharedPreferenceHelper.setString(
              Preferences.currency_code, response.data!.currencyCode!);
        }

        if (response.data!.doctorAppId != null) {
          SharedPreferenceHelper.setString(
              Preferences.doctorAppId, response.data!.doctorAppId!);
        }
      } else {
        if (response.data!.currencySymbol != null) {
          SharedPreferenceHelper.setString(
              Preferences.currency_symbol, response.data!.currencySymbol!);
        }

        if (response.data!.currencyCode != null) {
          SharedPreferenceHelper.setString(
              Preferences.currency_code, response.data!.currencyCode!);
        }

        if (response.data!.doctorAppId != null) {
          setState(() {
            SharedPreferenceHelper.setString(
                Preferences.doctorAppId, response.data!.doctorAppId!);
          });
        }

        if (response.data!.doctorAppId != null) {
          // setState(() {
          //   getOneSignalToken(
          //       SharedPreferenceHelper.getString(Preferences.doctorAppId));
          // });
        }
      }
    } catch (error, stacktrace) {

      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  // getOneSignalToken(appId) async {
  //   log("From getOneSignalToken appId frommm api = $appId");
  //
  //   OneSignal.Debug.setLogLevel(OSLogLevel.verbose);
  //
  //   OneSignal.initialize(appId);
  //   if (kDebugMode) {
  //     log("OneSignal App ID: " + appId);
  //   }
  //   OneSignal.LiveActivities.setupDefault();
  //   // OneSignal.LiveActivities.setupDefault(options: new LiveActivitySetupOptions(enablePushToStart: false, enablePushToUpdate: true));
  //
  //   // AndroidOnly stat only
  //   // OneSignal.Notifications.removeNotification(1);
  //   // OneSignal.Notifications.removeGroupedNotifications("group5");
  //
  //   OneSignal.Notifications.clearAll();
  //
  //   OneSignal.User.pushSubscription.addObserver((state) {
  //     log("optedIn = ${OneSignal.User.pushSubscription.optedIn}");
  //     log("id = ${OneSignal.User.pushSubscription.id}");
  //     log("token = ${OneSignal.User.pushSubscription.token}");
  //     log("jsonRepresentation = ${state.current.jsonRepresentation()}");
  //   });
  //   OneSignal.Notifications.addPermissionObserver((state) {
  //     log("Has permission " + state.toString());
  //   });
  //   log("Permission ${OneSignal.Notifications.permission}");
  //   Platform.isIOS
  //       ? OneSignal.Notifications.permission == false &&
  //               SharedPreferenceHelper.getBoolean(
  //                       Preferences.notificationPermissionDialog) ==
  //                   false
  //           ? OneSignal.Notifications.requestPermission(true)
  //           : null
  //       : null;
  //   Platform.isAndroid ? OneSignal.Notifications.requestPermission(true) : null;
  //   if (kDebugMode) {
  //     log("Permission ${OneSignal.Notifications.permission}");
  //
  //     log("OneSignal ID : ${OneSignal.User.pushSubscription.id}");
  //     log("OneSignal Token : ${OneSignal.User.pushSubscription.token}");
  //     var status = await OneSignal.User.getOnesignalId();
  //
  //     log("Test gopi main status = $status");
  //
  //     // return;
  //   }
  //   OneSignal.Debug.setAlertLevel(OSLogLevel.none);
  //   log("OneSignal.User.pushSubscription.id = ${OneSignal.User.pushSubscription.id.toString()}");
  //   if (OneSignal.User.pushSubscription.id != null) {
  //     SharedPreferenceHelper.setString(Preferences.device_token,
  //         OneSignal.User.pushSubscription.id.toString());
  //   }
  //
  //   if (SharedPreferenceHelper.getString(Preferences.device_token) != 'N_A') {
  //     SharedPreferenceHelper.getString(Preferences.device_token);
  //     log("preference device_token = ${SharedPreferenceHelper.getString(Preferences.device_token)}");
  //   } else {
  //     getOneSignalToken(appId);
  //   }
  // }

  void setLocale(Locale locale) {
    setState(() {
      _locale = locale;
    });
  }

  void didChangeDependencies() {
    getLocale().then((local) => {
          setState(() {
            this._locale = local;
          })
        });
    super.didChangeDependencies();
  }

  Widget build(BuildContext context) {
    if (_locale == null) {
      return SizedBox(
        child: Center(
          child: CircularProgressIndicator(),
        ),
      );
    } else {
      if (!widget.firebaseInitialized) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          home: const FirebaseUnavailableScreen(),
        );
      }

      final FirebaseFirestore firebaseFirestore = FirebaseFirestore.instance;
      final FirebaseStorage firebaseStorage = FirebaseStorage.instance;

      return AnnotatedRegion<SystemUiOverlayStyle>(
        value: SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          statusBarIconBrightness: Brightness.dark,
          systemNavigationBarColor: Colors.white,
          systemNavigationBarIconBrightness: Brightness.dark,
        ),
        child: ChangeNotifierProvider<OverlayHandlerProvider>(
          create: (_) => OverlayHandlerProvider(),
          child: MultiProvider(
            providers: [
              ChangeNotifierProvider<provider.AuthProvider>(
                create: (_) => provider.AuthProvider(
                  firebaseAuth: FirebaseAuth.instance,
                  prefs: widget.prefs,
                  firebaseFirestore: firebaseFirestore,
                ),
              ),
              Provider<HomeProvider>(
                create: (_) => HomeProvider(
                  firebaseFirestore: firebaseFirestore,
                ),
              ),
              Provider<ChatProvider>(
                create: (_) => ChatProvider(
                  prefs: widget.prefs,
                  firebaseFirestore: firebaseFirestore,
                  firebaseStorage: firebaseStorage,
                ),
              ),
              ChangeNotifierProvider<ThemeProvider>(
                create: (_) => ThemeProvider(),
              ),
            ],
            child: Consumer<ThemeProvider>(
                builder: (context, themeProvider, child) {
                  return MaterialApp(
                    themeMode: ThemeMode.light,
                    navigatorKey: navigatorKey,
                    title: "Ayureze",
                    debugShowCheckedModeBanner: false,
                    theme: themeProvider.theme,
                    home: SharedPreferenceHelper.getBoolean(Preferences.is_logged_in)
                        ? LoginHomeScreen(chat: "")
                        : SignIn(),
                    locale: _locale,
              supportedLocales: const [
                Locale(ENGLISH, 'US'),
                Locale(TAMIL, 'IN'),
                Locale(HINDI, 'IN'),
                Locale(MALAYALAM, 'IN'),
                Locale(TELUGU, 'IN'),
                Locale(KANNADA, 'IN'),
              ],
              localizationsDelegates: [
                LanguageLocalization.delegate,
                GlobalMaterialLocalizations.delegate,
                GlobalWidgetsLocalizations.delegate,
                GlobalCupertinoLocalizations.delegate,
              ],
              localeResolutionCallback: (deviceLocal, supportedLocales) {
                if (deviceLocal == null) {
                  return supportedLocales.first;
                }
                for (var local in supportedLocales) {
                  if (local.languageCode == deviceLocal.languageCode) {
                    return local;
                  }
                }
                return supportedLocales.first;
              },
              routes: {
                // '/': (context) => SignIn(),
                'SignIn': (context) => SignIn(),
                'signup': (context) => CreateAccount(),
                'ForgotPasswordScreen': (context) => ForgotPasswordScreen(),
                'phoneverification': (context) => PhoneVerificationScreen(),
                'loginHome': (context) => LoginHomeScreen(chat: ""),
                'patientInformation': (context) => patientDetailsScreen(),
                'cancelAppoitmentRoutes': (context) =>
                    CancelAppointmentScreen(),
                'AppointmentHistoryScreen': (context) =>
                    AppointmentHistoryScreen(),
                'rateAndReviewRoutes': (context) => RateAndReviewRoutesScreen(),
                'notifications': (context) => NotificationsScreen(),
                'profile': (context) => ProfileScreen(),
                'payment': (context) => PaymentScreen(),
                'subscription': (context) => SubSubscription(),
                'paymentGatewayRoutes': (context) => PaymentGatewayScreen(),
                'Subscription History': (context) => SubscriptionHistory(),
                'Schedule Timings': (context) => ScheduleTimings(),
                'Change Password': (context) => ChangePassword(),
                'Change Language': (context) => ChangeLanguage(),
                'ViewAllNotification': (context) => ViewAllNotification(),
                // 'Stripe': (context) => Stripe(),
                'VideoCallHistory': (context) => VideoCallHistory(),
                'Settings': (context) => SettingScreen(),
                'ChatHome': (context) => HomePage(),
              },
              );
            },
            ),
          ),
        ),
      );
    }
  }
}

class FirebaseUnavailableScreen extends StatelessWidget {
  const FirebaseUnavailableScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: const [
                Icon(Icons.cloud_off, size: 52, color: Colors.redAccent),
                SizedBox(height: 12),
                Text(
                  'Service setup error',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
                ),
                SizedBox(height: 8),
                Text(
                  'The app could not connect to required services. Please check Firebase configuration and restart the app.',
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

@pragma('vm:entry-point')
void notificationTapBackground(NotificationResponse response) {
  NotificationHandler.notificationResponse.value = response;
}
