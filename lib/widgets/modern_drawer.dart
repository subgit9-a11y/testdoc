import 'package:flutter/material.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/screens/auth/professional_registration_screen.dart';

class ModernDrawer extends StatelessWidget {
  const ModernDrawer({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final String? dName = SharedPreferenceHelper.getString(Preferences.name);
    final String? dFullImage = SharedPreferenceHelper.getString(Preferences.image);
    final String? phone = SharedPreferenceHelper.getString(Preferences.phone_no);

    return Drawer(
      child: Container(
        color: Colors.white,
        child: Column(
          children: [
            Container(
              height: 230,
              width: double.infinity,
              padding: const EdgeInsets.only(top: 50, left: 20, right: 20, bottom: 20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [purple, const Color(0xFF9C27B0)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 70,
                    height: 70,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 2),
                      image: DecorationImage(
                        image: NetworkImage(dFullImage ?? "https://via.placeholder.com/150"),
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                  const SizedBox(height: 15),
                  Text(
                    "Dr. ${dName ?? "Doctor"}",
                    style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    phone ?? "",
                    style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 13),
                  ),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: const Text("Verified Professional", style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w600)),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(vertical: 10),
                children: [
                  _drawerItem(context, Icons.dashboard_outlined, getTranslated(context, AppString.drawer_home).toString(), () => Navigator.popUntil(context, ModalRoute.withName('loginHome'))),
                  _drawerItem(context, Icons.calendar_month_outlined, getTranslated(context, AppString.drawer_appointments).toString(), () => Navigator.popAndPushNamed(context, 'AppointmentHistoryScreen')),
                  _drawerItem(context, Icons.cancel_outlined, getTranslated(context, AppString.drawer_canceled_appointment).toString(), () => Navigator.popAndPushNamed(context, 'cancelAppoitmentRoutes')),
                  _drawerItem(context, Icons.payments_outlined, getTranslated(context, AppString.drawer_payments).toString(), () => Navigator.popAndPushNamed(context, 'payment')),
                  _drawerItem(context, Icons.star_outline, getTranslated(context, AppString.drawer_review).toString(), () => Navigator.popAndPushNamed(context, 'rateAndReviewRoutes')),
                  _drawerItem(context, Icons.notifications_none_outlined, getTranslated(context, AppString.drawer_notification).toString(), () => Navigator.popAndPushNamed(context, 'notifications')),
                  _drawerItem(context, Icons.chat_outlined, getTranslated(context, AppString.chats).toString(), () => Navigator.popAndPushNamed(context, 'ChatHome')),
                  _drawerItem(context, Icons.how_to_reg_outlined, "Profile & Registration", () {
                    Navigator.pop(context);
                    Navigator.push(context, MaterialPageRoute(builder: (context) => ProfessionalRegistrationScreen()));
                  }),
                  _drawerItem(context, Icons.schedule_outlined, getTranslated(context, AppString.drawer_schedule_timing).toString(), () => Navigator.popAndPushNamed(context, 'Schedule Timings')),
                  _drawerItem(context, Icons.settings_outlined, getTranslated(context, AppString.drawer_setting).toString(), () => Navigator.popAndPushNamed(context, 'Settings')),
                  const Divider(indent: 20, endIndent: 20),
                  _drawerItem(context, Icons.logout, getTranslated(context, AppString.drawer_logout).toString(), () => _showLogoutDialog(context), isDestructive: true),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _drawerItem(BuildContext context, IconData icon, String label, VoidCallback onTap, {bool isDestructive = false}) {
    return ListTile(
      leading: Icon(icon, color: isDestructive ? Colors.red : hintColor, size: 22),
      title: Text(label, style: TextStyle(color: isDestructive ? Colors.red : hintColor, fontSize: 14)),
      onTap: onTap,
      dense: true,
    );
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(getTranslated(context, AppString.drawer_logout).toString()),
        content: Text(getTranslated(context, AppString.are_you_sure_logout).toString()),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: Text(getTranslated(context, AppString.cancel_button).toString())),
          TextButton(
            onPressed: () {
              SharedPreferenceHelper.clearPref();
              Navigator.pushNamedAndRemoveUntil(context, 'SignIn', (route) => false);
            },
            child: Text(getTranslated(context, AppString.logout_button).toString(), style: const TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
