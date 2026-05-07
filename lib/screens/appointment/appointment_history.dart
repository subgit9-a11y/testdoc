import 'dart:async';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/common_function.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/appointment_history.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:doctro/widgets/modern_drawer.dart';
import 'package:doctro/screens/auth/SignIn.dart';
import 'package:doctro/theme/ayureze_theme.dart';


class AppointmentHistoryScreen extends StatefulWidget {
  @override
  _AppointmentHistoryScreen createState() => _AppointmentHistoryScreen();
}

class _AppointmentHistoryScreen extends State<AppointmentHistoryScreen>
    with TickerProviderStateMixin {
  //Set Loader
  Future? appointment;

  //Set Drawer Open
  final _scaffoldKey = GlobalKey<ScaffoldState>();

  //Add List Data
  List<PastAppointment> pastAppointmentReq = [];
  List<UpcomingAppointment> upcomingAppointmentReq = [];

  //Search Patient
  TextEditingController _search = TextEditingController();
  List<UpcomingAppointment> _searchResult = [];
  List<UpcomingAppointment> _userDetails = [];
  List<PastAppointment> _pastSearch = [];
  List<PastAppointment> _pastData = [];
  bool? isShow;

  //get preferences
  String? dName;

  String? dFullImage;

  String? phone;

  int? subscription;

  //Set Height/Width using MediaQuery
  late double width;
  late double height;

  //Set Tabbar
  List<Tab> tabList = [];
  TabController? _tabController;

  List<String> _drawer = [];
  List<String> _drawerMenu = [];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    //Set Drawer Menu Item List

    _drawer = [
      getTranslated(context, AppString.drawer_home).toString(),
      getTranslated(context, AppString.drawer_payments).toString(),
      getTranslated(context, AppString.drawer_canceled_appointment).toString(),
      getTranslated(context, AppString.drawer_appointments).toString(),
      getTranslated(context, AppString.drawer_review).toString(),
      getTranslated(context, AppString.drawer_notification).toString(),
      getTranslated(context, AppString.drawer_callHistory).toString(),
      getTranslated(context, AppString.drawer_schedule_timing).toString(),
      getTranslated(context, AppString.drawer_setting).toString(),
      getTranslated(context, AppString.chats).toString(),
      getTranslated(context, AppString.drawer_logout).toString(),
    ];

    _drawerMenu = [
      getTranslated(context, AppString.drawer_home).toString(),
      getTranslated(context, AppString.drawer_payments).toString(),
      getTranslated(context, AppString.drawer_canceled_appointment).toString(),
      getTranslated(context, AppString.drawer_appointments).toString(),
      getTranslated(context, AppString.drawer_review).toString(),
      getTranslated(context, AppString.drawer_notification).toString(),
      getTranslated(context, AppString.drawer_callHistory).toString(),
      getTranslated(context, AppString.drawer_schedule_timing).toString(),
      getTranslated(context, AppString.drawer_setting).toString(),
      getTranslated(context, AppString.chats).toString(),
      getTranslated(context, AppString.drawer_logout).toString(),
    ];
  }

  @override
  void initState() {
    super.initState();
    Future.delayed(Duration.zero, () {
      tabList.add(new Tab(
        child: Text(
          getTranslated(context, AppString.upcoming_appointment).toString(),
          textAlign: TextAlign.center,
        ),
      ));
      tabList.add(new Tab(
        child: Text(
          getTranslated(context, AppString.past_appointment).toString(),
          textAlign: TextAlign.center,
        ),
      ));
      _tabController = new TabController(vsync: this, length: tabList.length);
      _tabController!.addListener(() {
        setState(() {
          _searchResult.clear();
          _pastSearch.clear();
          _search.clear();
        });
      });

      appointment = appointmentHistoryScreen();
      dName = SharedPreferenceHelper.getString(Preferences.name);
      dFullImage = SharedPreferenceHelper.getString(Preferences.image);
      phone = SharedPreferenceHelper.getString(Preferences.phone_no);
      subscription =
          SharedPreferenceHelper.getInt(Preferences.subscription_status);
    });
  }

  @override
  void dispose() {
    _tabController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) return;
        Navigator.pushNamedAndRemoveUntil(context, 'loginHome', (route) => false);
      },
      child: Scaffold(
        key: _scaffoldKey,
        backgroundColor: AyurezeTheme.canvas,
        drawer: const ModernDrawer(),
        appBar: AppBar(
          backgroundColor: AyurezeTheme.canvas,
          elevation: 0,
          leading: IconButton(
            icon: SvgPicture.asset("assets/icons/dMenuBar.svg", height: 18, color: AyurezeTheme.forestDeep),
            onPressed: () => _scaffoldKey.currentState!.openDrawer(),
          ),
          actions: [
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: GestureDetector(
                onTap: () => Navigator.pushNamed(context, "profile"),
                child: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    image: DecorationImage(
                      image: (dFullImage != null && dFullImage!.isNotEmpty)
                          ? NetworkImage(dFullImage!)
                          : const AssetImage("assets/images/no_image.jpg")
                              as ImageProvider,
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
        body: RefreshIndicator(
          onRefresh: appointmentHistoryScreen,
          color: AyurezeTheme.forestDeep,
          child: SingleChildScrollView(
            padding: AyurezeTheme.screenPadding,
            child: FutureBuilder(
                future: appointment,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.done) {
                    return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(22),
                        decoration: AyurezeTheme.heroDecoration(),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              getTranslated(context, AppString.drawer_appointments).toString(),
                              style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: Colors.white),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              "Manage and track your patient interactions.",
                              style: TextStyle(fontSize: 14, color: Colors.white.withOpacity(0.8)),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 20),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        decoration: AyurezeTheme.panelDecoration(),
                        child: TextField(
                          controller: _search,
                          onChanged: onSearchTextChanged,
                          decoration: InputDecoration(
                            hintText: getTranslated(context, AppString.search_appointment_history).toString(),
                            hintStyle: TextStyle(color: AyurezeTheme.textSecondary, fontSize: 14),
                            border: InputBorder.none,
                            icon: Icon(Icons.search_rounded, color: AyurezeTheme.forestDeep, size: 20),
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
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
                      const SizedBox(height: 16),
                      SizedBox(
                        height: height * 0.7,
                        child: TabBarView(
                          controller: _tabController,
                          children: [
                                            upcomingAppointmentReq.length == 0
                                                ? Container(
                                                    child: Center(
                                                      child: Image.asset(
                                                          "assets/images/no-data.png"),
                                                    ),
                                                  )
                                                : _search.text.isNotEmpty
                                                    ? _searchResult.length > 0
                                                        ? ListView.builder(
                                                            padding:
                                                                EdgeInsets.only(
                                                                    bottom: 40),
                                                            scrollDirection:
                                                                Axis.vertical,
                                                            shrinkWrap: true,
                                                            physics:
                                                                AlwaysScrollableScrollPhysics(),
                                                            itemCount:
                                                                _searchResult
                                                                    .length,
                                                            itemBuilder:
                                                                (context, i) {
                                                              String
                                                                  searchDate =
                                                                  _searchResult[
                                                                          i]
                                                                      .date!;
                                                              var statusColor =
                                                                  status;
                                                              if (_searchResult[
                                                                          i]
                                                                      .appointmentStatus!
                                                                      .toUpperCase() ==
                                                                  getTranslated(
                                                                          context,
                                                                          AppString
                                                                              .status_pending)
                                                                      .toString()) {
                                                                statusColor =
                                                                    hintColor
                                                                        .withOpacity(
                                                                            0.6);
                                                              } else if (_searchResult[
                                                                          i]
                                                                      .appointmentStatus!
                                                                      .toUpperCase() ==
                                                                  getTranslated(
                                                                          context,
                                                                          AppString
                                                                              .status_cancel)
                                                                      .toString()) {
                                                                statusColor =
                                                                    statusCancel;
                                                              } else if (_searchResult[
                                                                          i]
                                                                      .appointmentStatus!
                                                                      .toUpperCase() ==
                                                                  getTranslated(
                                                                          context,
                                                                          AppString
                                                                              .status_approve)
                                                                      .toString()) {
                                                                statusColor =
                                                                    status;
                                                              }
                                                              return Container(
                                                                  width: width *
                                                                      0.87,
                                                                  child: Card(
                                                                      elevation:
                                                                          2,
                                                                      shape:
                                                                          RoundedRectangleBorder(
                                                                        borderRadius:
                                                                            BorderRadius.circular(15.0),
                                                                      ),
                                                                      child: Column(
                                                                          mainAxisAlignment:
                                                                              MainAxisAlignment.center,
                                                                          children: <Widget>[
                                                                            Container(
                                                                              child: ListTile(
                                                                                isThreeLine: true,
                                                                                leading: SizedBox(
                                                                                  height: height * 0.20,
                                                                                  width: width * 0.15,
                                                                                  child: ClipRRect(
                                                                                    borderRadius: BorderRadius.circular(10),
                                                                                    child: Container(decoration: new BoxDecoration(image: new DecorationImage(fit: BoxFit.fitHeight, image: NetworkImage(_searchResult[i].user!.fullImage!)))),
                                                                                  ),
                                                                                ),
                                                                                title: Text(_searchResult[i].patientName!, style: TextStyle(fontSize: 16.0)),
                                                                                trailing: Container(
                                                                                  child: Text(
                                                                                    _searchResult[i].appointmentStatus!.toUpperCase(),
                                                                                    style: TextStyle(color: statusColor),
                                                                                  ),
                                                                                ),
                                                                                subtitle: Column(
                                                                                  crossAxisAlignment: CrossAxisAlignment.start,
                                                                                  children: <Widget>[
                                                                                    Text(
                                                                                      _searchResult[i].treatment!,
                                                                                      style: TextStyle(fontSize: 14, color: passwordVisibility),
                                                                                    ),
                                                                                    Text(
                                                                                      _searchResult[i].patientAddress!,
                                                                                      style: TextStyle(fontSize: 12, color: passwordVisibility),
                                                                                      overflow: TextOverflow.ellipsis,
                                                                                      maxLines: 2,
                                                                                    ),
                                                                                  ],
                                                                                ),
                                                                              ),
                                                                            ),
                                                                            Container(
                                                                              margin: EdgeInsets.symmetric(horizontal: 20),
                                                                              child: Row(
                                                                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                                children: [
                                                                                  Column(
                                                                                    mainAxisAlignment: MainAxisAlignment.start,
                                                                                    crossAxisAlignment: CrossAxisAlignment.start,
                                                                                    children: [
                                                                                      Text(getTranslated(context, AppString.date_and_time).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                      Row(
                                                                                        children: [
                                                                                          Text('$searchDate', style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                          SizedBox(width: 5),
                                                                                          Text(_searchResult[i].time!, style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                        ],
                                                                                      ),
                                                                                    ],
                                                                                  ),
                                                                                  Column(
                                                                                    mainAxisAlignment: MainAxisAlignment.start,
                                                                                    crossAxisAlignment: CrossAxisAlignment.end,
                                                                                    children: [
                                                                                      Text(getTranslated(context, AppString.doctor_name).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                      Container(
                                                                                        margin: EdgeInsets.only(),
                                                                                        child: Text(_searchResult[i].doctorName!, style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                      ),
                                                                                    ],
                                                                                  ),
                                                                                ],
                                                                              ),
                                                                            ),
                                                                            Divider(
                                                                              color: divider,
                                                                            ),
                                                                            Container(
                                                                              margin: EdgeInsets.symmetric(horizontal: 20),
                                                                              child: Column(
                                                                                children: [
                                                                                  Row(
                                                                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                                    children: [
                                                                                      Text(getTranslated(context, AppString.hospital_name_heading).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                      Text(getTranslated(context, AppString.hospital_address).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                    ],
                                                                                  ),
                                                                                  Row(
                                                                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                                    children: [
                                                                                      _searchResult[i].hospital != null
                                                                                          ? Container(
                                                                                              width: 120,
                                                                                              child: Text(_searchResult[i].hospital!.name!, style: TextStyle(fontSize: 14, color: hintColor), overflow: TextOverflow.ellipsis, maxLines: 2),
                                                                                            )
                                                                                          : Text('', style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                      _searchResult[i].hospital != null
                                                                                          ? Container(
                                                                                              width: 120,
                                                                                              child: Text(_searchResult[i].hospital!.address!, style: TextStyle(fontSize: 14, color: hintColor), overflow: TextOverflow.ellipsis, maxLines: 2),
                                                                                            )
                                                                                          : Text(''),
                                                                                    ],
                                                                                  ),
                                                                                  SizedBox(height: 5)
                                                                                ],
                                                                              ),
                                                                            ),
                                                                                                                                                        ],
                                                                                                                                                      ), 
                                                                                                                                                      ), 
                                                                                                                                                      ), 
                                                                                                                                                      );
                                                                          },
                                                                        )
                                                        : Center(
                                                            child: Container(
                                                            child: Text(getTranslated(
                                                                    context,
                                                                    AppString
                                                                        .result_not_found)
                                                                .toString()),
                                                          ))
                                                    : ListView.builder(
                                                        physics:
                                                            AlwaysScrollableScrollPhysics(),
                                                        padding:
                                                            EdgeInsets.only(
                                                                bottom: 40),
                                                        shrinkWrap: true,
                                                        scrollDirection:
                                                            Axis.vertical,
                                                        itemCount:
                                                            upcomingAppointmentReq
                                                                .length,
                                                        itemBuilder:
                                                            (context, index) {
                                                          var statusColor =
                                                              status;
                                                          if (upcomingAppointmentReq[
                                                                      index]
                                                                  .appointmentStatus!
                                                                  .toUpperCase() ==
                                                              getTranslated(
                                                                      context,
                                                                      AppString
                                                                          .status_pending)
                                                                  .toString()) {
                                                            statusColor =
                                                                hintColor
                                                                    .withOpacity(
                                                                        0.6);
                                                          } else if (upcomingAppointmentReq[
                                                                      index]
                                                                  .appointmentStatus!
                                                                  .toUpperCase() ==
                                                              getTranslated(
                                                                      context,
                                                                      AppString
                                                                          .status_cancel)
                                                                  .toString()) {
                                                            statusColor =
                                                                statusCancel;
                                                          } else if (upcomingAppointmentReq[
                                                                      index]
                                                                  .appointmentStatus!
                                                                  .toUpperCase() ==
                                                              getTranslated(
                                                                      context,
                                                                      AppString
                                                                          .status_approve)
                                                                  .toString()) {
                                                            statusColor =
                                                                status;
                                                          }
                                                          //Set Date Formate dd-mm-yy
                                                          String date =
                                                              upcomingAppointmentReq[
                                                                      index]
                                                                  .date!;
                                                          return Container(
                                                              width:
                                                                  width * 0.87,
                                                              child: Card(
                                                                  elevation: 2,
                                                                  shape:
                                                                      RoundedRectangleBorder(
                                                                    borderRadius:
                                                                        BorderRadius.circular(
                                                                            15.0),
                                                                  ),
                                                                  child: Column(
                                                                      mainAxisAlignment:
                                                                          MainAxisAlignment
                                                                              .center,
                                                                      children: <Widget>[
                                                                        Container(
                                                                          child:
                                                                              ListTile(
                                                                            isThreeLine:
                                                                                true,
                                                                            leading:
                                                                                SizedBox(
                                                                              height: height * 0.20,
                                                                              width: width * 0.15,
                                                                              child: ClipRRect(
                                                                                borderRadius: BorderRadius.circular(10),
                                                                                child: Container(decoration: new BoxDecoration(image: new DecorationImage(fit: BoxFit.fitHeight, image: NetworkImage(upcomingAppointmentReq[index].user!.fullImage!)))),
                                                                              ),
                                                                            ),
                                                                            title:
                                                                                Text(upcomingAppointmentReq[index].patientName!, style: TextStyle(fontSize: 16.0)),
                                                                            trailing:
                                                                                Container(
                                                                              child: Text(
                                                                                upcomingAppointmentReq[index].appointmentStatus!.toUpperCase(),
                                                                                style: TextStyle(color: statusColor),
                                                                              ),
                                                                            ),
                                                                            subtitle:
                                                                                Column(
                                                                              crossAxisAlignment: CrossAxisAlignment.start,
                                                                              children: <Widget>[
                                                                                Text(
                                                                                  upcomingAppointmentReq[index].treatment!,
                                                                                  style: TextStyle(fontSize: 14, color: passwordVisibility),
                                                                                ),
                                                                                Text(
                                                                                  upcomingAppointmentReq[index].patientAddress!,
                                                                                  style: TextStyle(fontSize: 12, color: passwordVisibility),
                                                                                  overflow: TextOverflow.ellipsis,
                                                                                  maxLines: 2,
                                                                                ),
                                                                              ],
                                                                            ),
                                                                          ),
                                                                        ),
                                                                        Container(
                                                                          margin:
                                                                              EdgeInsets.symmetric(horizontal: 20),
                                                                          child:
                                                                              Row(
                                                                            mainAxisAlignment:
                                                                                MainAxisAlignment.spaceBetween,
                                                                            children: [
                                                                              Column(
                                                                                mainAxisAlignment: MainAxisAlignment.start,
                                                                                crossAxisAlignment: CrossAxisAlignment.start,
                                                                                children: [
                                                                                  Text(getTranslated(context, AppString.date_and_time).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                  Row(
                                                                                    children: [
                                                                                      Text('$date', style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                      SizedBox(width: 5),
                                                                                      Text(upcomingAppointmentReq[index].time!, style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                    ],
                                                                                  ),
                                                                                ],
                                                                              ),
                                                                              Column(
                                                                                mainAxisAlignment: MainAxisAlignment.start,
                                                                                crossAxisAlignment: CrossAxisAlignment.end,
                                                                                children: [
                                                                                  Text(getTranslated(context, AppString.doctor_name).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                  Container(
                                                                                    margin: EdgeInsets.only(),
                                                                                    child: Text(upcomingAppointmentReq[index].doctorName!, style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                  ),
                                                                                ],
                                                                              ),
                                                                            ],
                                                                          ),
                                                                        ),
                                                                        Divider(
                                                                          color:
                                                                              divider,
                                                                        ),
                                                                        Container(
                                                                          margin:
                                                                              EdgeInsets.symmetric(horizontal: 20),
                                                                          child:
                                                                              Column(
                                                                            children: [
                                                                              Row(
                                                                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                                crossAxisAlignment: CrossAxisAlignment.end,
                                                                                children: [
                                                                                  Text(getTranslated(context, AppString.hospital_name_heading).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                  Text(getTranslated(context, AppString.hospital_address).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                ],
                                                                              ),
                                                                              Row(
                                                                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                                children: [
                                                                                  upcomingAppointmentReq[index].hospital != null
                                                                                      ? Container(
                                                                                          width: 120,
                                                                                          child: Text(upcomingAppointmentReq[index].hospital!.name!, style: TextStyle(fontSize: 14, color: hintColor), overflow: TextOverflow.ellipsis, maxLines: 2),
                                                                                        )
                                                                                      : Text('', style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                  upcomingAppointmentReq[index].hospital != null
                                                                                      ? Container(
                                                                                          width: 100,
                                                                                          child: Text(upcomingAppointmentReq[index].hospital!.address!, style: TextStyle(fontSize: 14, color: hintColor), overflow: TextOverflow.ellipsis, maxLines: 2),
                                                                                        )
                                                                                      : Text(''),
                                                                                ],
                                                                              ),
                                                                              SizedBox(height: 5)
                                                                            ],
                                                                          ),
                                                                        ),
                                                                                                                                                    ],
                                                                                                                                                  ), 
                                                                                                                                                  ), 
                                                                                                                                                  ), 
                                                                                                                                                  );
                                                                          },
                                                                        ),
                                            pastAppointmentReq.length == 0
                                                ? Container(
                                                    height: height / 2,
                                                    child: Image.asset(
                                                        "assets/images/no-data.png"),
                                                  )
                                                : _search.text.isNotEmpty
                                                    ? _pastSearch.length > 0
                                                        ? new ListView.builder(
                                                            padding:
                                                                EdgeInsets.only(
                                                                    bottom: 40),
                                                            shrinkWrap: true,
                                                            itemCount:
                                                                _pastSearch
                                                                    .length,
                                                            itemBuilder:
                                                                (context, i) {
                                                              String
                                                                  searchDate =
                                                                  _pastSearch[i]
                                                                      .date!;
                                                              var statusColor =
                                                                  status;
                                                              if (_pastSearch[i]
                                                                      .appointmentStatus!
                                                                      .toUpperCase() ==
                                                                  getTranslated(
                                                                          context,
                                                                          AppString
                                                                              .status_pending)
                                                                      .toString()) {
                                                                statusColor =
                                                                    hintColor
                                                                        .withOpacity(
                                                                            0.6);
                                                              } else if (_pastSearch[
                                                                          i]
                                                                      .appointmentStatus!
                                                                      .toUpperCase() ==
                                                                  getTranslated(
                                                                          context,
                                                                          AppString
                                                                              .status_cancel)
                                                                      .toString()) {
                                                                statusColor =
                                                                    statusCancel;
                                                              } else if (_pastSearch[
                                                                          i]
                                                                      .appointmentStatus!
                                                                      .toUpperCase() ==
                                                                  getTranslated(
                                                                          context,
                                                                          AppString
                                                                              .status_approve)
                                                                      .toString()) {
                                                                statusColor =
                                                                    status;
                                                              }
                                                              return Container(
                                                                  width: width *
                                                                      0.87,
                                                                  child: Card(
                                                                      elevation:
                                                                          2,
                                                                      shape:
                                                                          RoundedRectangleBorder(
                                                                        borderRadius:
                                                                            BorderRadius.circular(15.0),
                                                                      ),
                                                                      child: Column(
                                                                          crossAxisAlignment:
                                                                              CrossAxisAlignment.start,
                                                                          children: <Widget>[
                                                                            Container(
                                                                              child: ListTile(
                                                                                isThreeLine: true,
                                                                                leading: SizedBox(
                                                                                  height: height * 0.20,
                                                                                  width: width * 0.15,
                                                                                  child: ClipRRect(
                                                                                    borderRadius: BorderRadius.circular(10),
                                                                                    child: Container(decoration: new BoxDecoration(image: new DecorationImage(fit: BoxFit.fitHeight, image: NetworkImage(_pastSearch[i].user!.fullImage!)))),
                                                                                  ),
                                                                                ),
                                                                                title: Text(_pastSearch[i].patientName!, style: TextStyle(fontSize: 16.0)),
                                                                                trailing: Container(
                                                                                  child: Text(
                                                                                    _pastSearch[i].appointmentStatus!.toUpperCase(),
                                                                                    style: TextStyle(color: statusColor),
                                                                                  ),
                                                                                ),
                                                                                subtitle: Column(
                                                                                  crossAxisAlignment: CrossAxisAlignment.start,
                                                                                  children: <Widget>[
                                                                                    Text(
                                                                                      _pastSearch[i].treatment!,
                                                                                      style: TextStyle(fontSize: 14, color: passwordVisibility),
                                                                                    ),
                                                                                    Text(
                                                                                      _pastSearch[i].patientAddress!,
                                                                                      style: TextStyle(fontSize: 12, color: passwordVisibility),
                                                                                      overflow: TextOverflow.ellipsis,
                                                                                      maxLines: 2,
                                                                                    ),
                                                                                  ],
                                                                                ),
                                                                              ),
                                                                            ),
                                                                            Container(
                                                                              margin: EdgeInsets.symmetric(horizontal: 20),
                                                                              child: Row(
                                                                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                                children: [
                                                                                  Column(
                                                                                    mainAxisAlignment: MainAxisAlignment.start,
                                                                                    crossAxisAlignment: CrossAxisAlignment.start,
                                                                                    children: [
                                                                                      Text(getTranslated(context, AppString.date_and_time).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                      Row(
                                                                                        children: [
                                                                                          Text("$searchDate", style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                          Container(
                                                                                            margin: EdgeInsets.only(left: 5),
                                                                                            child: Text(_pastSearch[i].time!, style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                          ),
                                                                                        ],
                                                                                      ),
                                                                                    ],
                                                                                  ),
                                                                                  Column(
                                                                                    mainAxisAlignment: MainAxisAlignment.start,
                                                                                    crossAxisAlignment: CrossAxisAlignment.end,
                                                                                    children: [
                                                                                      Text(getTranslated(context, AppString.doctor_name).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                      Container(
                                                                                        margin: EdgeInsets.only(),
                                                                                        child: Text(_pastSearch[i].doctorName!, style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                      ),
                                                                                    ],
                                                                                  ),
                                                                                ],
                                                                              ),
                                                                            ),
                                                                            Divider(
                                                                              color: divider,
                                                                            ),
                                                                            Container(
                                                                              margin: EdgeInsets.symmetric(horizontal: 20),
                                                                              child: Column(
                                                                                children: [
                                                                                  Row(
                                                                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                                    crossAxisAlignment: CrossAxisAlignment.end,
                                                                                    children: [
                                                                                      Text(getTranslated(context, AppString.hospital_name_heading).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                      Text(getTranslated(context, AppString.hospital_address).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                    ],
                                                                                  ),
                                                                                  Row(
                                                                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                                    children: [
                                                                                      _pastSearch[i].hospital?.name != null
                                                                                          ? Container(
                                                                                              width: 120,
                                                                                              child: Text(_pastSearch[i].hospital!.name.toString(), style: TextStyle(fontSize: 14, color: hintColor), overflow: TextOverflow.ellipsis, maxLines: 2),
                                                                                            )
                                                                                          : Text('', style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                      _pastSearch[i].hospital?.address != null
                                                                                          ? Container(
                                                                                              width: 100,
                                                                                              child: Text(_pastSearch[i].hospital!.address.toString(), style: TextStyle(fontSize: 14, color: hintColor), overflow: TextOverflow.ellipsis, maxLines: 2),
                                                                                            )
                                                                                          : Text(''),
                                                                                    ],
                                                                                  ),
                                                                                  SizedBox(height: 5)
                                                                                ],
                                                                              ),
                                                                            ),
                                                                                                                                                        ],
                                                                                                                                                      ), 
                                                                                                                                                      ), 
                                                                                                                                                      ), 
                                                                                                                                                      );
                                                                          },
                                                                        )
                                                        : Center(
                                                            child: Container(
                                                            child: Text(getTranslated(
                                                                    context,
                                                                    AppString
                                                                        .result_not_found)
                                                                .toString()),
                                                          ))
                                                    : ListView.builder(
                                                        physics:
                                                            AlwaysScrollableScrollPhysics(),
                                                        padding:
                                                            EdgeInsets.only(
                                                                bottom: 40),
                                                        shrinkWrap: true,
                                                        scrollDirection:
                                                            Axis.vertical,
                                                        itemCount:
                                                            pastAppointmentReq
                                                                .length,
                                                        itemBuilder:
                                                            (context, index) {
                                                          String date =
                                                              pastAppointmentReq[
                                                                      index]
                                                                  .date!;
                                                          var statusColor =
                                                              status;
                                                          if (pastAppointmentReq[
                                                                      index]
                                                                  .appointmentStatus!
                                                                  .toUpperCase() ==
                                                              getTranslated(
                                                                      context,
                                                                      AppString
                                                                          .status_pending)
                                                                  .toString()) {
                                                            statusColor =
                                                                hintColor
                                                                    .withOpacity(
                                                                        0.6);
                                                          } else if (pastAppointmentReq[
                                                                      index]
                                                                  .appointmentStatus!
                                                                  .toUpperCase() ==
                                                              getTranslated(
                                                                      context,
                                                                      AppString
                                                                          .status_cancel)
                                                                  .toString()) {
                                                            statusColor =
                                                                statusCancel;
                                                          } else if (pastAppointmentReq[
                                                                      index]
                                                                  .appointmentStatus!
                                                                  .toUpperCase() ==
                                                              getTranslated(
                                                                      context,
                                                                      AppString
                                                                          .status_approve)
                                                                  .toString()) {
                                                            statusColor =
                                                                status;
                                                          }
                                                          return Container(
                                                              width:
                                                                  width * 0.87,
                                                              child: Card(
                                                                  elevation: 2,
                                                                  shape:
                                                                      RoundedRectangleBorder(
                                                                    borderRadius:
                                                                        BorderRadius.circular(
                                                                            15.0),
                                                                  ),
                                                                  child: Column(
                                                                      crossAxisAlignment:
                                                                          CrossAxisAlignment
                                                                              .start,
                                                                      children: <Widget>[
                                                                        Container(
                                                                          child:
                                                                              ListTile(
                                                                            isThreeLine:
                                                                                true,
                                                                            leading:
                                                                                SizedBox(
                                                                              height: height * 0.20,
                                                                              width: width * 0.15,
                                                                              child: ClipRRect(
                                                                                borderRadius: BorderRadius.circular(10),
                                                                                child: Container(decoration: new BoxDecoration(image: new DecorationImage(fit: BoxFit.fitHeight, image: NetworkImage(pastAppointmentReq[index].user!.fullImage!)))),
                                                                              ),
                                                                            ),
                                                                            title:
                                                                                Text(pastAppointmentReq[index].patientName!, style: TextStyle(fontSize: 16.0)),
                                                                            trailing:
                                                                                Container(
                                                                              child: Text(
                                                                                pastAppointmentReq[index].appointmentStatus!.toUpperCase(),
                                                                                style: TextStyle(color: statusColor),
                                                                              ),
                                                                            ),
                                                                            subtitle:
                                                                                Column(
                                                                              crossAxisAlignment: CrossAxisAlignment.start,
                                                                              children: <Widget>[
                                                                                Text(
                                                                                  pastAppointmentReq[index].treatment!,
                                                                                  style: TextStyle(fontSize: 14, color: passwordVisibility),
                                                                                ),
                                                                                Text(
                                                                                  pastAppointmentReq[index].patientAddress!,
                                                                                  style: TextStyle(fontSize: 12, color: passwordVisibility),
                                                                                  overflow: TextOverflow.ellipsis,
                                                                                  maxLines: 2,
                                                                                ),
                                                                              ],
                                                                            ),
                                                                          ),
                                                                        ),
                                                                        Container(
                                                                          margin:
                                                                              EdgeInsets.symmetric(horizontal: 20),
                                                                          child:
                                                                              Row(
                                                                            mainAxisAlignment:
                                                                                MainAxisAlignment.spaceBetween,
                                                                            children: [
                                                                              Column(
                                                                                mainAxisAlignment: MainAxisAlignment.start,
                                                                                crossAxisAlignment: CrossAxisAlignment.start,
                                                                                children: [
                                                                                  Text(getTranslated(context, AppString.date_and_time).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                  Row(
                                                                                    children: [
                                                                                      Text("$date", style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                      Container(
                                                                                        margin: EdgeInsets.only(left: 5),
                                                                                        child: Text(pastAppointmentReq[index].time!, style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                      ),
                                                                                    ],
                                                                                  ),
                                                                                ],
                                                                              ),
                                                                              Container(
                                                                                child: Column(
                                                                                  mainAxisAlignment: MainAxisAlignment.start,
                                                                                  crossAxisAlignment: CrossAxisAlignment.end,
                                                                                  children: [
                                                                                    Text(getTranslated(context, AppString.doctor_name).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                    Container(
                                                                                      margin: EdgeInsets.only(),
                                                                                      child: Text(pastAppointmentReq[index].doctorName!, style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                    ),
                                                                                  ],
                                                                                ),
                                                                              ),
                                                                            ],
                                                                          ),
                                                                        ),
                                                                        Divider(
                                                                          color:
                                                                              divider,
                                                                        ),
                                                                        Container(
                                                                          margin:
                                                                              EdgeInsets.symmetric(horizontal: 20),
                                                                          child:
                                                                              Column(
                                                                            children: [
                                                                              Row(
                                                                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                                crossAxisAlignment: CrossAxisAlignment.end,
                                                                                children: [
                                                                                  Text(getTranslated(context, AppString.hospital_name_heading).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                  Text(getTranslated(context, AppString.hospital_address).toString(), style: TextStyle(fontSize: 14, color: passwordVisibility)),
                                                                                ],
                                                                              ),
                                                                              Row(
                                                                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                                children: [
                                                                                  pastAppointmentReq[index].hospital != null
                                                                                      ? Container(
                                                                                          width: 120,
                                                                                          child: Text(pastAppointmentReq[index].hospital!.name!, style: TextStyle(fontSize: 14, color: hintColor), overflow: TextOverflow.ellipsis, maxLines: 2),
                                                                                        )
                                                                                      : Text('', style: TextStyle(fontSize: 14, color: hintColor)),
                                                                                  pastAppointmentReq[index].hospital != null
                                                                                      ? Container(
                                                                                          width: 100,
                                                                                          child: Text(pastAppointmentReq[index].hospital!.address!, style: TextStyle(fontSize: 14, color: hintColor), overflow: TextOverflow.ellipsis, maxLines: 2),
                                                                                        )
                                                                                      : Text(''),
                                                                                ],
                                                                              ),
                                                                              SizedBox(height: 5)
                                                                            ],
                                                                          ),
                                                                        ),
                                                                                                                                                    ],
                                                                                                                                                  ), 
                                                                                                                                                  ), 
                                                                                                                                                  ), 
                                                                                                                                                  );
                                                                          },
                                                                        ),
                                          ],
                                        ),
                                      ),
                                    ],
                                    ],
                                  ), 
                                  ), 
                                  ), 
                                  );
                        } else {
                          return Center(
                            child: CircularProgressIndicator(
                              color: AyurezeTheme.forestDeep,
                            ),
                            ],
                          ), 
                          ), 
                          ), 
                          );
                        }
                      }),
                ),
              ),
            ),
          );
  }

  Future<BaseModel<AppointmentHistory>> appointmentHistoryScreen() async {
    AppointmentHistory response;
    try {
      pastAppointmentReq.clear();
      upcomingAppointmentReq.clear();
      _pastData.clear();
      _userDetails.clear();
      response = await RestClient(await RetroApi().dioData(context))
          .appointmentHistoryScreenRequest();
      setState(() {
        pastAppointmentReq.addAll(response.data!.pastAppointment!);
        upcomingAppointmentReq.addAll(response.data!.upcomingAppointment!);
        _userDetails.addAll(response.data!.upcomingAppointment!);
        _pastData.addAll(response.data!.pastAppointment!);
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<void> logoutUser() async {
    SharedPreferenceHelper.clearPref();
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (BuildContext context) => SignIn()),
      ModalRoute.withName('SignIn'),
    );
  }

  showAlertDialog(BuildContext context) {
    // set up the button
    Widget cancel = TextButton(
      child: Text(
        getTranslated(context, AppString.cancel_button).toString(),
        style: TextStyle(color: hintColor),
      ),
      onPressed: () {
        Navigator.pop(context);
      },
    );

    Widget okButton = TextButton(
      child: Text(
        getTranslated(context, AppString.logout_button).toString(),
        style: TextStyle(color: hintColor),
      ),
      onPressed: () {
        CommonFunction.checkNetwork().then((value) {
          if (value == true) {
            logoutUser();
          }
        });
      },
    );

    // set up the AlertDialog
    AlertDialog alert = AlertDialog(
      content: Text(
          getTranslated(context, AppString.are_you_sure_logout).toString()),
      actions: [cancel, okButton],
    );
    // show the dialog
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return alert;
      },
    );
  }

  onSearchTextChanged(String text) async {
    _searchResult.clear();
    _pastSearch.clear();
    if (text.isEmpty) {
      setState(() {});
      return;
    }

    final isUpcomingTab = _tabController?.index == 0;
    if (isUpcomingTab) {
      _userDetails.forEach((upcomingAppointment) {
        if ((upcomingAppointment.patientName ?? "")
            .toLowerCase()
            .contains(text.toLowerCase()))
          _searchResult.add(upcomingAppointment);
      });
    } else {
      _pastData.forEach((pastAppointment) {
        if ((pastAppointment.patientName ?? "")
            .toLowerCase()
            .contains(text.toLowerCase())) _pastSearch.add(pastAppointment);
      });
    }

    setState(() {});
  }
}
