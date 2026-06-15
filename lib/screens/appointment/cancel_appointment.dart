import 'dart:async';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/CancelAppointment.dart';
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
import 'package:intl/intl.dart';

class CancelAppointmentScreen extends StatefulWidget {
  @override
  _CancelAppointmentScreen createState() => _CancelAppointmentScreen();
}

class _CancelAppointmentScreen extends State<CancelAppointmentScreen> {
  Future? cancelAppointment;

  late double width;
  late double height;

  String? dName;
  String? dFullImage;
  String? phone;
  int? subscription;

  TextEditingController _search = TextEditingController();
  List<AppointmentCancel> _searchResult = [];
  List<AppointmentCancel> _userCancel = [];

  List<AppointmentCancel> cancelAppointmentReq = [];

  final _scaffoldKey = GlobalKey<ScaffoldState>();

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

  @override
  void dispose() {
    _search.dispose();
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
        Navigator.pushNamedAndRemoveUntil(
            context, 'loginHome', (route) => false);
      },
      child: RefreshIndicator(
        onRefresh: cancelAppointmentRequest,
        color: AyurezeTheme.forestDeep,
        child: Scaffold(
          key: _scaffoldKey,
          backgroundColor: AyurezeTheme.canvas,
          drawer: const ModernDrawer(),
          appBar: AppBar(
            backgroundColor: AyurezeTheme.canvas,
            elevation: 0,
            iconTheme: IconThemeData(color: AyurezeTheme.iconPrimary),
            title: Text(
              getTranslated(
                      context, AppString.cancel_appointment_heading)
                  .toString(),
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: AyurezeTheme.textPrimary,
              ),
            ),
          ),
          body: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: () {
              FocusScope.of(context).requestFocus(new FocusNode());
            },
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
                  FutureBuilder(
                    future: cancelAppointment,
                    builder: (context, snapshot) {
                      if (snapshot.connectionState != ConnectionState.done) {
                        return SizedBox(
                          height: height * 0.4,
                          child: const Center(
                            child: CircularProgressIndicator(),
                          ),
                        );
                      }
                      final list = _search.text.isNotEmpty
                          ? _searchResult
                          : cancelAppointmentReq;
                      if (list.isEmpty) {
                        return _buildEmptyState();
                      }
                      return Column(
                        children: list
                            .map((appt) => Padding(
                                  padding: const EdgeInsets.only(bottom: 12),
                                  child: _buildCancelCard(appt),
                                ))
                            .toList(),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeroSummary() {
    final int count = cancelAppointmentReq.length;
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
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.14),
              borderRadius: BorderRadius.circular(999),
            ),
            child: const Text(
              "Cancelled ledger",
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Theme.of(context).colorScheme.onPrimary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 14),
          Text(
            "$count cancelled",
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              height: 1.05,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            "Appointments cancelled by patient or doctor",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
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
                        context, AppString.search_cancel_appointment)
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

  Widget _buildEmptyState() {
    return SizedBox(
      height: height * 0.35,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset("assets/images/no-data.png", height: 90),
            const SizedBox(height: 10),
            Text(
              getTranslated(context, AppString.result_not_found).toString(),
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

  Widget _buildCancelCard(AppointmentCancel appt) {
    final String name = appt.patientName ?? "Patient";
    final String? image = appt.user?.fullImage;
    final String address = appt.patientAddress ?? "";
    final String dateText = appt.date != null
        ? _safeFormattedDate(appt.date!)
        : "";
    final String timeText = appt.time ?? "";
    final String amount =
        "${SharedPreferenceHelper.getString(Preferences.currency_symbol)}${appt.amount ?? 0}";
    final String ageLine = appt.age != null
        ? "${getTranslated(context, AppString.home_age_data).toString()}: ${appt.age}"
        : "";

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
                    if (ageLine.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(
                        ageLine,
                        style: TextStyle(
                          fontSize: 12,
                          color: AyurezeTheme.textSecondary,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 8),
              OslerStatusBadge(
                status: AppointmentStatus.cancel,
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
                    "$dateText  •  $timeText",
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: AyurezeTheme.textPrimary,
                    ),
                  ),
                ),
                Text(
                  amount,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    color: AyurezeTheme.forestDeep,
                  ),
                ),
              ],
            ),
          ),
          if (address.isNotEmpty) ...[
            const SizedBox(height: 10),
            Row(
              children: [
                Icon(AppIcons.location,
                    size: 14, color: AyurezeTheme.textSecondary),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    address,
                    style: TextStyle(
                      fontSize: 12,
                      color: AyurezeTheme.textSecondary,
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 2,
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

  String _safeFormattedDate(String raw) {
    try {
      return DateFormat('dd-MM-yyyy').format(DateTime.parse(raw));
    } catch (_) {
      return raw;
    }
  }

  Future<BaseModel<CancelAppointment>> cancelAppointmentRequest() async {
    CancelAppointment response;
    try {
      cancelAppointmentReq.clear();
      _userCancel.clear();
      _searchResult.clear();
      response = await RestClient(await RetroApi().dioData(context))
          .cancelAppointmentRequest();
      setState(() {
        if (response.data != null) {
          cancelAppointmentReq.addAll(response.data!);
          _userCancel.addAll(response.data!);
        }
      });
    } catch (error) {
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
