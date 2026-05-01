import 'dart:convert';

import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/Subscription.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/paymentScreen/PaymentGateway.dart';
import 'package:doctro/theme/osler_theme.dart';
import 'package:flutter/material.dart';

class SubSubscription extends StatefulWidget {
  @override
  _SubSubscriptionState createState() => _SubSubscriptionState();
}

class _SubSubscriptionState extends State<SubSubscription> {
  late double width;
  late double height;

  Future? subscriptions;
  int? value;

  @override
  void initState() {
    subscriptions = subscribe();
    value = 0;
    super.initState();
  }

  final List<Data> subscribeReq = [];

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: OslerTheme.canvas,
      appBar: AppBar(
        backgroundColor: OslerTheme.canvas,
        leading: IconButton(
          icon: const Icon(
            Icons.arrow_back_ios_new_rounded,
            color: OslerTheme.forestDeep,
            size: 20,
          ),
          onPressed: () {
            Navigator.pushReplacementNamed(context, 'loginHome');
          },
        ),
        title: Text(
          getTranslated(context, AppString.choose_your_best_plan).toString(),
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w800,
            color: OslerTheme.textPrimary,
          ),
        ),
      ),
      body: FutureBuilder(
        future: subscriptions,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(
              child: CircularProgressIndicator(color: OslerTheme.forestDeep),
            );
          }

          return SingleChildScrollView(
            padding: OslerTheme.screenPadding,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHero(),
                const SizedBox(height: 18),
                ...subscribeReq.asMap().entries.map(
                  (entry) => Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: _buildPlanCard(entry.key, entry.value),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildHero() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: OslerTheme.heroDecoration(),
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
              "Subscription plans",
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 14),
          const Text(
            "Choose the plan that fits your clinic rhythm.",
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              height: 1.05,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "Compare bookings, monthly options, and billing details in a calmer Osler-style layout.",
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

  Widget _buildPlanCard(int planIndex, Data data) {
    final List planOptions = json.decode(data.plan!);
    final bool hasMultipleOptions = planOptions.length > 1;
    final selectedIndex = value ?? 0;
    final currentIndex = hasMultipleOptions
        ? (selectedIndex >= planOptions.length ? 0 : selectedIndex)
        : 0;

    return Container(
      decoration: OslerTheme.panelDecoration(),
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: OslerTheme.forestDeep,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  data.name ?? "",
                  style: const TextStyle(
                    fontSize: 13,
                    color: Colors.white,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              const Spacer(),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    "${data.totalAppointment}${getTranslated(context, AppString.total_booking).toString()}",
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: OslerTheme.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    hasMultipleOptions ? "Flexible billing options" : "Single plan option",
                    style: const TextStyle(
                      fontSize: 12,
                      color: OslerTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (hasMultipleOptions)
            ...planOptions.asMap().entries.map(
              (entry) => _buildOptionTile(entry.key, entry.value),
            )
          else
            _buildSingleOption(planOptions[0]),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                if (data.name == 'free') {
                  return;
                }
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => PaymentGatewayScreen(
                      plan: data.plan,
                      value: currentIndex,
                      id: data.id,
                      name: data.name,
                    ),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor:
                    data.name == 'free' ? OslerTheme.moss : OslerTheme.forestDeep,
              ),
              child: Text(
                getTranslated(context, AppString.subscription_buy).toString(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSingleOption(dynamic option) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: OslerTheme.mutedPanelDecoration(),
      child: option['month'] != null
          ? Row(
              children: [
                Text(
                  "${_currencyPrefix()}${option['price']} / ",
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 18,
                    color: OslerTheme.textPrimary,
                  ),
                ),
                Text(
                  "${option['month']} MONTH",
                  style: const TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                    color: OslerTheme.textSecondary,
                  ),
                ),
              ],
            )
          : Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  getTranslated(context, AppString.free_validity).toString(),
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 16,
                    color: OslerTheme.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  getTranslated(context, AppString.edit_or_delete).toString(),
                  style: const TextStyle(
                    fontSize: 12,
                    color: OslerTheme.textSecondary,
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildOptionTile(int optionIndex, dynamic option) {
    final selected = value == optionIndex;
    return GestureDetector(
      onTap: () {
        setState(() {
          value = optionIndex;
        });
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: selected ? OslerTheme.limeSoft : OslerTheme.surfaceMuted,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(
            color: selected ? OslerTheme.lime : OslerTheme.border,
          ),
        ),
        child: Row(
          children: [
            Icon(
              selected
                  ? Icons.radio_button_checked_rounded
                  : Icons.radio_button_off_rounded,
              color: selected ? OslerTheme.forestDeep : OslerTheme.textSecondary,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Row(
                children: [
                  Text(
                    "${_currencyPrefix()}${option['price']} / ",
                    style: const TextStyle(
                      fontWeight: FontWeight.w800,
                      fontSize: 16,
                      color: OslerTheme.textPrimary,
                    ),
                  ),
                  Text(
                    "${option['month']} MONTH",
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 13,
                      color: OslerTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _currencyPrefix() {
    final symbol =
        SharedPreferenceHelper.getString(Preferences.currency_symbol);
    return symbol != "N_A" ? "$symbol " : "";
  }

  Future<BaseModel<SubscriptionPlan>> subscribe() async {
    SubscriptionPlan response;
    try {
      response = await RestClient(await RetroApi().dioData(context))
          .subscriptionRequest();
      setState(() {
        subscribeReq.addAll(response.data!);
      });
    } catch (error, stacktrace) {
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }
}

class PaymentData {
  int? id;
  String? name;
  String? plan;
  int? totalAppointment;

  PaymentData({this.id, this.name, this.plan, this.totalAppointment});

  PaymentData.fromJson(Map<String, dynamic> json) {
    id = json['id'];
    name = json['name'];
    plan = json['plan'];
    totalAppointment = json['total_appointment'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = <String, dynamic>{};
    data['id'] = id;
    data['name'] = name;
    data['plan'] = plan;
    data['total_appointment'] = totalAppointment;
    return data;
  }
}
