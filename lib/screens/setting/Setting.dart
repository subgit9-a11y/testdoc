import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/theme/theme_provider.dart';
import 'package:provider/provider.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/theme/osler_theme.dart';
import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

import '../../model/UpdateProfile.dart';
import '../../model/doctor_profile.dart';
import '../../retrofit/api_header.dart';
import '../../retrofit/base_model.dart';
import '../../retrofit/network_api.dart';
import '../../retrofit/server_error.dart';
import '../subscription/SubscriptionHistory.dart';
import 'ChangePassword.dart';
import 'changeLanguage.dart';

class SettingScreen extends StatefulWidget {
  @override
  _SettingScreenState createState() => _SettingScreenState();
}

class _SettingScreenState extends State<SettingScreen> {
  bool isCallEnable = false;
  bool isDarkMode = false;
  bool isNotificationEnabled = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
    doctorProfile();
  }

  void _loadSettings() {
    setState(() {
      isDarkMode = SharedPreferenceHelper.getBoolean(Preferences.is_dark_mode);
      isNotificationEnabled =
          SharedPreferenceHelper.getBoolean(Preferences.is_notification_enabled);
    });
  }

  @override
  Widget build(BuildContext context) {
    final hasSubscription =
        SharedPreferenceHelper.getInt(Preferences.subscription_status) == 1;

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
          getTranslated(context, AppString.drawer_setting).toString(),
          style: const TextStyle(
            color: OslerTheme.textPrimary,
            fontSize: 20,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SingleChildScrollView(
        padding: OslerTheme.screenPadding,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeroCard(),
            const SizedBox(height: 18),
            _buildSection(
              title: getTranslated(context, AppString.settings_appearance)
                  .toString(),
              items: [
                _buildToggleItem(
                  icon: AppIcons.settings,
                  title: getTranslated(
                    context,
                    AppString.settings_dark_mode,
                  ).toString(),
                  value: isDarkMode,
                  color: const Color(0xFF7E8D9B),
                  onChanged: (val) async {
                    setState(() => isDarkMode = val);
                    // Use ThemeProvider for instant theme change
                    await context.read<ThemeProvider>().setDarkMode(val);
                    Fluttertoast.showToast(
                      msg: "Dark mode: ${val ? 'ON' : 'OFF'}",
                    );
                  },
                ),
                _buildNavigationItem(
                  icon: AppIcons.language2,
                  title: getTranslated(
                    context,
                    AppString.drawer_change_language,
                  ).toString(),
                  color: const Color(0xFFE0B65A),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ChangeLanguage()),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 18),
            _buildSection(
              title: getTranslated(
                context,
                AppString.settings_notifications_section,
              ).toString(),
              items: [
                _buildToggleItem(
                  icon: AppIcons.notifications,
                  title: getTranslated(
                    context,
                    AppString.settings_push_notifications,
                  ).toString(),
                  value: isNotificationEnabled,
                  color: const Color(0xFFE37C61),
                  onChanged: (val) {
                    setState(() => isNotificationEnabled = val);
                    SharedPreferenceHelper.setBoolean(
                      Preferences.is_notification_enabled,
                      val,
                    );
                  },
                ),
                _buildToggleItem(
                  icon: AppIcons.videoCall,
                  title: getTranslated(context, AppString.video_call).toString(),
                  subtitle: getTranslated(
                    context,
                    AppString.settings_video_call_desc,
                  ).toString(),
                  value: isCallEnable,
                  color: const Color(0xFF84A98C),
                  onChanged: (val) {
                    setState(() => isCallEnable = val);
                    updateVCall(val ? 1 : 0);
                  },
                ),
              ],
            ),
            const SizedBox(height: 18),
            _buildSection(
              title: getTranslated(
                context,
                AppString.settings_security_section,
              ).toString(),
              items: [
                _buildNavigationItem(
                  icon: AppIcons.password,
                  title: getTranslated(
                    context,
                    AppString.drawer_change_password,
                  ).toString(),
                  color: const Color(0xFF5B7F6A),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ChangePassword()),
                  ),
                ),
              ],
            ),
            if (hasSubscription) ...[
              const SizedBox(height: 18),
              _buildSection(
                title: getTranslated(
                  context,
                  AppString.settings_account_section,
                ).toString(),
                items: [
                  _buildNavigationItem(
                    icon: Icons.history_rounded,
                    title: getTranslated(
                      context,
                      AppString.drawer_subscription_history,
                    ).toString(),
                    color: OslerTheme.lime,
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => SubscriptionHistory(),
                      ),
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 18),
            _buildSection(
              title: getTranslated(
                context,
                AppString.settings_support_section,
              ).toString(),
              items: [
                _buildNavigationItem(
                  icon: Icons.support_agent_outlined,
                  title: "Contact Support",
                  color: const Color(0xFF7AA6D8),
                  onTap: () {
                    Fluttertoast.showToast(
                      msg: "Support ticket system coming soon",
                    );
                  },
                ),
                _buildNavigationItem(
                  icon: Icons.privacy_tip_outlined,
                  title: getTranslated(
                    context,
                    AppString.settings_privacy_policy,
                  ).toString(),
                  color: const Color(0xFF84A98C),
                  onTap: () {},
                ),
                _buildNavigationItem(
                  icon: Icons.description_outlined,
                  title: getTranslated(
                    context,
                    AppString.settings_terms_conditions,
                  ).toString(),
                  color: const Color(0xFF9A8F6A),
                  onTap: () {},
                ),
              ],
            ),
            const SizedBox(height: 22),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: _showDeleteAccountDialog,
                style: OutlinedButton.styleFrom(
                  foregroundColor: OslerTheme.danger,
                  side: const BorderSide(color: OslerTheme.danger),
                ),
                child: Text(
                  getTranslated(context, AppString.settings_delete_account)
                      .toString(),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeroCard() {
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
              "Workspace controls",
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 14),
          const Text(
            "Tune how your Osler desk behaves day to day.",
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              height: 1.05,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "Appearance, patient call controls, account security, and support live here.",
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

  Widget _buildSection({
    required String title,
    required List<Widget> items,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 10),
          child: Text(
            title.toUpperCase(),
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w800,
              color: OslerTheme.textSecondary,
              letterSpacing: 1.1,
            ),
          ),
        ),
        Container(
          decoration: OslerTheme.panelDecoration(),
          child: Column(
            children: List.generate(items.length, (index) {
              return Column(
                children: [
                  items[index],
                  if (index != items.length - 1)
                    const Divider(
                      height: 1,
                      indent: 68,
                      endIndent: 18,
                      color: OslerTheme.border,
                    ),
                ],
              );
            }),
          ),
        ),
      ],
    );
  }

  Widget _buildToggleItem({
    required IconData icon,
    required String title,
    String? subtitle,
    required bool value,
    required Color color,
    required ValueChanged<bool> onChanged,
  }) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      leading: _iconBadge(icon, color),
      title: Text(
        title,
        style: const TextStyle(
          fontSize: 15,
          fontWeight: FontWeight.w700,
          color: OslerTheme.textPrimary,
        ),
      ),
      subtitle: subtitle != null
          ? Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(
                subtitle,
                style: const TextStyle(
                  fontSize: 12,
                  color: OslerTheme.textSecondary,
                ),
              ),
            )
          : null,
      trailing: Switch.adaptive(
        value: value,
        activeColor: OslerTheme.forestDeep,
        activeTrackColor: OslerTheme.lime,
        onChanged: onChanged,
      ),
    );
  }

  Widget _buildNavigationItem({
    required IconData icon,
    required String title,
    required Color color,
    required VoidCallback onTap,
  }) {
    return ListTile(
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      leading: _iconBadge(icon, color),
      title: Text(
        title,
        style: const TextStyle(
          fontSize: 15,
          fontWeight: FontWeight.w700,
          color: OslerTheme.textPrimary,
        ),
      ),
      trailing: const Icon(
        Icons.arrow_forward_ios_rounded,
        size: 14,
        color: OslerTheme.textSecondary,
      ),
    );
  }

  Widget _iconBadge(IconData icon, Color color) {
    return Container(
      width: 42,
      height: 42,
      decoration: BoxDecoration(
        color: color.withOpacity(0.16),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Icon(icon, color: color, size: 22),
    );
  }

  void _showDeleteAccountDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: const Text(
          "Delete Account?",
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        content: const Text(
          "This action is permanent and cannot be undone. All your data will be removed from our servers.",
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Fluttertoast.showToast(msg: "Request submitted to admin");
            },
            child: const Text(
              "Delete",
              style: TextStyle(color: OslerTheme.danger),
            ),
          ),
        ],
      ),
    );
  }

  Future<BaseModel<DoctorProfile>> doctorProfile() async {
    DoctorProfile response;
    try {
      response =
          await RestClient(await RetroApi().dioData(context)).doctorProfile();
      if (response.data?.patientVCall != null) {
        setState(() => isCallEnable = response.data?.patientVCall == 1);
      }
    } catch (error) {
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<UpdateProfile>> updateVCall(vCallData) async {
    UpdateProfile response;
    Map<String, dynamic> body = {"patient_vcall": vCallData};
    try {
      response = await RestClient(await RetroApi().dioData(context))
          .updatePatientVcallRequest(body);
      if (response.success == true) {
        Fluttertoast.showToast(msg: response.msg!);
      }
    } catch (error) {
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }
}
