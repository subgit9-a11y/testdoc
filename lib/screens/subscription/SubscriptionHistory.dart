import 'package:doctro/constant/app_string.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/FinanceDetails.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/theme/osler_theme.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class SubscriptionHistory extends StatefulWidget {
  const SubscriptionHistory({Key? key}) : super(key: key);

  @override
  _SubscriptionHistoryState createState() => _SubscriptionHistoryState();
}

class _SubscriptionHistoryState extends State<SubscriptionHistory> {
  Future? purchaseReq;

  final List<PurchaseDetails> purchaseDetail = [];
  final TextEditingController _search = TextEditingController();
  final List<PurchaseDetails> _searchResult = [];
  final List<PurchaseDetails> _subscriptionHistory = [];

  @override
  void initState() {
    purchaseReq = purchaseDetailsFunction();
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: OslerTheme.canvas,
      appBar: AppBar(
        backgroundColor: OslerTheme.canvas,
        leading: IconButton(
          icon: Icon(
            AppIcons.back,
            color: OslerTheme.forestDeep,
            size: 20,
          ),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          getTranslated(context, AppString.subscription_history_heading)
              .toString(),
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w800,
            color: OslerTheme.textPrimary,
          ),
        ),
      ),
      body: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () {
          FocusScope.of(context).requestFocus(FocusNode());
        },
        child: FutureBuilder(
          future: purchaseReq,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(
                child: CircularProgressIndicator(color: OslerTheme.forestDeep),
              );
            }

            final activeSource =
                _search.text.isNotEmpty ? _searchResult : purchaseDetail;

            return SingleChildScrollView(
              padding: OslerTheme.screenPadding,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHero(),
                  const SizedBox(height: 18),
                  _buildSearchCard(),
                  const SizedBox(height: 18),
                  _buildSummary(),
                  const SizedBox(height: 14),
                  if (activeSource.isEmpty)
                    _buildEmptyState()
                  else
                    ...activeSource.map((item) => _buildHistoryCard(item)),
                ],
              ),
            );
          },
        ),
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
              "Plan history",
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 14),
          const Text(
            "Review every clinic subscription in one place.",
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              height: 1.05,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "Search plan purchases, payment types, and expiry dates without falling back to the old utility layout.",
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
      decoration: OslerTheme.panelDecoration(),
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 6),
      child: TextField(
        controller: _search,
        decoration: InputDecoration(
          border: InputBorder.none,
          filled: false,
          hintText: getTranslated(
            context,
            AppString.subscription_search_history,
          ).toString(),
          hintStyle: const TextStyle(color: OslerTheme.textSecondary),
          suffixIcon: const Icon(
            AppIcons.search,
            color: OslerTheme.forestDeep,
          ),
        ),
        onChanged: onSearchTextChanged,
      ),
    );
  }

  Widget _buildSummary() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          getTranslated(context, AppString.subscription_history_heading)
              .toString(),
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: OslerTheme.textPrimary,
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: OslerTheme.limeSoft,
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            "${purchaseDetail.length} ${getTranslated(context, AppString.subscription_title).toString()}",
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: OslerTheme.forestDeep,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildHistoryCard(PurchaseDetails item) {
    final statusActive = item.status == 1;
    final endDate = item.endDate != null
        ? DateFormat('dd MMM yyyy').format(DateTime.parse(item.endDate!))
        : "--";
    final startDate = item.startDate != null
        ? DateFormat('dd MMM yyyy').format(DateTime.parse(item.startDate!))
        : "--";

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(18),
      decoration: OslerTheme.panelDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Text(
                  "${getTranslated(context, AppString.subscription_plan).toString()}: ${item.subscription?.name ?? ""}",
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    color: OslerTheme.textPrimary,
                  ),
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: statusActive
                      ? const Color(0xFFDDF0D0)
                      : const Color(0xFFF8D6CF),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  statusActive
                      ? getTranslated(
                          context,
                          AppString.subscription_active_button,
                        ).toString()
                      : getTranslated(
                          context,
                          AppString.subscription_expired,
                        ).toString(),
                  style: TextStyle(
                    color: statusActive
                        ? OslerTheme.forestDeep
                        : OslerTheme.danger,
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            item.amount == null
                ? getTranslated(context, AppString.subscription_free).toString()
                : "${getTranslated(context, AppString.subscription_payment).toString()}: ${item.amount}",
            style: const TextStyle(
              fontSize: 14,
              color: OslerTheme.textSecondary,
            ),
          ),
          if (item.paymentType != null) ...[
            const SizedBox(height: 4),
            Text(
              "${getTranslated(context, AppString.subscription_payment_type).toString()} ${item.paymentType!}",
              style: const TextStyle(
                fontSize: 14,
                color: OslerTheme.textSecondary,
              ),
            ),
          ],
          const SizedBox(height: 14),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: OslerTheme.mutedPanelDecoration(),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _dateColumn("Start", startDate),
                _dateColumn("Expiry", endDate),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _dateColumn(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: OslerTheme.textSecondary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w800,
            color: OslerTheme.textPrimary,
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 36),
      decoration: OslerTheme.panelDecoration(),
      child: Column(
        children: [
          Image.asset("assets/images/no-data.png", height: 88),
          const SizedBox(height: 10),
          const Text(
            "No subscription history yet.",
            style: TextStyle(color: OslerTheme.textSecondary),
          ),
        ],
      ),
    );
  }

  Future<BaseModel<FinanceDetails>> purchaseDetailsFunction() async {
    FinanceDetails response;
    try {
      purchaseDetail.clear();
      _subscriptionHistory.clear();
      response = await RestClient(await RetroApi().dioData(context))
          .purchaseDetailsRequest();
      setState(() {
        purchaseDetail.addAll(response.data!);
        _subscriptionHistory.addAll(response.data!);
      });
    } catch (error, stacktrace) {
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

    for (final subscription in _subscriptionHistory) {
      if ((subscription.subscription?.name ?? "")
          .toLowerCase()
          .contains(text.toLowerCase())) {
        _searchResult.add(subscription);
      }
    }
    setState(() {});
  }
}
