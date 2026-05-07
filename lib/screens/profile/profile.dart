import 'dart:convert';
import 'dart:core';
import 'dart:io';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/EducationCertificate.dart';
import 'package:doctro/model/EducationModel.dart';
import 'package:doctro/model/Treatment.dart';
import 'package:doctro/model/UpdateProfile.dart';
import 'package:doctro/model/categories.dart';
import 'package:doctro/model/doctor_profile.dart';
import 'package:doctro/model/expertise.dart';
import 'package:doctro/model/hospital.dart';
import 'package:doctro/model/update_profile_image.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  _ProfileScreen createState() => _ProfileScreen();
}

//profile image
String? name = "";
String? msg = "";

//Choose Images
String? image;

class _ProfileScreen extends State<ProfileScreen> {
  Future? doctorLoader;

  //Add List Data
  List<EducationModel> educationList = [];
  List<EducationCertificate> certificateList = [];

  bool oldPassword = false;

  //alertdialog
  TextEditingController _degree = TextEditingController();
  TextEditingController _college = TextEditingController();
  TextEditingController _completeYear = TextEditingController();
  TextEditingController _certificate = TextEditingController();
  TextEditingController _year = TextEditingController();

  String callDegree = '';
  String callCollege = '';
  String callYear = '';
  String callCertificate = '';
  String callCertificateYear = '';
  String valueDegree = '';
  String valueCollege = '';
  String valueYear = '';
  String certificate = '';
  String certificateYear = '';

  //Select Dob
  DateTime? _selectedDate;
  String newDateApiPass = "";
  String? showFormat = '';
  var temp;
  List<String> selectedHospitals = [];

  //Set Stepper
  int _currentStep = 0;
  StepperType stepperType = StepperType.horizontal;

  //Doctor Profile Controller
  TextEditingController _pDegree = TextEditingController();
  TextEditingController _pExperience = TextEditingController();
  TextEditingController _pStartTime = TextEditingController();
  TextEditingController _pEndTime = TextEditingController();
  TextEditingController _pTimeSlot = TextEditingController();
  TextEditingController _vAppointmentFees = TextEditingController();
  TextEditingController _aAppointmentFees = TextEditingController();
  TextEditingController _pName = TextEditingController();
  TextEditingController _pDob = TextEditingController();
  TextEditingController _pDesc = TextEditingController();
  TextEditingController _pCollege = TextEditingController();
  TextEditingController _pCollegeYear = TextEditingController();
  TextEditingController _pCertificate = TextEditingController();
  TextEditingController _pCertificateYear = TextEditingController();
  TextEditingController _pBasedOn = TextEditingController();

  //Set Open Drawer
  final GlobalKey<FormState> _formkey = GlobalKey<FormState>();
  final GlobalKey<FormState> _step1 = GlobalKey<FormState>();
  final GlobalKey<FormState> _step2 = GlobalKey<FormState>();

  //Set List Data Hospital
  List<HospitalName> hospitalReq = [];

  //Set List Data Treatment
  List<TreatmentData> treatmentReq = [];
  TreatmentData? _valueTreatment;

  //Set List Data Category
  List<CategoriesData> categoryReq = [];
  CategoriesData? _valueCategories;

  //Set List Data Expertise
  List<Expert> expertReq = [];
  Expert? _valueExpertise;

  //update user image
  File? proImage;
  final picker = ImagePicker();

  //Set DropDown Popular Field
  List<String> popular = [];
  String? _selectedPopular;

  //Set DropDown For Male/Female
  List<String> gender = [];
  String? _genderSelect;

  int? isFilled;

  //Set MediaQuery Height / Width
  double? width;
  late double height;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    gender = [
      "male",
      "female",
    ];

    popular = [
      getTranslated(context, AppString.popular_yes).toString(),
      getTranslated(context, AppString.popular_no).toString(),
    ];
  }

  @override
  void initState() {
    super.initState();
    Future.delayed(Duration.zero, () {
      doctorLoader = treatment();
      hospital();
      name = SharedPreferenceHelper.getString(Preferences.name);
      isFilled = SharedPreferenceHelper.getInt(Preferences.is_filled);
      image = SharedPreferenceHelper.getString(Preferences.image);
    });
  }

  @override
  void dispose() {
    _degree.dispose();
    _college.dispose();
    _completeYear.dispose();
    _certificate.dispose();
    _year.dispose();
    _pDegree.dispose();
    _pExperience.dispose();
    _pStartTime.dispose();
    _pEndTime.dispose();
    _pTimeSlot.dispose();
    _vAppointmentFees.dispose();
    _aAppointmentFees.dispose();
    _pName.dispose();
    _pDob.dispose();
    _pDesc.dispose();
    _pCollege.dispose();
    _pCollegeYear.dispose();
    _pCertificate.dispose();
    _pCertificateYear.dispose();
    _pBasedOn.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: AyurezeTheme.canvas,
      appBar: PreferredSize(
        preferredSize: Size(width! * 0.3, 220),
        child: SafeArea(
          top: true,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: Container(
              decoration: AyurezeTheme.heroDecoration(),
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      GestureDetector(
                        child: Icon(
                          AppIcons.back,
                          size: 20,
                          color: Colors.white,
                        ),
                        onTap: () {
                          if (_currentStep == 0) Navigator.pop(context);
                          if (_currentStep == 1) cancel();
                          if (_currentStep == 2) cancel();
                        },
                      ),
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
                          "Profile workspace",
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 18),
                  Row(
                    children: [
                      SizedBox(
                        height: 90,
                        width: 90,
                        child: Stack(
                          children: [
                            proImage != null
                                ? Container(
                                    width: 82,
                                    height: 82,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      border: Border.all(
                                        color: AyurezeTheme.lime,
                                        width: 2,
                                      ),
                                    ),
                                    child: ClipRRect(
                                      borderRadius: BorderRadius.circular(50),
                                      child: Image.file(
                                        proImage!,
                                        fit: BoxFit.cover,
                                      ),
                                    ),
                                  )
                                : Container(
                                    width: 82,
                                    height: 82,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      border: Border.all(
                                        color: AyurezeTheme.lime,
                                        width: 2,
                                      ),
                                    ),
                                    child: CachedNetworkImage(
                                      imageUrl: SharedPreferenceHelper
                                          .getString(Preferences.image),
                                      imageBuilder: (context, imageProvider) =>
                                          CircleAvatar(
                                        backgroundColor: colorWhite,
                                        child: CircleAvatar(
                                          radius: 36,
                                          backgroundImage: imageProvider,
                                        ),
                                      ),
                                      placeholder: (context, url) =>
                                          CircularProgressIndicator(
                                        color: AyurezeTheme.lime,
                                      ),
                                      errorWidget: (context, url, error) =>
                                          Image.asset("images/no_image.png"),
                                    ),
                                  ),
                            Positioned(
                              top: 56,
                              left: 58,
                              child: GestureDetector(
                                onTap: () {
                                  chooseProfileImage();
                                },
                                child: CircleAvatar(
                                  backgroundColor: AyurezeTheme.lime,
                                  radius: 14,
                                  child: Icon(
                                    Icons.add,
                                    color: AyurezeTheme.forestDeep,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              "Doctor profile",
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 24,
                                fontWeight: FontWeight.w800,
                                height: 1.05,
                              ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              "$name",
                              style: TextStyle(
                                fontSize: width! * 0.047,
                                color: Colors.white.withOpacity(0.88),
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
      body: FutureBuilder(
          future: doctorLoader,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.done) {
              return Theme(
                data: Theme.of(context).copyWith(
                  colorScheme: Theme.of(context).colorScheme.copyWith(
                        primary: AyurezeTheme.forestDeep,
                        secondary: AyurezeTheme.lime,
                      ),
                ),
                child: Container(
                  width: width,
                  margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                  child: Column(
                    children: [
                    Expanded(
                      child: Stepper(
                        type: stepperType,
                        physics: ScrollPhysics(),
                        onStepCancel: null,
                        currentStep: _currentStep,
                        onStepTapped: (step) => tapped(step),
                        onStepContinue: continued,
                        steps: <Step>[
                          // Step 1 //
                          Step(
                            title: new Text(
                              getTranslated(context,
                                      AppString.profile_personal_information)
                                  .toString(),
                              style: TextStyle(fontSize: 12),
                            ),
                            content: GestureDetector(
                              onTap: () {
                                FocusScope.of(context)
                                    .requestFocus(new FocusNode());
                              },
                              child: Form(
                                key: _step1,
                                child: SingleChildScrollView(
                                  child: Container(
                                    child: Column(
                                      children: [
                                        Container(
                                          alignment: Alignment.topLeft,
                                          margin: EdgeInsets.only(
                                              top: width! * 0.01),
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                getTranslated(context, AppString.profile_doctor_name).toString(),
                                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                              ),
                                              const SizedBox(height: 8),
                                              TextFormField(
                                                controller: _pName,
                                                keyboardType: TextInputType.name,
                                                inputFormatters: [
                                                  FilteringTextInputFormatter.allow(RegExp("[a-zA-Z ]")),
                                                ],
                                                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                                decoration: AyurezeTheme.textFieldDecoration(
                                                  hintText: getTranslated(context, AppString.profile_enter_name_hint).toString(),
                                                ),
                                                validator: (String? value) {
                                                  if (value!.isEmpty) {
                                                    return getTranslated(context, AppString.please_enter_profile_valid_name).toString();
                                                  } else if (value.trim().length < 1) {
                                                    return getTranslated(context, AppString.please_enter_valid_name).toString();
                                                  }
                                                  return null;
                                                },
                                              ),
                                            ],
                                          ),
                                        ),
                                        const SizedBox(height: 16),
                                        Container(
                                          alignment: Alignment.topLeft,
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                getTranslated(context, AppString.profile_date_of_birth).toString(),
                                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                              ),
                                              const SizedBox(height: 8),
                                              TextFormField(
                                                controller: _pDob,
                                                readOnly: true,
                                                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                                decoration: AyurezeTheme.textFieldDecoration(
                                                  hintText: getTranslated(context, AppString.profile_date_of_birth_hint).toString(),
                                                ).copyWith(suffixIcon: Icon(Icons.calendar_today_rounded, size: 20, color: AyurezeTheme.forestDeep)),
                                                validator: (String? value) {
                                                  if (value!.isEmpty) {
                                                    return getTranslated(context, AppString.please_enter_birth_date).toString();
                                                  }
                                                  return null;
                                                },
                                                onTap: () => _selectDate(context),
                                              ),
                                            ],
                                          ),
                                        ),
                                        const SizedBox(height: 24),
                                        Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              getTranslated(context, AppString.select_hospital).toString(),
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 12),
                                            Container(
                                              decoration: AyurezeTheme.panelDecoration(),
                                              child: ListView.separated(
                                                shrinkWrap: true,
                                                physics: const NeverScrollableScrollPhysics(),
                                                itemCount: hospitalReq.length,
                                                separatorBuilder: (context, index) => Divider(height: 1, color: AyurezeTheme.border),
                                                itemBuilder: (context, index) {
                                                  return CheckboxListTile(
                                                    activeColor: AyurezeTheme.forestDeep,
                                                    checkColor: Colors.white,
                                                    value: hospitalReq[index].isSelected,
                                                    title: Text(
                                                      hospitalReq[index].name!,
                                                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                                    ),
                                                    onChanged: (val) {
                                                      setState(() {
                                                        hospitalReq[index].isSelected = val!;
                                                      });
                                                    },
                                                  );
                                                },
                                              ),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 24),
                                        Container(
                                          alignment: Alignment.topLeft,
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                getTranslated(context, AppString.profile_gender).toString(),
                                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                              ),
                                              const SizedBox(height: 8),
                                              StatefulBuilder(
                                                builder: (context, myState) {
                                                  return DropdownButtonFormField<String>(
                                                    decoration: AyurezeTheme.textFieldDecoration(
                                                      hintText: getTranslated(context, AppString.profile_gender_hint).toString(),
                                                    ),
                                                    value: _genderSelect,
                                                    isExpanded: true,
                                                    icon: Icon(Icons.keyboard_arrow_down_rounded, color: AyurezeTheme.forestDeep),
                                                    items: gender.map((genders) {
                                                      return DropdownMenuItem<String>(
                                                        value: genders,
                                                        child: Text(genders, style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary)),
                                                      );
                                                    }).toList(),
                                                    onChanged: (newValue) {
                                                      myState(() {
                                                        _genderSelect = newValue;
                                                      });
                                                    },
                                                    validator: (value) {
                                                      if (_genderSelect == null) {
                                                        return getTranslated(context, AppString.please_enter_profile_valid_name).toString();
                                                      }
                                                      return null;
                                                    },
                                                  );
                                                },
                                              ),
                                            ],
                                          ),
                                          const SizedBox(height: 24),
                                          Container(
                                            alignment: Alignment.topLeft,
                                            child: Column(
                                              crossAxisAlignment: CrossAxisAlignment.start,
                                              children: [
                                                Text(
                                                  getTranslated(context, AppString.profile_description).toString(),
                                                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                                ),
                                                const SizedBox(height: 8),
                                                TextFormField(
                                                  controller: _pDesc,
                                                  keyboardType: TextInputType.multiline,
                                                  maxLines: 3,
                                                  inputFormatters: [
                                                    FilteringTextInputFormatter.allow(RegExp("[a-zA-Z &.,]")),
                                                  ],
                                                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                                  decoration: AyurezeTheme.textFieldDecoration(
                                                    hintText: getTranslated(context, AppString.profile_description_hint).toString(),
                                                  ),
                                                  validator: (String? value) {
                                                    if (value!.isEmpty) {
                                                      return getTranslated(context, AppString.please_enter_description).toString();
                                                    } else if (value.trim().length < 1) {
                                                      return getTranslated(context, AppString.please_enter_valid_description).toString();
                                                    }
                                                    return null;
                                                  },
                                                ),
                                              ],
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                            isActive: _currentStep >= 0,
                            state: _currentStep >= 0 ? StepState.complete : StepState.disabled,
                          ),
                          // Step 2 //
                          Step(
                            title: new Text(
                              getTranslated(context,
                                      AppString.profile_education_information)
                                  .toString(),
                              style: TextStyle(fontSize: 12),
                              textAlign: TextAlign.start,
                            ),
                            content: Form(
                              key: _step2,
                              child: SingleChildScrollView(
                                child: Container(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Container(
                                        alignment: Alignment.topLeft,
                                        margin:
                                            EdgeInsets.only(top: width! * 0.01),
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                              Text(
                                                getTranslated(context, AppString.profile_degree).toString(),
                                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                              ),
                                              const SizedBox(height: 8),
                                              TextFormField(
                                                controller: _pDegree,
                                                keyboardType: TextInputType.text,
                                                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                                decoration: AyurezeTheme.textFieldDecoration(
                                                  hintText: getTranslated(context, AppString.profile_degree_hint).toString(),
                                                ),
                                                validator: (String? value) {
                                                  if (value!.isEmpty) {
                                                    return getTranslated(context, AppString.please_enter_degree).toString();
                                                  } else if (value.trim().length < 1) {
                                                    return getTranslated(context, AppString.please_enter_valid_degree).toString();
                                                  }
                                                  return null;
                                                },
                                              ),
                                            ],
                                          ),
                                        ),
                                        const SizedBox(height: 16),
                                        Container(
                                          alignment: Alignment.topLeft,
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                getTranslated(context, AppString.profile_college).toString(),
                                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                              ),
                                              const SizedBox(height: 8),
                                              TextFormField(
                                                controller: _pCollege,
                                                keyboardType: TextInputType.text,
                                                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                                decoration: AyurezeTheme.textFieldDecoration(
                                                  hintText: getTranslated(context, AppString.profile_college_hint).toString(),
                                                ),
                                                validator: (String? value) {
                                                  if (value!.isEmpty) {
                                                    return getTranslated(context, AppString.please_enter_college).toString();
                                                  } else if (value.trim().length < 1) {
                                                    return getTranslated(context, AppString.please_enter_valid_college).toString();
                                                  }
                                                  return null;
                                                },
                                              ),
                                            ],
                                          ),
                                        ),
                                      Container(
                                        alignment: Alignment.topLeft,
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              getTranslated(context, AppString.profile_year_of_completion).toString(),
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            TextFormField(
                                              controller: _pCollegeYear,
                                              keyboardType: TextInputType.number,
                                              inputFormatters: [FilteringTextInputFormatter.allow(RegExp("[0-9]"))],
                                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                              decoration: AyurezeTheme.textFieldDecoration(
                                                hintText: getTranslated(context, AppString.profile_year_hint).toString(),
                                              ),
                                              validator: (String? value) {
                                                if (value!.isEmpty) {
                                                  return getTranslated(context, AppString.please_enter_year_of_completion).toString();
                                                }
                                                return null;
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                      GestureDetector(
                                        onTap: () {
                                          showDialog(
                                              context: context,
                                              builder: (context) {
                                                return AlertDialog(
                                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                                                  backgroundColor: AyurezeTheme.surface,
                                                  title: Text(
                                                    getTranslated(context, AppString.profile_education_information).toString(),
                                                    style: const TextStyle(fontWeight: FontWeight.w800),
                                                  ),
                                                  content: SizedBox(
                                                    height: height * 0.25,
                                                    width: width! * 0.9,
                                                    child: Column(
                                                      children: [
                                                        TextField(
                                                          controller: _degree,
                                                          decoration: AyurezeTheme.textFieldDecoration(
                                                            hintText: getTranslated(context, AppString.profile_degree).toString(),
                                                          ),
                                                        ),
                                                        const SizedBox(height: 12),
                                                        TextField(
                                                          controller: _college,
                                                          decoration: AyurezeTheme.textFieldDecoration(
                                                            hintText: getTranslated(context, AppString.profile_college).toString(),
                                                          ),
                                                        ),
                                                        const SizedBox(height: 12),
                                                        TextField(
                                                          controller: _completeYear,
                                                          keyboardType: TextInputType.number,
                                                          inputFormatters: [FilteringTextInputFormatter.allow(RegExp("[0-9]"))],
                                                          decoration: AyurezeTheme.textFieldDecoration(
                                                            hintText: getTranslated(context, AppString.profile_dialog_year_of_completion).toString(),
                                                          ),
                                                        ),
                                                      ],
                                                    ),
                                                  ),
                                                  actions: <Widget>[
                                                    TextButton(
                                                      child: Text("Cancel", style: TextStyle(color: AyurezeTheme.textSecondary)),
                                                      onPressed: () => Navigator.pop(context),
                                                    ),
                                                    ElevatedButton(
                                                      child: Text(getTranslated(context, AppString.profile_dialog_ok_button).toString()),
                                                      onPressed: () {
                                                        setState(() {
                                                          if (_degree.text.isNotEmpty && _college.text.isNotEmpty && _completeYear.text.isNotEmpty) {
                                                            _pDegree.text = _pDegree.text.isEmpty ? _degree.text : "${_pDegree.text},${_degree.text}";
                                                            _pCollege.text = _pCollege.text.isEmpty ? _college.text : "${_pCollege.text},${_college.text}";
                                                            _pCollegeYear.text = _pCollegeYear.text.isEmpty ? _completeYear.text : "${_pCollegeYear.text},${_completeYear.text}";

                                                            _degree.clear();
                                                            _college.clear();
                                                            _completeYear.clear();
                                                            Navigator.pop(context);
                                                          } else {
                                                            Fluttertoast.showToast(msg: getTranslated(context, AppString.please_fill_data).toString());
                                                          }
                                                        });
                                                      },
                                                    ),
                                                  ],
                                                );
                                              });
                                        },
                                        child: Container(
                                          margin: const EdgeInsets.only(top: 16),
                                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                                          decoration: AyurezeTheme.mutedPanelDecoration(),
                                          child: Row(
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                              Icon(Icons.add_rounded, color: AyurezeTheme.forestDeep, size: 20),
                                              const SizedBox(width: 8),
                                              Text(
                                                getTranslated(context, AppString.profile_add_more_button).toString(),
                                                style: TextStyle(fontWeight: FontWeight.w700, color: AyurezeTheme.forestDeep),
                                              )
                                            ],
                                          ),
                                        ),
                                      ),
                                      Container(
                                        alignment: Alignment.topLeft,
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              getTranslated(context, AppString.profile_dialog_certificate).toString(),
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            TextFormField(
                                              controller: _pCertificate,
                                              keyboardType: TextInputType.text,
                                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                              decoration: AyurezeTheme.textFieldDecoration(
                                                hintText: getTranslated(context, AppString.profile_dialog_certificate_hint).toString(),
                                              ),
                                              validator: (String? value) {
                                                if (value!.isEmpty) {
                                                  return getTranslated(context, AppString.dialog_please_enter_certificate).toString();
                                                } else if (value.trim().length < 1) {
                                                  return getTranslated(context, AppString.dialog_please_enter_valid_certificate).toString();
                                                }
                                                return null;
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                      const SizedBox(height: 16),
                                      Container(
                                        alignment: Alignment.topLeft,
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              getTranslated(context, AppString.profile_dialog_certificate_year).toString(),
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            TextFormField(
                                              controller: _pCertificateYear,
                                              keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                              inputFormatters: [FilteringTextInputFormatter.allow(RegExp("[0-9]"))],
                                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                              decoration: AyurezeTheme.textFieldDecoration(
                                                hintText: getTranslated(context, AppString.profile_dialog_certificate_year_hint).toString(),
                                              ),
                                              validator: (String? value) {
                                                if (value!.isEmpty) {
                                                  return getTranslated(context, AppString.dialog_please_enter_certificate_year).toString();
                                                }
                                                return null;
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                      GestureDetector(
                                        onTap: () {
                                          showDialog(
                                              context: context,
                                              builder: (context) {
                                                return AlertDialog(
                                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                                                  backgroundColor: AyurezeTheme.surface,
                                                  title: Text(
                                                    getTranslated(context, AppString.profile_dialog_certificate).toString(),
                                                    style: const TextStyle(fontWeight: FontWeight.w800),
                                                  ),
                                                  content: SizedBox(
                                                    height: height * 0.2,
                                                    width: width! * 0.9,
                                                    child: Column(
                                                      children: [
                                                        TextField(
                                                          controller: _certificate,
                                                          decoration: AyurezeTheme.textFieldDecoration(
                                                            hintText: getTranslated(context, AppString.profile_dialog_certificate).toString(),
                                                          ),
                                                        ),
                                                        const SizedBox(height: 12),
                                                        TextField(
                                                          controller: _year,
                                                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                                          inputFormatters: [FilteringTextInputFormatter.allow(RegExp("[0-9]"))],
                                                          decoration: AyurezeTheme.textFieldDecoration(
                                                            hintText: getTranslated(context, AppString.profile_dialog_year).toString(),
                                                          ),
                                                        ),
                                                      ],
                                                    ),
                                                  ),
                                                  actions: <Widget>[
                                                    TextButton(
                                                      child: Text("Cancel", style: TextStyle(color: AyurezeTheme.textSecondary)),
                                                      onPressed: () => Navigator.pop(context),
                                                    ),
                                                    ElevatedButton(
                                                      child: Text(getTranslated(context, AppString.profile_dialog_ok_button).toString()),
                                                      onPressed: () {
                                                        setState(() {
                                                          if (_certificate.text.isNotEmpty && _year.text.isNotEmpty) {
                                                            _pCertificate.text = _pCertificate.text.isEmpty ? _certificate.text : "${_pCertificate.text},${_certificate.text}";
                                                            _pCertificateYear.text = _pCertificateYear.text.isEmpty ? _year.text : "${_pCertificateYear.text},${_year.text}";

                                                            _certificate.clear();
                                                            _year.clear();
                                                            Navigator.pop(context);
                                                          } else {
                                                            Fluttertoast.showToast(msg: getTranslated(context, AppString.please_fill_data).toString());
                                                          }
                                                        });
                                                      },
                                                    ),
                                                  ],
                                                );
                                              });
                                        },
                                        child: Container(
                                          margin: const EdgeInsets.only(top: 16),
                                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                                          decoration: AyurezeTheme.mutedPanelDecoration(),
                                          child: Row(
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                              Icon(Icons.add_rounded, color: AyurezeTheme.forestDeep, size: 20),
                                              const SizedBox(width: 8),
                                              Text(
                                                getTranslated(context, AppString.profile_add_more_button).toString(),
                                                style: TextStyle(fontWeight: FontWeight.w700, color: AyurezeTheme.forestDeep),
                                              )
                                            ],
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                            isActive: _currentStep >= 0,
                            state: _currentStep >= 1
                                ? StepState.complete
                                : StepState.disabled,
                          ),
                          // Step 3 //
                          Step(
                            title: new Text(
                              getTranslated(context,
                                      AppString.profile_other_information)
                                  .toString(),
                              style: TextStyle(fontSize: 12),
                            ),
                            content: Form(
                              key: _formkey,
                              child: SingleChildScrollView(
                                child: Container(
                                  child: Column(
                                    children: [
                                      Container(
                                        alignment: Alignment.topLeft,
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              getTranslated(context, AppString.profile_experience).toString(),
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            TextFormField(
                                              controller: _pExperience,
                                              keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                              inputFormatters: [FilteringTextInputFormatter.allow(RegExp("[0-9]"))],
                                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                              decoration: AyurezeTheme.textFieldDecoration(
                                                hintText: getTranslated(context, AppString.profile_experience_hint).toString(),
                                              ),
                                              validator: (String? value) {
                                                if (value!.isEmpty) {
                                                  return getTranslated(context, AppString.please_enter_experience).toString();
                                                }
                                                return null;
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                      Container(
                                        alignment: Alignment.topLeft,
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              "Video call fee",
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            TextFormField(
                                              controller: _vAppointmentFees,
                                              keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                              inputFormatters: [FilteringTextInputFormatter.allow(RegExp("[0-9]"))],
                                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                              decoration: AyurezeTheme.textFieldDecoration(
                                                hintText: getTranslated(context, AppString.profile_appointment_fees_hint).toString(),
                                              ),
                                              validator: (String? value) {
                                                if (value!.isEmpty) {
                                                  return getTranslated(context, AppString.please_enter_appointment_fees).toString();
                                                }
                                                return null;
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                      const SizedBox(height: 16),
                                      Container(
                                        alignment: Alignment.topLeft,
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              "Audio call fee",
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            TextFormField(
                                              controller: _aAppointmentFees,
                                              keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                              inputFormatters: [FilteringTextInputFormatter.allow(RegExp("[0-9]"))],
                                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                              decoration: AyurezeTheme.textFieldDecoration(
                                                hintText: getTranslated(context, AppString.profile_appointment_fees_hint).toString(),
                                              ),
                                              validator: (String? value) {
                                                if (value!.isEmpty) {
                                                  return getTranslated(context, AppString.please_enter_appointment_fees).toString();
                                                }
                                                return null;
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                      const SizedBox(height: 16),
                                      Container(
                                        alignment: Alignment.topLeft,
                                        margin:
                                            EdgeInsets.only(top: width! * 0.02),
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Container(
                                              alignment: Alignment.topLeft,
                                              child: Column(
                                                crossAxisAlignment: CrossAxisAlignment.start,
                                                children: [
                                            Text(
                                              getTranslated(context, AppString.profile_time_slot).toString(),
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            TextFormField(
                                              controller: _pTimeSlot,
                                              keyboardType: TextInputType.number,
                                              inputFormatters: [FilteringTextInputFormatter.allow(RegExp("[0-9]"))],
                                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                              decoration: AyurezeTheme.textFieldDecoration(
                                                hintText: getTranslated(context, AppString.profile_time_slot_hint).toString(),
                                              ),
                                              validator: (String? value) {
                                                if (value!.isEmpty) {
                                                  return getTranslated(context, AppString.please_enter_time_slot).toString();
                                                }
                                                return null;
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                      const SizedBox(height: 16),
                                      Container(
                                        alignment: Alignment.topLeft,
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              "Revenue model",
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            DropdownButtonFormField<String>(
                                              value: ["Commission", "Subscription"].contains(_pBasedOn.text) ? _pBasedOn.text : null,
                                              decoration: AyurezeTheme.textFieldDecoration(
                                                hintText: getTranslated(context, AppString.revenue_model_hint).toString(),
                                              ),
                                              icon: Icon(Icons.keyboard_arrow_down_rounded, color: AyurezeTheme.forestDeep),
                                              items: ["Commission", "Subscription"].map((String value) {
                                                return DropdownMenuItem<String>(
                                                  value: value,
                                                  child: Text(value, style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary)),
                                                );
                                              }).toList(),
                                              onChanged: (newValue) {
                                                setState(() {
                                                  _pBasedOn.text = newValue!;
                                                });
                                              },
                                              validator: (value) {
                                                if (_pBasedOn.text.isEmpty) {
                                                  return getTranslated(context, AppString.please_enter_based_on).toString();
                                                }
                                                return null;
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                      const SizedBox(height: 16),
                                      Container(
                                        alignment: Alignment.topLeft,
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              getTranslated(context, AppString.profile_start_time).toString(),
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            TextFormField(
                                              controller: _pStartTime,
                                              readOnly: true,
                                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                              decoration: AyurezeTheme.textFieldDecoration(
                                                hintText: getTranslated(context, AppString.profile_start_time_hint).toString(),
                                              ).copyWith(suffixIcon: Icon(Icons.access_time_rounded, size: 20, color: AyurezeTheme.forestDeep)),
                                              onTap: () async {
                                                final TimeOfDay? result = await showTimePicker(
                                                    context: context,
                                                    initialTime: TimeOfDay.now(),
                                                    builder: (context, child) {
                                                      return Theme(
                                                        data: Theme.of(context).copyWith(
                                                          colorScheme: const ColorScheme.light(
                                                            primary: AyurezeTheme.forestDeep,
                                                            onPrimary: Colors.white,
                                                            onSurface: AyurezeTheme.forestDeep,
                                                          ),
                                                        ),
                                                        child: MediaQuery(
                                                            data: MediaQuery.of(context).copyWith(alwaysUse24HourFormat: false),
                                                            child: child!),
                                                      );
                                                    });
                                                if (result != null) {
                                                  setState(() {
                                                    String data = result.format(context).toLowerCase();
                                                    var parts = data.split(":");
                                                    String startPart = parts[0].trim();
                                                    int checkData = int.parse(startPart);
                                                    if (checkData > 9) {
                                                      _pStartTime.text = data;
                                                    } else {
                                                      _pStartTime.text = "0$data";
                                                    }
                                                  });
                                                }
                                              },
                                              validator: (String? value) {
                                                if (value!.isEmpty) {
                                                  return getTranslated(context, AppString.please_enter_start_time).toString();
                                                }
                                                return null;
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                      Container(
                                        alignment: Alignment.topLeft,
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              getTranslated(context, AppString.profile_end_time).toString(),
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            TextFormField(
                                              controller: _pEndTime,
                                              readOnly: true,
                                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary),
                                              decoration: AyurezeTheme.textFieldDecoration(
                                                hintText: getTranslated(context, AppString.profile_end_time_hint).toString(),
                                              ).copyWith(suffixIcon: Icon(Icons.access_time_rounded, size: 20, color: AyurezeTheme.forestDeep)),
                                              onTap: () async {
                                                final TimeOfDay? result = await showTimePicker(
                                                    context: context,
                                                    initialTime: TimeOfDay.now(),
                                                    builder: (context, child) {
                                                      return Theme(
                                                        data: Theme.of(context).copyWith(
                                                          colorScheme: const ColorScheme.light(
                                                            primary: AyurezeTheme.forestDeep,
                                                            onPrimary: Colors.white,
                                                            onSurface: AyurezeTheme.forestDeep,
                                                          ),
                                                        ),
                                                        child: MediaQuery(
                                                            data: MediaQuery.of(context).copyWith(alwaysUse24HourFormat: false),
                                                            child: child!),
                                                      );
                                                    });
                                                if (result != null) {
                                                  setState(() {
                                                    String data = result.format(context).toLowerCase();
                                                    var parts = data.split(":");
                                                    String startPart = parts[0].trim();
                                                    int checkData = int.parse(startPart);
                                                    if (checkData > 9) {
                                                      _pEndTime.text = data;
                                                    } else {
                                                      _pEndTime.text = "0$data";
                                                    }
                                                  });
                                                }
                                              },
                                              validator: (String? value) {
                                                if (value!.isEmpty) {
                                                  return getTranslated(context, AppString.please_enter_end_time).toString();
                                                }
                                                return null;
                                              },
                                            ),
                                          ],
                                        ),
                                      ),
                                      const SizedBox(height: 16),
                                      Container(
                                        alignment: Alignment.topLeft,
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              getTranslated(context, AppString.profile_popular).toString(),
                                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                            ),
                                            const SizedBox(height: 8),
                                            DropdownButtonFormField<String>(
                                              hint: Text(getTranslated(context, AppString.profile_popular).toString()),
                                              value: _selectedPopular == '0'
                                                  ? getTranslated(context, AppString.popular_no).toString()
                                                  : getTranslated(context, AppString.popular_yes).toString(),
                                              decoration: AyurezeTheme.textFieldDecoration(),
                                              icon: Icon(Icons.keyboard_arrow_down_rounded, color: AyurezeTheme.forestDeep),
                                              items: popular.map((pop) {
                                                return DropdownMenuItem<String>(
                                                  value: pop,
                                                  child: Text(pop, style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AyurezeTheme.textPrimary)),
                                                );
                                              }).toList(),
                                              onChanged: (newValue) {
                                                setState(() {
                                                  _selectedPopular = newValue!;
                                                });
                                              },
                                            ),
                                          ],
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
                      isActive: _currentStep >= 2,
                      state: _currentStep >= 2
                          ? StepState.complete
                          : StepState.disabled,
                    ),
                        ],
                        controlsBuilder:
                            (BuildContext context, ControlsDetails controls) {
                          return Row(
                            mainAxisSize: MainAxisSize.max,
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: <Widget>[
                              SizedBox(),
                              SizedBox(),
                            ],
                          );
                        },
                      ),
                    ),
                  ],
                ),
                ),
              );
            } else {
              return Center(
                child: CircularProgressIndicator(
                  color: AyurezeTheme.forestDeep,
                ),
              );
            }
          }),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: AyurezeTheme.surface,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, -5),
            ),
          ],
        ),
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: AyurezeTheme.forestDeep,
            foregroundColor: Colors.white,
            minimumSize: const Size(double.infinity, 56),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            elevation: 0,
          ),
          child: Text(
            _currentStep == 2 
                ? getTranslated(context, AppString.profile_submit_button).toString()
                : getTranslated(context, AppString.profile_continue_button).toString(),
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
          ),
          onPressed: () {
            if (_currentStep == 0 && _step1.currentState!.validate()) {
              selectedHospitals.clear();
              for (int i = 0; i < hospitalReq.length; i++) {
                if (hospitalReq[i].isSelected == true) {
                  selectedHospitals.add(hospitalReq[i].id.toString());
                }
              }

              if (selectedHospitals.isNotEmpty) {
                continued();
              } else {
                Fluttertoast.showToast(msg: getTranslated(context, AppString.please_select_hospital).toString());
              }
            } else if (_currentStep == 1 && _step2.currentState!.validate()) {
              List<String> degree = _pDegree.text.toString().split(",");
              List<String> college = _pCollege.text.toString().split(',');
              List<String> year = _pCollegeYear.text.toString().split(',');
              List<String> certificate = _pCertificate.text.toString().split(',');
              List<String> certificateYear = _pCertificateYear.text.toString().split(',');

              educationList.clear();
              certificateList.clear();

              for (int i = 0; i < degree.length; i++) {
                if (degree[i].trim().isNotEmpty) {
                  EducationModel education = EducationModel();
                  education.degree = degree[i].trim();
                  education.college = college[i].trim();
                  education.year = year[i].trim();
                  educationList.add(education);
                }
              }

              for (int i = 0; i < certificate.length; i++) {
                if (certificate[i].trim().isNotEmpty) {
                  EducationCertificate certificateData = EducationCertificate();
                  certificateData.certificate = certificate[i].trim();
                  certificateData.certificateYear = certificateYear[i].trim();
                  certificateList.add(certificateData);
                }
              }

              continued();
            } else if (_currentStep == 2 && _formkey.currentState!.validate()) {
              updateProfile();
            }
          },
        ),
      ),
    );
  }

  Future<BaseModel<UpdateProfile>> updateProfile() async {
    var eEducationList = JsonEncoder().convert(educationList);
    var cCertificateList = JsonEncoder().convert(certificateList);

    //pass date formate
    if (_selectedDate != null) {
      temp = '$_selectedDate';
    } else {
      temp = '$showFormat';
    }

    String hospitalIds = '';
    List<String> data = [];
    for (int i = 0; i < hospitalReq.length; i++) {
      if (hospitalReq[i].isSelected == true) {
        data.add(hospitalReq[i].id.toString());
      }
    }

    for (int j = 0; j < data.length; j++) {
      if (data.length <= 1) {
        hospitalIds = data[j];
      } else {
        hospitalIds += data[j] + ',';
      }
    }

    if (data.length > 1) {
      String result = hospitalIds.substring(0, hospitalIds.length - 1);
      hospitalIds = result + " ";
    }

    newDateApiPass = DateFormat('yyyy-MM-dd').format(DateFormat('dd-MM-yyyy').parse(_pDob.text));
    Map<String, dynamic> body = {
      "name": _pName.text,
      "treatment_id": 1, // Default value as it is removed from UI
      "category_id": 1,
      "expertise_id": 1,
      "hospital_id": hospitalIds,
      "dob": newDateApiPass,
      "gender": _genderSelect,
      "education": eEducationList,
      "certificate": cCertificateList,
      "experience": _pExperience.text,
      "appointment_fees": _aAppointmentFees.text,
      "video_appointment_fees": _vAppointmentFees.text,
      "start_time": _pStartTime.text.toLowerCase(),
      "end_time": _pEndTime.text.toLowerCase(),
      "timeslot": _pTimeSlot.text,
      "desc": _pDesc.text,
      "based_on": _pBasedOn.text,
      "is_popular": _selectedPopular ==
              getTranslated(context, AppString.popular_yes).toString()
          ? 1
          : 0
    };
    UpdateProfile response;
    try {
      response = await RestClient(await RetroApi().dioData(context))
          .updateProfile(body);
      Navigator.pushNamed(context, "loginHome");
      SharedPreferenceHelper.setInt(Preferences.is_filled, 1);
      Fluttertoast.showToast(
        msg: response.msg!,
        toastLength: Toast.LENGTH_SHORT,
        gravity: ToastGravity.BOTTOM,
      );
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<DoctorProfile>> doctorProfile() async {
    DoctorProfile response;

    try {
      response =
          await RestClient(await RetroApi().dioData(context)).doctorProfile();

      var convertDegree;
      var eduCertificate;
      if (response.data!.education != null) {
        convertDegree = json.decode(response.data!.education!);
      }

      if (response.data!.certificate != null) {
        eduCertificate = json.decode(response.data!.certificate!);
      }
      _pName.text = response.data!.name!;
      showFormat = response.data!.dob;

      _genderSelect = response.data!.gender!;

      if (convertDegree != null) {
        for (int i = 0; i < convertDegree.length; i++) {
          if (_pDegree.text.length == 0) {
            _pDegree.text = _pDegree.text + convertDegree[i]['degree'];
          } else {
            _pDegree.text = _pDegree.text + ',' + convertDegree[i]['degree'];
          }
          if (_pCollege.text.length == 0) {
            _pCollege.text = _pCollege.text + convertDegree[i]['college'];
          } else {
            _pCollege.text = _pCollege.text + ',' + convertDegree[i]['college'];
          }
          if (_pCollegeYear.text.length == 0) {
            _pCollegeYear.text = _pCollegeYear.text + convertDegree[i]['year'];
          } else {
            _pCollegeYear.text =
                _pCollegeYear.text + ',' + convertDegree[i]['year'];
          }
        }
      }

      if (eduCertificate != null) {
        for (int i = 0; i < eduCertificate.length; i++) {
          if (_pCertificate.text.length == 0) {
            _pCertificate.text =
                _pCertificate.text + eduCertificate[i]['certificate'];
          } else {
            _pCertificate.text =
                _pCertificate.text + ',' + eduCertificate[i]['certificate'];
          }

          if (_pCertificateYear.text.length == 0) {
            _pCertificateYear.text =
                _pCertificateYear.text + eduCertificate[i]['certificate_year'];
          } else {
            _pCertificateYear.text = _pCertificateYear.text +
                ',' +
                eduCertificate[i]['certificate_year'];
          }
        }
      }

      if (response.data!.experience != null) {
        _pExperience.text = response.data!.experience!;
      }

      if (response.data!.appointmentFees != null) {
        _aAppointmentFees.text = response.data!.appointmentFees!;
      }
      if (response.data!.videoAppointmentFees != null) {
        _vAppointmentFees.text = response.data!.videoAppointmentFees!;
      }

      if (response.data!.desc != null) {
        _pDesc.text = response.data!.desc!;
      }

      if (response.data!.dob != null && response.data!.dob!.isNotEmpty) {
        String rawDob = response.data!.dob!;
        try {
          // If yyyy-MM-dd
          if (rawDob.contains("-") && rawDob.indexOf("-") == 4) {
             DateTime parsedDate = DateFormat('yyyy-MM-dd').parse(rawDob);
             _pDob.text = DateFormat('dd-MM-yyyy').format(parsedDate);
             _selectedDate = parsedDate;
          } else {
             _pDob.text = rawDob;
             try {
                _selectedDate = DateFormat('dd-MM-yyyy').parse(rawDob);
             } catch (e) {}
          }
        } catch (e) {
          _pDob.text = rawDob;
        }
      }

      _pTimeSlot.text = response.data!.timeslot!;
      _pStartTime.text = response.data!.startTime!;
      _pEndTime.text = response.data!.endTime!;
      _pBasedOn.text = response.data!.basedOn!;

      _selectedPopular = response.data!.isPopular.toString();

      if (response.data!.hospitalId != null) {
        List<String> list = response.data!.hospitalId!.split(",");
        for (int i = 0; i < hospitalReq.length; i++) {
          for (int j = 0; j < list.length; j++) {
            if (int.parse(list[j]) == hospitalReq[i].id) {
              setState(() {
                hospitalReq[i].isSelected = true;
              });
            }
          }
        }
      }

      // Removed treatment settings as it is removed from UI

      setState(() {});
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<Hospitals>> hospital() async {
    Hospitals response;
    try {
      hospitalReq.clear();
      response =
          await RestClient(await RetroApi().dioData(context)).hospitalRequest();
      setState(() {
        for (int i = 0; i < response.data!.length; i++) {
          hospitalReq.add(response.data![i]);
        }
        doctorProfile();
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<ImageUpload>> uploadImage() async {
    Map<String, dynamic> body = {
      "image": image,
    };
    ImageUpload response;
    try {
      response =
          await RestClient(await RetroApi().dioData(context)).uploadImage(body);
      setState(() {
        msg = response.data;
        SharedPreferenceHelper.setString(Preferences.image, response.data!);
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  void proImageFromGallery() async {
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    setState(() {
      if (pickedFile != null) {
        SharedPreferenceHelper.setString(Preferences.image, pickedFile.path);
        proImage = File(SharedPreferenceHelper.getString(Preferences.image));
        List<int> imageBytes = proImage!.readAsBytesSync();
        image = base64Encode(imageBytes);
        uploadImage();
      } else {
        // print('No image selected.');
      }
    });
  }

  void proImageFromCamera() async {
    final pickedFile = await picker.pickImage(source: ImageSource.camera);
    setState(() {
      if (pickedFile != null) {
        SharedPreferenceHelper.setString(Preferences.image, pickedFile.path);
        proImage = File(SharedPreferenceHelper.getString(Preferences.image));
        List<int> imageBytes = proImage!.readAsBytesSync();
        image = base64Encode(imageBytes);
        uploadImage();
      } else {
        // print('No image selected.');
      }
    });
  }

  void chooseProfileImage() {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext bc) {
        return SafeArea(
          child: Container(
            child: new Wrap(
              children: <Widget>[
                new ListTile(
                    leading: new Icon(AppIcons.photo),
                    title: new Text(
                      getTranslated(context, AppString.choose_image_gallery)
                          .toString(),
                    ),
                    onTap: () {
                      proImageFromGallery();
                      Navigator.of(context).pop();
                    }),
                new ListTile(
                  leading: new Icon(AppIcons.camera),
                  title: new Text(
                    getTranslated(context, AppString.choose_image_camera)
                        .toString(),
                  ),
                  onTap: () {
                    proImageFromCamera();
                    Navigator.of(context).pop();
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<BaseModel> treatment() async {
    Treatment response;
    try {
      response = await RestClient(await RetroApi().dioData(context))
          .treatmentRequest();
      setState(() {
        for (int i = 0; i < response.data!.length; i++) {
          treatmentReq.add(response.data![i]);
        }
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<Categories>> category(
      id, categoryId, int? expertiseId) async {
    Categories response;
    try {
      response = await RestClient(await RetroApi().dioData(context))
          .categoryRequest(id);
      setState(() {
        for (int i = 0; i < response.categoriesData!.length; i++) {
          categoryReq.add(response.categoriesData![i]);
        }

        if (categoryReq.length != 0) {
          for (int i = 0; i < categoryReq.length; i++) {
            if (categoryId == categoryReq[i].id) {
              _valueCategories = categoryReq[i];
              expertise(_valueCategories!.id, expertiseId);
            }
          }
        }
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<Expertise>> expertise(id, expertiseId) async {
    Expertise response;
    try {
      response = await RestClient(await RetroApi().dioData(context))
          .expertiseRequest(id);
      setState(() {
        for (int i = 0; i < response.expertiseData!.length; i++) {
          expertReq.add(response.expertiseData![i]);
        }
        if (expertReq.length != 0) {
          for (int i = 0; i < expertReq.length; i++) {
            if (expertiseId == expertReq[i].id) {
              _valueExpertise = expertReq[i];
            }
          }
        }
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
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
            primaryColor: purple,
            colorScheme: ColorScheme.light(
              primary: purple,
              onPrimary: Colors.white,
              surface: Colors.white,
              onSurface: purple,
            ),
            dialogBackgroundColor: Colors.white,
            textButtonTheme: TextButtonThemeData(
              style: TextButton.styleFrom(foregroundColor: purple),
            ),
          ),
          child: child!,
        );
      },
    );
    if (newSelectedDate != null) {
      _selectedDate = newSelectedDate;
      _pDob
        ..text = DateFormat('dd-MM-yyyy').format(_selectedDate!)
        ..selection = TextSelection.fromPosition(
          TextPosition(
              offset: _pDob.text.length, affinity: TextAffinity.upstream),
        );
    }
  }

  tapped(int step) {
    setState(() => _currentStep = step);
  }

  continued() {
    if (_currentStep < 2) {
      setState(() => _currentStep += 1);
    }
  }

  cancel() {
    if (_currentStep > 0) {
      setState(() => _currentStep -= 1);
    }
  }
}

class AlwaysDisabledFocusNode extends FocusNode {
  @override
  bool get hasFocus => false;
}

//Pass Date Like this format  in api
class DateUtilForPass {
  static const DATE_FORMAT = 'yyyy-MM-dd';

  String formattedDate(DateTime dateTime) {
    return DateFormat(DATE_FORMAT).format(dateTime);
  }
}

//Show Date like this format in User
class DateUtil {
  static const DATE_FORMAT = 'dd-MM-yyyy';

  String formattedDate(DateTime dateTime) {
    return DateFormat(DATE_FORMAT).format(dateTime);
  }
}

