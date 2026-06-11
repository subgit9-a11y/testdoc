import 'dart:async';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/appointment_history.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/auth/SignIn.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/widgets/modern_drawer.dart';
import 'package:doctro/widgets/osler_card.dart';
import 'package:doctro/widgets/osler_status_badge.dart';
import 'package:flutter/material.dart';

class AppointmentHistoryScreen extends StatefulWidget {
  @override
  _AppointmentHistoryScreenState createState() =>
      _AppointmentHistoryScreenState();
}

class _AppointmentHistoryScreenState extends State<AppointmentHistoryScreen>
    with TickerProviderStateMixin {
  Future? appointment;

  final _scaffoldKey = GlobalKey<ScaffoldState>();

  List<PastAppointment> pastAppointmentReq = [];
  List<UpcomingAppointment> upcomingAppointmentReq = [];

  TextEditingController _search = TextEditingController();
  List<UpcomingAppointment> _searchResult = [];
  List<UpcomingAppointment> _userDetails = [];
  List<PastAppointment> _pastSearch = [];
  List<PastAppointment> _pastData = [];
  bool? isShow;

  String? dName;
  String? dFullImage;
  String? phone;
  int? subscription;

  late double width;
  late double height;

  late TabController _tabController;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
  }

  @override
  void initState() {
    super.initState();
    _tabController = TabController(vsync: this, length: 2);
    _tabController.addListener(() {
      if (_tabController.indexIsChanging) {
        setState(() {
          if (isShow == null) {
            isShow = true;
            _searchResult.clear();
            _search.clear();
          } else {
            isShow = false;
            _pastSearch.clear();
            _search.clear();
          }
        });
      }
    });
    Future.delayed(Duration.zero, () {
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
    _tabController.dispose();
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: AyurezeTheme.canvas,
      drawer: const ModernDrawer(),
      appBar: AppBar(
        backgroundColor: AyurezeTheme.canvas,
        elevation: 0,
        iconTheme: IconThemeData(color: AyurezeTheme.iconPrimary),
        title: Text(
          getTranslated(context, AppString.appointment_history_heading)
              .toString(),
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w800,
            color: AyurezeTheme.textPrimary,
          ),
        ),
      ),
      body: PopScope(
        canPop: false,
        onPopInvokedWithResult: (didPop, result) {
          if (didPop) return;
          Navigator.pushNamedAndRemoveUntil(
              context, 'loginHome', (route) => false);
        },
        child: RefreshIndicator(
          onRefresh: appointmentHistoryScreen,
          color: AyurezeTheme.forestDeep,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: AyurezeTheme.screenPadding,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeroSummary(),
                const SizedBox(height: 18),
                _buildSearchCard(),
                const SizedBox(height: 18),
                _buildTabSwitch(),
                const SizedBox(height: 14),
                FutureBuilder(
                  future: appointment,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState != ConnectionState.done) {
                      return SizedBox(
                        height: height * 0.4,
                        child: const Center(
                          child: CircularProgressIndicator(),
                        ),
                      );
                    }
                    if (_tabController.index == 0) {
                      return _buildUpcomingList();
                    } else {
                      return _buildPastList();
                    }
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeroSummary() {
    final int upcomingCount = upcomingAppointmentReq.length;
    final int pastCount = pastAppointmentReq.length;
    final int total = upcomingCount + pastCount;

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
              "Appointment ledger",
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 14),
          Text(
            "$total total appointments",
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              height: 1.05,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              _buildPill("$upcomingCount upcoming", AyurezeTheme.healingGreen10),
              const SizedBox(width: 8),
              _buildPill("$pastCount past", Colors.white.withOpacity(0.18)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPill(String text, Color bg) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: bg == AyurezeTheme.healingGreen10
              ? AyurezeTheme.forestDeep
              : Colors.white,
          fontSize: 11,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }

  Widget _buildSearchCard() {
    return OslerCard(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Row(
        children: [
          Icon(AppIcons.search, size: 18, color: AyurezeTheme.textSecondary),
          const SizedBox(width: 10),
          Expanded(
            child: TextField(
              controller: _search,
              onChanged: onSearchTextChanged,
              decoration: InputDecoration(
                border: InputBorder.none,
                hintText: getTranslated(
                        context, AppString.search_appointment_history)
                    .toString(),
                hintStyle: TextStyle(
                  color: AyurezeTheme.textSecondary.withOpacity(0.6),
                  fontSize: 14,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabSwitch() {
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: AyurezeTheme.mutedPanelDecoration(),
      child: TabBar(
        controller: _tabController,
        labelColor: Colors.white,
        unselectedLabelColor: AyurezeTheme.textSecondary,
        indicator: BoxDecoration(
          color: AyurezeTheme.forestDeep,
          borderRadius: BorderRadius.circular(16),
        ),
        indicatorSize: TabBarIndicatorSize.tab,
        dividerColor: Colors.transparent,
        labelStyle: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w800,
        ),
        tabs: [
          Tab(text: getTranslated(context, AppString.upcoming_appointment).toString()),
          Tab(text: getTranslated(context, AppString.past_appointment).toString()),
        ],
      ),
    );
  }

  Widget _buildUpcomingList() {
    final list = _search.text.isNotEmpty
        ? _searchResult
        : upcomingAppointmentReq;
    if (list.isEmpty) {
      return _buildEmptyState("No upcoming appointments");
    }
    return Column(
      children: list
          .map((appt) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildUpcomingCard(appt),
              ))
          .toList(),
    );
  }

  Widget _buildPastList() {
    final list = _search.text.isNotEmpty ? _pastSearch : pastAppointmentReq;
    if (list.isEmpty) {
      return _buildEmptyState("No past appointments");
    }
    return Column(
      children: list
          .map((appt) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildPastCard(appt),
              ))
          .toList(),
    );
  }

  Widget _buildEmptyState(String text) {
    return SizedBox(
      height: height * 0.35,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset("assets/images/no-data.png", height: 90),
            const SizedBox(height: 10),
            Text(
              text,
              style: TextStyle(
                color: AyurezeTheme.textSecondary,
                fontSize: 14,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUpcomingCard(UpcomingAppointment appt) {
    final String name = appt.patientName ?? "Patient";
    final String? image = appt.user?.fullImage;
    final String treatment = appt.treatment ?? "";
    final String date = appt.date ?? "";
    final String time = appt.time ?? "";
    final String doctor = appt.doctorName ?? "";
    final String status =
        (appt.appointmentStatus ?? "pending").toLowerCase();

    return OslerCard(
      onTap: () {},
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              ClipOval(
                child: SizedBox(
                  width: 50,
                  height: 50,
                  child: (image != null && image.isNotEmpty)
                      ? CachedNetworkImage(
                          imageUrl: image,
                          fit: BoxFit.cover,
                          errorWidget: (c, u, e) => Container(
                            color: AyurezeTheme.surfaceMuted,
                            child: Icon(
                              Icons.person,
                              color: AyurezeTheme.textSecondary,
                            ),
                          ),
                        )
                      : Container(
                          color: AyurezeTheme.surfaceMuted,
                          child: Icon(
                            Icons.person,
                            color: AyurezeTheme.textSecondary,
                          ),
                        ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        color: AyurezeTheme.textPrimary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (treatment.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(
                        treatment,
                        style: TextStyle(
                          fontSize: 12,
                          color: AyurezeTheme.textSecondary,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 8),
              OslerStatusBadge(
                status: OslerStatusBadge.fromString(status),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AyurezeTheme.surfaceMuted,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Row(
              children: [
                Icon(AppIcons.clock,
                    size: 14, color: AyurezeTheme.forestDeep),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    "$date  •  $time",
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: AyurezeTheme.textPrimary,
                    ),
                  ),
                ),
                if (doctor.isNotEmpty)
                  Flexible(
                    child: Text(
                      "Dr. $doctor",
                      style: TextStyle(
                        fontSize: 12,
                        color: AyurezeTheme.textSecondary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
              ],
            ),
          ),
          if (appt.hospital != null &&
              (appt.hospital!.name != null || appt.hospital!.address != null)) ...[
            const SizedBox(height: 10),
            Row(
              children: [
                Icon(AppIcons.hospital,
                    size: 14, color: AyurezeTheme.textSecondary),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    appt.hospital!.name ?? "",
                    style: TextStyle(
                      fontSize: 12,
                      color: AyurezeTheme.textSecondary,
                      fontWeight: FontWeight.w700,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildPastCard(PastAppointment appt) {
    final String name = appt.patientName ?? "Patient";
    final String? image = appt.user?.fullImage;
    final String treatment = appt.treatment ?? "";
    final String date = appt.date ?? "";
    final String time = appt.time ?? "";
    final String doctor = appt.doctorName ?? "";
    final String status =
        (appt.appointmentStatus ?? "complete").toLowerCase();

    return OslerCard(
      onTap: () {},
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              ClipOval(
                child: SizedBox(
                  width: 50,
                  height: 50,
                  child: (image != null && image.isNotEmpty)
                      ? CachedNetworkImage(
                          imageUrl: image,
                          fit: BoxFit.cover,
                          errorWidget: (c, u, e) => Container(
                            color: AyurezeTheme.surfaceMuted,
                            child: Icon(
                              Icons.person,
                              color: AyurezeTheme.textSecondary,
                            ),
                          ),
                        )
                      : Container(
                          color: AyurezeTheme.surfaceMuted,
                          child: Icon(
                            Icons.person,
                            color: AyurezeTheme.textSecondary,
                          ),
                        ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        color: AyurezeTheme.textPrimary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (treatment.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(
                        treatment,
                        style: TextStyle(
                          fontSize: 12,
                          color: AyurezeTheme.textSecondary,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 8),
              OslerStatusBadge(
                status: OslerStatusBadge.fromString(status),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AyurezeTheme.surfaceMuted,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Row(
              children: [
                Icon(AppIcons.clock,
                    size: 14, color: AyurezeTheme.forestDeep),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    "$date  •  $time",
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: AyurezeTheme.textPrimary,
                    ),
                  ),
                ),
                if (doctor.isNotEmpty)
                  Flexible(
                    child: Text(
                      "Dr. $doctor",
                      style: TextStyle(
                        fontSize: 12,
                        color: AyurezeTheme.textSecondary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
              ],
            ),
          ),
        ],
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
        if (response.data != null) {
          if (response.data!.pastAppointment != null) {
            pastAppointmentReq.addAll(response.data!.pastAppointment!);
            _pastData.addAll(response.data!.pastAppointment!);
          }
          if (response.data!.upcomingAppointment != null) {
            upcomingAppointmentReq.addAll(response.data!.upcomingAppointment!);
            _userDetails.addAll(response.data!.upcomingAppointment!);
          }
        }
      });
    } catch (error) {
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  onSearchTextChanged(String text) async {
    _searchResult.clear();
    _pastSearch.clear();
    if (text.isEmpty) {
      setState(() {});
      return;
    }
    if (isShow == null) {
      _userDetails.forEach((appt) {
        if ((appt.patientName ?? "")
            .toLowerCase()
            .contains(text.toLowerCase())) {
          _searchResult.add(appt);
        }
      });
    } else {
      _pastData.forEach((appt) {
        if ((appt.patientName ?? "")
            .toLowerCase()
            .contains(text.toLowerCase())) {
          _pastSearch.add(appt);
        }
      });
    }
    setState(() {});
  }
}
