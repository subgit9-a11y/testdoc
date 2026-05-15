import 'dart:core';
import 'dart:io' show Platform;

import 'package:dio/dio.dart';
import 'package:doctro/chat/providers/auth_provider.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/login.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/auth/signup.dart';
import 'package:doctro/screens/auth/forgotpassword.dart';
import 'package:doctro/screens/auth/phoneverification.dart';
import 'package:doctro/screens/home%20page/login_home.dart';
import 'package:doctro/services/supabase_service.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/widgets/osler_button.dart';
import 'package:doctro/widgets/osler_input.dart';
import 'package:doctro/widgets/osler_alert.dart';
import 'package:doctro/widgets/osler_tooltip.dart';
import 'package:firebase_auth/firebase_auth.dart';
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

  @override
  void dispose() {
    email.dispose();
    password.dispose();
    super.dispose();
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
      backgroundColor: AyurezeTheme.canvas,
      body: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () {
          FocusScope.of(context).unfocus();
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
                    decoration: AyurezeTheme.heroDecoration(),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.14),
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: const Text(
                            "Doctor workspace",
                            style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700),
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
                                    getTranslated(context, AppString.login_heading).toString(),
                                    style: const TextStyle(fontSize: 30, height: 1.05, fontWeight: FontWeight.w800, color: Colors.white),
                                  ),
                                  const SizedBox(height: 10),
                                  Text(
                                    "Run your practice with a calmer Ayureze-style workflow for visits, patients, and follow-up.",
                                    style: TextStyle(fontSize: 14, height: 1.4, color: Colors.white.withOpacity(0.78)),
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
                    decoration: AyurezeTheme.panelDecoration(),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          getTranslated(context, AppString.login_to_your_account).toString(),
                          style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textSecondary),
                        ),
                        const SizedBox(height: 18),
                        OslerInput(
                          label: getTranslated(context, AppString.login_email_hint).toString(),
                          hint: "example@email.com",
                          controller: email,
                          keyboardType: TextInputType.emailAddress,
                          prefixIcon: Icon(Icons.alternate_email_rounded, size: 20, color: AyurezeTheme.healingGreen100),
                          validator: (String? value) {
                            if (value!.isEmpty) {
                              return getTranslated(context, AppString.login_email_validator).toString();
                            }
                            if (!RegExp(r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+").hasMatch(value)) {
                              return getTranslated(context, AppString.login_email_validator2).toString();
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 14),
                        OslerInput(
                          label: getTranslated(context, AppString.login_password_hint).toString(),
                          hint: "••••••••",
                          controller: password,
                          isPassword: _isHidden,
                          prefixIcon: Icon(Icons.lock_outline_rounded, size: 20, color: AyurezeTheme.healingGreen100),
                          suffixIcon: IconButton(
                            icon: Icon(_isHidden ? Icons.visibility_off_rounded : Icons.visibility_rounded, size: 20, color: AyurezeTheme.healingGreen100),
                            onPressed: () => setState(() => _isHidden = !_isHidden),
                          ),
                          validator: (String? value) {
                            if (value!.isEmpty) {
                              return getTranslated(context, AppString.login_password_validator).toString();
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 8),
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: () => Navigator.pushNamed(context, 'ForgotPasswordScreen'),
                            child: Text(
                              getTranslated(context, AppString.login_forgot_password).toString(),
                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AyurezeTheme.healingGreen100),
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),
                        OslerButton(
                          text: getTranslated(context, AppString.login_button).toString(),
                          onPressed: () {
                            if (_formkey.currentState!.validate()) {
                              callApiForLogin();
                            }
                          },
                        ),
                        const SizedBox(height: 24),
                        Row(
                          children: [
                            Expanded(child: Divider(color: AyurezeTheme.textSecondary.withOpacity(0.1))),
                            Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 16),
                              child: Text(
                                "Or continue with",
                                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AyurezeTheme.textSecondary.withOpacity(0.5)),
                              ),
                            ),
                            Expanded(child: Divider(color: AyurezeTheme.textSecondary.withOpacity(0.1))),
                          ],
                        ),
                        const SizedBox(height: 20),
                        OutlinedButton(
                          style: OutlinedButton.styleFrom(
                            minimumSize: const Size(double.infinity, 56),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                            side: BorderSide(color: AyurezeTheme.textSecondary.withOpacity(0.1)),
                          ),
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
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AyurezeTheme.textPrimary),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 18),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                    decoration: AyurezeTheme.mutedPanelDecoration(),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          getTranslated(context, AppString.login_dont_have_account).toString(),
                          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: AyurezeTheme.textSecondary),
                        ),
                        TextButton(
                          onPressed: () => Navigator.pushNamed(context, 'signup'),
                          child: Text(
                            getTranslated(context, AppString.login_sign_up).toString(),
                            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AyurezeTheme.forestDeep),
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
        errorText = "Google Sign In Error: Please ensure:\n1. Internet connection is active\n2. Google Play Services are installed\n3. Your Google account is properly configured";
      } else if (authProvider.status == Status.authenticateCanceled) {
        errorText = "Google Sign In was canceled";
      }
      // Show error using OslerAlert in the build context
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorText),
            backgroundColor: AyurezeTheme.remoteRed100,
          ),
        );
      }
    }
  }

  void _saveUserData(LoginResponse response) {
    SharedPreferenceHelper.setString(Preferences.name, response.data!.name ?? '');
    SharedPreferenceHelper.setString(
      Preferences.phone_no,
      response.data!.phone ?? '',
    );
    SharedPreferenceHelper.setString(Preferences.email, response.data!.email ?? '');
    SharedPreferenceHelper.setString(Preferences.image, response.data!.image ?? '');
    SharedPreferenceHelper.setInt(
      Preferences.is_filled,
      response.data!.isFilled ?? 0,
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
      response.data!.fullImage ?? '',
    );
    SharedPreferenceHelper.setString(
      Preferences.user_name,
      response.data!.name ?? '',
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

    LoginResponse response;

    try {
      CommonFunction.onLoading(context);
      response = await RestClient(await RetroApi().dioData(context))
          .loginRequest(body);
      CommonFunction.hideDialog(context);

      if (response.success == true) {
        _saveUserData(response);
        OslerToast.success(context, response.msg!);

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
          OslerToast.error(context, response.msg!);
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

