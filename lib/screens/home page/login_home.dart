import 'dart:async';

import 'package:cached_network_image/cached_network_image.dart';
// import 'package:onesignal_flutter/onesignal_flutter.dart';
import 'package:doctro/chat/constants/firestore_constants.dart';
import 'package:doctro/chat/pages/chat_page.dart';
import 'package:doctro/chat/providers/auth_provider.dart' as provider;
import 'package:doctro/chat/providers/home_provider.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/today_appointment.dart';
import 'package:doctro/model/payment.dart';
import 'package:doctro/model/review.dart';

import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/auth/SignIn.dart';
import 'package:doctro/screens/home%20page/patient_information.dart';
import 'package:doctro/screens/subscription/Subscription.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:doctro/screens/astra/astra_ai_chat_screen.dart';
import 'package:doctro/screens/auth/professional_registration_screen.dart';
import 'package:doctro/widgets/modern_drawer.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../../model/setting.dart';

class LoginHomeScreen extends StatefulWidget {
  final String? chat;

  LoginHomeScreen({
    this.chat,
  });

  @override
  _LoginHomeScreenState createState() => _LoginHomeScreenState();
}

class _LoginHomeScreenState extends State<LoginHomeScreen> with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;
  var appointment;

  //Set Loader
  Future? todayAppointment;
  Timer? timer;

  //Set Open Drawer
  final GlobalKey<ScaffoldState> _scaffoldKey = new GlobalKey<ScaffoldState>();

  //Set Preferences Data
  String? dName;
  String? dFullImage;
  int? isFilled;
  int? subscription;
  String? phone;

  late HomeProvider homeProvider;
  late provider.AuthProvider authProvider;

  String messageImage = '';
  String messageName = '';
  String messageId = '';
  String token = '';
  String userToken = '';

  //Search Data
  TextEditingController _search = TextEditingController();
  List<Today> _searchResult = [];
  List<Tomorrow> _tomorrowSearchResult = [];
  List<Upcoming> _upcomingSearchResult = [];


  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
  }

  @override
  void initState() {
    super.initState();
    
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);
    
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.15).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _initializeData();
  }

  void _initializeData() {
    _initializeAuthAndMessage();
  }
  
  void _initializeAuthAndMessage() {
    Future.delayed(Duration.zero, () async {
      final isLoggedIn = SharedPreferenceHelper.getBoolean(Preferences.is_logged_in);
      
      if (isLoggedIn) {
        settingRequest();
        todayAppointment = todayAppointmentsFunction();
      }
      
      dName = SharedPreferenceHelper.getString(Preferences.name);
      dFullImage = SharedPreferenceHelper.getString(Preferences.image);
      isFilled = SharedPreferenceHelper.getInt(Preferences.is_filled);
      subscription = SharedPreferenceHelper.getInt(Preferences.subscription_status);
      phone = SharedPreferenceHelper.getString(Preferences.phone_no);
    });
    
    Future.delayed(const Duration(seconds: 5), () {
      if (FirebaseAuth.instance.currentUser != null) {
        homeProvider.updateDataFirestore(FirestoreConstants.pathUserCollection,
            FirebaseAuth.instance.currentUser!.uid, {
          'pushToken': SharedPreferenceHelper.getString(Preferences.messageToken)
        });
      }
    });

    FirebaseMessaging.instance.getInitialMessage().then((RemoteMessage? message) {
      if (message != null) {
        Map<String, dynamic> dataValue = message.data;
        messageImage = dataValue['userImage'].toString();
        messageName = dataValue['userName'].toString();
        messageId = dataValue['userId'].toString();
        userToken = dataValue['userToken'].toString();

        if (widget.chat == "") {
          if (SharedPreferenceHelper.getString(Preferences.email).isNotEmpty) {
            Navigator.of(context).pushReplacement(MaterialPageRoute(
                builder: (context) => ChatPage(
                      peerNickname: messageName,
                      peerAvatar: messageImage,
                      peerId: messageId,
                      token: userToken,
                      isNavigate: '',
                    )));
          } else {
            Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => SignIn()));
          }
        }
      }
    });

    authProvider = Provider.of<provider.AuthProvider>(context, listen: false);
    homeProvider = Provider.of<HomeProvider>(context, listen: false);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  //Set Double Tap to exit value //
  DateTime? currentBackPressTime;

  //Set Double Tap exit //
  Future<bool> onWillPop() {
    DateTime now = DateTime.now();
    if (currentBackPressTime == null ||
        now.difference(currentBackPressTime!) > Duration(seconds: 2)) {
      currentBackPressTime = now;
      Fluttertoast.showToast(
          gravity: ToastGravity.BOTTOM,
          msg: getTranslated(context, AppString.tap_again_to_exit_app)
              .toString());
      return Future.value(false);
    }
    return Future.value(true);
  }

  // Add List Data //
  List<Today> todayAppointments = [];
  List<Tomorrow> tomorrowAppointments = [];
  List<Upcoming> upcomingAppointments = [];
  double totalEarnings = 0;
  int reviewCount = 0;
  int patientCount = 0;

  bool todayView = false;
  bool tomorrowView = false;
  bool upcomingView = false;

  // Set MediaQuery Size //
  late double width;
  late double height;

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return WillPopScope(
      onWillPop: onWillPop,
      child: Scaffold(
        key: _scaffoldKey,
        backgroundColor: Color(0xFFF8F9FE),
        drawer: const ModernDrawer(),
        appBar: AppBar(
          backgroundColor: Color(0xFFF8F9FE),
          elevation: 0,
          leading: IconButton(
            icon: SvgPicture.asset("assets/icons/dMenuBar.svg", height: 18, color: purple),
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
                      image: NetworkImage(dFullImage ?? "https://via.placeholder.com/150"),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
        body: RefreshIndicator(
          onRefresh: todayAppointmentsFunction,
          color: purple,
          child: SingleChildScrollView(
            physics: AlwaysScrollableScrollPhysics(),
            padding: EdgeInsets.symmetric(horizontal: 20),
            child: FutureBuilder(
                future: todayAppointment,
                builder: (context, snapshot) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildWelcomeHeader(),
                      SizedBox(height: 25),
                      _buildStatsGrid(),
                      SizedBox(height: 25),
                      _buildQuickActions(),
                      SizedBox(height: 25),
                      _buildSectionTitle(getTranslated(context, AppString.home_title).toString(), todayAppointments.length),
                      SizedBox(height: 15),
                      _buildAppointmentList(snapshot.connectionState == ConnectionState.waiting),
                      SizedBox(height: 30),
                    ],
                  );
                }),
          ),
        ),
        floatingActionButton: ScaleTransition(
          scale: _pulseAnimation,
          child: FloatingActionButton.extended(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const AstraAIChatScreen()),
              );
            },
            label: const Text("Astra AI", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
            icon: const Icon(Icons.psychology_outlined, color: Colors.white),
            backgroundColor: purple,
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeHeader() {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [purple, Color(0xFF9C27B0)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(color: purple.withOpacity(0.3), blurRadius: 15, offset: Offset(0, 8)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Hello, Dr. ${dName?.split(' ').first ?? 'Doctor'}",
            style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 5),
          Text(
            "You have ${todayAppointments.length} appointments scheduled for today.",
            style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsGrid() {
    double totalRevenue = 0;
    todayAppointments.forEach((a) => totalRevenue += (double.tryParse(a.amount.toString()) ?? 0));

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: NeverScrollableScrollPhysics(),
      crossAxisSpacing: 15,
      mainAxisSpacing: 15,
      childAspectRatio: 1.6,
      children: [
        _buildStatCard(getTranslated(context, AppString.dashboard_today_appointments).toString(), todayAppointments.length.toString(), Icons.calendar_today, Colors.blue),
        _buildStatCard(getTranslated(context, AppString.dashboard_total_revenue).toString(), "₹${totalEarnings.toInt()}", Icons.account_balance_wallet, Colors.green),
        _buildStatCard(getTranslated(context, AppString.dashboard_active_patients).toString(), patientCount.toString(), Icons.people, Colors.orange),
        _buildStatCard(getTranslated(context, AppString.dashboard_feedbacks).toString(), reviewCount.toString(), Icons.star, Colors.red),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 10, offset: Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: EdgeInsets.all(6),
                decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                child: Icon(icon, size: 18, color: color),
              ),
              Icon(Icons.arrow_forward_ios, size: 12, color: Colors.grey[300]),
            ],
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: hintColor)),
              Text(title, style: TextStyle(fontSize: 12, color: Colors.grey)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(getTranslated(context, AppString.dashboard_quick_actions).toString(), style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: hintColor)),
        SizedBox(height: 15),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            _buildActionButton(getTranslated(context, AppString.drawer_schedule_timing).toString(), Icons.schedule, Colors.indigo, () => Navigator.pushNamed(context, 'Schedule Timings')),
            _buildActionButton(getTranslated(context, AppString.profile_personal_information).toString(), Icons.person_search, Colors.teal, () => Navigator.pushNamed(context, 'profile')),
            _buildActionButton(getTranslated(context, AppString.chats).toString(), Icons.chat_bubble_outline, Colors.cyan, () => Navigator.pushNamed(context, 'ChatHome')),
            _buildActionButton(getTranslated(context, AppString.drawer_setting).toString(), Icons.settings, Colors.blueGrey, () => Navigator.pushNamed(context, 'Settings')),
          ],
        ),
      ],
    );
  }

  Widget _buildActionButton(String label, IconData icon, Color color, VoidCallback onTap) {
    return Column(
      children: [
        GestureDetector(
          onTap: onTap,
          child: Container(
            width: 55,
            height: 55,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 24),
          ),
        ),
        SizedBox(height: 8),
        Text(label, style: TextStyle(fontSize: 12, color: hintColor)),
      ],
    );
  }

  Widget _buildSectionTitle(String title, int count) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: hintColor)),
        if (count > 0)
          Text("$count Active", style: TextStyle(fontSize: 12, color: purple, fontWeight: FontWeight.w600)),
      ],
    );
  }

  Widget _buildAppointmentList(bool isLoading) {
    if (isLoading) {
      return Center(child: CircularProgressIndicator(color: purple));
    }
    
    List<Widget> sections = [];
    
    // Today Section
    if (todayAppointments.isNotEmpty) {
      sections.add(_buildSectionHeader(getTranslated(context, AppString.today_appointment_heading).toString(), todayAppointments.length));
      sections.addAll(todayAppointments.take(5).map((app) => _buildAppointmentCard(app)));
    }
    
    // Tomorrow Section
    if (tomorrowAppointments.isNotEmpty) {
      sections.add(SizedBox(height: 20));
      sections.add(_buildSectionHeader(getTranslated(context, AppString.tomorrow_appointment).toString(), tomorrowAppointments.length));
      sections.addAll(tomorrowAppointments.take(3).map((app) => _buildAppointmentCard(app)));
    }
    
    // Upcoming Section
    if (upcomingAppointments.isNotEmpty) {
      sections.add(SizedBox(height: 20));
      sections.add(_buildSectionHeader(getTranslated(context, AppString.up_coming_appointment).toString(), upcomingAppointments.length));
      sections.addAll(upcomingAppointments.take(3).map((app) => _buildAppointmentCard(app)));
    }

    if (sections.isEmpty) {
      return Container(
        height: 150,
        width: double.infinity,
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20)),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset("assets/images/no-data.png", height: 80),
            SizedBox(height: 10),
            Text(getTranslated(context, AppString.no_user).toString(), style: TextStyle(color: Colors.grey)),
          ],
        ),
      );
    }
    
    return Column(children: sections);
  }

  Widget _buildSectionHeader(String title, int count) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: hintColor)),
          Text("${getTranslated(context, AppString.view_more).toString()} ($count)", style: TextStyle(fontSize: 12, color: purple)),
        ],
      ),
    );
  }

  Widget _buildAppointmentCard(dynamic app) {
    return GestureDetector(
      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => patientDetailsScreen(id: app.id))),
      child: Container(
        margin: EdgeInsets.only(bottom: 12),
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10, offset: Offset(0, 4)),
          ],
        ),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(15),
              child: CachedNetworkImage(
                imageUrl: app.user?.fullImage ?? "",
                width: 50,
                height: 50,
                fit: BoxFit.cover,
                errorWidget: (context, url, error) => Container(color: Colors.grey[100], child: Icon(Icons.person, color: Colors.grey)),
              ),
            ),
            SizedBox(width: 15),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(app.patientName ?? "Patient", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: hintColor)),
                  Text(app.time ?? "", style: TextStyle(color: Colors.grey, fontSize: 13)),
                ],
              ),
            ),
            Icon(Icons.chevron_right, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }


  Future<BaseModel<TodayAppointment>> todayAppointmentsFunction() async {
    TodayAppointment response;

    try {
      todayAppointments.clear();
      tomorrowAppointments.clear();
      upcomingAppointments.clear();
      totalEarnings = 0;

      final client = RestClient(await RetroApi().dioData(context));
      
      final futures = await Future.wait([
        client.todayAppointments(),
        client.paymentRequest().catchError((_) => Payment(success: false, paymentData: [])),
        client.reviewRequest().catchError((_) => Review(success: false, data: [])),
      ]);

      response = futures[0] as TodayAppointment;
      final payments = futures[1] as Payment;
      final reviews = futures[2] as Review;

      if (payments.paymentData != null) {
        for (var p in payments.paymentData!) {
          totalEarnings += double.tryParse(p.amount.toString()) ?? 0;
        }
      }

      if (reviews.data != null) {
        reviewCount = reviews.data!.length;
      }

      setState(() {
        if (response.data!.today!.isNotEmpty) {
          response.data!.today!.sort((a, b) => DateFormat("yyyy-MM-dd h:mm a")
              .parse(DateTime.now().toString().split(" ")[0] +
                  " " +
                  (a.time ?? "00:00 AM").toUpperCase())
              .compareTo(DateFormat("yyyy-MM-dd h:mm a").parse(
                  DateTime.now().toString().split(" ")[0] +
                      " " +
                      (b.time ?? "00:00 AM").toUpperCase())));
          todayAppointments.addAll(response.data!.today!);
        }

        if (response.data!.tomorrow!.isNotEmpty) {
          response.data!.tomorrow!.sort((a, b) => DateFormat("yyyy-MM-dd h:mm a")
              .parse(DateTime.now().toString().split(" ")[0] +
                  " " +
                  (a.time ?? "00:00 AM").toUpperCase())
              .compareTo(DateFormat("yyyy-MM-dd h:mm a").parse(
                  DateTime.now().toString().split(" ")[0] +
                      " " +
                      (b.time ?? "00:00 AM").toUpperCase())));
          tomorrowAppointments.addAll(response.data!.tomorrow!);
        }

        if (response.data!.upcoming!.isNotEmpty) {
          response.data!.upcoming!.sort((a, b) => DateFormat("yyyy-MM-dd h:mm a")
              .parse(DateTime.now().toString().split(" ")[0] +
                  " " +
                  (a.time ?? "00:00 AM").toUpperCase())
              .compareTo(DateFormat("yyyy-MM-dd h:mm a").parse(
                  DateTime.now().toString().split(" ")[0] +
                      " " +
                      (b.time ?? "00:00 AM").toUpperCase())));
          upcomingAppointments.addAll(response.data!.upcoming!);
        }

        // Simple way to estimate active patients: unique patient names across all categories
        Set<String> uniquePatients = {};
        todayAppointments.forEach((a) { if (a.patientName != null) uniquePatients.add(a.patientName!); });
        tomorrowAppointments.forEach((a) { if (a.patientName != null) uniquePatients.add(a.patientName!); });
        upcomingAppointments.forEach((a) { if (a.patientName != null) uniquePatients.add(a.patientName!); });
        patientCount = uniquePatients.length;
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }


  Widget dialog() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: width * 0.1),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(1.0),
        borderRadius: BorderRadius.circular(40),
      ),
      width: width * 0.8,
      child: Container(
        height: 280,
        child: Align(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                height: width * 0.15,
                child: SizedBox.expand(
                  child: Image.asset(
                    'assets/images/alert.png',
                  ),
                ),
              ),
              SizedBox(
                height: 10,
              ),
              Container(
                  child: Text(
                getTranslated(context, AppString.home_subscription_deActive)
                    .toString(),
                style: TextStyle(
                    fontSize: 20,
                    color: hintColor,
                    decoration: TextDecoration.none),
                textAlign: TextAlign.center,
              )),
              GestureDetector(
                onTap: () {
                  SubSubscription();
                },
                child: Container(
                    margin: EdgeInsets.only(top: height * 0.02),
                    child: Text(
                      getTranslated(context, AppString.home_please_active_plan)
                          .toString(),
                      style: TextStyle(
                          fontSize: 14,
                          color: darkGrey,
                          decoration: TextDecoration.none),
                      textAlign: TextAlign.center,
                    )),
              ),
              SizedBox(
                height: 10,
              ),
              Container(
                  margin: EdgeInsets.only(left: 12, right: 12),
                  child: ElevatedButton(
                      onPressed: () => Navigator.pushReplacementNamed(
                          context, "subscription"),
                      child: Text(getTranslated(
                              context, AppString.home_activate_subscription)
                          .toString())))
            ],
          ),
        ),
      ),
    );
  }

  // Future<void> getOneSingleToken() async {
  //   try {
  //     OneSignal.Notifications.addClickListener((event) async {
  //       if (event.result.actionId == "") {
  //       } else if (event.result.actionId == "decline") {
  //         setState(() {
  //           Navigator.push(
  //             context,
  //             MaterialPageRoute(
  //               builder: (context) => VideoCall(
  //                 callEnd: true,
  //                 id: event.notification.additionalData!["id"],
  //               ),
  //             ),
  //           );
  //         });
  //
  //         setState(() {});
  //       } else if (event.result.actionId == "accept") {
  //         Navigator.push(
  //           context,
  //           MaterialPageRoute(
  //             builder: (context) => VideoCall(
  //               callEnd: false,
  //               id: event.notification.additionalData!["id"],
  //             ),
  //           ),
  //         );
  //       } else {
  //         Navigator.pushReplacement(
  //           context,
  //           MaterialPageRoute(
  //               builder: (context) =>
  //                   PhoneScreen(event.notification.additionalData)),
  //         );
  //       }
  //     });
  //   } catch (error) {
  //     // print(error);
  //   }
  // }


  onSearchTextChanged(String text) async {
    _searchResult.clear();
    _tomorrowSearchResult.clear();
    _upcomingSearchResult.clear();
    if (text.isEmpty) {
      setState(() {});
      return;
    }

    todayAppointments.forEach((appointmentData) {
      if ((appointmentData.patientName ?? "")
          .toLowerCase()
          .contains(text.toLowerCase())) {
        _searchResult.add(appointmentData);
      }
    });

    tomorrowAppointments.forEach((tomorrowData) {
      if ((tomorrowData.patientName ?? "")
          .toLowerCase()
          .contains(text.toLowerCase())) {
        _tomorrowSearchResult.add(tomorrowData);
      }
    });
    upcomingAppointments.forEach((upcomingData) {
      if ((upcomingData.patientName ?? "")
          .toLowerCase()
          .contains(text.toLowerCase())) {
        _upcomingSearchResult.add(upcomingData);
      }
    });

    setState(() {});
  }

  Future<BaseModel<Setting>> settingRequest() async {
    Setting response;
    try {
      response =
          await RestClient(await RetroApi().dioData(context)).settingRequest();
      setState(() {
        if (response.data?.agoraAppId != null) {
          SharedPreferenceHelper.setString(
              Preferences.agoraAppId, response.data!.agoraAppId!);
        }
        if (SharedPreferenceHelper.getBoolean(Preferences.is_logged_in) ==
            true) {
          if (response.data!.stripeSecretKey != null) {
            SharedPreferenceHelper.setString(
                Preferences.stripeSecretKey, response.data!.stripeSecretKey!);
          }

          if (response.data!.stripePublicKey != null) {
            SharedPreferenceHelper.setString(
                Preferences.stripPublicKey, response.data!.stripePublicKey!);
          }

          if (response.data!.flutterwaveEncryptionKey != null) {
            SharedPreferenceHelper.setString(
                Preferences.flutterWave_encryption_key,
                response.data!.flutterwaveEncryptionKey!);
          }

          if (response.data!.flutterwaveKey != null) {
            SharedPreferenceHelper.setString(
                Preferences.flutterWave_key, response.data!.flutterwaveKey!);
          }

          if (response.data!.paystackPublicKey != null) {
            SharedPreferenceHelper.setString(Preferences.payStack_public_key,
                response.data!.paystackPublicKey!);
          }

          if (response.data!.razorKey != null) {
            SharedPreferenceHelper.setString(
                Preferences.razor_key, response.data!.razorKey!);
          }

          if (response.data!.paypalProducationKey != null) {
            SharedPreferenceHelper.setString(Preferences.payPal_production_key,
                response.data!.paypalProducationKey!);
          }

          if (response.data!.paypalSandboxKey != null) {
            SharedPreferenceHelper.setString(Preferences.payPal_sandbox_key,
                response.data!.paypalSandboxKey!);
          }

          if (response.data!.paypalClientId != null) {
            SharedPreferenceHelper.setString(
                Preferences.paypal_client_key, response.data!.paypalClientId!);
          }

          if (response.data!.paypalSecretKey != null) {
            SharedPreferenceHelper.setString(
                Preferences.paypal_secret_key, response.data!.paypalSecretKey!);
          }

          if (response.data!.currencySymbol != null) {
            SharedPreferenceHelper.setString(
                Preferences.currency_symbol, response.data!.currencySymbol!);
          }

          if (response.data!.currencyCode != null) {
            SharedPreferenceHelper.setString(
                Preferences.currency_code, response.data!.currencyCode!);
          }

          if (response.data!.doctorAppId != null) {
            setState(() {
              SharedPreferenceHelper.setString(
                  Preferences.doctorAppId, response.data!.doctorAppId!);
            });
          }
        }
      });
    } catch (error, stacktrace) {
      // print("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }
}
