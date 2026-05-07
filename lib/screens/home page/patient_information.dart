import 'dart:collection';
import 'dart:convert';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:doctro/chat/providers/home_provider.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/AllMedicines.dart';
import 'package:doctro/model/DoctorStatusChange.dart';
import 'package:doctro/model/appointment_details.dart';
import 'package:doctro/pdf_creation/report_pdf.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/svg.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:full_screen_image_null_safe/full_screen_image_null_safe.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../chat/constants/firestore_constants.dart';
import '../../chat/models/user_chat.dart';
import '../../chat/pages/chat_page.dart';
import '../videoCall/video_Call.dart';
import 'package:doctro/screens/astra/prescription_screen.dart';
import 'package:doctro/widgets/astra_fill_display.dart';
import 'package:doctro/services/astra_api_service.dart';

class PatientDetailsScreen extends StatefulWidget {
  final int? id;

  PatientDetailsScreen({this.id});

  @override
  _PatientDetailsScreenState createState() => _PatientDetailsScreenState();
}

//Pass Medicine list in pdf
List medicineData = [];
List<Map<String, dynamic>> listOfMedicine = [];

//Add Medicine List
List<String> medicineReq = [];

class _PatientDetailsScreenState extends State<PatientDetailsScreen>
    with TickerProviderStateMixin {
  //Set Loader
  Future? appointmentDetail;
  
  // Astra Fill Data (Health intake from patient's app)
  final AstraApiService _astraService = AstraApiService();
  Map<String, dynamic>? _astraFillData;
  bool _isLoadingAstraFill = false;

  //Pdf Pass Data
  String? valueDays;
  bool? alertValueFirst = false;
  bool? alertValueSecond = false;
  bool? alertValueThird = false;

  //alert dialog validation
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  //set high/width using mediaQuery
  double? width;
  late double height;

  //Set List for Report Image
  List<String> reportImages = [];

  //set hide show approve and cancel button
  bool hideButton = true;

  //checkbox
  List<Tab> tabList = [];
  TabController? _tabController;

  //Add Medicine Data dialog
  TextEditingController _days = TextEditingController();
  String? selectedMedicineValue;

  //Show Signal Appointment Details
  int? id;
  int? userId;
  int? age;
  double? amount;
  String? phoneNo = "";
  String? name = "";
  String? appointmentId = "";
  String? patientAddress = "";
  String date = "";
  String? illness = "";
  String? note = "";
  String? drugEffect = "";
  String? time = "";
  String? fullImage = "";
  String? appointment = "";
  String? appointmentType = "";
  String? appointmentStatus = "";
  String? pdf = "";
  late HomeProvider homeProvider;
  int isInsured = 0;
  String policyInsurerName = "";
  String policyNumber = "";

  Widget _buildQuickActionButton(IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.15),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(icon, color: Colors.white, size: 22),
      ),
    );
  }

  Widget _buildCompactInfo(String label, String? value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label.toUpperCase(),
          style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 0.5),
        ),
        const SizedBox(height: 4),
        Text(
          value ?? "N/A",
          style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w700),
        ),
      ],
    );
  }


  void initState() {
    super.initState();
    homeProvider = Provider.of(context, listen: false);
    id = widget.id;
    Future.delayed(Duration.zero, () {
      appointmentDetail = appointmentDetails();
      _loadAstraFillData(); // Load patient's health intake from Astra

      tabList.add(new Tab(
        text: getTranslated(context, AppString.patient_information).toString(),
      ));
      tabList.add(new Tab(
        text: getTranslated(context, AppString.patient_illness).toString(),
      ));
      tabList.add(new Tab(
        text: getTranslated(context, AppString.doctor_prescription).toString(),
      ));
      _tabController = new TabController(vsync: this, length: tabList.length);

      listOfMedicine.clear();

      // allMedicinesRequest();
    });
  }

  /// Load Astra Fill data (health intake submitted by patient)
  Future<void> _loadAstraFillData({String? patientId, String? searchPhone}) async {
    final targetId = patientId ?? userId?.toString();
    final targetPhone = searchPhone ?? phoneNo;
    
    if (targetId == null && targetPhone == null) return;
    
    setState(() => _isLoadingAstraFill = true);
    try {
      Map<String, dynamic> data = {};
      
      // 1. Try loading by ID if available
      if (targetId != null) {
        data = await _astraService.getLatestAstraFill(targetId);
      }
      
      // 2. Fallback: If no data or loading by ID failed, try searching by phone in Astra
      if ((data == null || data.isEmpty) && targetPhone != null && targetPhone.isNotEmpty) {
        // Clean phone number (remove +, spaces, etc. for search)
        String cleanPhone = targetPhone.replaceAll(RegExp(r'\D'), '');
        final searchResults = await _astraService.searchPatients(cleanPhone);
        
        if (searchResults.isNotEmpty) {
          // Found matching patient in Astra! Use their Astra ID
          final astraPatient = searchResults[0];
          final astraId = astraPatient['id']?.toString() ?? astraPatient['uid']?.toString();
          if (astraId != null) {
            data = await _astraService.getLatestAstraFill(astraId);
          }
        }
      }

      if (mounted) {
        setState(() {
          _astraFillData = data;
          _isLoadingAstraFill = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoadingAstraFill = false);
      }
    }
  }

  Map<String, String> body = {};

  @override
  void dispose() {
    _tabController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    homeProvider = Provider.of(context, listen: false);
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
        actions: [
          IconButton(
            icon: Icon(Icons.more_vert_rounded, color: AyurezeTheme.textPrimary),
            onPressed: () {},
          ),
        ],
      ),
      body: FutureBuilder(
        future: appointmentDetail,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: AyurezeTheme.heroDecoration(),
                    child: Column(
                      children: [
                        Row(
                          children: [
                            Container(
                              width: 80,
                              height: 80,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                border: Border.all(color: Colors.white.withOpacity(0.3), width: 3),
                                image: DecorationImage(
                                  image: (fullImage != null && fullImage!.isNotEmpty)
                                      ? NetworkImage(fullImage!)
                                      : const AssetImage("assets/images/no_image.jpg") as ImageProvider,
                                  fit: BoxFit.cover,
                                ),
                              ),
                            ),
                            const SizedBox(width: 20),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    name ?? "Patient",
                                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: Colors.white),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    "ID: $appointmentId",
                                    style: TextStyle(fontSize: 14, color: Colors.white.withOpacity(0.8), fontWeight: FontWeight.w600),
                                  ),
                                  const SizedBox(height: 12),
                                  Row(
                                    children: [
                                      _buildQuickActionButton(Icons.call_rounded, () => launchUrl(Uri.parse("tel:$phoneNo"))),
                                      const SizedBox(width: 12),
                                      _buildQuickActionButton(Icons.chat_bubble_rounded, () {
                                        Navigator.push(context, MaterialPageRoute(builder: (context) => ChatPage(
                                          peerId: body['peerId'].toString(),
                                          peerAvatar: body['peerAvatar'].toString(),
                                          peerNickname: body['nickName'].toString(),
                                          token: body['token'].toString(),
                                          isNavigate: 'chatHome',
                                        )));
                                      }),
                                      if (appointmentType == 'video') ...[
                                        const SizedBox(width: 12),
                                        _buildQuickActionButton(Icons.videocam_rounded, () => _addVideoOverlay(context)),
                                      ],
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            _buildCompactInfo("Amount", "₹$amount"),
                            _buildCompactInfo("Date", date),
                            _buildCompactInfo("Slot", time ?? ""),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  Container(
                    decoration: AyurezeTheme.panelDecoration(),
                    padding: const EdgeInsets.all(10),
                    child: TabBar(
                      controller: _tabController,
                      indicator: BoxDecoration(color: AyurezeTheme.limeSoft, borderRadius: BorderRadius.circular(16)),
                      labelColor: AyurezeTheme.forestDeep,
                      unselectedLabelColor: AyurezeTheme.textSecondary,
                      labelStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                      tabs: tabList,
                    ),
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    height: height * 0.6,
                    child: TabBarView(
                      controller: _tabController,
                      children: [
                            ///tab 1
                            SingleChildScrollView(
                              scrollDirection: Axis.vertical,
                              physics: AlwaysScrollableScrollPhysics(),
                              child: Column(
                                children: [
                                  hideButton == false
                                      ? Column(
                                          children: [
                                            Row(
                                              mainAxisAlignment:
                                                  MainAxisAlignment
                                                      .spaceBetween,
                                              children: [
                                                Container(
                                                  margin: EdgeInsets.only(
                                                      left: width! * 0.06,
                                                      top: height * 0.01,
                                                      right: width! * 0.06),
                                                  alignment:
                                                      AlignmentDirectional
                                                          .topStart,
                                                  child: Text(
                                                    getTranslated(
                                                            context,
                                                            AppString
                                                                .information_appointment_status)
                                                        .toString(),
                                                    style: TextStyle(
                                                        fontSize: 18,
                                                        color: hintColor),
                                                  ),
                                                ),
                                                appointmentStatus == 'approve'
                                                    ? Container(
                                                        margin: EdgeInsets.only(
                                                            right:
                                                                width! * 0.06,
                                                            top: 5,
                                                            left:
                                                                width! * 0.06),
                                                        child: ElevatedButton(
                                                          onPressed: () {
                                                            setState(() {
                                                              statusChangeRequest(
                                                                  "complete");
                                                            });
                                                            setState(() {});
                                                          },
                                                          child: Text(
                                                            getTranslated(
                                                                    context,
                                                                    AppString
                                                                        .information_complete_status)
                                                                .toString(),
                                                          ),
                                                        ),
                                                      )
                                                    : Container(),
                                              ],
                                            ),
                                            Container(
                                              margin: EdgeInsets.only(
                                                  left: width! * 0.06,
                                                  top: height * 0.001,
                                                  right: width! * 0.06),
                                              alignment:
                                                  AlignmentDirectional.topStart,
                                              child: Text(
                                                '$appointmentStatus',
                                                style: TextStyle(
                                                    fontSize: 15,
                                                    color: passwordVisibility),
                                              ),
                                            ),
                                          ],
                                        )
                                      : StatefulBuilder(
                                          builder: (context, myState) {
                                          return Visibility(
                                            visible: hideButton,
                                            child: Row(
                                              mainAxisAlignment:
                                                  MainAxisAlignment.spaceAround,
                                              children: [
                                                Container(
                                                  child: ElevatedButton(
                                                    onPressed: () {
                                                      myState(() {
                                                        statusChangeRequest(
                                                            "approve");
                                                      });
                                                    },
                                                    child: Text(getTranslated(
                                                            context,
                                                            AppString
                                                                .information_approve_status)
                                                        .toString()),
                                                  ),
                                                ),
                                                Container(
                                                  child: ElevatedButton(
                                                    onPressed: () {
                                                      setState(() {
                                                        statusChangeRequest(
                                                            "cancel");
                                                      });
                                                    },
                                                    child: Text(getTranslated(
                                                            context,
                                                            AppString
                                                                .information_cancel_status)
                                                        .toString()),
                                                  ),
                                                ),
                                              ],
                                            ),
                                          );
                                        }),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.01,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      getTranslated(
                                              context,
                                              AppString
                                                  .information_patient_name)
                                          .toString(),
                                      style: TextStyle(
                                          fontSize: 18, color: hintColor),
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.001,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      '$name',
                                      style: TextStyle(
                                          fontSize: 15,
                                          color: passwordVisibility),
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.01,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      getTranslated(context,
                                              AppString.information_patient_age)
                                          .toString(),
                                      style: TextStyle(
                                          fontSize: 18, color: hintColor),
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.001,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      '$age',
                                      style: TextStyle(
                                          fontSize: 15,
                                          color: passwordVisibility),
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.01,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      getTranslated(
                                              context,
                                              AppString
                                                  .information_patient_phone_number)
                                          .toString(),
                                      style: TextStyle(
                                          fontSize: 18, color: hintColor),
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.001,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      '$phoneNo',
                                      style: TextStyle(
                                          fontSize: 15,
                                          color: passwordVisibility),
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.01,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      getTranslated(
                                              context,
                                              AppString
                                                  .information_patient_time)
                                          .toString(),
                                      style: TextStyle(
                                          fontSize: 18, color: hintColor),
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.001,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      '$time',
                                      style: TextStyle(
                                          fontSize: 15,
                                          color: passwordVisibility),
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.01,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      getTranslated(
                                              context,
                                              AppString
                                                  .information_patient_address)
                                          .toString(),
                                      style: TextStyle(
                                          fontSize: 18, color: hintColor),
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.001,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      '$patientAddress',
                                      style: TextStyle(
                                          fontSize: 15,
                                          color: passwordVisibility),
                                      overflow: TextOverflow.ellipsis,
                                      maxLines: 2,
                                    ),
                                  ),

                                  ///Patient Insured
                                  isInsured == 0
                                      ? Container(
                                          margin: EdgeInsets.only(
                                              left: width! * 0.06,
                                              top: height * 0.01,
                                              right: width! * 0.06),
                                          alignment:
                                              AlignmentDirectional.topStart,
                                          child: Text(
                                            getTranslated(context,
                                                    AppString.patientInsured)
                                                .toString(),
                                            style: TextStyle(
                                                fontSize: 18, color: hintColor),
                                          ),
                                        )
                                      : SizedBox(),
                                  isInsured == 0
                                      ? Container(
                                          margin: EdgeInsets.only(
                                              left: width! * 0.06,
                                              top: height * 0.001,
                                              right: width! * 0.06),
                                          alignment:
                                              AlignmentDirectional.topStart,
                                          child: Text(
                                            "${isInsured == 1 ? isInsured : getTranslated(context, AppString.patientIsNotInsured).toString()}",
                                            style: TextStyle(
                                                fontSize: 15,
                                                color: passwordVisibility),
                                            overflow: TextOverflow.ellipsis,
                                            maxLines: 2,
                                          ),
                                        )
                                      : SizedBox(),

                                  ///Policy Provider
                                  isInsured == 1
                                      ? Container(
                                          margin: EdgeInsets.only(
                                              left: width! * 0.06,
                                              top: height * 0.01,
                                              right: width! * 0.06),
                                          alignment:
                                              AlignmentDirectional.topStart,
                                          child: Text(
                                            getTranslated(context,
                                                    AppString.policy_provider)
                                                .toString(),
                                            style: TextStyle(
                                                fontSize: 18, color: hintColor),
                                          ),
                                        )
                                      : SizedBox(),
                                  isInsured == 1
                                      ? Container(
                                          margin: EdgeInsets.only(
                                              left: width! * 0.06,
                                              top: height * 0.001,
                                              right: width! * 0.06),
                                          alignment:
                                              AlignmentDirectional.topStart,
                                          child: Text(
                                            '$policyInsurerName',
                                            style: TextStyle(
                                                fontSize: 15,
                                                color: passwordVisibility),
                                            overflow: TextOverflow.ellipsis,
                                            maxLines: 2,
                                          ),
                                        )
                                      : SizedBox(),

                                  ///Policy Number
                                  isInsured == 1
                                      ? Container(
                                          margin: EdgeInsets.only(
                                              left: width! * 0.06,
                                              top: height * 0.01,
                                              right: width! * 0.06),
                                          alignment:
                                              AlignmentDirectional.topStart,
                                          child: Text(
                                            getTranslated(context,
                                                    AppString.policy_number)
                                                .toString(),
                                            style: TextStyle(
                                                fontSize: 18, color: hintColor),
                                          ),
                                        )
                                      : SizedBox(),
                                  isInsured == 1
                                      ? Container(
                                          margin: EdgeInsets.only(
                                              left: width! * 0.06,
                                              top: height * 0.001,
                                              right: width! * 0.06,
                                              bottom: 20),
                                          alignment:
                                              AlignmentDirectional.topStart,
                                          child: Text(
                                            '$policyNumber',
                                            style: TextStyle(
                                                fontSize: 15,
                                                color: passwordVisibility),
                                            overflow: TextOverflow.ellipsis,
                                            maxLines: 2,
                                          ),
                                        )
                                      : SizedBox(),
                                ],
                              ),
                            ),

                            ///tab 2
                            SingleChildScrollView(
                              scrollDirection: Axis.vertical,
                              physics: AlwaysScrollableScrollPhysics(),
                              child: Column(
                                children: [
                                  // NEW: Astra Fill Widget - Shows health intake from patient's app
                                  if (userId != null)
                                    AstraFillDisplayWidget(
                                      patientId: userId.toString(),
                                      preloadedData: _astraFillData,
                                    ),
                                  
                                  SizedBox(height: 8),
                                  
                                  // Original illness information section
                                  Center(
                                    child: Container(
                                      margin: EdgeInsets.only(
                                          left: width! * 0.06,
                                          top: height * 0.02,
                                          right: width! * 0.06),
                                      alignment: AlignmentDirectional.topStart,
                                      child: Text(
                                        getTranslated(
                                                context,
                                                AppString
                                                    .information_patient_illness_information)
                                            .toString(),
                                        style: TextStyle(
                                            fontSize: 18, color: hintColor),
                                      ),
                                    ),
                                  ),
                                  Container(
                                    margin: EdgeInsets.only(
                                        left: width! * 0.06,
                                        top: height * 0.01,
                                        right: width! * 0.06),
                                    alignment: AlignmentDirectional.topStart,
                                    child: Text(
                                      '* ' + '$illness',
                                      style: TextStyle(
                                          fontSize: 15,
                                          color: passwordVisibility),
                                    ),
                                  ),
                                  Center(
                                    child: Container(
                                      margin: EdgeInsets.only(
                                          left: width! * 0.06,
                                          top: height * 0.01,
                                          right: width! * 0.06),
                                      alignment: AlignmentDirectional.topStart,
                                      child: Text(
                                        getTranslated(
                                                context,
                                                AppString
                                                    .information_side_effect_drug)
                                            .toString(),
                                        style: TextStyle(
                                            fontSize: 18, color: hintColor),
                                      ),
                                    ),
                                  ),
                                  Center(
                                    child: Container(
                                      margin: EdgeInsets.only(
                                          left: width! * 0.06,
                                          top: height * 0.01,
                                          right: width! * 0.06),
                                      alignment: AlignmentDirectional.topStart,
                                      child: Text(
                                        ' *  $drugEffect',
                                        style: TextStyle(
                                            fontSize: 14.5,
                                            color: passwordVisibility),
                                      ),
                                    ),
                                  ),
                                  Center(
                                    child: Container(
                                      margin: EdgeInsets.only(
                                          left: width! * 0.06,
                                          top: height * 0.02,
                                          right: width! * 0.06),
                                      alignment: AlignmentDirectional.topStart,
                                      child: Text(
                                        getTranslated(context,
                                                AppString.information_note)
                                            .toString(),
                                        style: TextStyle(
                                            fontSize: 18, color: hintColor),
                                      ),
                                    ),
                                  ),
                                  Center(
                                    child: Container(
                                      margin: EdgeInsets.only(
                                          left: width! * 0.06,
                                          top: height * 0.01,
                                          right: width! * 0.06),
                                      alignment: AlignmentDirectional.topStart,
                                      child: Text(
                                        ' * $note',
                                        style: TextStyle(
                                            fontSize: 14.5,
                                            color: passwordVisibility),
                                      ),
                                    ),
                                  ),
                                  reportImages.length == 0
                                      ? Container()
                                      : Center(
                                          child: Container(
                                            margin: EdgeInsets.only(
                                                left: width! * 0.06,
                                                top: height * 0.02,
                                                right: width! * 0.06),
                                            alignment:
                                                AlignmentDirectional.topStart,
                                            child: Text(
                                              getTranslated(
                                                      context,
                                                      AppString
                                                          .information_report_image_title)
                                                  .toString(),
                                              style: TextStyle(
                                                  fontSize: 18,
                                                  color: hintColor),
                                            ),
                                          ),
                                        ),
                                  Container(
                                    margin: EdgeInsets.symmetric(
                                        horizontal: width! * 0.05),
                                    height: 120,
                                    width: width,
                                    child: GridView.builder(
                                      physics: NeverScrollableScrollPhysics(),
                                      shrinkWrap: true,
                                      scrollDirection: Axis.vertical,
                                      itemCount: reportImages.length,
                                      gridDelegate:
                                          SliverGridDelegateWithFixedCrossAxisCount(
                                        crossAxisCount: 3,
                                      ),
                                      itemBuilder: (context, index) {
                                        return Card(
                                          shape: RoundedRectangleBorder(
                                            borderRadius:
                                                BorderRadius.circular(10),
                                          ),
                                          child: Container(
                                              height: 100,
                                              width: 100,
                                              margin: EdgeInsets.all(5),
                                              child: FullScreenWidget(
                                                child: ClipRRect(
                                                  borderRadius:
                                                      BorderRadius.circular(10),
                                                  child: Image.network(
                                                    reportImages[index],
                                                    fit: BoxFit.fitWidth,
                                                  ),
                                                ),
                                              )),
                                        );
                                      },
                                    ),
                                  ),
                                ],
                              ),
                            ),

                            ///tab 3
                            SingleChildScrollView(
                                scrollDirection: Axis.vertical,
                                physics: AlwaysScrollableScrollPhysics(),
                                child: pdf == ''
                                    ? Column(
                                        mainAxisAlignment:
                                            MainAxisAlignment.spaceAround,
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Container(
                                            width: double.infinity,
                                            margin: EdgeInsets.symmetric(horizontal: width! * 0.06, vertical: 10),
                                            child: ElevatedButton.icon(
                                              icon: Icon(Icons.auto_awesome, color: colorWhite),
                                              label: Text("Smart Prescribe (Astra AI)", style: TextStyle(color: colorWhite, fontWeight: FontWeight.bold)),
                                              style: ElevatedButton.styleFrom(
                                                backgroundColor: Colors.purple,
                                                padding: EdgeInsets.symmetric(vertical: 12),
                                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                              ),
                                              onPressed: () {
                                                Navigator.push(
                                                  context, 
                                                  MaterialPageRoute(builder: (context) => PrescriptionScreen(
                                                    patientId: userId.toString(), 
                                                    patientName: name ?? "Patient",
                                                    patientPhone: phoneNo,
                                                    astraFillData: _astraFillData,
                                                  ))
                                                );
                                              },
                                            ),
                                          ),
                                          Container(
                                            margin: EdgeInsets.only(
                                                left: width! * 0.06,
                                                right: width! * 0.06),
                                            child: GestureDetector(
                                              onTap: () {
                                                _days.clear();
                                                alertValueFirst = false;
                                                alertValueSecond = false;
                                                alertValueThird = false;

                                                showDialog(
                                                    context: context,
                                                    builder: (context) {
                                                      return Form(
                                                        key: _formKey,
                                                        child: StatefulBuilder(
                                                          builder: (BuildContext
                                                                  context,
                                                              StateSetter
                                                                  myState) {
                                                            return AlertDialog(
                                                              insetPadding:
                                                                  EdgeInsets
                                                                      .all(10),
                                                              title: Text(getTranslated(
                                                                      context,
                                                                      AppString
                                                                          .information_medicine_title)
                                                                  .toString()),
                                                              content:
                                                                  Container(
                                                                margin: EdgeInsets.symmetric(
                                                                    horizontal:
                                                                        width! *
                                                                            0.02),
                                                                height: height *
                                                                    0.4,
                                                                width: width! *
                                                                    1.0,
                                                                child: Column(
                                                                  children: [
                                                                    Row(
                                                                      mainAxisAlignment:
                                                                          MainAxisAlignment
                                                                              .spaceBetween,
                                                                      crossAxisAlignment:
                                                                          CrossAxisAlignment
                                                                              .start,
                                                                      children: [
                                                                        Container(
                                                                          width:
                                                                              200,
                                                                          height:
                                                                              80,
                                                                          child:
                                                                              TextFormField(
                                                                            onChanged:
                                                                                (text) {
                                                                              myState(() {
                                                                                selectedMedicineValue = text;
                                                                              });
                                                                            },
                                                                            enableInteractiveSelection:
                                                                                false,
                                                                            keyboardType:
                                                                                TextInputType.name,
                                                                            inputFormatters: [
                                                                              FilteringTextInputFormatter.allow(RegExp("[a-zA-Z ]")),
                                                                            ],
                                                                            style:
                                                                                TextStyle(fontSize: 14, color: passwordVisibility),
                                                                            decoration:
                                                                                InputDecoration(
                                                                              hintText: getTranslated(context, AppString.medicine_name).toString(),
                                                                              hintStyle: TextStyle(fontSize: width! * 0.035, color: passwordVisibility),
                                                                            ),
                                                                            validator:
                                                                                (String? value) {
                                                                              if (value!.isEmpty) {
                                                                                return getTranslated(context, AppString.please_enter_profile_valid_name).toString();
                                                                              } else if (value.trim().length < 1) {
                                                                                return getTranslated(context, AppString.please_enter_valid_name).toString();
                                                                              }
                                                                              return null;
                                                                            },
                                                                            onSaved:
                                                                                (String? name) {},
                                                                          ),
                                                                          // child:
                                                                          //     TextDropdownFormField(
                                                                          //   options:
                                                                          //       medicineReq,
                                                                          //   decoration: InputDecoration(
                                                                          //       enabledBorder: UnderlineInputBorder(borderSide: BorderSide(color: black)),
                                                                          //       suffixIcon: Icon(Icons.arrow_drop_down),
                                                                          //       labelText: getTranslated(context, AppString.information_medicine_title).toString()),
                                                                          //   dropdownHeight:
                                                                          //       200,
                                                                          //   onChanged:
                                                                          //       (dynamic value) {
                                                                          //     selectedMedicineValue = value;
                                                                          //   },
                                                                          // ),
                                                                        ),
                                                                        FittedBox(
                                                                          fit: BoxFit
                                                                              .fitWidth,
                                                                          child:
                                                                              Container(
                                                                            height:
                                                                                70,
                                                                            width:
                                                                                width! / 5,
                                                                            alignment:
                                                                                Alignment.center,
                                                                            child:
                                                                                TextFormField(
                                                                              keyboardType: TextInputType.numberWithOptions(decimal: true),
                                                                              inputFormatters: [
                                                                                new FilteringTextInputFormatter.allow(RegExp("[0-9]"))
                                                                              ],
                                                                              controller: _days,
                                                                              decoration: InputDecoration(
                                                                                contentPadding: EdgeInsets.all(5),
                                                                                enabledBorder: UnderlineInputBorder(borderSide: BorderSide(color: black)),
                                                                                hintText: getTranslated(context, AppString.information_medicine_days).toString(),
                                                                              ),
                                                                              onChanged: (value) {
                                                                                myState(() {
                                                                                  valueDays = value;
                                                                                });
                                                                              },
                                                                            ),
                                                                          ),
                                                                        ),
                                                                      ],
                                                                    ),
                                                                    Container(
                                                                        margin: EdgeInsets
                                                                            .only(
                                                                          left: width! *
                                                                              0.04,
                                                                          right:
                                                                              width! * 0.04,
                                                                        ),
                                                                        child:
                                                                            Column(
                                                                          children: [
                                                                            Container(
                                                                              margin: EdgeInsets.only(top: height * 0.01),
                                                                              child: Transform.scale(
                                                                                scale: 1.2,
                                                                                child: CheckboxListTile(
                                                                                  controlAffinity: ListTileControlAffinity.leading,
                                                                                  title: Text(
                                                                                    getTranslated(context, AppString.information_medicine_morning).toString(),
                                                                                    style: TextStyle(fontSize: 16, color: hintColor),
                                                                                  ),
                                                                                  checkColor: loginButton,
                                                                                  activeColor: hintColor,
                                                                                  value: this.alertValueFirst,
                                                                                  onChanged: (bool? value) {
                                                                                    myState(() {
                                                                                      alertValueFirst = value;
                                                                                    });
                                                                                  },
                                                                                ), //CheckboxL
                                                                              ),
                                                                            ),
                                                                            Container(
                                                                              margin: EdgeInsets.only(top: height * 0.01),
                                                                              child: Transform.scale(
                                                                                scale: 1.2,
                                                                                child: CheckboxListTile(
                                                                                  controlAffinity: ListTileControlAffinity.leading,
                                                                                  title: Text(
                                                                                    getTranslated(context, AppString.information_medicine_afternoon).toString(),
                                                                                    style: TextStyle(fontSize: 16, color: hintColor),
                                                                                  ),
                                                                                  checkColor: loginButton,
                                                                                  activeColor: hintColor,
                                                                                  value: this.alertValueSecond,
                                                                                  onChanged: (bool? value) {
                                                                                    myState(() {
                                                                                      alertValueSecond = value;
                                                                                    });
                                                                                  },
                                                                                ),
                                                                              ),
                                                                            ),
                                                                            Container(
                                                                              margin: EdgeInsets.only(top: height * 0.01),
                                                                              child: Transform.scale(
                                                                                scale: 1.2,
                                                                                child: CheckboxListTile(
                                                                                  controlAffinity: ListTileControlAffinity.leading,
                                                                                  title: Text(
                                                                                    getTranslated(context, AppString.information_medicine_night).toString(),
                                                                                    style: TextStyle(fontSize: 16, color: hintColor),
                                                                                  ),
                                                                                  checkColor: loginButton,
                                                                                  activeColor: hintColor,
                                                                                  value: this.alertValueThird,
                                                                                  onChanged: (bool? value) {
                                                                                    myState(() {
                                                                                      alertValueThird = value;
                                                                                    });
                                                                                  },
                                                                                ),
                                                                              ),
                                                                            ),
                                                                          ],
                                                                        )),
                                                                  ],
                                                                ),
                                                              ),
                                                              actions: <Widget>[
                                                                OutlinedButton(
                                                                  child: Text(getTranslated(
                                                                          context,
                                                                          AppString
                                                                              .profile_dialog_ok_button)
                                                                      .toString()),
                                                                  onPressed:
                                                                      () {
                                                                    if (selectedMedicineValue ==
                                                                        null) {
                                                                      Fluttertoast
                                                                          .showToast(
                                                                        msg: getTranslated(context,
                                                                                AppString.please_select_medicines)
                                                                            .toString(),
                                                                        toastLength:
                                                                            Toast.LENGTH_SHORT,
                                                                        gravity:
                                                                            ToastGravity.BOTTOM,
                                                                      );
                                                                    } else if (_days
                                                                        .text
                                                                        .isEmpty) {
                                                                      Fluttertoast
                                                                          .showToast(
                                                                        msg: getTranslated(context,
                                                                                AppString.please_enter_days)
                                                                            .toString(),
                                                                        toastLength:
                                                                            Toast.LENGTH_SHORT,
                                                                        gravity:
                                                                            ToastGravity.BOTTOM,
                                                                      );
                                                                    } else {
                                                                      Map<String,
                                                                              dynamic>
                                                                          param =
                                                                          new HashMap();
                                                                      param['name'] =
                                                                          selectedMedicineValue;
                                                                      param['day'] =
                                                                          _days
                                                                              .text;
                                                                      param['morning'] =
                                                                          alertValueFirst;
                                                                      param['afternoon'] =
                                                                          alertValueSecond;
                                                                      param['night'] =
                                                                          alertValueThird;
                                                                      listOfMedicine
                                                                          .add(
                                                                              param);
                                                                      Navigator.pop(
                                                                          context);

                                                                      setState(
                                                                          () {});
                                                                    }
                                                                  },
                                                                ),
                                                              ],
                                                            );
                                                          },
                                                        ),
                                                      );
                                                    });
                                              },
                                              child: Row(
                                                crossAxisAlignment:
                                                    CrossAxisAlignment.center,
                                                mainAxisAlignment:
                                                    MainAxisAlignment.start,
                                                children: [
                                                  Container(
                                                      margin: EdgeInsets.only(
                                                          top: height * 0.02),
                                                      height: 30,
                                                      width: width! * 0.09,
                                                      padding:
                                                          EdgeInsets.all(5),
                                                      decoration: BoxDecoration(
                                                        color: loginButton
                                                            .withOpacity(0.4),
                                                        borderRadius:
                                                            BorderRadius
                                                                .circular(50),
                                                      ),
                                                      child: Icon(Icons.add,
                                                          size: 20,
                                                          color: colorBlack)),
                                                  Container(
                                                    margin: EdgeInsets.only(
                                                        top: width! * 0.04,
                                                        left: width! * 0.02),
                                                    child: Text(
                                                      getTranslated(
                                                              context,
                                                              AppString
                                                                  .add_medicine_button)
                                                          .toString(),
                                                      style: TextStyle(
                                                          fontSize: 18,
                                                          color: hintColor),
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ),
                                          Container(
                                              margin: EdgeInsets.only(
                                                  left: width! * 0.04,
                                                  right: width! * 0.04,
                                                  top: height * 0.02),
                                              child: DataTableWidget()),
                                          Center(
                                            child: ElevatedButton(
                                                child: Text(
                                                  getTranslated(
                                                          context,
                                                          AppString
                                                              .generate_pdf_button)
                                                      .toString(),
                                                  style: TextStyle(
                                                      color: colorWhite,
                                                      fontWeight:
                                                          FontWeight.bold),
                                                ),
                                                onPressed: () {
                                                  medicineData.clear();
                                                  Map<String, dynamic>
                                                      medicines;
                                                  for (int i = 0;
                                                      i < listOfMedicine.length;
                                                      i++) {
                                                    medicines = {
                                                      "medicine":
                                                          listOfMedicine[i]
                                                              ['name'],
                                                      "days": listOfMedicine[i]
                                                          ['day'],
                                                      "morning": listOfMedicine[
                                                                      i]
                                                                  ['morning'] ==
                                                              true
                                                          ? 1
                                                          : 0,
                                                      "afternoon": listOfMedicine[
                                                                      i][
                                                                  'afternoon'] ==
                                                              true
                                                          ? 1
                                                          : 0,
                                                      "night": listOfMedicine[i]
                                                                  ['night'] ==
                                                              true
                                                          ? 1
                                                          : 0
                                                    };
                                                    medicineData.add(medicines);
                                                  }

                                                  var convertMedicine =
                                                      jsonEncode(medicineData);

                                                  List<Map<String, dynamic>>
                                                      pdfData = [];

                                                  for (int i = 0;
                                                      i < listOfMedicine.length;
                                                      i++) {
                                                    Map<String, dynamic>
                                                        mapEducationData = {
                                                      "medicine":
                                                          listOfMedicine[i]
                                                              ['name'],
                                                      "days": listOfMedicine[i]
                                                          ['day'],
                                                      "morning": listOfMedicine[
                                                                      i]
                                                                  ['morning'] ==
                                                              true
                                                          ? 1
                                                          : 0,
                                                      "afternoon": listOfMedicine[
                                                                      i][
                                                                  'afternoon'] ==
                                                              true
                                                          ? 1
                                                          : 0,
                                                      "night": listOfMedicine[i]
                                                                  ['night'] ==
                                                              true
                                                          ? 1
                                                          : 0
                                                    };
                                                    pdfData
                                                        .add(mapEducationData);
                                                  }

                                                  if (pdfData.length > 0) {
                                                    reportView(
                                                        this.context,
                                                        pdfData,
                                                        id,
                                                        userId,
                                                        convertMedicine);
                                                    Fluttertoast.showToast(
                                                      msg: getTranslated(
                                                              context,
                                                              AppString
                                                                  .pdf_generated)
                                                          .toString(),
                                                      toastLength:
                                                          Toast.LENGTH_SHORT,
                                                      gravity:
                                                          ToastGravity.BOTTOM,
                                                    );
                                                  } else {
                                                    Fluttertoast.showToast(
                                                      msg: getTranslated(
                                                              context,
                                                              AppString
                                                                  .please_enter_data)
                                                          .toString(),
                                                      toastLength:
                                                          Toast.LENGTH_SHORT,
                                                      gravity:
                                                          ToastGravity.BOTTOM,
                                                    );
                                                  }
                                                }),
                                          )
                                        ],
                                      )
                                    : Center(
                                        child: ElevatedButton(
                                          child: Text(
                                            getTranslated(context,
                                                    AppString.view_pdf_button)
                                                .toString(),
                                            style: TextStyle(
                                                fontWeight: FontWeight.bold),
                                          ),
                                          onPressed: () {
                                            launchUrl(Uri.parse("$pdf"));
                                          },
                                        ),
                                      )),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            } else {
              return Center(child: CircularProgressIndicator());
            }
          }),
    );
  }

  Future<BaseModel<DoctorStatusChange>> statusChangeRequest(
      String status) async {
    Map<String, dynamic> body = {"id": id, "status": status};

    DoctorStatusChange response;

    try {
      response = await RestClient(await RetroApi().dioData(context))
          .doctorStatusChangeRequest(body);
      setState(() {
        if (status == 'approve') {
          appointmentStatus = 'approve';
        } else if (status == 'complete') {
          appointmentStatus = 'complete';
        } else {
          appointmentStatus = 'cancel';
        }

        hideButton = false;
        setState(() {});

        Fluttertoast.showToast(
          msg: response.msg!,
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM,
        );
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<AllMedicines>> allMedicinesRequest() async {
    AllMedicines response;

    try {
      medicineReq.clear();

      response =
          await RestClient(await RetroApi().dioData(context)).allMedicines();
      setState(() {
        for (int i = 0; i < response.data!.length; i++) {
          medicineReq.add(response.data![i].name.toString());
        }
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<AppointmentDetails>> appointmentDetails() async {
    AppointmentDetails response;

    try {
      response = await RestClient(await RetroApi().dioData(context))
          .appointmentDetails(id);
      setState(() {
        name = response.data!.patientName;
        age = response.data!.age;
        amount = double.parse(response.data!.amount!);
        date = DateUtil().formattedDate(DateTime.parse(response.data!.date!));
        phoneNo = response.data!.phoneNo;
        patientAddress = response.data!.patientAddress;
        illness = response.data!.illnessInformation;
        note = response.data!.note;
        appointmentId = response.data!.appointmentId;
        drugEffect = response.data!.drugEffect;
        time = response.data!.time;
        fullImage = response.data!.user!.fullImage;
        appointment = response.data!.appointmentFor;
        appointmentType = response.data!.appointmentType;
        appointmentStatus = response.data!.appointmentStatus;
        userId = response.data!.userId;
        pdf = response.data!.pdf;
        reportImages.addAll(response.data!.reportImage!);
        isInsured = response.data!.isInsured!;
        policyInsurerName = response.data!.policyInsurerName ?? "";
        policyNumber = response.data!.policyNumber ?? "";
        appointmentStatus == 'Approve' ? hideButton = false : hideButton = true;
        appointmentStatus == 'pending' ? hideButton = true : hideButton = false;
        
        // After loading appointment details, refresh Astra Fill data with resolved IDs
        _loadAstraFillData(patientId: userId.toString(), searchPhone: phoneNo);
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  _addVideoOverlay(BuildContext context) {
    Navigator.push(
        context,
        MaterialPageRoute(
            builder: (context) => VideoCall(
                  id: userId,
                  callEnd: false,
                  flag: "OutGoing",
                )));
    // OverlayService().addVideosOverlay(
    //   context,
    //   VideoCall(
    //     id: userId,
    //     callEnd: false,
    //     flag: "OutGoing",
    //   ),
    // );
  }
}

class DataTableWidget extends StatefulWidget {
  @override
  _DataTableWidgetState createState() => _DataTableWidgetState();
}

class _DataTableWidgetState extends State<DataTableWidget> {
  @override
  Widget build(BuildContext context) {
    return DataTable(
      horizontalMargin: 15,
      columnSpacing: 20,
      columns: [
        DataColumn(
            label: Text(getTranslated(context, AppString.pdf_medicine_name)
                .toString())),
        DataColumn(
            label: Text(
                getTranslated(context, AppString.information_medicine_days)
                    .toString())),
        DataColumn(
            label: Text(getTranslated(context, AppString.pdf_medicine_morning)
                .toString())),
        DataColumn(
            label: Text(getTranslated(context, AppString.pdf_medicine_afternoon)
                .toString())),
        DataColumn(
            label: Text(getTranslated(context, AppString.pdf_medicine_night)
                .toString())),
        DataColumn(
            label: Text(getTranslated(context, AppString.pdf_medicine_status)
                .toString())),
      ],
      rows: listOfMedicine
          .map(
            ((element) => DataRow(
                  cells: <DataCell>[
                    DataCell(Text(element["name"]
                        .toString())), //Extracting from Map element the value
                    DataCell(Text(element["day"])),
                    DataCell(element["morning"]
                        ? Icon(Icons.check, size: 20)
                        : Icon(Icons.clear, size: 20)),
                    DataCell(element["afternoon"]
                        ? Icon(Icons.check, size: 20)
                        : Icon(Icons.clear, size: 20)),
                    DataCell(element["night"]
                        ? Icon(Icons.check, size: 20)
                        : Icon(Icons.clear, size: 20)),
                    DataCell(GestureDetector(
                        onTap: () {
                          setState(() {
                            listOfMedicine.remove(element);
                          });
                        },
                        child: Icon(Icons.delete, size: 20))),
                  ],
                )),
          )
          .toList(),
    );
  }
}

class DateUtil {
  static const DATE_FORMAT = 'dd-MM-yyyy';

  String formattedDate(DateTime dateTime) {
    return DateFormat(DATE_FORMAT).format(dateTime);
  }
}
