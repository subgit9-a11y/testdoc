import 'dart:async';

import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/common_function.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/payment.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/auth/SignIn.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/widgets/modern_drawer.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';

class PaymentScreen extends StatefulWidget {
  @override
  _PaymentScreen createState() => _PaymentScreen();
}

class _PaymentScreen extends State<PaymentScreen> {
  late double width;
  late double height;

  final _scaffoldKey = GlobalKey<ScaffoldState>();
  Future? payments;

  static double sum = 0;

  String? dName;
  String? dFullImage;
  String? phone;
  int? subscription;

  final TextEditingController _search = TextEditingController();
  final List<Payments> _searchResult = [];
  final List<Payments> _userPayment = [];

  @override
  void initState() {
    super.initState();

    Future.delayed(Duration.zero, () {
      payments = paymentsFunction();
      dName = SharedPreferenceHelper.getString(Preferences.name);
      dFullImage = SharedPreferenceHelper.getString(Preferences.image);
      phone = SharedPreferenceHelper.getString(Preferences.phone_no);
      subscription =
          SharedPreferenceHelper.getInt(Preferences.subscription_status);
    });
  }

  bool _paymentRequest = false;
  final List<Payments> paymentsRequest = [];

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) return;
        Navigator.pushNamedAndRemoveUntil(
          context,
          'loginHome',
          (route) => false,
        );
      },
      child: RefreshIndicator(
        onRefresh: paymentsFunction,
        color: AyurezeTheme.forestDeep,
        child: Scaffold(
          key: _scaffoldKey,
          backgroundColor: AyurezeTheme.canvas,
          drawer: const ModernDrawer(),
          appBar: AppBar(
            backgroundColor: AyurezeTheme.canvas,
            title: Text(
              getTranslated(context, AppString.payment_title).toString(),
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: AyurezeTheme.textPrimary,
              ),
            ),
          ),
          body: FutureBuilder(
            future: payments,
            builder: (context, snapshot) {
              if (snapshot.connectionState != ConnectionState.done) {
                return Center(
                  child: CircularProgressIndicator(
                    color: AyurezeTheme.forestDeep,
                  ),
                );
              }

              return GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: () {
                  FocusScope.of(context).requestFocus(FocusNode());
                },
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: AyurezeTheme.screenPadding,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildHero(),
                      const SizedBox(height: 18),
                      _buildSearchCard(),
                      const SizedBox(height: 18),
                      if (paymentsRequest.isEmpty)
                        _buildEmptyState()
                      else ...[
                        _buildHeaderSummary(),
                        const SizedBox(height: 12),
                        ..._buildPaymentItems(),
                        if (!_searching() &&
                            !_paymentRequest &&
                            paymentsRequest.length > 5) ...[
                          const SizedBox(height: 10),
                          _buildViewAllCard(),
                        ],
                        const SizedBox(height: 14),
                        _buildTotalBar(),
                      ],
                    ],
                  ),
                ),
              );
            },
          ),
        ),
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
              "Billing overview",
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 14),
          const Text(
            "Track patient payments in one calm ledger.",
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              height: 1.05,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "Search the ledger, review incoming totals, and keep the financial side of the clinic tidy.",
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

  Widget _buildSearchCard() {
    return Container(
      decoration: AyurezeTheme.panelDecoration(),
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 6),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _search,
              decoration: InputDecoration(
                border: InputBorder.none,
                filled: false,
                hintText:
                    getTranslated(context, AppString.payment_search).toString(),
                hintStyle: TextStyle(color: AyurezeTheme.textSecondary),
              ),
              onChanged: onSearchTextChanged,
            ),
          ),
          SvgPicture.asset(
            'assets/icons/dSearch.svg',
            height: 20,
            color: AyurezeTheme.forestDeep,
          ),
        ],
      ),
    );
  }

  Widget _buildHeaderSummary() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          getTranslated(context, AppString.payment_patient_list).toString(),
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: AyurezeTheme.textPrimary,
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: AyurezeTheme.lightGreenSoft,
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            "${getTranslated(context, AppString.payment_total).toString()} ${paymentsRequest.length}",
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: AyurezeTheme.forestDeep,
            ),
          ),
        ),
      ],
    );
  }

  List<Widget> _buildPaymentItems() {
    final List<Payments> source = _searching()
        ? _searchResult
        : paymentsRequest.take(_paymentRequest ? paymentsRequest.length : 5).toList();

    if (_searching() && source.isEmpty) {
      return [
        Padding(
          padding: const EdgeInsets.only(top: 18),
          child: Center(
            child: Text(
              getTranslated(context, AppString.result_not_found).toString(),
            ),
          ),
        ),
      ];
    }

    return source.map((payment) => _buildPaymentRow(payment)).toList();
  }

  Widget _buildPaymentRow(Payments payment) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(16),
      decoration: AyurezeTheme.panelDecoration(),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: AyurezeTheme.surfaceMuted,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(
              Icons.payments_outlined,
              color: AyurezeTheme.forestDeep,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  payment.user?.name ?? "",
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: AyurezeTheme.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  "Completed payment",
                  style: TextStyle(
                    fontSize: 12,
                    color: AyurezeTheme.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Text(
            "${SharedPreferenceHelper.getString(Preferences.currency_symbol)}${payment.amount}",
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w800,
              color: AyurezeTheme.forestDeep,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildViewAllCard() {
    return GestureDetector(
      onTap: () {
        setState(() {
          _paymentRequest = true;
        });
      },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: AyurezeTheme.mutedPanelDecoration(),
        child: Row(
          children: [
            Expanded(
              child: Text(
                getTranslated(context, AppString.view_all_payment).toString(),
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AyurezeTheme.textPrimary,
                ),
              ),
            ),
            SvgPicture.asset(
              'assets/icons/longArrow.svg',
              height: 12,
              color: AyurezeTheme.forestDeep,
            ),
            const SizedBox(width: 10),
            Text(
              "${paymentsRequest.length}",
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w800,
                color: AyurezeTheme.forestDeep,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTotalBar() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 18),
      decoration: BoxDecoration(
        color: AyurezeTheme.forestDeep,
        borderRadius: BorderRadius.circular(22),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            getTranslated(context, AppString.payment_rs_total).toString(),
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
          Text(
            "${SharedPreferenceHelper.getString(Preferences.currency_symbol)}$sum",
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w800,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 36),
      decoration: AyurezeTheme.panelDecoration(),
      child: Column(
        children: [
          Image.asset("assets/images/no-data.png", height: 88),
          const SizedBox(height: 10),
          Text(
            getTranslated(context, AppString.no_user).toString(),
            style: TextStyle(color: AyurezeTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  bool _searching() => _search.text.isNotEmpty;

  Future<void> logoutUser() async {
    SharedPreferenceHelper.clearPref();
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (BuildContext context) => SignIn()),
      ModalRoute.withName('SignIn'),
    );
  }

  Future<BaseModel<Payment>> paymentsFunction() async {
    Payment response;
    try {
      paymentsRequest.clear();
      _userPayment.clear();
      response =
          await RestClient(await RetroApi().dioData(context)).paymentRequest();
      setState(() {
        paymentsRequest.addAll(response.paymentData!);
        _userPayment.addAll(response.paymentData!);

        sum = 0;
        for (int i = 0; i < paymentsRequest.length; i++) {
          sum += double.parse(paymentsRequest[i].amount!);
        }
      });
    } catch (error, stacktrace) {
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<Payment>> allMedicinesReq() async {
    Payment response;
    try {
      paymentsRequest.clear();
      _userPayment.clear();
      response =
          await RestClient(await RetroApi().dioData(context)).paymentRequest();
      setState(() {
        paymentsRequest.addAll(response.paymentData!);
        _userPayment.addAll(response.paymentData!);

        sum = 0;
        for (int i = 0; i < paymentsRequest.length; i++) {
          sum += double.parse(paymentsRequest[i].amount!);
        }
      });
    } catch (error, stacktrace) {
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  showAlertDialog(BuildContext context) {
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

    AlertDialog alert = AlertDialog(
      content: Text(
        getTranslated(context, AppString.are_you_sure_logout).toString(),
      ),
      actions: [cancel, okButton],
    );
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return alert;
      },
    );
  }

  onSearchTextChanged(String text) async {
    _searchResult.clear();
    if (text.isEmpty) {
      setState(() {});
      return;
    }

    _userPayment.forEach((payment) {
      if ((payment.user?.name ?? "").toLowerCase().contains(text.toLowerCase())) {
        _searchResult.add(payment);
      }
    });
    setState(() {});
  }
}

