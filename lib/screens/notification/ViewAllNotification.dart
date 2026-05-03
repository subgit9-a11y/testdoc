import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/date_util.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/Notification.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/theme/osler_theme.dart';
import 'package:flutter/material.dart';

class ViewAllNotification extends StatefulWidget {
  @override
  _ViewAllAppointmentState createState() => _ViewAllAppointmentState();
}

class _ViewAllAppointmentState extends State<ViewAllNotification> {
  late double width;
  late double height;

  Future? loadData;
  List<NotificationData> patientNotification = [];

  @override
  void initState() {
    super.initState();
    loadData = bookNotifications();
  }

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
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          getTranslated(context, AppString.notification_heading).toString(),
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w800,
            color: OslerTheme.textPrimary,
          ),
        ),
      ),
      body: FutureBuilder(
        future: loadData,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(
              child: CircularProgressIndicator(color: OslerTheme.forestDeep),
            );
          }

          return SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: OslerTheme.screenPadding,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(22),
                  decoration: OslerTheme.heroDecoration(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.14),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: const Text(
                          "Full inbox",
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),
                      const Text(
                        "Every patient notification, in one scroll.",
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          height: 1.05,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                if (patientNotification.isEmpty)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(vertical: 36),
                    decoration: OslerTheme.panelDecoration(),
                    child: Column(
                      children: [
                        Image.asset("assets/images/no-data.png", height: 88),
                        const SizedBox(height: 10),
                        const Text(
                          "No notifications yet.",
                          style: TextStyle(color: OslerTheme.textSecondary),
                        ),
                      ],
                    ),
                  )
                else
                  ...patientNotification.map((item) => _buildNotificationCard(item)),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildNotificationCard(NotificationData item) {
    final date = DateUtil().formattedDate(DateTime.parse(item.createdAt!));
    return InkWell(
      onTap: () {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(24),
            ),
            content: Text(item.message!),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                child: Text(
                  getTranslated(context, AppString.schedule_ok_button)
                      .toString(),
                ),
              ),
            ],
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: OslerTheme.panelDecoration(),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: Image.network(
                item.user?.fullImage ?? "",
                width: 58,
                height: 58,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    width: 58,
                    height: 58,
                    color: OslerTheme.surfaceMuted,
                    child: const Icon(
                      AppIcons.profile,
                      color: OslerTheme.textSecondary,
                    ),
                  );
                },
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          item.user?.name ?? "",
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w800,
                            color: OslerTheme.textPrimary,
                          ),
                        ),
                      ),
                      Text(
                        date,
                        style: const TextStyle(
                          fontSize: 12,
                          color: OslerTheme.textSecondary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    item.message ?? "",
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
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
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }
}
