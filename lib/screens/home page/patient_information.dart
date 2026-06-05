import 'dart:collection';
import 'dart:convert';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:doctro/chat/providers/home_provider.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/today_appointment.dart';
import 'package:doctro/model/DoctorStatusChange.dart';
import 'package:doctro/model/AllMedicines.dart';
import 'package:doctro/model/appointment_details.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/widgets/osler_button.dart';
import 'package:doctro/widgets/osler_loader.dart';
import 'package:doctro/widgets/osler_toast.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/svg.dart';
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
import 'package:doctro/services/astra_service.dart';

class patientDetailsScreen extends StatefulWidget {
  final int? id;

  patientDetailsScreen({this.id});

  @override
  _patientDetailsScreenState createState() => _patientDetailsScreenState();
}

//Pass Medicine list in pdf
List medicineData = [];
List<Map<String, dynamic>> listOfMedicine = [];

//Add Medicine List
List<String> medicineReq = [];

class _patientDetailsScreenState extends State<patientDetailsScreen>
    with TickerProviderStateMixin {
  //Set Loader
  Future? appointmentDetail;
  
  // Astra Fill Data (Health intake from patient's app)
  final AstraService _astraService = AstraService();
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

  void initState() {
    super.initState();
    homeProvider = Provider.of(context, listen: false);
    id = widget.id;
    Future.delayed(Duration.zero, () {
      appointmentDetail = appointmentDetails();
      _loadAstraFillData(); // Load patient's health intake from Astra

      _tabController = new TabController(vsync: this, length: 3);

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
    _tabController!.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    homeProvider = Provider.of(context, listen: false);
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return Scaffold( backgroundColor: AyurezeTheme.canvas,
      appBar: PreferredSize(
        preferredSize: Size(width! * 0.3, height * 0.2),
        child: SafeArea(
          top: true,
          child: Container(
              margin: EdgeInsets.only(top: height * 0.02),
              color: AyurezeTheme.canvas,
              child: Padding(
                padding: const EdgeInsets.all(1.0),
                child: Container(
                    margin: EdgeInsets.only(
                        left: width! * 0.9, right: width! * 0.02),
                    child: InkWell(
                      child: Icon(Icons.arrow_back_ios, color: AyurezeTheme.forestDeep),
                      onTap: () {
                        Navigator.pop(context);
                      },
                    )),
              )),
        ),
      ),
      body: FutureBuilder(
          future: appointmentDetail,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.done) {
              return SingleChildScrollView(
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () {
                    FocusScope.of(context).requestFocus(new FocusNode());
                  },
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Container(
                            margin: EdgeInsets.only(
                                left: width! * 0.16, right: width! * 0.03),
                          ),
                          GestureDetector(
                            onTap: () {
                              showModalBottomSheet(
                                context: context,
                                builder: (BuildContext bc) {
                                  return SafeArea(
                                    child: Container(
                                      child: new Wrap(
                                        children: <Widget>[
                                          new ListTile(
                                            leading:
                                                new Icon(AppIcons.call),
                                            title: new Text(
                                              getTranslated(
                                                      context, "call_text")
                                                  .toString(),
                                            ),
                                            onTap: () {
                                              if (SharedPreferenceHelper
                                                      .getBoolean(Preferences
                                                          .is_logged_in) ==
                                                  true) {
                                                Navigator.of(context).pop();
                                                launchUrl(
                                                    Uri.parse("tel:$phoneNo"));
                                              } else {
                                                Navigator.of(context).pop();
                                              }
                                            },
                                          ),
                                          if (appointmentType == 'video')
                                            new ListTile(
                                              leading: new Icon(Icons.videocam),
                                              title: new Text(
                                                getTranslated(
                                                        context, "video_call")
                                                    .toString(),
                                              ),
                                              onTap: () {
                                                setState(
                                                  () {
                                                    if (SharedPreferenceHelper
                                                            .getBoolean(Preferences
                                                                .is_logged_in) ==
                                                        true) {
                                                      Navigator.of(context)
                                                          .pop();
                                                      _addVideoOverlay(context);
                                                    } else {
                                                      Navigator.of(context)
                                                          .pop();
                                                    }
                                                  },
                                                );
                                              },
                                            ),
                                        ],
                                      ),
                                    ),
                                  );
                                },
                              );
                            },
                            child: Container(
                              child: SvgPicture.asset(
                                'assets/icons/call_dialler.svg',
                                colorFilter: ColorFilter.mode(AyurezeTheme.iconPrimary, BlendMode.srcIn),
                              ),
                            ),
                          ),
                          Container(
                            margin: EdgeInsets.only(
                              left: width! * 0.04,
                              right: width! * 0.03,
                            ),
                            child: Column(
                              children: [
                                Container(
                                  width: 120,
                                  height: 120,
                                  child: CachedNetworkImage(
                                    alignment: Alignment.center,
                                    imageUrl: '$fullImage',
                                    imageBuilder: (context, imageProvider) =>
                                        CircleAvatar(
                                      radius: 50,
                                      backgroundColor: AyurezeTheme.textPrimary,
                                      child: CircleAvatar(
                                        radius: 52,
                                        backgroundImage: imageProvider,
                                      ),
                                    ),
                                    placeholder: (context, url) =>
                                        CircularProgressIndicator(color: AyurezeTheme.healingGreen50),
                                    errorWidget: (context, url, error) =>
                                        Image.asset(
                                            "assets/images/no_image.jpg"),
                                  ),
                                ),
                                Container(
                                    margin:
                                        EdgeInsets.only(top: height * 0.015),
                                    child: Text(
                                      '${name ?? ''}',
                                      style: TextStyle(
                                          fontSize: 20, color: AyurezeTheme.textPrimary),
                                    )),
                                Text(
                                  getTranslated(context,
                                              AppString.information_booking_id)
                                          .toString() +
                                      '$appointmentId',
                                  style: TextStyle(
                                      fontSize: 14, color: AyurezeTheme.textPrimary),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            margin: EdgeInsets.only(
                                right: width! * 0.01, top: height * 0.2),
                          ),
                          GestureDetector(
                            onTap: () {
                              Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                      builder: (context) => ChatPage(
                                            peerId: body['peerId'].toString(),
                                            peerAvatar:
                                                body['peerAvatar'].toString(),
                                            peerNickname:
                                                body['nickName'].toString(),
                                            token: body['token'].toString(),
                                            isNavigate: 'chatHome',
                                          )));
                              // launchUrl(Uri.parse("sms:$phoneNo"));
                            },
                            child: SvgPicture.asset(
                              'assets/icons/message_dialler.svg',
                              colorFilter: ColorFilter.mode(AyurezeTheme.iconPrimary, BlendMode.srcIn),
                            ),
                          ),
                          StreamBuilder<QuerySnapshot>(
                            stream: homeProvider.getStreamFireStoreSpecificUser(
                                FirestoreConstants.pathUserCollection,
                                1,
                                userId.toString()),
                            builder: (BuildContext context,
                                AsyncSnapshot<QuerySnapshot> snapshot) {
                              if (snapshot.hasData) {
                                if ((snapshot.data?.docs.length ?? 0) > 0) {
                                  UserChat userChat = UserChat.fromDocument(
                                      snapshot.data!.docs[0]);
                                  body = {
                                    "peerId": userChat.id,
                                    "nickName": userChat.nickname,
                                    "peerAvatar": userChat.photoUrl,
                                    "token": userChat.token
                                  };
                                  return SizedBox();
                                } else {
                                  return SizedBox();
                                }
                              } else {
                                return SizedBox();
                              }
                            },
                          ),
                        ],
                      ),
                      Container(
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Expanded(
                              child: Column(
                              children: [
                                Text(
                                  getTranslated(
                                          context, AppString.information_amount)
                                      .toString(),
                                  style: TextStyle(
                                      fontSize: 16,
                                      color: AyurezeTheme.textPrimary,
                                      fontWeight: FontWeight.bold),
                                ),
                                Text(
                                  SharedPreferenceHelper.getString(
                                          Preferences.currency_symbol) +
                                      '$amount',
                                  style:
                                      TextStyle(fontSize: 16, color: AyurezeTheme.textPrimary),
                                ),
                              ],
                            ),
                            ),
                            Expanded(
                              child: Column(
                              children: [
                                Text(
                                  getTranslated(
                                          context, AppString.information_date)
                                      .toString(),
                                  style: TextStyle(
                                      fontSize: 16,
                                      color: AyurezeTheme.textPrimary,
                                      fontWeight: FontWeight.bold),
                                ),
                                Text(
                                  '$date',
                                  style:
                                      TextStyle(fontSize: 16, color: AyurezeTheme.textPrimary),
                                ),
                              ],
                            ),
                            ),
                            Expanded(
                              child: Column(
                              children: [
                                Text(
                                  getTranslated(context,
                                          AppString.information_appointment)
                                      .toString(),
                                  style: TextStyle(
                                      fontSize: 16,
                                      color: AyurezeTheme.textPrimary,
                                      fontWeight: FontWeight.bold),
                                ),
                                Text(
                                  "${appointmentType ?? '-'}${appointmentType != null ? ' appointment' : ''}\n${appointment ?? ''}",
                                  style: TextStyle(
                                    fontSize: 16,
                                    color: AyurezeTheme.textPrimary,
                                  ),
                                  textAlign: TextAlign.center,
                                  maxLines: 3,
                                  overflow: TextOverflow.ellipsis,
                                )
                              ],
                            ),
                            )
                          ],
                        ),
                      ),
                      new Container(
                        margin: EdgeInsets.only(top: 20),
                        color: divider,
                        padding: EdgeInsets.all(15),
                        child: new TabBar(
                          labelColor: AyurezeTheme.textPrimary,
                          controller: _tabController,
                          indicatorSize: TabBarIndicatorSize.tab,
                          tabs: [
                            Tab(text: getTranslated(context, AppString.patient_information)),
                            Tab(text: getTranslated(context, AppString.patient_illness)),
                            Tab(text: getTranslated(context, AppString.doctor_prescription)),
                          ],
                          unselectedLabelColor: AyurezeTheme.textSecondary,
                        ),
                      ),
                      new Container(
                        height: height * 0.54,
                        child: new TabBarView(
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
                                                        color: AyurezeTheme.textPrimary),
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
                                                        child: OslerButton(
                                                          text: getTranslated(context, AppString.information_complete_status).toString(),
                                                          onPressed: () {
                                                            setState(() {
                                                              statusChangeRequest("complete");
                                                            });
                                                          },
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
                                                    color: AyurezeTheme.textSecondary),
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
                                                  child: OslerButton(
                                                    text: getTranslated(context, AppString.information_approve_status).toString(),
                                                    onPressed: () {
                                                      myState(() {
                                                        statusChangeRequest("approve");
                                                      });
                                                    },
                                                  ),
                                                ),
                                                Container(
                                                  child: OslerButton(
                                                    text: getTranslated(context, AppString.information_cancel_status).toString(),
                                                    customColor: AyurezeTheme.remoteRed50,
                                                    onPressed: () {
                                                      setState(() {
                                                        statusChangeRequest("cancel");
                                                      });
                                                    },
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
                                          fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                          color: AyurezeTheme.textSecondary),
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
                                          fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                          color: AyurezeTheme.textSecondary),
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
                                          fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                          color: AyurezeTheme.textSecondary),
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
                                          fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                          color: AyurezeTheme.textSecondary),
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
                                          fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                          color: AyurezeTheme.textSecondary),
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
                                                fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                                color: AyurezeTheme.textSecondary),
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
                                                fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                                color: AyurezeTheme.textSecondary),
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
                                                fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                                color: AyurezeTheme.textSecondary),
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
                                            fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                          color: AyurezeTheme.textSecondary),
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
                                            fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                            color: AyurezeTheme.textSecondary),
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
                                            fontSize: 18, color: AyurezeTheme.textPrimary),
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
                                            color: AyurezeTheme.textSecondary),
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
                                                  color: AyurezeTheme.textPrimary),
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
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Container(
                                    width: double.infinity,
                                    margin: EdgeInsets.symmetric(
                                      horizontal: width! * 0.06,
                                      vertical: 12,
                                    ),
                                    child: ElevatedButton.icon(
                                      icon: Icon(Icons.auto_awesome, color: colorWhite),
                                      label: Text(
                                        "Smart Prescribe (Astra AI)",
                                        style: TextStyle(
                                          color: colorWhite,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: AyurezeTheme.forestDeep,
                                        padding: EdgeInsets.symmetric(vertical: 14),
                                        shape: RoundedRectangleBorder(
                                          borderRadius: BorderRadius.circular(12),
                                        ),
                                      ),
                                      onPressed: () {
                                        Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                            builder: (context) => PrescriptionScreen(
                                              patientId: userId.toString(),
                                              patientName: name ?? "Patient",
                                              patientPhone: phoneNo,
                                              doctorId: SharedPreferenceHelper.getString(Preferences.doctorId),
                                              prescriptionId: id?.toString(),
                                              astraFillData: _astraFillData,
                                            ),
                                          ),
                                        );
                                      },
                                    ),
                                  ),
                                  Padding(
                                    padding: EdgeInsets.symmetric(horizontal: width! * 0.06),
                                    child: Text(
                                      "Manual PDF generation removed. Use Smart Prescribe for AI-assisted prescription workflow.",
                                      style: TextStyle(
                                        color: AyurezeTheme.textSecondary,
                                        fontSize: 13,
                                      ),
                                    ),
                                  ),
                                  SizedBox(height: 14),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            } else {
              return Center(child: OslerLoader());
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

        OslerToast.success(context, response.msg!);
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
