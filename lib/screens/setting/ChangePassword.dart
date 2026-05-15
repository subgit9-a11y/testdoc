import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/ChangePassword.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/widgets/osler_button.dart';
import 'package:doctro/widgets/osler_toast.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class ChangePassword extends StatefulWidget {
  const ChangePassword({Key? key}) : super(key: key);

  @override
  _ChangePasswordState createState() => _ChangePasswordState();
}

class _ChangePasswordState extends State<ChangePassword> {
  late double height;
  late double width;

  final TextEditingController _oldPassword = TextEditingController();
  final TextEditingController _newPassword = TextEditingController();
  final TextEditingController _confirmPassword = TextEditingController();

  final _formKey = GlobalKey<FormState>();

  bool _isHidden = true;
  bool _isHidden1 = true;
  bool _isHidden2 = true;

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: AyurezeTheme.canvas,
      appBar: AppBar(
        backgroundColor: AyurezeTheme.canvas,
        leading: IconButton(
          icon: Icon(
            AppIcons.back,
            color: AyurezeTheme.forestDeep,
            size: 20,
          ),
          onPressed: () {
            Navigator.pop(context);
          },
        ),
        title: Text(
          getTranslated(context, AppString.change_password_heading).toString(),
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w800,
            color: AyurezeTheme.textPrimary,
          ),
        ),
      ),
      body: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () {
          FocusScope.of(context).requestFocus(FocusNode());
        },
        child: SingleChildScrollView(
          padding: AyurezeTheme.screenPadding,
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHero(),
                const SizedBox(height: 18),
                _buildFormCard(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHero() {
    return Container(
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
              "Security update",
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 14),
          const Text(
            "Keep your doctor workspace protected.",
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              height: 1.05,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "Update your password with a calmer Ayureze-style form that keeps the task focused and clear.",
            style: TextStyle(
              color: Colors.white.withOpacity(0.78),
              fontSize: 14,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFormCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: AyurezeTheme.panelDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _fieldLabel(getTranslated(context, AppString.change_old_password).toString()),
          TextFormField(
            controller: _oldPassword,
            keyboardType: TextInputType.name,
            inputFormatters: [
              FilteringTextInputFormatter.allow(RegExp('[a-zA-Z0-9!@#\$.*&~_]'))
            ],
            decoration: InputDecoration(
              hintText: getTranslated(context, AppString.change_old_password_hint).toString(),
              suffixIcon: _toggleIcon(_isHidden, () {
                setState(() {
                  _isHidden = !_isHidden;
                });
              }),
            ),
            obscureText: _isHidden,
            validator: (String? value) {
              if (value!.isEmpty) {
                return getTranslated(context, AppString.please_enter_old_password).toString();
              } else if (value.length < 6) {
                return getTranslated(context, AppString.please_enter_valid_password).toString();
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          _fieldLabel(getTranslated(context, AppString.change_enter_new_password).toString()),
          TextFormField(
            controller: _newPassword,
            keyboardType: TextInputType.name,
            inputFormatters: [
              FilteringTextInputFormatter.allow(RegExp('[a-zA-Z0-9!@#\$.*&~_]'))
            ],
            decoration: InputDecoration(
              hintText: getTranslated(context, AppString.change_enter_new_password_hint).toString(),
              suffixIcon: _toggleIcon(_isHidden1, () {
                setState(() {
                  _isHidden1 = !_isHidden1;
                });
              }),
            ),
            obscureText: _isHidden1,
            validator: (String? value) {
              if (value!.isEmpty) {
                return getTranslated(context, AppString.please_enter_new_password).toString();
              } else if (value.length < 6) {
                return getTranslated(context, AppString.please_enter_valid_password).toString();
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          _fieldLabel(getTranslated(context, AppString.change_enter_confirm_password).toString()),
          TextFormField(
            controller: _confirmPassword,
            keyboardType: TextInputType.name,
            inputFormatters: [
              FilteringTextInputFormatter.allow(RegExp('[a-zA-Z0-9!@#\$.*&~_]'))
            ],
            decoration: InputDecoration(
              hintText: getTranslated(context, AppString.change_enter_confirm_password_hint).toString(),
              suffixIcon: _toggleIcon(_isHidden2, () {
                setState(() {
                  _isHidden2 = !_isHidden2;
                });
              }),
            ),
            obscureText: _isHidden2,
            validator: (String? value) {
              if (value!.isEmpty) {
                return getTranslated(context, AppString.please_enter_confirm_password).toString();
              } else if (_newPassword.text != _confirmPassword.text) {
                return getTranslated(context, AppString.confirm_not_match).toString();
              }
              return null;
            },
          ),
          const SizedBox(height: 22),
          SizedBox(
            width: double.infinity,
            child: OslerButton(
              text: getTranslated(context, AppString.change_password_button).toString(),
              onPressed: () {
                if (_formKey.currentState!.validate()) {
                  passwordChange();
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _fieldLabel(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w700,
          color: AyurezeTheme.textPrimary,
        ),
      ),
    );
  }

  Widget _toggleIcon(bool hidden, VoidCallback onTap) {
    return IconButton(
      icon: Icon(
        hidden ? AppIcons.visibility : AppIcons.visibilityOff,
        color: AyurezeTheme.textSecondary,
      ),
      onPressed: onTap,
    );
  }

  Future<BaseModel<ChangePasswordModel>> passwordChange() async {
    ChangePasswordModel response;
    Map<String, dynamic> body = {
      "old_password": _oldPassword.text,
      "new_password": _newPassword.text,
      "confirm_password": _confirmPassword.text,
    };

    try {
      response = await RestClient(await RetroApi().dioData(context))
          .changePasswordRequest(body);
      if (response.success == true) {
        OslerToast.success(context, response.data!);
        Navigator.pop(context);
      } else {
        OslerToast.error(context, response.data!);
      }
    } catch (error, stacktrace) {
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }
}

