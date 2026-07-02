import 'package:flutter/material.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:dio/dio.dart';
import 'package:doctro/retrofit/apis.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/widgets/osler_toast.dart';

class WithdrawScreen extends StatefulWidget {
  final double balance;
  
  WithdrawScreen({required this.balance});

  @override
  _WithdrawScreenState createState() => _WithdrawScreenState();
}

class _WithdrawScreenState extends State<WithdrawScreen> {
  final _amountController = TextEditingController();
  bool isProcessing = false;

  Future<void> submitWithdrawal() async {
    if (_amountController.text.isEmpty) return;
    double amount = double.tryParse(_amountController.text) ?? 0;
    
    if (amount <= 0 || amount > widget.balance) {
      OslerToast.error(context, "Invalid amount. Must be between 1 and ${widget.balance}");
      return;
    }

    setState(() {
      isProcessing = true;
    });

    try {
      int? doctorId = SharedPreferenceHelper.getInt(Preferences.doctorId);
      String url = "${Apis.baseUrl}finance/wallet/$doctorId/withdraw";
      
      var response = await Dio().post(url, data: {"amount": amount});
      if (response.statusCode == 200 && response.data['success']) {
        OslerToast.success(context, "Withdrawal successful via Cashfree");
        Navigator.pop(context);
      } else {
        OslerToast.error(context, response.data['error'] ?? "Withdrawal failed");
      }
    } catch (e) {
      OslerToast.error(context, "Withdrawal failed. Check bank details.");
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
        title: Text("Withdraw Funds", style: TextStyle(color: AyurezeTheme.textPrimary, fontWeight: FontWeight.w800)),
        leading: IconButton(
          icon: Icon(Icons.keyboard_backspace_outlined, color: AyurezeTheme.forestDeep, size: 35.0),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Available to Withdraw: ₹${widget.balance.toStringAsFixed(2)}", 
                 style: TextStyle(fontSize: 16, color: AyurezeTheme.textSecondary)),
            SizedBox(height: 24),
            TextField(
              controller: _amountController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: "Amount (₹)",
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            SizedBox(height: 32),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: AyurezeTheme.forestDeep,
                padding: EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                minimumSize: Size(double.infinity, 50),
              ),
              onPressed: isProcessing ? null : submitWithdrawal,
              child: isProcessing 
                ? CircularProgressIndicator(color: Colors.white)
                : Text("Confirm Payout", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
            )
          ],
        ),
      ),
    );
  }
}
