import 'package:flutter/material.dart';
import 'package:doctro/services/astra_service.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/widgets/astra_fill_display.dart';
import 'dart:async';

class PrescriptionScreen extends StatefulWidget {
  final String patientId;
  final String patientName;
  final String? doctorId;

  const PrescriptionScreen({
    Key? key,
    required this.patientId,
    required this.patientName,
    this.doctorId,
  }) : super(key: key);

  @override
  _PrescriptionScreenState createState() => _PrescriptionScreenState();
}

class _PrescriptionScreenState extends State<PrescriptionScreen> {
  final _diagnosisController = TextEditingController();
  final AstraService _astraService = AstraService();
  
  List<Map<String, dynamic>> _medicines = [];
  bool _isLoading = false;
  Map<String, dynamic>? _patientData;

  @override
  void initState() {
    super.initState();
    _loadPatientData();
  }

  Future<void> _loadPatientData() async {
    setState(() => _isLoading = true);
    try {
      final data = await _astraService.getPatientView(widget.patientId);
      setState(() {
        _patientData = data;
        // Auto-fill diagnosis if available from AI intake
        if (data['latest_astra_fill'] != null && data['latest_astra_fill']['extracted_symptoms'] != null) {
           dynamic symptoms = data['latest_astra_fill']['extracted_symptoms'];
           if(symptoms != null) {
             String symptomsText = (symptoms is List) ? symptoms.join(', ') : symptoms.toString();
             _diagnosisController.text = "Possible condition related to: $symptomsText";
           }
        }
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Failed to load patient AI view")));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _addMedicine(Map<String, dynamic> medicine) {
    setState(() {
      _medicines.add({
        "name": medicine['medicine_name'], // Standardized key
        "shopify_variant_id": medicine['shopify_variant_id'],
        "price": medicine['price'],
        "dosage": "1 tablet", // Standardized key
        "frequency": "twice_daily", // Standardized key (once_daily, twice_daily, etc.)
        "timing": "After Food",
        "duration_days": 5, // Standardized key (must be int)
        "quantity": 1,
        "instructions": "",
      });
    });
  }

  void _updateMedicineQuantity(int index, int quantity) {
    setState(() {
      _medicines[index]['quantity'] = quantity;
    });
  }

  Future<void> _submitPrescription() async {
    if (_medicines.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Please add at least one medicine")));
      return;
    }

    setState(() => _isLoading = true);
    try {
      // Check if all medicines have shopify_variant_id
      bool allHaveShopify = _medicines.every((m) => m['shopify_variant_id'] != null);
      
      final payload = {
        "doctor_id": widget.doctorId ?? SharedPreferenceHelper.getString(Preferences.doctorId),
        "patient_id": widget.patientId,
        "diagnosis": _diagnosisController.text,
        "medicines": _medicines,
        "lifestyle_advice": "Rest and hydration", 
        "auto_process": true,
        "create_shopify_cart": allHaveShopify // Only attempt if possible
      };

      final response = await _astraService.submitPrescription(payload);
      
      String msg = "Prescription Sent via WhatsApp!";
      if (allHaveShopify) {
        msg += " & Shopify Cart Created!";
      } else {
        msg += "\n(Note: Some items were not in stock, Shopify cart skipped)";
      }

      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(msg),
        backgroundColor: allHaveShopify ? Colors.green : Colors.orange,
        duration: Duration(seconds: 4),
      ));
      
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Submission Failed: $e")));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showSearchSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => SearchMedicineSheet(
        onSelect: (medicine) {
          _addMedicine(medicine);
          Navigator.pop(context);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Prescription for ${widget.patientName}"),
        backgroundColor: colorWhite,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: _isLoading && _patientData == null
          ? Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 1. Patient AI Summary - Health intake from patient's app
                  if (_patientData != null && _patientData!['latest_astra_fill'] != null)
                    AstraFillCompactWidget(astraFillData: _patientData!['latest_astra_fill']),
                  
                  SizedBox(height: 20),
                  
                  // 2. Diagnosis
                  TextField(
                    controller: _diagnosisController,
                    decoration: InputDecoration(
                      labelText: "Diagnosis",
                      border: OutlineInputBorder(),
                      suffixIcon: Icon(Icons.medical_services),
                    ),
                  ),
                  
                  SizedBox(height: 20),
                  
                  // 3. Medicines List
                  Text("Medicines", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  ..._medicines.asMap().entries.map((entry) {
                    int idx = entry.key;
                    Map med = entry.value;
                    bool noShopify = med['shopify_variant_id'] == null;

                    return Card(
                      margin: EdgeInsets.only(bottom: 10),
                      color: noShopify ? Colors.orange.shade50 : Colors.white,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8.0),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: noShopify ? Colors.orange : Colors.purple,
                            child: Text("${idx + 1}", style: TextStyle(color: Colors.white))),
                          title: Row(
                            children: [
                              Expanded(child: Text(med['medicine_name'], style: TextStyle(fontWeight: FontWeight.bold))),
                              if (noShopify)
                                Tooltip(
                                  message: "Not available for Auto-Cart",
                                  child: Icon(Icons.warning_amber_rounded, color: Colors.orange, size: 20),
                                ),
                            ],
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text("${med['dosage']} | ${med['frequency']} | ${med['duration_days']} days"),
                              Row(
                                children: [
                                  Text("Qty: ", style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                                  DropdownButton<int>(
                                    value: med['quantity'],
                                    items: [1, 2, 3, 5, 10, 20, 30].map((int value) {
                                      return DropdownMenuItem<int>(
                                        value: value,
                                        child: Text(value.toString()),
                                      );
                                    }).toList(),
                                    onChanged: (val) => _updateMedicineQuantity(idx, val!),
                                  ),
                                  Spacer(),
                                  if (med['price'] != null)
                                    Text("₹ ${med['price']}", style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
                                ],
                              ),
                            ],
                          ),
                          trailing: IconButton(
                            icon: Icon(Icons.delete, color: Colors.red),
                            onPressed: () => setState(() => _medicines.removeAt(idx)),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                  
                  SizedBox(height: 10),
                  
                  // 4. Add Button
                  ElevatedButton.icon(
                    onPressed: _showSearchSheet,
                    icon: Icon(Icons.add),
                    label: Text("Add Medicine"),
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(double.infinity, 50),
                      backgroundColor: Colors.blue.shade50,
                      foregroundColor: Colors.blue,
                    ),
                  ),
                  
                  SizedBox(height: 30),
                  
                  // 5. Submit Button
                  ElevatedButton(
                    onPressed: _isLoading ? null : _submitPrescription,
                    child: _isLoading 
                      ? CircularProgressIndicator(color: Colors.white)
                      : Text("Submit & Automate (PDF + WhatsApp)"),
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(double.infinity, 50),
                      backgroundColor: Colors.purple,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildAISummaryCard(Map data) {
    return Card(
      color: Colors.purple.shade50,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.auto_awesome, color: Colors.purple),
                SizedBox(width: 8),
                Text("Astra AI Summary", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.purple)),
              ],
            ),
            SizedBox(height: 8),
            if (data['extracted_symptoms'] != null)
              Text("Symptoms: ${(data['extracted_symptoms'] as List).join(', ')}"),
            if (data['severity_score'] != null)
              Text("Severity Score: ${data['severity_score']}/10"),
          ],
        ),
      ),
    );
  }
}

class SearchMedicineSheet extends StatefulWidget {
  final Function(Map<String, dynamic>) onSelect;
  const SearchMedicineSheet({Key? key, required this.onSelect}) : super(key: key);

  @override
  _SearchMedicineSheetState createState() => _SearchMedicineSheetState();
}

class _SearchMedicineSheetState extends State<SearchMedicineSheet> {
  final _searchController = TextEditingController();
  final AstraService _astraService = AstraService();
  List _results = [];
  bool _isLoading = false;
  Timer? _debounce;

  void _onSearchChanged(String query) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      if (query.isNotEmpty) _performSearch(query);
    });
  }

  Future<void> _performSearch(String query) async {
    setState(() => _isLoading = true);
    try {
      final results = await _astraService.searchMedicines(query);
      setState(() => _results = results);
    } catch (e) {
      // handle error
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
      padding: EdgeInsets.all(16),
      child: Column(
        children: [
          Text("Search Medicines", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: "Type medicine name (e.g. Ashwagandha)",
              prefixIcon: Icon(Icons.search),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onChanged: _onSearchChanged,
          ),
          SizedBox(height: 10),
          Expanded(
            child: _isLoading 
              ? Center(child: CircularProgressIndicator())
              : ListView.builder(
                  itemCount: _results.length,
                  itemBuilder: (context, index) {
                    final item = _results[index];
                    return ListTile(
                      title: Text(item['medicine_name'] ?? 'Unknown'),
                      subtitle: Text("₹ ${item['price'] ?? '0'}"),
                      trailing: Icon(Icons.add_circle, color: Colors.green),
                      onTap: () => widget.onSelect(item),
                    );
                  },
                ),
          ),
        ],
      ),
    );
  }
}
