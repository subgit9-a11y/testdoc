import 'package:flutter/material.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/screens/auth/professional_registration_screen.dart';
import 'package:doctro/services/session_service.dart';
import 'package:doctro/theme/ayureze_theme.dart';

class ModernDrawer extends StatelessWidget {
  const ModernDrawer({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final String? dName = SharedPreferenceHelper.getString(Preferences.name);
    final String? dFullImage = SharedPreferenceHelper.getString(Preferences.image);
    final String? phone = SharedPreferenceHelper.getString(Preferences.phone_no);

    return Drawer(
      child: Container(
        color: AyurezeTheme.canvas,
        child: Column(
          children: [
            Container(
              constraints: const BoxConstraints(minHeight: 260),
              width: double.infinity,
              padding: const EdgeInsets.only(top: 54, left: 22, right: 22, bottom: 22),
              decoration: AyurezeTheme.heroDecoration(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.14),
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(color: Colors.white.withOpacity(0.16)),
                    ),
                    child: const Text(
                      "Ayureze Doctor Desk",
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.3,
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),
                  Container(
                    width: 76,
                    height: 76,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: AyurezeTheme.healingGreen50, width: 2),
                      image: DecorationImage(
                        image: (dFullImage != null && dFullImage!.isNotEmpty)
                            ? NetworkImage(dFullImage!)
                            : const AssetImage("assets/images/no_image.jpg")
                                as ImageProvider,
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    "Dr. ${dName ?? "Doctor"}",
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    phone ?? "",
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(color: Colors.white.withOpacity(0.74), fontSize: 13),
                  ),
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AyurezeTheme.healingGreen50,
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(
                      "Verified Professional",
                      style: TextStyle(
                        color: AyurezeTheme.forestDeep,
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(14, 16, 14, 10),
                children: [
                  _drawerItem(context, AppIcons.home, getTranslated(context, AppString.drawer_home).toString(), () => Navigator.popUntil(context, ModalRoute.withName('loginHome'))),
                  _drawerItem(context, AppIcons.appointment, getTranslated(context, AppString.drawer_appointments).toString(), () => Navigator.popAndPushNamed(context, 'AppointmentHistoryScreen')),
                  _drawerItem(context, AppIcons.close, getTranslated(context, AppString.drawer_canceled_appointment).toString(), () => Navigator.popAndPushNamed(context, 'cancelAppoitmentRoutes')),
                  _drawerItem(context, AppIcons.payment, getTranslated(context, AppString.drawer_payments).toString(), () => Navigator.popAndPushNamed(context, 'payment')),
                  _drawerItem(context, AppIcons.star, getTranslated(context, AppString.drawer_review).toString(), () => Navigator.popAndPushNamed(context, 'rateAndReviewRoutes')),
                  _drawerItem(context, AppIcons.notifications, getTranslated(context, AppString.drawer_notification).toString(), () => Navigator.popAndPushNamed(context, 'notifications')),
                  _drawerItem(context, AppIcons.verified, "Profile & Registration", () {
                    Navigator.pop(context);
                    Navigator.push(context, MaterialPageRoute(builder: (context) => ProfessionalRegistrationScreen()));
                  }),
                  _drawerItem(context, AppIcons.clock, getTranslated(context, AppString.drawer_schedule_timing).toString(), () => Navigator.popAndPushNamed(context, 'Schedule Timings')),
                  _drawerItem(context, AppIcons.settings, getTranslated(context, AppString.drawer_setting).toString(), () => Navigator.popAndPushNamed(context, 'Settings')),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                    child: Divider(color: AyurezeTheme.border),
                  ),
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
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: AyurezeTheme.panelDecoration(),
      child: ListTile(
        leading: Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            color: isDestructive ? Colors.red.withOpacity(0.1) : AyurezeTheme.surfaceMuted,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Icon(icon, color: isDestructive ? Colors.red : AyurezeTheme.textPrimary, size: 20),
        ),
        title: Text(
          label,
          style: TextStyle(
            color: isDestructive ? Colors.red : AyurezeTheme.textPrimary,
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
        trailing: Icon(
          Icons.arrow_forward_ios,
          size: 14,
          color: isDestructive ? Colors.red.withOpacity(0.7) : AyurezeTheme.textSecondary,
        ),
        onTap: onTap,
        dense: true,
      ),
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
              Navigator.pop(context);
              SessionService.logout();
            },
            child: Text(getTranslated(context, AppString.logout_button).toString(), style: const TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}

