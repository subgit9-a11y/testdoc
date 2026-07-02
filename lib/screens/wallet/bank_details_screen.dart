import 'package:flutter/material.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:dio/dio.dart';
import 'package:doctro/retrofit/apis.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/widgets/osler_toast.dart';

class BankDetailsScreen extends StatefulWidget {
  @override
  _BankDetailsScreenState createState() => _BankDetailsScreenState();
}

class _BankDetailsScreenState extends State<BankDetailsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _accountController = TextEditingController();
  final _ifscController = TextEditingController();
  final _nameController = TextEditingController();
  final _upiController = TextEditingController();
  bool isProcessing = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  Future<void> saveDetails() async {
    bool isUpiTab = _tabController.index == 1;

    if (!isUpiTab) {
      if (_accountController.text.isEmpty || _ifscController.text.isEmpty || _nameController.text.isEmpty) {
        OslerToast.error(context, "All bank details are required");
        return;
      }
    } else {
      if (_upiController.text.isEmpty || _nameController.text.isEmpty) {
        OslerToast.error(context, "Name and UPI ID are required");
        return;
      }
    }

    setState(() {
      isProcessing = true;
    });

    try {
      int? doctorId = SharedPreferenceHelper.getInt(Preferences.doctorId);
      String url = "${Apis.baseUrl}finance/wallet/$doctorId/bank-details";
      
      Map<String, dynamic> data = {
        "account_holder_name": _nameController.text
      };
      
      if (isUpiTab) {
        data["upi_id"] = _upiController.text;
      } else {
        data["bank_account_number"] = _accountController.text;
        data["bank_ifsc"] = _ifscController.text;
      }

      var response = await Dio().post(url, data: data);
      
      if (response.statusCode == 200 && response.data['success']) {
        OslerToast.success(context, "Payment details saved successfully");
        Navigator.pop(context);
      } else {
        OslerToast.error(context, response.data['error'] ?? "Failed to save details");
      }
    } catch (e) {
      OslerToast.error(context, "Failed to save details.");
      print(e);
    } finally {
      setState(() {
        isProcessing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AyurezeTheme.canvas,
      appBar: AppBar(
        backgroundColor: AyurezeTheme.canvas,
        elevation: 0,
        title: Text("Payment Details", style: TextStyle(color: AyurezeTheme.textPrimary, fontWeight: FontWeight.w800)),
        leading: IconButton(
          icon: Icon(Icons.keyboard_backspace_outlined, color: AyurezeTheme.forestDeep, size: 35.0),
          onPressed: () => Navigator.pop(context),
        ),
        bottom: TabBar(
          controller: _tabController,
          labelColor: AyurezeTheme.forestDeep,
          unselectedLabelColor: AyurezeTheme.textSecondary,
          indicatorColor: AyurezeTheme.forestDeep,
          tabs: [
            Tab(text: "Bank Account"),
            Tab(text: "UPI ID"),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildBankForm(),
          _buildUpiForm(),
        ],
      ),
    );
  }

  Widget _buildBankForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Enter your bank details for Cashfree payouts.", 
               style: TextStyle(fontSize: 16, color: AyurezeTheme.textSecondary)),
          SizedBox(height: 24),
          _buildNameField(),
          SizedBox(height: 16),
          TextField(
            controller: _accountController,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(
              labelText: "Bank Account Number",
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
          SizedBox(height: 16),
          TextField(
            controller: _ifscController,
            decoration: InputDecoration(
              labelText: "IFSC Code",
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
          SizedBox(height: 32),
          _buildSaveButton(),
        ],
      ),
    );
  }

  Widget _buildUpiForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Enter your UPI ID (VPA) for instant payouts.", 
               style: TextStyle(fontSize: 16, color: AyurezeTheme.textSecondary)),
          SizedBox(height: 24),
          _buildNameField(),
          SizedBox(height: 16),
          TextField(
            controller: _upiController,
            decoration: InputDecoration(
              labelText: "UPI ID (e.g., name@okicici)",
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
          SizedBox(height: 32),
          _buildSaveButton(),
        ],
      ),
    );
  }

  Widget _buildNameField() {
    return TextField(
      controller: _nameController,
      decoration: InputDecoration(
        labelText: "Account Holder Name",
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  Widget _buildSaveButton() {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: AyurezeTheme.forestDeep,
        padding: EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        minimumSize: Size(double.infinity, 50),
      ),
      onPressed: isProcessing ? null : saveDetails,
      child: isProcessing 
        ? CircularProgressIndicator(color: Colors.white)
        : Text("Save Details", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
    );
  }
}

