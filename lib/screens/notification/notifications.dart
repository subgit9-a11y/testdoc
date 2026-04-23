import 'package:cached_network_image/cached_network_image.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/common_function.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/Notification.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/auth/SignIn.dart';
import 'package:flutter/material.dart';
import 'package:doctro/widgets/modern_drawer.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:intl/intl.dart';

class NotificationsScreen extends StatefulWidget {
  @override
  _NotificationsScreenState createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  //Set Drawer Open
  final _scaffoldKey = GlobalKey<ScaffoldState>();

  //Set Height/Width Using MediaQuery
  late double width;
  late double height;

  //Loader Data
  Future? loadData;

  //get preferences
  String? dName;
  String? dFullImage;
  String? phone;
  int? subscription;


  //Notification List
  List<NotificationData> patientNotification = [];


  @override
  void initState() {
    super.initState();
    Future.delayed(Duration.zero, () {
      loadData = bookNotifications();
      dName = SharedPreferenceHelper.getString(Preferences.name);
      dFullImage = SharedPreferenceHelper.getString(Preferences.image);
      phone = SharedPreferenceHelper.getString(Preferences.phone_no);
      subscription =
          SharedPreferenceHelper.getInt(Preferences.subscription_status);
    });
  }

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return Scaffold(
        key: _scaffoldKey,
        drawer: const ModernDrawer(),
        appBar: PreferredSize(
            preferredSize: Size(20, 60),
            child: SafeArea(
                top: true,
                child: Column(children: [
                  Container(
                    margin: EdgeInsets.only(
                        left: width * 0.04,
                        right: width * 0.04,
                        top: height * 0.01),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          child: IconButton(
                            onPressed: () {
                              Navigator.pop(context);
                            },
                            icon: Icon(Icons.arrow_back_ios),
                          ),
                        ),
                        Container(
                            child: Text(
                          getTranslated(context, AppString.notification_heading)
                              .toString(),
                          style: TextStyle(
                              fontSize: 18, fontWeight: FontWeight.w600),
                          textAlign: TextAlign.center,
                        )),
                        Container(
                          margin: EdgeInsets.only(),
                          child: IconButton(
                            onPressed: () {
                              _scaffoldKey.currentState!.openDrawer();
                            },
                            icon: SvgPicture.asset(
                              "assets/icons/dMenuBar.svg",
                              height: 16.0,
                              // width: 15.0,
                              fit: BoxFit.fill,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ]))),
        body: WillPopScope(
          onWillPop: () {
            Navigator.pushNamedAndRemoveUntil(
                context, 'loginHome', (route) => false);
            return Future<bool>.value(false);
          },
          child: RefreshIndicator(
            onRefresh: bookNotifications,
            child: FutureBuilder(
              future: loadData,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.done) {
                  return SingleChildScrollView(
                    physics: AlwaysScrollableScrollPhysics(),
                    scrollDirection: Axis.vertical,
                    child: Center(
                      child: patientNotification.length == 0
                          ? Center(
                              child: Container(
                                margin: EdgeInsets.only(top: height * 0.3),
                                child: Container(
                                  child:
                                      Image.asset("assets/images/no-data.png"),
                                ),
                              ),
                            )
                          : Column(
                              children: [
                                ListView.builder(
                                    physics: NeverScrollableScrollPhysics(),
                                    shrinkWrap: true,
                                    reverse: true,
                                    itemCount: 6 < patientNotification.length
                                        ? 6
                                        : patientNotification.length,
                                    itemBuilder: (context, index) {
                                      String date = DateUtil().formattedDate(
                                          DateTime.parse(
                                              patientNotification[index]
                                                  .createdAt!));
                                      return InkWell(
                                        onTap: () {
                                          showDialog(
                                            context: context,
                                            builder: (context) =>
                                                new AlertDialog(
                                              content: Text(
                                                  patientNotification[index]
                                                      .message!),
                                              actions: [
                                                ElevatedButton(
                                                    onPressed: () {
                                                      Navigator.pop(context);
                                                    },
                                                    child: Text(getTranslated(
                                                            context,
                                                            AppString
                                                                .schedule_ok_button)
                                                        .toString()))
                                              ],
                                            ),
                                          );
                                        },
                                        child: Column(
                                          children: [
                                            Container(
                                                margin: EdgeInsets.only(
                                                    left: width * 0.02,
                                                    right: width * 0.02),
                                                child:
                                                    Column(children: <Widget>[
                                                  Container(
                                                    child: ListTile(
                                                      isThreeLine: true,
                                                      leading: SizedBox(
                                                        height: 70,
                                                        width: 60,
                                                        child: ClipRRect(
                                                          borderRadius:
                                                              BorderRadius
                                                                  .circular(10),
                                                          child: Container(
                                                              decoration: new BoxDecoration(
                                                                  image: new DecorationImage(
                                                                      fit: BoxFit
                                                                          .fitHeight,
                                                                      image: NetworkImage(patientNotification[
                                                                              index]
                                                                          .user!
                                                                          .fullImage!)))),
                                                        ),
                                                      ),
                                                      title: Row(
                                                        mainAxisAlignment:
                                                            MainAxisAlignment
                                                                .spaceBetween,
                                                        children: [
                                                          Container(
                                                            child: Text(
                                                                patientNotification[
                                                                        index]
                                                                    .user!
                                                                    .name!,
                                                                style: TextStyle(
                                                                    fontSize:
                                                                        16.0)),
                                                          ),
                                                          Container(
                                                              child: Text(
                                                            '$date',
                                                            style: TextStyle(
                                                                fontSize: 14,
                                                                color:
                                                                    passwordVisibility),
                                                          )),
                                                        ],
                                                      ),
                                                      subtitle: Container(
                                                        child: Text(
                                                          patientNotification[
                                                                  index]
                                                              .message!,
                                                          style: TextStyle(
                                                              fontSize: 13,
                                                              color:
                                                                  passwordVisibility),
                                                          maxLines: 2,
                                                          overflow: TextOverflow
                                                              .ellipsis,
                                                        ),
                                                      ),
                                                    ),
                                                  ),
                                                  Divider(
                                                    thickness: 2,
                                                    color: divider,
                                                  ),
                                                ])),
                                          ],
                                        ),
                                      );
                                    }),
                                patientNotification.length < 6
                                    ? Container()
                                    : GestureDetector(
                                        onTap: () => Navigator.pushNamed(
                                            context, "ViewAllNotification"),
                                        child: Container(
                                          margin: EdgeInsets.only(
                                              top: height * 0.02),
                                          alignment:
                                              AlignmentDirectional.centerStart,
                                          height: height * 0.07,
                                          width: width * 0.88,
                                          color: divider,
                                          child: Container(
                                            margin: EdgeInsets.only(
                                                left: width * 0.02,
                                                right: width * 0.02),
                                            child: Row(
                                              mainAxisAlignment:
                                                  MainAxisAlignment
                                                      .spaceBetween,
                                              children: [
                                                Text(
                                                  getTranslated(
                                                          context,
                                                          AppString
                                                              .notification_view_all)
                                                      .toString(),
                                                  style: TextStyle(
                                                      fontSize: 16,
                                                      fontWeight:
                                                          FontWeight.w500,
                                                      color: hintColor),
                                                ),
                                                Container(
                                                  margin: EdgeInsets.only(
                                                      right: width * 0.4),
                                                  child: SvgPicture.asset(
                                                    'assets/icons/longArrow.svg',
                                                    height: height * 0.012,
                                                  ),
                                                ),
                                                Text(
                                                  "${patientNotification.length}",
                                                  style: TextStyle(
                                                      fontSize: 16,
                                                      fontWeight:
                                                          FontWeight.w500,
                                                      color: hintColor),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ),
                                      ),
                              ],
                            ),
                    ),
                  );
                } else {
                  return Center(
                    child: CircularProgressIndicator(),
                  );
                }
              },
            ),
          ),
        ));
  }

  Future<BaseModel<Notifications>> bookNotifications() async {
    Notifications response;

    try {
      patientNotification.clear();
      response =
          await RestClient(await RetroApi().dioData(context)).notifications();
      setState(() {
        patientNotification.addAll(response.data!);
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }


}

class DateUtil {
  static const DATE_FORMAT = 'dd-MM-yyyy';

  String formattedDate(DateTime dateTime) {
    return DateFormat(DATE_FORMAT).format(dateTime);
  }
}
