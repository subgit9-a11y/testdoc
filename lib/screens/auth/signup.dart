import 'dart:core';
import 'dart:io';

import 'package:country_picker/country_picker.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/common_function.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/register.dart';
import 'package:doctro/model/otp_verify.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/auth/SignIn.dart';
import 'package:doctro/screens/auth/phoneverification.dart';
import 'package:doctro/screens/auth/forgotpassword.dart';
import 'package:doctro/screens/auth/professional_registration_screen.dart';
import 'package:doctro/screens/auth/registration_success_screen.dart';
import 'package:doctro/services/supabase_service.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/widgets/osler_button.dart';
import 'package:doctro/widgets/osler_input.dart';
import 'package:doctro/widgets/osler_dropdown.dart';
import 'package:doctro/widgets/osler_alert.dart';
import 'package:doctro/widgets/osler_toast.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';

class CreateAccount extends StatefulWidget {
  final Map<String, dynamic>? prefillData;
  CreateAccount({this.prefillData});
  @override
  _CreateAccountState createState() => _CreateAccountState();
}

class _CreateAccountState extends State<CreateAccount> {
  late double width;
  late double height;

  bool _isHidden = true;

  List<String> gender = ["Male", "Female"];
  String? _genderSelect;

  @override
  void initState() {
    super.initState();
    if (widget.prefillData != null) {
      _name.text = widget.prefillData!['name'] ?? "";
      _email.text = widget.prefillData!['email'] ?? "";
    }

    Future.delayed(Duration.zero, () {
      gender = [
        getTranslated(context, AppString.gender_male).toString(),
        getTranslated(context, AppString.gender_female).toString(),
      ];
    });
  }

  @override
  void dispose() {
    _name.dispose();
    _email.dispose();
    _dob.dispose();
    _phone.dispose();
    _password.dispose();
    _phoneCode.dispose();
    super.dispose();
  }

  DateTime? _selectedDate;
  String newDateApiPass = "";

  final _formkey = GlobalKey<FormState>();

  TextEditingController _name = TextEditingController();
  TextEditingController _email = TextEditingController();
  TextEditingController _dob = TextEditingController();
  TextEditingController _phone = TextEditingController();
  TextEditingController _password = TextEditingController();
  TextEditingController _phoneCode = TextEditingController(text: "+91");

  bool _isFaceVerified = false;
  String? _capturedImagePath;
  final SupabaseService _supabaseService = SupabaseService();

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
        onTap: () => FocusScope.of(context).requestFocus(FocusNode()),
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 28),
          child: Form(
            key: _formkey,
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
                        getTranslated(context, AppString.register_heading).toString(),
                        style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w800, color: Colors.white, letterSpacing: -0.5),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        "Join the world's most advanced Ayurveda platform",
                        style: TextStyle(fontSize: 14, color: Colors.white.withOpacity(0.8)),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: AyurezeTheme.panelDecoration(),
                  child: Column(
                    children: [
                      OslerInput(
                        label: getTranslated(context, AppString.register_full_name).toString(),
                        hint: "Enter your full name",
                        controller: _name,
                        keyboardType: TextInputType.name,
                        inputFormatters: [FilteringTextInputFormatter.allow(RegExp("[a-zA-Z ]"))],
                        textCapitalization: TextCapitalization.words,
                        prefixIcon: Icon(Icons.person_outline_rounded, size: 20, color: AyurezeTheme.healingGreen100),
                        validator: (String? value) {
                          if (value!.isEmpty) {
                            return getTranslated(context, AppString.please_enter_full_name).toString();
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 14),
                      OslerInput(
                        label: getTranslated(context, AppString.register_email_hint).toString(),
                        hint: "Enter your email",
                        controller: _email,
                        keyboardType: TextInputType.emailAddress,
                        prefixIcon: Icon(Icons.alternate_email_rounded, size: 20, color: AyurezeTheme.healingGreen100),
                        validator: (String? value) {
                          if (value!.isEmpty) {
                            return getTranslated(context, AppString.please_enter_email).toString();
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 14),
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            flex: 2,
                            child: OslerInput(
                              label: "Code",
                              hint: "+91",
                              controller: _phoneCode,
                              readOnly: true,
                              onTap: () {
                                showCountryPicker(
                                  context: context,
                                  showPhoneCode: true,
                                  onSelect: (Country country) => setState(() => _phoneCode.text = "+${country.phoneCode}"),
                                );
                              },
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            flex: 5,
                            child: OslerInput(
                              label: getTranslated(context, AppString.register_phone_no).toString(),
                              hint: "Enter phone number",
                              controller: _phone,
                              keyboardType: TextInputType.phone,
                              inputFormatters: [FilteringTextInputFormatter.digitsOnly, LengthLimitingTextInputFormatter(10)],
                              prefixIcon: Icon(Icons.phone_iphone_rounded, size: 20, color: AyurezeTheme.healingGreen100),
                              validator: (String? value) {
                                if (value!.isEmpty) return getTranslated(context, AppString.please_enter_phone_no).toString();
                                if (value.length != 10) return getTranslated(context, AppString.please_enter_valid_number).toString();
                                return null;
                              },
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 14),
                      OslerInput(
                        label: getTranslated(context, AppString.register_birth_date_hint).toString(),
                        hint: "Select your DOB",
                        controller: _dob,
                        readOnly: true,
                        onTap: () => _selectDate(context),
                        prefixIcon: Icon(Icons.calendar_month_rounded, size: 20, color: AyurezeTheme.healingGreen100),
                        validator: (String? value) {
                          if (value!.isEmpty) return getTranslated(context, AppString.please_select_birth_date).toString();
                          return null;
                        },
                      ),
                      const SizedBox(height: 14),
                      OslerDropdown(
                        label: '',
                        hint: getTranslated(context, AppString.register_select_gender_hint).toString(),
                        value: _genderSelect,
                        items: gender,
                        prefixIcon: Icons.people_alt_rounded,
                        onChanged: (newValue) => setState(() => _genderSelect = newValue),
                        validator: (value) => value == null ? getTranslated(context, AppString.please_select_gender).toString() : null,
                      ),
                      const SizedBox(height: 14),
                      OslerInput(
                        label: getTranslated(context, AppString.register_password_hint).toString(),
                        hint: "••••••••",
                        controller: _password,
                        isPassword: _isHidden,
                        prefixIcon: Icon(Icons.lock_outline_rounded, size: 20, color: AyurezeTheme.healingGreen100),
                        suffixIcon: IconButton(
                          icon: Icon(_isHidden ? Icons.visibility_off_rounded : Icons.visibility_rounded, size: 20, color: AyurezeTheme.healingGreen100),
                          onPressed: () => setState(() => _isHidden = !_isHidden),
                        ),
                        validator: (String? value) {
                          if (value!.isEmpty) return getTranslated(context, AppString.please_enter_password).toString();
                          return null;
                        },
                      ),
                      const SizedBox(height: 24),
                      OslerButton(
                        text: getTranslated(context, AppString.register_button).toString(),
                        onPressed: () {
                          if (_formkey.currentState!.validate()) {
                            Map<String, dynamic> personalData = {
                              "name": _name.text,
                              "email": _email.text,
                              "dob": _dob.text,
                              "gender": _genderSelect,
                              "phone": _phone.text,
                              "password": _password.text,
                              "phone_code": _phoneCode.text,
                            };
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => ProfessionalRegistrationScreen(personalData: personalData),
                              ),
                            );
                          }
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                  decoration: AyurezeTheme.mutedPanelDecoration(),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        getTranslated(context, AppString.register_all_ready_account).toString(),
                        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: AyurezeTheme.textSecondary),
                      ),
                      TextButton(
                        onPressed: () => Navigator.pushNamed(context, 'SignIn'),
                        child: Text(
                          getTranslated(context, AppString.register_sign_in).toString(),
                          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AyurezeTheme.healingGreen100),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                Text(
                  getTranslated(context, AppString.register_description).toString(),
                  style: TextStyle(fontSize: 11, color: AyurezeTheme.textSecondary),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<BaseModel<Register>> callApiForRegister() async {
    if (_selectedDate == null) {
      OslerToast.warning(context, "Please select your birth date");
      return BaseModel()..setException(ServerError.withError(error: "Date not selected"));
    }

    newDateApiPass = DateUtilForPass().formattedDate(_selectedDate!);

    Register response;
    try {
      CommonFunction.onLoading(context);

      final doctorId = _supabaseService.generateDoctorID();

      String? photoUrl;
      if (_capturedImagePath != null) {
        photoUrl = await _supabaseService.uploadProfilePhoto(File(_capturedImagePath!), doctorId);
      }

      Map<String, dynamic> body = {
        "name": _name.text,
        "email": _email.text,
        "dob": newDateApiPass,
        "gender": _genderSelect,
        "phone": _phone.text,
        "password": _password.text,
        "phone_code": _phoneCode.text,
        "unique_id": doctorId,
        "is_face_verified": _isFaceVerified ? 1 : 0,
        "photo_url": photoUrl ?? "",
      };

      await _supabaseService.saveDoctorProfile(
        doctorId: doctorId,
        name: _name.text,
        email: _email.text,
        phone: _phoneCode.text + _phone.text,
        gender: _genderSelect ?? "",
        dob: newDateApiPass,
        photoUrl: photoUrl,
        isFaceVerified: _isFaceVerified,
      );

      response = await RestClient(await RetroApi().dioData(context)).registerRequest(body);

      CommonFunction.hideDialog(context);
      final data = OtpData(otp: response.data!.otp, id: response.data!.id);

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => RegistrationSuccessScreen(
            doctorName: _name.text,
            doctorId: doctorId,
            email: _email.text,
            subtitle: "Step 1 complete! Now verify your phone number to activate your account.",
            onContinue: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => PhoneVerificationScreen(data: data)),
              );
            },
          ),
        ),
      );
    } catch (error, stacktrace) {
      CommonFunction.hideDialog(context);
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  _selectDate(BuildContext context) async {
    DateTime? newSelectedDate = await showDatePicker(
      context: context,
      initialDate: _selectedDate != null ? _selectedDate! : DateTime.now().subtract(const Duration(days: 365 * 25)),
      firstDate: DateTime(1950, 1),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: ThemeData.light().copyWith(
            primaryColor: loginButton,
            colorScheme: ColorScheme.light(
              primary: loginButton,
              onPrimary: Colors.white,
              surface: Colors.white,
              onSurface: loginButton,
            ),
            dialogBackgroundColor: Colors.white,
            textButtonTheme: TextButtonThemeData(
              style: TextButton.styleFrom(foregroundColor: loginButton),
            ),
          ),
          child: child!,
        );
      },
    );
    if (newSelectedDate != null) {
      _selectedDate = newSelectedDate;
      _dob
        ..text = DateFormat('dd-MM-yyyy').format(_selectedDate!)
        ..selection = TextSelection.fromPosition(
          TextPosition(offset: _dob.text.length, affinity: TextAffinity.upstream),
        );
    }
  }
}

class DateUtilForPass {
  static const DATE_FORMAT = 'yyyy-MM-dd';

  String formattedDate(DateTime dateTime) {
    return DateFormat(DATE_FORMAT).format(dateTime);
  }
}