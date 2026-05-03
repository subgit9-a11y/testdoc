import 'dart:core';
import 'dart:io' show Platform;

import 'package:dio/dio.dart';
import 'package:doctro/chat/providers/auth_provider.dart';
import 'package:doctro/constant/app_icons.dart';
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
import 'package:doctro/screens/auth/signup.dart';
import 'package:doctro/theme/osler_theme.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase;
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:provider/provider.dart';

class SignIn extends StatefulWidget {
  @override
  _SignInState createState() => _SignInState();
}

class _SignInState extends State<SignIn> {
  late double width;
  late double height;

  final GlobalKey<FormState> _formkey = GlobalKey<FormState>();

  final TextEditingController email = TextEditingController();
  final TextEditingController password = TextEditingController();

  bool _isHidden = true;

  String? deviceToken;

  late AuthProvider authProvider;

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

  Future<void> getToken() async {
    try {
      String? token = await FirebaseMessaging.instance.getToken();
      if (token != null && token.isNotEmpty) {
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
      backgroundColor: OslerTheme.canvas,
      body: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () {
          FocusScope.of(context).requestFocus(FocusNode());
        },
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 24, 20, 28),
          child: Form(
            key: _formkey,
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: height - 52),
              child: Column(
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(22),
                    decoration: OslerTheme.heroDecoration(),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.14),
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: const Text(
                            "Doctor workspace",
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                        const SizedBox(height: 18),
                        Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    getTranslated(context, AppString.login_heading)
                                        .toString(),
                                    style: const TextStyle(
                                      fontSize: 30,
                                      height: 1.05,
                                      fontWeight: FontWeight.w800,
                                      color: Colors.white,
                                    ),
                                  ),
                                  const SizedBox(height: 10),
                                  Text(
                                    "Run your practice with a calmer Osler-style workflow for visits, patients, and follow-up.",
                                    style: TextStyle(
                                      fontSize: 14,
                                      height: 1.4,
                                      color: Colors.white.withOpacity(0.78),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 16),
                            ClipRRect(
                              borderRadius: BorderRadius.circular(24),
                              child: Image.asset(
                                "assets/images/confident-doctor-half.png",
                                height: 150,
                                width: 100,
                                fit: BoxFit.cover,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 18),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.fromLTRB(20, 22, 20, 20),
                    decoration: OslerTheme.panelDecoration(),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          getTranslated(context, AppString.login_to_your_account)
                              .toString(),
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                            color: OslerTheme.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 18),
                        TextFormField(
                          controller: email,
                          keyboardType: TextInputType.emailAddress,
                          style: TextStyle(fontSize: 16, color: cardText),
                          decoration: InputDecoration(
                            labelText: getTranslated(
                              context,
                              AppString.login_email_hint,
                            ).toString(),
                            hintText: "example@email.com",
                            prefixIcon: Icon(
                              Icons.alternate_email_rounded,
                              color: loginButton,
                            ),
                          ),
                          validator: (String? value) {
                            if (value!.isEmpty) {
                              return getTranslated(
                                context,
                                AppString.please_enter_email,
                              ).toString();
                            }
                            if (!RegExp(
                              r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+",
                            ).hasMatch(value)) {
                              return getTranslated(
                                context,
                                AppString.please_enter_valid_email,
                              ).toString();
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 14),
                        TextFormField(
                          controller: password,
                          style: TextStyle(fontSize: 16, color: cardText),
                          decoration: InputDecoration(
                            labelText: getTranslated(
                              context,
                              AppString.login_password_hint,
                            ).toString(),
                            hintText: "........",
                            prefixIcon: Icon(
                              Icons.lock_outline_rounded,
                              color: loginButton,
                            ),
                            suffixIcon: IconButton(
                              icon: Icon(
                                _isHidden
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                                color: hintColor,
                              ),
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
                              return getTranslated(
                                context,
                                AppString.please_enter_password,
                              ).toString();
                            } else if (value.length < 6) {
                              return getTranslated(
                                context,
                                AppString.please_enter_valid_password,
                              ).toString();
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 18),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: () {
                              if (_formkey.currentState!.validate()) {
                                callApiForLogin();
                              }
                            },
                            child: Text(
                              getTranslated(context, AppString.login_button)
                                  .toString(),
                            ),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            child: Text(
                              getTranslated(
                                context,
                                AppString.login_forgot_password,
                              ).toString(),
                              style: const TextStyle(
                                fontSize: 14,
                                color: ForgotPasswordScreen,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            onPressed: () {
                              Navigator.pushNamed(
                                context,
                                'ForgotPasswordScreen',
                              );
                            },
                          ),
                        ),
                        Row(
                          children: [
                            Expanded(
                              child: Divider(
                                color: hintColor.withOpacity(0.18),
                              ),
                            ),
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 10),
                              child: Text(
                                "Or continue with",
                                style: TextStyle(
                                  color: hintColor,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                            Expanded(
                              child: Divider(
                                color: hintColor.withOpacity(0.18),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 14),
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton(
                            onPressed: _handleGoogleSignIn,
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                SvgPicture.string(
                                  '<svg viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/><path fill="none" d="M0 0h48v48H0z"/></svg>',
                                  height: 24,
                                  width: 24,
                                ),
                                const SizedBox(width: 12),
                                Text(
                                  "Sign in with Google",
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w700,
                                    color: cardText,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 18),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(18),
                    decoration: OslerTheme.mutedPanelDecoration(),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            getTranslated(
                              context,
                              AppString.login_dont_have_account,
                            ).toString(),
                            style: TextStyle(
                              fontSize: width * 0.04,
                              color: subheading,
                            ),
                          ),
                        ),
                        TextButton(
                          child: Text(
                            getTranslated(context, AppString.login_sign_up)
                                .toString(),
                            style: TextStyle(
                              fontSize: width * 0.04,
                              color: loginButton,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          onPressed: () {
                            Navigator.pushNamed(context, 'signup');
                          },
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _handleGoogleSignIn() async {
    firebase.User? user = await authProvider.signInWithGoogle();
    if (user != null) {
      try {
        CommonFunction.onLoading(context);
        final loginBody = {
          "email": user.email,
          "password": "GOOGLE_USER_AUTH",
          "device_token":
              SharedPreferenceHelper.getString(Preferences.messageToken)
        };

        final response =
            await RestClient(await RetroApi().dioData(context))
                .loginRequest(loginBody);

        CommonFunction.hideDialog(context);

        if (response.success == true && response.data != null) {
          _saveUserData(response);
          SharedPreferenceHelper.setBoolean(Preferences.is_logged_in, true);
          Navigator.pushNamedAndRemoveUntil(
            context,
            'loginHome',
            (route) => false,
          );
        } else {
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
        errorText =
            "Sign-in error: Please check your Google account settings or connection.";
      }
      Fluttertoast.showToast(msg: errorText);
    }
  }

  void _saveUserData(LoginResponse response) {
    SharedPreferenceHelper.setString(Preferences.name, response.data!.name!);
    SharedPreferenceHelper.setString(
      Preferences.phone_no,
      response.data!.phone!,
    );
    SharedPreferenceHelper.setString(Preferences.email, response.data!.email!);
    SharedPreferenceHelper.setString(Preferences.image, response.data!.image!);
    SharedPreferenceHelper.setInt(
      Preferences.is_filled,
      response.data!.isFilled!,
    );

    if (response.token != null) {
      SharedPreferenceHelper.setString(
        Preferences.auth_token,
        response.token!,
      );
    }
    if (response.refreshToken != null) {
      SharedPreferenceHelper.setString(
        Preferences.refresh_token,
        response.refreshToken!,
      );
    }
    if (response.expiresIn != null) {
      SharedPreferenceHelper.setInt(
        Preferences.expiresIn,
        int.parse('${response.expiresIn}'),
      );
      SharedPreferenceHelper.setInt(
        'token_saved_at',
        DateTime.now().millisecondsSinceEpoch,
      );
    }
    if (response.data!.subscriptionStatus == null) {
      SharedPreferenceHelper.setInt(Preferences.subscription_status, -1);
    } else {
      SharedPreferenceHelper.setInt(
        Preferences.subscription_status,
        response.data!.subscriptionStatus!,
      );
    }
    SharedPreferenceHelper.setString(
      Preferences.chat_profile,
      response.data!.fullImage!,
    );
    SharedPreferenceHelper.setString(
      Preferences.user_name,
      response.data!.name!,
    );
    SharedPreferenceHelper.setString(
      Preferences.doctorId,
      response.data!.id.toString(),
    );

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
              builder: (context) => PhoneVerificationScreen(data: data),
            ),
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
              builder: (context) => PhoneVerificationScreen(data: data),
            ),
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
            Preferences.stripeSecretKey,
            response.data!.stripeSecretKey!,
          );
        }

        if (response.data!.stripePublicKey != null) {
          SharedPreferenceHelper.setString(
            Preferences.stripPublicKey,
            response.data!.stripePublicKey!,
          );
        }

        if (response.data!.flutterwaveEncryptionKey != null) {
          SharedPreferenceHelper.setString(
            Preferences.flutterWave_encryption_key,
            response.data!.flutterwaveEncryptionKey!,
          );
        }

        if (response.data!.flutterwaveKey != null) {
          SharedPreferenceHelper.setString(
            Preferences.flutterWave_key,
            response.data!.flutterwaveKey!,
          );
        }

        if (response.data!.paystackPublicKey != null) {
          SharedPreferenceHelper.setString(
            Preferences.payStack_public_key,
            response.data!.paystackPublicKey!,
          );
        }

        if (response.data!.razorKey != null) {
          SharedPreferenceHelper.setString(
            Preferences.razor_key,
            response.data!.razorKey!,
          );
        }

        if (response.data!.paypalProducationKey != null) {
          SharedPreferenceHelper.setString(
            Preferences.payPal_production_key,
            response.data!.paypalProducationKey!,
          );
        }

        if (response.data!.paypalSandboxKey != null) {
          SharedPreferenceHelper.setString(
            Preferences.payPal_sandbox_key,
            response.data!.paypalSandboxKey!,
          );
        }

        if (response.data!.paypalClientId != null) {
          SharedPreferenceHelper.setString(
            Preferences.paypal_client_key,
            response.data!.paypalClientId!,
          );
        }

        if (response.data!.paypalSecretKey != null) {
          SharedPreferenceHelper.setString(
            Preferences.paypal_secret_key,
            response.data!.paypalSecretKey!,
          );
        }

        if (response.data!.currencySymbol != null) {
          SharedPreferenceHelper.setString(
            Preferences.currency_symbol,
            response.data!.currencySymbol!,
          );
        }

        if (response.data!.currencyCode != null) {
          SharedPreferenceHelper.setString(
            Preferences.currency_code,
            response.data!.currencyCode!,
          );
        }

        if (response.data!.doctorAppId != null) {
          setState(() {
            SharedPreferenceHelper.setString(
              Preferences.doctorAppId,
              response.data!.doctorAppId!,
            );
          });
        }
      } else {
        if (response.data!.currencySymbol != null) {
          SharedPreferenceHelper.setString(
            Preferences.currency_symbol,
            response.data!.currencySymbol!,
          );
        }

        if (response.data!.currencyCode != null) {
          SharedPreferenceHelper.setString(
            Preferences.currency_code,
            response.data!.currencyCode!,
          );
        }

        if (response.data!.doctorAppId != null) {
          setState(() {
            SharedPreferenceHelper.setString(
              Preferences.doctorAppId,
              response.data!.doctorAppId!,
            );
          });
        }
      }
    } catch (error) {
      debugPrint("Exception in settingRequest: $error");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }
}
