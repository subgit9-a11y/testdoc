import 'dart:convert';

import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/common_function.dart';
import 'package:doctro/constant/date_util.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/localization/language_model.dart';
import 'package:doctro/model/doctor_profile.dart';
import 'package:doctro/model/UpdateProfile.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/widgets/osler_toast.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart';

class ChangeLanguage extends StatefulWidget {
  const ChangeLanguage({Key? key}) : super(key: key);

  @override
  _ChangeLanguageState createState() => _ChangeLanguageState();
}

class _ChangeLanguageState extends State<ChangeLanguage> {
  Future? languageLoader;
  String? name;

  var convertDegree;
  var eduCertificate;

  final TextEditingController _pDegree = TextEditingController();
  final TextEditingController _pExperience = TextEditingController();
  final TextEditingController _pStartTime = TextEditingController();
  final TextEditingController _pEndTime = TextEditingController();
  final TextEditingController _pTimeSlot = TextEditingController();
  final TextEditingController _pAppointmentFees = TextEditingController();
  final TextEditingController _pName = TextEditingController();
  final TextEditingController _pDob = TextEditingController();
  final TextEditingController _pDesc = TextEditingController();
  final TextEditingController _pCollege = TextEditingController();
  final TextEditingController _pCollegeYear = TextEditingController();
  final TextEditingController _pCertificate = TextEditingController();
  final TextEditingController _pCertificateYear = TextEditingController();
  final TextEditingController _pBasedOn = TextEditingController();

  final picker = ImagePicker();

  List<String> popular = [];
  String? _selectedPopular;

  List<String> gender = [];
  String? _genderSelect;

  int? isFilled;
  int? treatmentId;
  int? categoryId;
  int? expertiseId;
  String? hospitalId;
  String? image;
  String? videoAppointmentFees;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    gender = [
      getTranslated(context, AppString.gender_male).toString(),
      getTranslated(context, AppString.gender_female).toString(),
    ];

    popular = [
      getTranslated(context, AppString.popular_yes).toString(),
      getTranslated(context, AppString.popular_no).toString(),
    ];
  }

  @override
  void initState() {
    super.initState();
    languageLoader = doctorProfile();
    name = SharedPreferenceHelper.getString(Preferences.name);
    isFilled = SharedPreferenceHelper.getInt(Preferences.is_filled);
    image = SharedPreferenceHelper.getString(Preferences.image);
  }

  int? value;

  @override
  Widget build(BuildContext context) {
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
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          getTranslated(context, AppString.chang_language).toString(),
          style: TextStyle(
            color: AyurezeTheme.textPrimary,
            fontSize: 20,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: FutureBuilder(
        future: languageLoader,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return Center(
              child: CircularProgressIndicator(color: AyurezeTheme.forestDeep),
            );
          }

          return GestureDetector(
            onTap: () {
              FocusScope.of(context).requestFocus(FocusNode());
            },
            child: SingleChildScrollView(
              padding: AyurezeTheme.screenPadding,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHero(),
                  const SizedBox(height: 18),
                  ...List.generate(Language.languageList().length, (index) {
                    value = Language.languageList()[index].languageCode ==
                            SharedPreferenceHelper.getString(
                                Preferences.current_language_code)
                        ? index
                        : null;
                    if (SharedPreferenceHelper.getString(
                            Preferences.current_language_code) ==
                        'N_A') {
                      value = 0;
                    }

                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Container(
                        decoration: AyurezeTheme.panelDecoration(),
                        child: RadioListTile(
                          value: index,
                          controlAffinity: ListTileControlAffinity.trailing,
                          groupValue: value,
                          activeColor: AyurezeTheme.forestDeep,
                          onChanged: (dynamic selected) async {
                            Future.delayed(const Duration(seconds: 1), () async {
                              value = selected;
                              Locale local = await setLocale(
                                Language.languageList()[index].languageCode,
                              );
                              setState(() {
                                SharedPreferenceHelper.setString(
                                  Preferences.current_language_code,
                                  Language.languageList()[index].languageCode,
                                );
                                SharedPreferenceHelper.setString(
                                  Preferences.language_name,
                                  Language.languageList()[index].name,
                                );
                                updateProfile();
                                Navigator.popAndPushNamed(context, "loginHome");
                              });
                            });
                          },
                          title: Text(
                            Language.languageList()[index].name,
                            style: TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.w700,
                              color: AyurezeTheme.textPrimary,
                            ),
                          ),
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
          );
        },
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
              "Language preferences",
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 14),
          const Text(
            "Choose how your Ayureze workspace speaks to you.",
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              height: 1.05,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "Pick the language that fits your workflow best. The app will switch as soon as the preference is saved.",
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

  Future<BaseModel<DoctorProfile>> doctorProfile() async {
    DoctorProfile response;

    try {
      response =
          await RestClient(await RetroApi().dioData(context)).doctorProfile();
      setState(() {
        if (response.data!.education != null) {
          convertDegree = json.decode(response.data!.education!);
        }

        if (response.data!.certificate != null) {
          eduCertificate = json.decode(response.data!.certificate!);
        }

        _pName.text = response.data!.name!;
        final showFormat = response.data!.dob;
        final newDateApiPass =
            DateUtil().formattedDate(DateTime.parse('$showFormat'));
        _pDob.text = newDateApiPass;

        _genderSelect = response.data!.gender!;

        if (convertDegree != null) {
          for (int i = 0; i < convertDegree.length; i++) {
            _pDegree.text = _pDegree.text.length == 0
                ? _pDegree.text + convertDegree[i]['degree']
                : _pDegree.text + ',' + convertDegree[i]['degree'];
            _pCollege.text = _pCollege.text.length == 0
                ? _pCollege.text + convertDegree[i]['college']
                : _pCollege.text + ',' + convertDegree[i]['college'];
            _pCollegeYear.text = _pCollegeYear.text.length == 0
                ? _pCollegeYear.text + convertDegree[i]['year']
                : _pCollegeYear.text + ',' + convertDegree[i]['year'];
          }
        }

        if (eduCertificate != null) {
          for (int i = 0; i < eduCertificate.length; i++) {
            _pCertificate.text = _pCertificate.text.length == 0
                ? _pCertificate.text + eduCertificate[i]['certificate']
                : _pCertificate.text + ',' + eduCertificate[i]['certificate'];

            _pCertificateYear.text = _pCertificateYear.text.length == 0
                ? _pCertificateYear.text + eduCertificate[i]['certificate_year']
                : _pCertificateYear.text +
                    ',' +
                    eduCertificate[i]['certificate_year'];
          }
        }

        _pExperience.text = response.data!.experience!;
        _pAppointmentFees.text = response.data!.appointmentFees!;
        _pTimeSlot.text = response.data!.timeslot!;
        _pStartTime.text = response.data!.startTime!;
        _pEndTime.text = response.data!.endTime!;
        _pBasedOn.text = response.data!.basedOn!;
        _pDesc.text = response.data!.desc!;

        _selectedPopular = response.data!.isPopular.toString();

        treatmentId = response.data!.treatmentId!;
        categoryId = response.data!.categoryId;
        expertiseId = response.data!.expertiseId;
        hospitalId = response.data!.hospitalId;
        videoAppointmentFees = response.data!.videoAppointmentFees;
      });
    } catch (error, stacktrace) {
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<UpdateProfile>> updateProfile() async {
    UpdateProfile response;
    Map<String, dynamic> body = {
      "name": _pName.text,
      "dob": _pDob.text,
      "gender": _genderSelect,
      "education": convertDegree != null ? json.encode(convertDegree) : _pDegree.text,
      "certificate": eduCertificate != null ? json.encode(eduCertificate) : null,
      "video_appointment_fees": videoAppointmentFees,
      "experience": _pExperience.text,
      "appointment_fees": _pAppointmentFees.text,
      "timeslot": _pTimeSlot.text,
      "start_time": _pStartTime.text,
      "end_time": _pEndTime.text,
      "based_on": _pBasedOn.text,
      "desc": _pDesc.text,
      "treatment_id": treatmentId,
      "category_id": categoryId,
      "expertise_id": expertiseId,
      "hospital_id": hospitalId,
      "is_popular": _selectedPopular,
      "language": SharedPreferenceHelper.getString(Preferences.language_name),
    };
    try {
      response = await RestClient(await RetroApi().dioData(context))
          .updateProfile(body);
      OslerToast.success(context, response.msg!);
    } catch (error, stacktrace) {
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }
}

