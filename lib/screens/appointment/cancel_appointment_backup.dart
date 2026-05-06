import 'dart:async';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/common_function.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/CancelAppointment.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/auth/SignIn.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:doctro/widgets/modern_drawer.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:intl/intl.dart';

class CancelAppointmentScreen extends StatefulWidget {
  @override
  _CancelAppointmentScreen createState() => _CancelAppointmentScreen();
}

class _CancelAppointmentScreen extends State<CancelAppointmentScreen> {
  //Set Loader
  Future? cancelAppointment;

  //Set Height/Width Using MediaQuery
  late double width;
  late double height;

  //get preferences
  String? dName;

  String? dFullImage;

  String? phone;
  int? subscription;

  //Search view
  TextEditingController _search = TextEditingController();
  List<AppointmentCancel> _searchResult = [];
  List<AppointmentCancel> _userCancel = [];



  @override
  void initState() {
    super.initState();
    Future.delayed(Duration.zero, () {
      cancelAppointment = cancelAppointmentRequest();
      dName = SharedPreferenceHelper.getString(Preferences.name);
      dFullImage = SharedPreferenceHelper.getString(Preferences.image);
      phone = SharedPreferenceHelper.getString(Preferences.phone_no);
      subscription =
          SharedPreferenceHelper.getInt(Preferences.subscription_status);
    });
  }

  List<AppointmentCancel> cancelAppointmentReq = [];

  //Set Open Drawer
  final _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) return;
        Navigator.pushNamedAndRemoveUntil(
            context, 'loginHome', (route) => false);
      },
      child: RefreshIndicator(
        onRefresh: cancelAppointmentRequest,
        child: Scaffold( backgroundColor: AyurezeTheme.canvas,
          key: _scaffoldKey,
          drawer: const ModernDrawer(),
          appBar: PreferredSize(
              preferredSize: Size(20, 150),
              child: SafeArea(
                  top: true,
                  child: Column(children: [
                    Column(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          margin: EdgeInsets.only(
                              left: width * 0.06,
                              right: width * 0.06,
                              top: height * 0.01),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Container(
                                    child: Text(
                                      getTranslated(
                                              context,
                                              AppString
                                                  .cancel_appointment_heading)
                                          .toString(),
                                       style: TextStyle(
                                           fontSize: width * 0.05,
                                           color: AyurezeTheme.textPrimary),
                                    ),
                                  ),
                                ],
                              ),
                              Container(
                                margin: EdgeInsets.only(),
                                child: IconButton(
                                  onPressed: () {
                                    _scaffoldKey.currentState!.openDrawer();
                                  },
                                  icon: SvgPicture.asset(
                                    "assets/icons/dMenuBar.svg",
                                    height: 16.0,
                                    fit: BoxFit.fill,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    Container(
                      margin: EdgeInsets.only(top: height * 0.01),
                      padding: EdgeInsets.all(10),
                      child: Card(
                        color: AyurezeTheme.surface,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(30),
                        ),
                        child: Container(
                            alignment: AlignmentDirectional.center,
                            margin: EdgeInsets.only(
                                left: width * 0.05, right: width * 0.05),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                Container(
                                  // height: height * 0.06,
                                  width: width * 0.7,
                                  child: TextField(
                                    controller: _search,
                                    decoration: InputDecoration(
                                      border: InputBorder.none,
                                      hintText: getTranslated(
                                              context,
                                              AppString
                                                  .search_cancel_appointment)
                                          .toString(),
                                      hintStyle: TextStyle(
                                        fontSize: width * 0.045,
                                        color: AyurezeTheme.textSecondary.withOpacity(0.3),
                                      ),
                                    ),
                                    onChanged: onSearchTextChanged,
                                    textAlign: TextAlign.left,
                                  ),
                                ),
                                Container(
                                  child: SvgPicture.asset(
                                    'assets/icons/dSearch.svg',
                                    height: 20,
                                  ),
                                ),
                              ],
                            )),
                      ),
                    ),
                  ]))),
          body: FutureBuilder(
              future: cancelAppointment,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.done) {
                  return GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: () {
                      FocusScope.of(context).requestFocus(new FocusNode());
                    },
                    child: SingleChildScrollView(
                      physics: AlwaysScrollableScrollPhysics(),
                      child: Center(
                        child: Column(
                          children: [
                            cancelAppointmentReq.length == 0
                                ? Container(
                                    margin: EdgeInsets.only(top: height * 0.2),
                                    child: Container(
                                      child: Image.asset(
                                          "assets/images/no-data.png"),
                                    ),
                                  )
                                : Container(
                                    color: AyurezeTheme.surfaceMuted,
                                    width: width * 1.0,
                                    padding: EdgeInsets.all(15),
                                    child: Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.spaceBetween,
                                      children: [
                                        Container(
                                          margin: EdgeInsets.symmetric(
                                              horizontal: width * 0.04),
                                          child: Text(
                                            getTranslated(
                                                    context,
                                                    AppString
                                                        .cancel_appointment_heading)
                                                .toString(),
                                            style: TextStyle(
                                                fontSize: 16, color: AyurezeTheme.textPrimary),
                                          ),
                                        ),
                                        Text(
                                          getTranslated(
                                                      context,
                                                      AppString
                                                          .cancel_appointment_length)
                                                  .toString() +
                                              " ${cancelAppointmentReq.length} ",
                                          style: TextStyle(
                                              fontSize: 13,
                                              color: passwordVisibility),
                                        ),
                                      ],
                                    ),
                                  ),
                            _search.text.isNotEmpty
                                ? _searchResult.length > 0
                                    ? ListView.builder(
                                        scrollDirection: Axis.vertical,
                                        shrinkWrap: true,
                                        physics: NeverScrollableScrollPhysics(),
                                        itemCount: _searchResult.length,
                                        itemBuilder: (context, i) {
                                          return Column(
                                            children: [
                                              Row(
                                                children: [
                                                  Column(
                                                    children: [
                                                      Container(
                                                        margin: EdgeInsets.only(
                                                            left: width * 0.06,
                                                            right:
                                                                width * 0.02),
                                                        child: Text(
                                                           DateUtil().formattedDate(
                                                               DateTime.parse(
                                                                   _searchResult[
                                                                           i]
                                                                       .date!)),
                                                           style: TextStyle(
                                                               fontSize: 14,
                                                               color:
                                                                   AyurezeTheme.forestDeep),
                                                        ),
                                                      ),
                                                      Container(
                                                        margin: EdgeInsets.only(
                                                            left: width * 0.06,
                                                            right:
                                                                width * 0.02),
                                                        child: Text(
                                                           _searchResult[i]
                                                               .time!,
                                                           style: TextStyle(
                                                               fontSize: 14,
                                                               color:
                                                                   AyurezeTheme.forestDeep),
                                                        ),
                                                      )
                                                    ],
                                                  ),
                                                  Expanded(
                                                    child: Container(
                                                        margin: EdgeInsets.only(
                                                            left: width * 0.02,
                                                            right:
                                                                width * 0.02),
                                                        height: 100,
                                                        child: Card(
                                                            shape:
                                                                RoundedRectangleBorder(
                                                              borderRadius:
                                                                  BorderRadius
                                                                      .circular(
                                                                          15.0),
                                                            ),
                                                            child: Column(
                                                                children: <Widget>[
                                                                  Container(
                                                                    child:
                                                                        ListTile(
                                                                      isThreeLine:
                                                                          true,
                                                                      leading:
                                                                          SizedBox(
                                                                        height:
                                                                            70,
                                                                        width:
                                                                            60,
                                                                        child:
                                                                            ClipRRect(
                                                                          borderRadius:
                                                                              BorderRadius.circular(10),
                                                                          child:
                                                                              Container(decoration: new BoxDecoration(image: new DecorationImage(fit: BoxFit.fitHeight, image: NetworkImage(_searchResult[i].user!.fullImage!)))),
                                                                        ),
                                                                      ),
                                                                      title:
                                                                          Container(
                                                                        alignment:
                                                                            AlignmentDirectional.topStart,
                                                                        margin:
                                                                            EdgeInsets.only(
                                                                          top: height *
                                                                              0.01,
                                                                        ),
                                                                        child:
                                                                            Text(
                                                                          _searchResult[i]
                                                                              .patientName!,
                                                                          style:
                                                                              TextStyle(fontSize: 16.0),
                                                                          overflow:
                                                                              TextOverflow.ellipsis,
                                                                          maxLines:
                                                                              1,
                                                                        ),
                                                                      ),
                                                                      trailing:
                                                                          Container(
                                                                              child: Text(
                                                                        SharedPreferenceHelper.getString(Preferences.currency_symbol) +
                                                                            _searchResult[i].amount.toString(),
                                                                        style: TextStyle(
                                                                            fontSize:
                                                                                16,
                                                                            color:
                                                                                hintColor),
                                                                      )),
                                                                      subtitle:
                                                                          Column(
                                                                        children: <Widget>[
                                                                          Container(
                                                                              alignment: AlignmentDirectional.topStart,
                                                                              child: Text(
                                                                                getTranslated(context, AppString.home_age_data).toString() + ":" + _searchResult[i].age.toString(),
                                                                                style: TextStyle(fontSize: 12, color: hintColor),
                                                                              )),
                                                                          Container(
                                                                            width:
                                                                                width * 0.6,
                                                                            alignment:
                                                                                AlignmentDirectional.topStart,
                                                                            child:
                                                                                Text(
                                                                              _searchResult[i].patientAddress!,
                                                                              style: TextStyle(fontSize: 12, color: passwordVisibility),
                                                                              overflow: TextOverflow.ellipsis,
                                                                              maxLines: 2,
                                                                            ),
                                                                          ),
                                                                        ],
                                                                      ),
                                                                    ),
                                                                  )
                                                                ]))),
                                                  ),
                                                ],
                                              ),
                                            ],
                                          );
                                        },
                                      )
                                    : Container(
                                        height: height / 1.5,
                                        child: Center(
                                            child: Container(
                                          margin: EdgeInsets.only(
                                              top: height * 0.02),
                                          child: Text(getTranslated(context,
                                                  AppString.result_not_found)
                                              .toString()),
                                        )))
                                : ListView.builder(
                                    itemCount: cancelAppointmentReq.length,
                                    physics: NeverScrollableScrollPhysics(),
                                    shrinkWrap: true,
                                    reverse: true,
                                    scrollDirection: Axis.vertical,
                                    itemBuilder: (context, index) {
                                      return Column(
                                        children: [
                                          Row(
                                            children: [
                                              Column(
                                                children: [
                                                  Container(
                                                    margin: EdgeInsets.only(
                                                        left: width * 0.06,
                                                        right: width * 0.02),
                                                    child: Text(
                                                      DateUtil().formattedDate(
                                                          DateTime.parse(
                                                              cancelAppointmentReq[
                                                                      index]
                                                                  .date!)),
                                                      style: TextStyle(
                                                          fontSize: 14,
                                                          color:
                                                              passwordVisibility),
                                                    ),
                                                  ),
                                                  Container(
                                                    margin: EdgeInsets.only(
                                                        left: width * 0.06,
                                                        right: width * 0.02),
                                                    child: Text(
                                                      cancelAppointmentReq[
                                                              index]
                                                          .time!,
                                                      style: TextStyle(
                                                          fontSize: 14,
                                                          color:
                                                              passwordVisibility),
                                                    ),
                                                  )
                                                ],
                                              ),
                                              Expanded(
                                                child: Container(
                                                    margin: EdgeInsets.only(
                                                        left: width * 0.02,
                                                        right: width * 0.02),
                                                    height: 100,
                                                    child: Card(
                                                        shape:
                                                            RoundedRectangleBorder(
                                                          borderRadius:
                                                              BorderRadius
                                                                  .circular(
                                                                      15.0),
                                                        ),
                                                        child: Column(
                                                            children: <Widget>[
                                                              Container(
                                                                child: ListTile(
                                                                  isThreeLine:
                                                                      true,
                                                                  leading:
                                                                      SizedBox(
                                                                    height: 70,
                                                                    width: 60,
                                                                    child:
                                                                        ClipRRect(
                                                                      borderRadius:
                                                                          BorderRadius.circular(
                                                                              10),
                                                                      child: Container(
                                                                          decoration:
                                                                              new BoxDecoration(image: new DecorationImage(fit: BoxFit.fitHeight, image: NetworkImage(cancelAppointmentReq[index].user!.fullImage!)))),
                                                                    ),
                                                                  ),
                                                                  title:
                                                                      Container(
                                                                    alignment:
                                                                        AlignmentDirectional
                                                                            .topStart,
                                                                    margin:
                                                                        EdgeInsets
                                                                            .only(
                                                                      top: height *
                                                                          0.01,
                                                                    ),
                                                                    child: Text(
                                                                        cancelAppointmentReq[index]
                                                                            .patientName!,
                                                                        style: TextStyle(
                                                                            fontSize:
                                                                                16.0),
                                                                        overflow:
                                                                            TextOverflow
                                                                                .ellipsis,
                                                                        maxLines:
                                                                            1),
                                                                  ),
                                                                  trailing:
                                                                      Container(
                                                                          child:
                                                                              Text(
                                                                    SharedPreferenceHelper.getString(Preferences
                                                                            .currency_symbol) +
                                                                        cancelAppointmentReq[index]
                                                                            .amount
                                                                            .toString(),
                                                                    style: TextStyle(
                                                                        fontSize:
                                                                            16,
                                                                        color:
                                                                            hintColor),
                                                                  )),
                                                                  subtitle:
                                                                      Column(
                                                                    children: <Widget>[
                                                                      Container(
                                                                          alignment: AlignmentDirectional
                                                                              .topStart,
                                                                          child:
                                                                              Text(
                                                                            getTranslated(context, AppString.home_age_data).toString() +
                                                                                ":" +
                                                                                cancelAppointmentReq[index].age.toString(),
                                                                            style:
                                                                                TextStyle(fontSize: 12, color: hintColor),
                                                                          )),
                                                                      Container(
                                                                        width: width *
                                                                            0.6,
                                                                        alignment:
                                                                            AlignmentDirectional.topStart,
                                                                        child:
                                                                            Text(
                                                                          cancelAppointmentReq[index]
                                                                              .patientAddress!,
                                                                          style: TextStyle(
                                                                              fontSize: 12,
                                                                              color: passwordVisibility),
                                                                          overflow:
                                                                              TextOverflow.ellipsis,
                                                                          maxLines:
                                                                              2,
                                                                        ),
                                                                      ),
                                                                    ],
                                                                  ),
                                                                ),
                                                              )
                                                            ]))),
                                              ),
                                            ],
                                          ),
                                        ],
                                      );
                                    }),
                          ],
                        ),
                      ),
                    ),
                  );
                } else {
                  return Center(child: CircularProgressIndicator());
                }
              }),
        ),
      ),
    );
  }


  Future<BaseModel<CancelAppointment>> cancelAppointmentRequest() async {
    CancelAppointment response;
    try {
      cancelAppointmentReq.clear();
      _userCancel.clear();
      response = await RestClient(await RetroApi().dioData(context))
          .cancelAppointmentRequest();
      setState(() {
        cancelAppointmentReq.addAll(response.data!);
        _userCancel.addAll(response.data!);
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }


  onSearchTextChanged(String text) async {
    _searchResult.clear();
    if (text.isEmpty) {
      setState(() {});
      return;
    }
    cancelAppointmentReq.forEach((cancelAppointmentData) {
      if ((cancelAppointmentData.patientName ?? "")
          .toLowerCase()
          .contains(text.toLowerCase())) {
        _searchResult.add(cancelAppointmentData);
      }
    });
    setState(() {});
  }
}

class DateUtil {
  static const DATE_FORMAT = 'dd-MM-yyyy';

  String formattedDate(DateTime dateTime) {
    return DateFormat(DATE_FORMAT).format(dateTime);
  }
}
