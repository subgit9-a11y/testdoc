import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/widgets/osler_button.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/ForgotPassword.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:flutter/material.dart';
import 'package:doctro/widgets/osler_toast.dart';

class ForgotPasswordScreen extends StatefulWidget {
  @override
  _ForgotPasswordScreenState createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  late double width;
  late double height;

  String msg = "";

  //validation form
  var _formKey = GlobalKey<FormState>();

  TextEditingController _email = TextEditingController();

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: AyurezeTheme.canvas,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios_new_rounded, color: AyurezeTheme.textPrimary, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => FocusScope.of(context).requestFocus(FocusNode()),
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 0),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(22),
                  decoration: AyurezeTheme.heroDecoration(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        getTranslated(context, AppString.forgot_password_title).toString(),
                        style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w800, color: Colors.white, letterSpacing: -0.5),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        getTranslated(context, AppString.forgot_password_description).toString(),
                        style: TextStyle(fontSize: 14, color: Colors.white.withOpacity(0.8), height: 1.4),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 30),
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: AyurezeTheme.panelDecoration(),
                  child: Column(
                    children: [
                      TextFormField(
                        controller: _email,
                        keyboardType: TextInputType.emailAddress,
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                        decoration: AyurezeTheme.textFieldDecoration(
                          labelText: getTranslated(context, AppString.forgot_email_hint).toString(),
                        ).copyWith(prefixIcon: Icon(Icons.alternate_email_rounded, size: 20, color: AyurezeTheme.forestDeep)),
                        validator: (String? value) {
                          if (value!.isEmpty) {
                            return getTranslated(context, AppString.please_enter_email).toString();
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 24),
                      OslerButton(
                        text: getTranslated(context, AppString.forgot_reset_button).toString(),
                        onPressed: () {
                          if (_formKey.currentState!.validate()) {
                            forgotPasswordScreenRequest();
                          }
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
    );
  }

  Future<BaseModel<ForgotPassword>> forgotPasswordScreenRequest() async {
    ForgotPassword response;
    try {
      Map<String, dynamic> body = {"email": _email.text};
      response = (await RestClient(await RetroApi().dioData(context))
          .forgotPasswordScreen(body));
      setState(() {
        if (response.success == true) {
          Navigator.pushReplacementNamed(context, "SignIn");
          OslerToast.success(context, response.msg!);
        } else {
          OslerToast.error(context, response.msg!);
        }
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }
}
