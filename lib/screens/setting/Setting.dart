import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
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
      isNotificationEnabled = SharedPreferenceHelper.getBoolean(Preferences.is_notification_enabled);
    });
  }

  @override
  Widget build(BuildContext context) {
    double width = MediaQuery.of(context).size.width;

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FE),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.black, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          getTranslated(context, AppString.drawer_setting).toString(),
          style: const TextStyle(color: Colors.black, fontSize: 18, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            const SizedBox(height: 20),
            _buildSection(
              title: getTranslated(context, AppString.settings_appearance).toString(),
              items: [
                _buildToggleItem(
                  icon: Icons.dark_mode_outlined,
                  title: getTranslated(context, AppString.settings_dark_mode).toString(),
                  value: isDarkMode,
                  color: Colors.indigo,
                  onChanged: (val) {
                    setState(() => isDarkMode = val);
                    SharedPreferenceHelper.setBoolean(Preferences.is_dark_mode, val);
                    Fluttertoast.showToast(msg: "Theme updated (Restart to apply)");
                  },
                ),
                _buildNavigationItem(
                  icon: Icons.language_outlined,
                  title: getTranslated(context, AppString.drawer_change_language).toString(),
                  color: Colors.orange,
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => ChangeLanguage())),
                ),
              ],
            ),
            _buildSection(
              title: getTranslated(context, AppString.settings_notifications_section).toString(),
              items: [
                _buildToggleItem(
                  icon: Icons.notifications_active_outlined,
                  title: getTranslated(context, AppString.settings_push_notifications).toString(),
                  value: isNotificationEnabled,
                  color: Colors.red,
                  onChanged: (val) {
                    setState(() => isNotificationEnabled = val);
                    SharedPreferenceHelper.setBoolean(Preferences.is_notification_enabled, val);
                  },
                ),
                _buildToggleItem(
                  icon: Icons.videocam_outlined,
                  title: getTranslated(context, AppString.video_call).toString(),
                  subtitle: getTranslated(context, AppString.settings_video_call_desc).toString(),
                  value: isCallEnable,
                  color: Colors.blue,
                  onChanged: (val) {
                    setState(() => isCallEnable = val);
                    updateVCall(val ? 1 : 0);
                  },
                ),
              ],
            ),
            _buildSection(
              title: getTranslated(context, AppString.settings_security_section).toString(),
              items: [
                _buildNavigationItem(
                  icon: Icons.lock_outline,
                  title: getTranslated(context, AppString.drawer_change_password).toString(),
                  color: Colors.teal,
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => ChangePassword())),
                ),
              ],
            ),
            if (SharedPreferenceHelper.getInt(Preferences.subscription_status) == 1)
              _buildSection(
                title: getTranslated(context, AppString.settings_account_section).toString(),
                items: [
                  _buildNavigationItem(
                    icon: Icons.history,
                    title: getTranslated(context, AppString.drawer_subscription_history).toString(),
                    color: Colors.purple,
                    onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => SubscriptionHistory())),
                  ),
                ],
              ),
            _buildSection(
              title: getTranslated(context, AppString.settings_support_section).toString(),
              items: [
                _buildNavigationItem(
                  icon: Icons.support_agent_outlined,
                  title: "Contact Support",
                  color: Colors.blueAccent,
                  onTap: () {
                    Fluttertoast.showToast(msg: "Support ticket system coming soon");
                  },
                ),
                _buildNavigationItem(
                  icon: Icons.privacy_tip_outlined,
                  title: getTranslated(context, AppString.settings_privacy_policy).toString(),
                  color: Colors.green,
                  onTap: () {
                     // Open URL for privacy policy
                  },
                ),
                _buildNavigationItem(
                  icon: Icons.description_outlined,
                  title: getTranslated(context, AppString.settings_terms_conditions).toString(),
                  color: Colors.grey,
                  onTap: () {},
                ),
              ],
            ),
            const SizedBox(height: 20),
            _buildDeleteAccountButton(),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({required String title, required List<Widget> items}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 16, 24, 12),
          child: Text(
            title.toUpperCase(),
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
              letterSpacing: 1.2,
            ),
          ),
        ),
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.03),
                blurRadius: 10,
                spreadRadius: 0,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            children: List.generate(items.length, (index) {
              return Column(
                children: [
                  items[index],
                  if (index != items.length - 1)
                    Divider(height: 1, indent: 60, color: Colors.grey[100]),
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
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(10)),
        child: Icon(icon, color: color, size: 22),
      ),
      title: Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
      subtitle: subtitle != null ? Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.grey)) : null,
      trailing: Switch.adaptive(
        value: value,
        activeColor: purple,
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
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(10)),
        child: Icon(icon, color: color, size: 22),
      ),
      title: Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
      trailing: const Icon(Icons.arrow_forward_ios, size: 14, color: Colors.grey),
    );
  }

  Widget _buildDeleteAccountButton() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: TextButton(
        onPressed: () => _showDeleteAccountDialog(),
        child: Text(
          getTranslated(context, AppString.settings_delete_account).toString(),
          style: const TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  void _showDeleteAccountDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text("Delete Account?", style: TextStyle(fontWeight: FontWeight.bold)),
        content: const Text("This action is permanent and cannot be undone. All your data will be removed from our servers."),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
          TextButton(
            onPressed: () {
              // Call delete API
              Navigator.pop(context);
              Fluttertoast.showToast(msg: "Request submitted to admin");
            },
            child: const Text("Delete", style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  Future<BaseModel<DoctorProfile>> doctorProfile() async {
    DoctorProfile response;
    try {
      response = await RestClient(await RetroApi().dioData(context)).doctorProfile();
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
      response = await RestClient(await RetroApi().dioData(context)).updatePatientVcallRequest(body);
      if (response.success == true) {
        Fluttertoast.showToast(msg: response.msg!);
      }
    } catch (error) {
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }
}
