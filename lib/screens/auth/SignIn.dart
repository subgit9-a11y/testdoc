import 'dart:core';
import 'dart:io' show Platform;
import 'package:dio/dio.dart';


import 'package:doctro/chat/providers/auth_provider.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/common_function.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/login.dart';
import 'package:doctro/model/otp_verify.dart';
import 'package:doctro/model/setting.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/auth/phoneverification.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:provider/provider.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase;
import 'package:doctro/screens/auth/signup.dart';

class SignIn extends StatefulWidget {
  @override
  _SignInState createState() => _SignInState();
}

class _SignInState extends State<SignIn> {
  //Set Height/Width Using MediaQuery
  late double width;
  late double height;

  //Set Open Drawer
  final GlobalKey<FormState> _formkey = GlobalKey<FormState>();

  // Sign In TextInput Controller //
  TextEditingController email = TextEditingController();
  TextEditingController password = TextEditingController();

  // Set Password Visibility //
  bool _isHidden = true;

  String? deviceToken;

  late AuthProvider authProvider;

  //set verify validation //
  int? verify;

  String messageImage = '';
  String messageName = '';
  String messageId = '';
  String token = '';
  String userToken = '';

  @override
  void initState() {
    super.initState();
    if (Platform.isAndroid) {
      SharedPreferenceHelper.setString(Preferences.device_platform, "Android");
    }
    settingRequest();
    getToken();
  }

  getToken() async {
    try {
      String? token = await FirebaseMessaging.instance.getToken();
      if (token != null && token.isNotEmpty) {
        // print("Firebase Token : " + token);
        SharedPreferenceHelper.setString(Preferences.messageToken, token);
      }
    } catch (e) {
      debugPrint("Error getting FCM token: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    authProvider = Provider.of<AuthProvider>(context);

    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return Scaffold(
      body: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () {
          FocusScope.of(context).requestFocus(new FocusNode());
        },
        child: SingleChildScrollView(
          child: Form(
            key: _formkey,
            child: Column(
              children: [
                Container(
                  height: height * 1,
                  width: width * 1,
                  child: Stack(
                    children: [
                      Image.asset(
                        "assets/images/confident-doctor-half.png",
                        height: height * 0.5,
                        width: width * 1,
                        fit: BoxFit.fill,
                      ),
                      Positioned(
                        top: height * 0.36,
                        child: Container(
                          width: width * 1,
                          height: height * 1,
                          decoration: BoxDecoration(
                              color: colorWhite,
                              borderRadius: BorderRadius.only(
                                topLeft: Radius.circular(width * 0.1),
                                topRight: Radius.circular(width * 0.1),
                              )),
                          child: SingleChildScrollView(
                            child: Container(
                              height: height * 0.6,
                              width: width * 1.0,
                              child: Column(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceEvenly,
                                children: [
                                  Text(
                                    getTranslated(
                                            context, AppString.login_heading)
                                        .toString(),
                                    style: TextStyle(
                                        fontSize: 28,
                                        fontWeight: FontWeight.bold,
                                        color: cardText),
                                  ),
                                  Text(
                                    getTranslated(context,
                                            AppString.login_to_your_account)
                                        .toString(),
                                    style: TextStyle(
                                        fontSize: width * 0.04,
                                        color: subheading),
                                  ),
                                  Padding(
                                    padding: const EdgeInsets.symmetric(horizontal: 25, vertical: 8),
                                    child: TextFormField(
                                      controller: email,
                                      keyboardType: TextInputType.emailAddress,
                                      style: TextStyle(fontSize: 16, color: cardText),
                                      decoration: InputDecoration(
                                        labelText: getTranslated(context, AppString.login_email_hint).toString(),
                                        hintText: "example@email.com",
                                        labelStyle: TextStyle(color: hintColor),
                                        prefixIcon: Icon(Icons.email_outlined, color: loginButton),
                                        filled: true,
                                        fillColor: scaffoldBg,
                                        enabledBorder: OutlineInputBorder(
                                          borderRadius: BorderRadius.circular(12),
                                          borderSide: BorderSide(color: cardBorder),
                                        ),
                                        focusedBorder: OutlineInputBorder(
                                          borderRadius: BorderRadius.circular(12),
                                          borderSide: BorderSide(color: loginButton, width: 2),
                                        ),
                                      ),
                                      validator: (String? value) {
                                        if (value!.isEmpty) {
                                          return getTranslated(context, AppString.please_enter_email).toString();
                                        }
                                        if (!RegExp(r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+").hasMatch(value)) {
                                          return getTranslated(context, AppString.please_enter_valid_email).toString();
                                        }
                                        return null;
                                      },
                                    ),
                                  ),
                                  Padding(
                                    padding: const EdgeInsets.symmetric(horizontal: 25, vertical: 8),
                                    child: TextFormField(
                                      controller: password,
                                      style: TextStyle(fontSize: 16, color: cardText),
                                      decoration: InputDecoration(
                                        labelText: getTranslated(context, AppString.login_password_hint).toString(),
                                        hintText: "••••••••",
                                        labelStyle: TextStyle(color: hintColor),
                                        prefixIcon: Icon(Icons.lock_outline, color: loginButton),
                                        filled: true,
                                        fillColor: scaffoldBg,
                                        enabledBorder: OutlineInputBorder(
                                          borderRadius: BorderRadius.circular(12),
                                          borderSide: BorderSide(color: cardBorder),
                                        ),
                                        focusedBorder: OutlineInputBorder(
                                          borderRadius: BorderRadius.circular(12),
                                          borderSide: BorderSide(color: loginButton, width: 2),
                                        ),
                                        suffixIcon: IconButton(
                                          icon: Icon(_isHidden ? Icons.visibility_outlined : Icons.visibility_off_outlined, color: hintColor),
                                          onPressed: () {
                                            setState(() {
                                              _isHidden = !_isHidden;
                                            });
                                          },
                                        ),
                                      ),
                                      obscureText: _isHidden,
                                      validator: (String? value) {
                                        if (value!.isEmpty) {
                                          return getTranslated(context, AppString.please_enter_password).toString();
                                        } else if (value.length < 6) {
                                          return getTranslated(context, AppString.please_enter_valid_password).toString();
                                        }
                                        return null;
                                      },
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.symmetric(horizontal: 25, vertical: 15),
                                    width: double.infinity,
                                    height: 55,
                                    child: ElevatedButton(
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: loginButton,
                                        shape: RoundedRectangleBorder(
                                          borderRadius: BorderRadius.circular(12),
                                        ),
                                        elevation: 5,
                                        shadowColor: loginButton.withOpacity(0.4),
                                      ),
                                      child: Text(
                                        getTranslated(context, AppString.login_button).toString(),
                                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                                      ),
                                      onPressed: () {
                                        if (_formkey.currentState!.validate()) {
                                          callApiForLogin();
                                        }
                                      },
                                    ),
                                  ),
                                  
                                  // Divider
                                  Padding(
                                    padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 10),
                                    child: Row(
                                      children: [
                                        Expanded(child: Divider(color: hintColor.withOpacity(0.3))),
                                        Padding(
                                          padding: const EdgeInsets.symmetric(horizontal: 10),
                                          child: Text("Or continue with", style: TextStyle(color: hintColor, fontSize: 12)),
                                        ),
                                        Expanded(child: Divider(color: hintColor.withOpacity(0.3))),
                                      ],
                                    ),
                                  ),

                                  // Google Sign In Button
                                  Container(
                                    margin: EdgeInsets.symmetric(horizontal: 25, vertical: 5),
                                    width: double.infinity,
                                    height: 55,
                                    child: OutlinedButton(
                                      style: OutlinedButton.styleFrom(
                                        backgroundColor: Colors.white,
                                        side: BorderSide(color: cardBorder),
                                        shape: RoundedRectangleBorder(
                                          borderRadius: BorderRadius.circular(12),
                                        ),
                                        elevation: 2,
                                        shadowColor: Colors.black.withOpacity(0.05),
                                      ),
                                      onPressed: () async {
                                        firebase.User? user = await authProvider.signInWithGoogle();
                                        if (user != null) {
                                          try {
                                            CommonFunction.onLoading(context);
                                            // Try to log in with Google Email to see if user exists in MySQL
                                            final loginBody = {
                                              "email": user.email,
                                              "password": "GOOGLE_USER_AUTH", // Placeholder/Flag
                                              "device_token": SharedPreferenceHelper.getString(Preferences.messageToken)
                                            };
                                            
                                            final response = await RestClient(await RetroApi().dioData(context))
                                                .loginRequest(loginBody);
                                            
                                            CommonFunction.hideDialog(context);

                                            if (response.success == true && response.data != null) {
                                              // OLD USER: Save details and go to Home
                                              _saveUserData(response);
                                              
                                              SharedPreferenceHelper.setBoolean(Preferences.is_logged_in, true);
                                              Navigator.pushNamedAndRemoveUntil(context, 'loginHome', (route) => false);
                                            } else {
                                              // NEW USER: Go to Signup
                                              Navigator.push(
                                                context,
                                                MaterialPageRoute(
                                                  builder: (context) => CreateAccount(
                                                    prefillData: {
                                                      "name": user.displayName,
                                                      "email": user.email,
                                                    },
                                                  ),
                                                ),
                                              );
                                            }
                                          } catch (e) {
                                            CommonFunction.hideDialog(context);
                                            // Fallback for new users if login fails with error
                                            Navigator.push(
                                              context,
                                              MaterialPageRoute(
                                                builder: (context) => CreateAccount(
                                                  prefillData: {
                                                    "name": user.displayName,
                                                    "email": user.email,
                                                  },
                                                ),
                                              ),
                                            );
                                          }
                                        } else {
                                          String errorText = "Google Sign In Failed or Canceled";
                                          if (authProvider.status == Status.authenticateError) {
                                            errorText = "Sign-in error: Please check your Google account settings or connection.";
                                          }
                                          Fluttertoast.showToast(msg: errorText);
                                        }
                                      },
                                      child: Row(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        children: [
                                          SvgPicture.string(
                                            '<svg viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/><path fill="none" d="M0 0h48v48H0z"/></svg>',
                                            height: 24,
                                            width: 24,
                                          ),
                                          SizedBox(width: 12),
                                          Text(
                                            "Sign in with Google",
                                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: cardText),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                  TextButton(
                                    child: Text(
                                      getTranslated(context,
                                              AppString.login_forgot_password)
                                          .toString(),
                                      style: TextStyle(
                                          fontSize: width * 0.042,
                                          color: ForgotPasswordScreen),
                                      textAlign: TextAlign.center,
                                    ),
                                    onPressed: () {
                                      Navigator.pushNamed(
                                          context, 'ForgotPasswordScreen');
                                    },
                                  ),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Container(
                                        child: Text(
                                          getTranslated(
                                                  context,
                                                  AppString
                                                      .login_dont_have_account)
                                              .toString(),
                                          style: TextStyle(
                                              fontSize: width * 0.04,
                                              color: subheading),
                                        ),
                                      ),
                                      TextButton(
                                        child: Text(
                                          getTranslated(context,
                                                  AppString.login_sign_up)
                                              .toString(),
                                          style: TextStyle(
                                              fontSize: width * 0.04,
                                              color: loginButton,
                                              fontWeight: FontWeight.bold),
                                        ),
                                        onPressed: () {
                                          Navigator.pushNamed(
                                              context, 'signup');
                                        },
                                      )
                                    ],
                                  )
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _saveUserData(LoginResponse response) {
    SharedPreferenceHelper.setString(Preferences.name, response.data!.name!);
    SharedPreferenceHelper.setString(Preferences.phone_no, response.data!.phone!);
    SharedPreferenceHelper.setString(Preferences.email, response.data!.email!);
    SharedPreferenceHelper.setString(Preferences.image, response.data!.image!);
    SharedPreferenceHelper.setInt(Preferences.is_filled, response.data!.isFilled!);
    
    if (response.token != null) {
      SharedPreferenceHelper.setString(Preferences.auth_token, response.token!);
    }
    if (response.refreshToken != null) {
      SharedPreferenceHelper.setString(Preferences.refresh_token, response.refreshToken!);
    }
    if (response.expiresIn != null) {
      SharedPreferenceHelper.setInt(Preferences.expiresIn, int.parse('${response.expiresIn}'));
      SharedPreferenceHelper.setInt('token_saved_at', DateTime.now().millisecondsSinceEpoch);
    }
    if (response.data!.subscriptionStatus == null) {
      SharedPreferenceHelper.setInt(Preferences.subscription_status, -1);
    } else {
      SharedPreferenceHelper.setInt(Preferences.subscription_status, response.data!.subscriptionStatus!);
    }
    SharedPreferenceHelper.setString(Preferences.chat_profile, response.data!.fullImage!);
    SharedPreferenceHelper.setString(Preferences.user_name, response.data!.name!);
    SharedPreferenceHelper.setString(Preferences.doctorId, response.data!.id.toString());
    
    authProvider.handleSignIn();
  }

  Future<BaseModel<LoginResponse>> callApiForLogin() async {
    Map<String, dynamic> body = {
      "email": email.text,
      "password": password.text,
      "device_token": SharedPreferenceHelper.getString(Preferences.messageToken)
    };

    SharedPreferenceHelper.setString(Preferences.user_email, email.text);
    SharedPreferenceHelper.setString(Preferences.password, password.text);

    LoginResponse response;

    try {
      CommonFunction.onLoading(context);
      response = await RestClient(await RetroApi().dioData(context))
          .loginRequest(body);
      CommonFunction.hideDialog(context);

      if (response.success == true) {
        _saveUserData(response);

        Fluttertoast.showToast(
          msg: response.msg!,
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM,
        );

        if (response.data!.verify == 0) {
          final data = OtpData(otp: response.data!.otp, id: response.data!.id);
          Navigator.push(
            context,
            MaterialPageRoute(
                builder: (context) => PhoneVerificationScreen(data: data)),
          );
        } else {
          SharedPreferenceHelper.setBoolean(Preferences.is_logged_in, true);
          Navigator.pushReplacementNamed(context, 'loginHome');
        }
      } else {
        if (response.data != null && response.data!.verify == 0) {
          final data = OtpData(otp: response.data!.otp, id: response.data!.id);
          Navigator.push(
            context,
            MaterialPageRoute(
                builder: (context) => PhoneVerificationScreen(data: data)),
          );
        } else {
          Fluttertoast.showToast(
            msg: response.msg!,
            toastLength: Toast.LENGTH_SHORT,
            gravity: ToastGravity.BOTTOM,
          );
        }
      }
    } catch (error, stacktrace) {
      CommonFunction.hideDialog(context);
      if (error is DioException) {
        print("Login Error Response: ${error.response?.data}");
      }
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<Setting>> settingRequest() async {
    Setting response;

    try {
      response =
          await RestClient(await RetroApi2().dioData2()).settingRequest();

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
          setState(() {
            SharedPreferenceHelper.setString(
                Preferences.doctorAppId, response.data!.doctorAppId!);
          });
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
          // getOneSingleToken(
          //     SharedPreferenceHelper.getString(Preferences.doctorAppId));
        }
      }
    } catch (error) {
      debugPrint("Exception in settingRequest: $error");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  // getOneSingleToken(appId) async {
  //   OneSignal.Debug.setLogLevel(OSLogLevel.info);
  //
  //   OneSignal.initialize(appId);
  //   if (kDebugMode) {
  //     // print("OneSignal App ID: " + appId);
  //     return;
  //   }
  //   OneSignal.Notifications.addPermissionObserver((state) {
  //     // print("Has permission " + state.toString());
  //   });
  //   // print("Permission ${OneSignal.Notifications.permission}");
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
  //     // print("OneSignal ID : ${OneSignal.User.pushSubscription.id}");
  //     // print("OneSignal Token : ${OneSignal.User.pushSubscription.token}");
  //   }
  //   OneSignal.Debug.setAlertLevel(OSLogLevel.none);
  //
  //   if (SharedPreferenceHelper.getString(Preferences.device_token) == "" ||
  //       SharedPreferenceHelper.getString(Preferences.device_token) == "N_A") {
  //     if (OneSignal.User.pushSubscription.id != null) {
  //       SharedPreferenceHelper.setString(Preferences.device_token,
  //           OneSignal.User.pushSubscription.id.toString());
  //     } else {
  //       // getOneSingleToken(appId);
  //       SharedPreferenceHelper.setString(Preferences.device_token, '');
  //     }
  //   }
  // }
}
