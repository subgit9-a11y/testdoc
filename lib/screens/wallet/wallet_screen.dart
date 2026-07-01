import 'package:flutter/material.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:dio/dio.dart';
import 'package:doctro/retrofit/apis.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'withdraw_screen.dart';
import 'bank_details_screen.dart';

class WalletScreen extends StatefulWidget {
  @override
  _WalletScreenState createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen> {
  bool isLoading = true;
  double availableBalance = 0.0;
  double totalEarned = 0.0;
  double withdrawnAmount = 0.0;

  @override
  void initState() {
    super.initState();
    fetchWalletData();
  }

  Future<void> fetchWalletData() async {
    setState(() {
      isLoading = true;
    });
    try {
      int? doctorId = SharedPreferenceHelper.getInt(Preferences.doctor_id);
      String url = "${Apis.baseUrl}finance/wallet/$doctorId";
      
      var response = await Dio().get(url);
      if (response.statusCode == 200 && response.data['success']) {
        var data = response.data['data'];
        setState(() {
          availableBalance = double.parse(data['available_balance'].toString());
          totalEarned = double.parse(data['total_earned'].toString());
          withdrawnAmount = double.parse(data['withdrawn_amount'].toString());
        });
      }
    } catch (e) {
      print("Error fetching wallet data: $e");
    } finally {
      setState(() {
        isLoading = false;
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
        title: Text(
          "My Earnings & Wallet",
          style: TextStyle(
            color: AyurezeTheme.textPrimary,
            fontWeight: FontWeight.w800,
          ),
        ),
        leading: IconButton(
          icon: Icon(
            Icons.keyboard_backspace_outlined,
            color: AyurezeTheme.forestDeep,
            size: 35.0,
          ),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: AyurezeTheme.forestDeep),
            onPressed: fetchWalletData,
          )
        ],
      ),
      body: isLoading
          ? Center(child: CircularProgressIndicator(color: AyurezeTheme.forestDeep))
          : SingleChildScrollView(
              padding: EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildBalanceCard(),
                  SizedBox(height: 24),
                  _buildStatsRow(),
                  SizedBox(height: 32),
                  _buildActionButtons(context),
                  SizedBox(height: 32),
                  Text(
                    "Recent Transactions",
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AyurezeTheme.textPrimary,
                    ),
                  ),
                  SizedBox(height: 16),
                  // Placeholder for transactions list
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.all(32.0),
                      child: Text(
                        "No recent transactions found.",
                        style: TextStyle(color: Colors.grey),
                      ),
                    ),
                  )
                ],
              ),
            ),
    );
  }

  Widget _buildBalanceCard() {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(24),
      decoration: AyurezeTheme.heroDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Available Balance",
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 16,
            ),
          ),
          SizedBox(height: 8),
          Text(
            "₹${availableBalance.toStringAsFixed(2)}",
            style: TextStyle(
              color: Colors.white,
              fontSize: 42,
              fontWeight: FontWeight.w900,
            ),
          ),
          SizedBox(height: 16),
          Text(
            "Ready for withdrawal.",
            style: TextStyle(
              color: Colors.white.withOpacity(0.9),
              fontSize: 14,
            ),
          )
        ],
      ),
    );
  }

  Widget _buildStatsRow() {
    return Row(
      children: [
        Expanded(
          child: _buildStatItem("Total Earned", "₹${totalEarned.toStringAsFixed(2)}", Colors.green),
        ),
        SizedBox(width: 16),
        Expanded(
          child: _buildStatItem("Withdrawn", "₹${withdrawnAmount.toStringAsFixed(2)}", Colors.orange),
        ),
      ],
    );
  }

  Widget _buildStatItem(String title, String value, Color color) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AyurezeTheme.surface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: Offset(0, 4),
          )
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              color: AyurezeTheme.textSecondary,
              fontSize: 14,
            ),
          ),
          SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButtons(BuildContext context) {
    return Column(
      children: [
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: AyurezeTheme.forestDeep,
            padding: EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            minimumSize: Size(double.infinity, 50),
          ),
          onPressed: () {
            Navigator.push(context, MaterialPageRoute(builder: (context) => WithdrawScreen(balance: availableBalance))).then((_) => fetchWalletData());
          },
          child: Text("Withdraw Funds", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
        ),
        SizedBox(height: 16),
        OutlinedButton(
          style: OutlinedButton.styleFrom(
            padding: EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            side: BorderSide(color: AyurezeTheme.forestDeep),
            minimumSize: Size(double.infinity, 50),
          ),
          onPressed: () {
            Navigator.push(context, MaterialPageRoute(builder: (context) => BankDetailsScreen()));
          },
          child: Text("Update Bank Details", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AyurezeTheme.forestDeep)),
        ),
      ],
    );
  }
}
