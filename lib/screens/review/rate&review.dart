import 'dart:async';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/review.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/auth/SignIn.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/widgets/modern_drawer.dart';
import 'package:doctro/widgets/osler_button.dart';
import 'package:doctro/widgets/osler_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
import 'package:intl/intl.dart';

class RateAndReviewRoutesScreen extends StatefulWidget {
  @override
  _RateAndReviewRoutesScreenState createState() =>
      _RateAndReviewRoutesScreenState();
}

class _RateAndReviewRoutesScreenState extends State<RateAndReviewRoutesScreen> {
  Future? reviewDatas;

  final _scaffoldKey = GlobalKey<ScaffoldState>();

  late double width;
  late double height;

  List<ReviewData> reviewData = [];

  String? dName;
  String? dFullImage;
  String? phone;
  int? subscription;

  TextEditingController _search = TextEditingController();
  List<ReviewData> _searchResult = [];
  List<ReviewData> _userReview = [];

  @override
  void initState() {
    super.initState();
    Future.delayed(Duration.zero, () {
      dName = SharedPreferenceHelper.getString(Preferences.name);
      dFullImage = SharedPreferenceHelper.getString(Preferences.image);
      phone = SharedPreferenceHelper.getString(Preferences.phone_no);
      subscription =
          SharedPreferenceHelper.getInt(Preferences.subscription_status);
      reviewDatas = reviewRequest();
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

    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: AyurezeTheme.canvas,
      drawer: const ModernDrawer(),
      appBar: AppBar(
        backgroundColor: AyurezeTheme.canvas,
        elevation: 0,
        iconTheme: IconThemeData(color: AyurezeTheme.iconPrimary),
        title: Text(
          getTranslated(context, AppString.review_heading).toString(),
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
          onRefresh: reviewRequest,
          color: AyurezeTheme.forestDeep,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: AyurezeTheme.screenPadding,
            child: FutureBuilder(
              future: reviewDatas,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return SizedBox(
                    height: height * 0.7,
                    child: const Center(
                      child: CircularProgressIndicator(),
                    ),
                  );
                }
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildHeroSummary(),
                    const SizedBox(height: 18),
                    _buildSearchCard(),
                    const SizedBox(height: 18),
                    if (_search.text.isEmpty && reviewData.isEmpty)
                      _buildEmptyState()
                    else if (_search.text.isNotEmpty && _searchResult.isEmpty)
                      _buildNoResults()
                    else
                      _buildReviewList(),
                  ],
                );
              },
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeroSummary() {
    final int total = reviewData.length;
    final double average = reviewData.isEmpty
        ? 0
        : reviewData
                .map((e) => (e.rate ?? 0).toDouble())
                .fold<double>(0, (a, b) => a + b) /
            total;

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
              "Patient feedback",
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 14),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                average.toStringAsFixed(1),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 40,
                  height: 1.0,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(width: 8),
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Text(
                  "/ 5.0",
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.78),
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            "Across $total patient reviews",
            style: TextStyle(
              color: Colors.white.withOpacity(0.82),
              fontSize: 14,
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
                        context, AppString.review_search)
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
      height: height * 0.45,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset("assets/images/no-data.png", height: 100),
            const SizedBox(height: 10),
            Text(
              "No reviews yet",
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

  Widget _buildNoResults() {
    return SizedBox(
      height: height * 0.3,
      child: Center(
        child: Text(
          getTranslated(context, AppString.result_not_found).toString(),
          style: TextStyle(color: AyurezeTheme.textSecondary),
        ),
      ),
    );
  }

  Widget _buildReviewList() {
    final list = _search.text.isNotEmpty ? _searchResult : reviewData;
    return Column(
      children: list
          .map((review) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildReviewCard(review),
              ))
          .toList(),
    );
  }

  Widget _buildReviewCard(ReviewData review) {
    final String name = review.user?.name ?? "Patient";
    final String? image = review.user?.fullImage;
    final double rate = (review.rate ?? 0).toDouble();
    final String text = review.review ?? "";
    final String dateText = review.createdAt != null && review.createdAt!.isNotEmpty
        ? DateUtil().formattedDate(DateTime.parse(review.createdAt!))
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
                  width: 48,
                  height: 48,
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
                    const SizedBox(height: 4),
                    RatingBarIndicator(
                      rating: rate,
                      itemBuilder: (context, index) => Icon(
                        Icons.star,
                        color: AyurezeTheme.forestDeep,
                      ),
                      itemCount: 5,
                      itemSize: 16,
                      direction: Axis.horizontal,
                    ),
                  ],
                ),
              ),
              if (dateText.isNotEmpty)
                Text(
                  dateText,
                  style: TextStyle(
                    fontSize: 11,
                    color: AyurezeTheme.textSecondary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
            ],
          ),
          if (text.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              text,
              style: TextStyle(
                fontSize: 13,
                height: 1.4,
                color: AyurezeTheme.textSecondary,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Future<BaseModel<Review>> reviewRequest() async {
    Review response;
    try {
      reviewData.clear();
      _userReview.clear();
      response =
          await RestClient(await RetroApi().dioData(context)).reviewRequest();
      setState(() {
        if (response.data != null) {
          reviewData.addAll(response.data!);
          _userReview.addAll(response.data!);
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
    _userReview.forEach((review) {
      if ((review.user?.name ?? "")
          .toLowerCase()
          .contains(text.toLowerCase())) {
        _searchResult.add(review);
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
