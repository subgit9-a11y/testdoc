import 'package:flutter/material.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/services/astra_api_service.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/theme/osler_theme.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/widgets/astra_fill_display.dart';
import 'dart:async';
import 'dart:typed_data';
import 'dart:convert';
import 'dart:ui' as ui;

class PrescriptionScreen extends StatefulWidget {
  final String patientId;
  final String patientName;
  final String? patientPhone;
  final String? doctorId;
  final Map<String, dynamic>? astraFillData;

  const PrescriptionScreen({
    Key? key,
    required this.patientId,
    required this.patientName,
    this.patientPhone,
    this.doctorId,
    this.astraFillData,
  }) : super(key: key);

  @override
  _PrescriptionScreenState createState() => _PrescriptionScreenState();
}

class _PrescriptionScreenState extends State<PrescriptionScreen> {
  final _diagnosisController = TextEditingController();
  final AstraApiService _astraApiService = AstraApiService();
  
  List<Map<String, dynamic>> _medicines = [];
  bool _isLoading = false;
  Map<String, dynamic>? _patientData;
  Uint8List? _signatureBytes;

  @override
  void dispose() {
    _diagnosisController.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    if (widget.astraFillData != null && widget.astraFillData!.isNotEmpty) {
      _patientData = {'latest_astra_fill': widget.astraFillData};
      _processAstraFillData(widget.astraFillData!);
    } else {
      _loadPatientData();
    }
  }

  void _processAstraFillData(Map<String, dynamic> astraFill) {
    if (astraFill['extracted_symptoms'] != null) {
      dynamic symptoms = astraFill['extracted_symptoms'];
      if (symptoms != null) {
        String symptomsText = (symptoms is List) ? symptoms.join(', ') : symptoms.toString();
        _diagnosisController.text = "Possible condition related to: $symptomsText";
      }
    }
  }

  Future<void> _loadPatientData() async {
    setState(() => _isLoading = true);
    try {
      final data = await _astraApiService.getPatientProfile(widget.patientId);
      if (!mounted) return;
      setState(() {
        _patientData = data;
        var latestFill = data['latest_astra_fill'];
        if (latestFill != null && latestFill is Map<String, dynamic> && latestFill.isNotEmpty) {
          _processAstraFillData(latestFill);
        } else {
          if (_patientData != null) _patientData!['latest_astra_fill'] = null;
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Failed to load patient AI view")));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _addMedicine(Map<String, dynamic> medicine) {
    setState(() {
      _medicines.add({
        "medicine_name": medicine['medicine_name'] ?? medicine['title'],
        "shopify_variant_id": medicine['shopify_variant_id'] ?? (medicine['variants'] != null && (medicine['variants'] as List).isNotEmpty ? medicine['variants'][0]['id'] : null),
        "price": medicine['price'] ?? (medicine['variants'] != null && (medicine['variants'] as List).isNotEmpty ? medicine['variants'][0]['price'] : null),
        "dosage": "1 tablet",
        "frequency": "twice_daily",
        "timing": "After Food",
        "duration_days": 5,
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

  Future<void> _suggestMedicines() async {
    if (_diagnosisController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Please enter a diagnosis or symptoms first")));
      return;
    }
    
    setState(() => _isLoading = true);
    try {
      // Use the unified AI Shop Assist endpoint
      final response = await _astraApiService.aiShopAssist({
        'symptoms': [_diagnosisController.text],
        'patient_id': widget.patientId,
        'precise': true
      });
      
      final suggestions = response['recommendations'] ?? response['medicines'] ?? [];
      
      if (!mounted) return;
      if (suggestions.isNotEmpty) {
        for (var med in suggestions) {
          _addMedicine(med);
        }
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("Added ${suggestions.length} AI suggested medicines"),
          backgroundColor: Colors.purple,
        ));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("No AI suggestions found. Try different symptoms or add medicines manually."),
          backgroundColor: OslerTheme.warning,
          duration: Duration(seconds: 3),
        ));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("AI Suggestion failed: $e. Check your connection."),
          backgroundColor: OslerTheme.danger,
        ));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _submitPrescription() async {
    if (_medicines.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Please add at least one medicine")));
      return;
    }

    if (_signatureBytes == null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Please provide your signature")));
      return;
    }

    setState(() => _isLoading = true);
    try {
      bool allHaveShopify = _medicines.every((m) => m['shopify_variant_id'] != null);
      
      final payload = {
        "doctor_id": widget.doctorId ?? SharedPreferenceHelper.getString(Preferences.doctorId),
        "patient_id": widget.patientId,
        "patient_name": widget.patientName,
        "patient_phone": widget.patientPhone,
        "diagnosis": _diagnosisController.text,
        "medicines": _medicines,
        "lifestyle_advice": "Rest and hydration", 
        "auto_process": true,
        "create_shopify_cart": allHaveShopify,
        "signature_image": base64Encode(_signatureBytes!),
      };

      // Use the unified executePrescriptionWorkflow instead of simple submit
      await _astraApiService.executePrescriptionWorkflow(payload);
      
      if (!mounted) return;

      String msg = "Prescription Sent via WhatsApp!";
      if (allHaveShopify) {
        msg += " & Shopify Cart Created!";
      } else {
        msg += "\n(Note: Some items were not in stock, Shopify cart skipped)";
      }

      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(msg),
        backgroundColor: allHaveShopify ? OslerTheme.forestDeep : OslerTheme.warning,
        duration: Duration(seconds: 4),
      ));
      
      Navigator.pop(context);
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Submission Failed: $e")));
    } finally {
      if (mounted) setState(() => _isLoading = false);
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

  Future<void> _showAllProducts() async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: Text("Loading All Products..."),
        content: Center(child: CircularProgressIndicator()),
      ),
    );
    try {
      final result = await _astraApiService.getAllShopifyProducts();
      if (!mounted) return;
      Navigator.pop(context);
      
      if (result['success'] == true) {
        final products = result['products'] as List? ?? [];
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          builder: (ctx) => Container(
            height: MediaQuery.of(context).size.height * 0.8,
            padding: EdgeInsets.all(16),
            child: Column(
              children: [
                Text("All Shopify Products (${products.length})", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                SizedBox(height: 10),
                Expanded(
                  child: products.isEmpty 
                    ? Center(child: Text("No products found"))
                    : ListView.builder(
                        itemCount: products.length,
                        itemBuilder: (ctx, i) {
                          final p = products[i];
                          return ListTile(
                            title: Text(p['title'] ?? p['medicine_name'] ?? 'Unknown'),
                            subtitle: Text("₹${p['price'] ?? '0'}"),
                            trailing: IconButton(
                              icon: Icon(Icons.add_circle, color: Colors.green),
                              onPressed: () {
                                _addMedicine(p);
                                Navigator.pop(ctx);
                              },
                            ),
                          );
                        },
                      ),
                ),
              ],
            ),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("Error: ${result['error']}"),
          backgroundColor: OslerTheme.danger,
        ));
      }
    } catch (e) {
      if (!mounted) return;
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text("Failed: $e"),
        backgroundColor: OslerTheme.danger,
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Prescription for ${widget.patientName}"),
        backgroundColor: OslerTheme.canvas,
        foregroundColor: OslerTheme.textPrimary,
        elevation: 0,
      ),
      body: _isLoading && _patientData == null
          ? Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (_patientData != null && _patientData!['latest_astra_fill'] != null)
                    AstraFillCompactWidget(astraFillData: _patientData!['latest_astra_fill']),
                  
                  SizedBox(height: 20),
                  
                  TextField(
                    controller: _diagnosisController,
                    decoration: InputDecoration(
                      labelText: "Diagnosis",
                      border: OutlineInputBorder(),
                      suffixIcon: Icon(Icons.medical_services),
                    ),
                  ),
                  
                  SizedBox(height: 20),
                  
                  Text("Medicines", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  ..._medicines.asMap().entries.map((entry) {
                    int idx = entry.key;
                    Map med = entry.value;
                    bool noShopify = med['shopify_variant_id'] == null;

                    return Card(
                      margin: EdgeInsets.only(bottom: 10),
                      color: noShopify ? OslerTheme.warning.withOpacity(0.1) : OslerTheme.surface,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8.0),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: noShopify ? OslerTheme.warning : OslerTheme.forestDeep,
                            child: Text("${idx + 1}", style: TextStyle(color: Colors.white))),
                          title: Row(
                            children: [
                              Expanded(child: Text(med['medicine_name'] ?? 'Unknown', style: TextStyle(fontWeight: FontWeight.bold))),
                              if (noShopify)
                                Tooltip(
                                  message: "Not available for Auto-Cart",
                                   child: Icon(Icons.warning_amber_rounded, color: OslerTheme.warning, size: 20),
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
                                     Text("₹ ${med['price']}", style: TextStyle(color: OslerTheme.forestDeep, fontWeight: FontWeight.bold)),
                                ],
                              ),
                            ],
                          ),
                          trailing: IconButton(
                            icon: Icon(AppIcons.delete, color: OslerTheme.danger),
                            onPressed: () => setState(() => _medicines.removeAt(idx)),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                  
                  SizedBox(height: 10),
                  
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _showSearchSheet,
                          icon: Icon(AppIcons.add),
                          label: Text("Add Medicine"),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue.shade50,
                            foregroundColor: Colors.blue,
                          ),
                        ),
                      ),
                      SizedBox(width: 10),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _isLoading ? null : _suggestMedicines,
                          icon: Icon(Icons.auto_awesome),
                          label: Text("AI Suggest"),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.purple.shade50,
                            foregroundColor: Colors.purple,
                          ),
                        ),
                      ),
                    ],
                  ),
                  
                  SizedBox(height: 30),

                  Text("Doctor Digital Signature", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  Container(
                    height: 150,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade300),
                      borderRadius: BorderRadius.circular(10),
                      color: Colors.white,
                    ),
                    child: DoctorSignaturePad(
                      onChanged: (bytes) {
                        setState(() {
                          _signatureBytes = bytes;
                        });
                      },
                    ),
                  ),
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton.icon(
                      onPressed: () => setState(() => _signatureBytes = null), 
                      icon: Icon(Icons.clear, size: 16),
                      label: Text("Clear Signature", style: TextStyle(fontSize: 12)),
                    ),
                  ),
                  
                  SizedBox(height: 20),
                  
                  ElevatedButton(
                    onPressed: _isLoading ? null : _submitPrescription,
                    child: _isLoading 
                      ? CircularProgressIndicator(color: Colors.white)
                      : Text("Submit & Automate (PDF + WhatsApp)"),
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(double.infinity, 50),
          backgroundColor: OslerTheme.forestDeep,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
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
  final AstraApiService _astraApiService = AstraApiService();
  List _results = [];
  bool _isLoading = false;
  bool _isSyncing = false;
  Timer? _debounce;

  @override
  void dispose() {
    _searchController.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    _loadAvailableMedicines();
  }

  Future<void> _loadAvailableMedicines() async {
    setState(() => _isLoading = true);
    try {
      final results = await _astraApiService.getAvailableMedicines();
      if (mounted) {
        setState(() => _results = results);
        if (results.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text("No medicines found. Tap 'Sync Shopify' to load products."),
            backgroundColor: OslerTheme.warning,
            duration: Duration(seconds: 4),
          ));
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("Failed to load medicines: $e"),
          backgroundColor: OslerTheme.danger,
        ));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _syncShopify() async {
    setState(() => _isSyncing = true);
    try {
      final response = await _astraApiService.syncShopifyProducts();
      await _loadAvailableMedicines();
      if (mounted) {
        final count = response['count'] ?? response['products_synced'] ?? response['total'] ?? 0;
        final message = response['message'] ?? response['status'] ?? '';
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("Shopify Sync: $count products loaded. $message"),
          backgroundColor: count > 0 ? Colors.green : OslerTheme.warning,
          duration: Duration(seconds: 4),
        ));
        debugPrint("Shopify Sync Response: $response");
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("Sync failed: $e"),
          backgroundColor: OslerTheme.danger,
          duration: Duration(seconds: 4),
        ));
        debugPrint("Shopify Sync Error: $e");
      }
    } finally {
      if (mounted) setState(() => _isSyncing = false);
    }
  }

  void _onSearchChanged(String query) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      if (query.isNotEmpty) {
        _performSearch(query);
      } else {
        _loadAvailableMedicines();
      }
    });
  }

  Future<void> _performSearch(String query) async {
    setState(() => _isLoading = true);
    try {
      final results = await _astraApiService.searchMedicineProducts(query);
      if (mounted) {
        setState(() => _results = results);
        if (results.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text("No medicines found for '$query'. Try different keywords."),
            backgroundColor: OslerTheme.warning,
            duration: Duration(seconds: 2),
          ));
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("Search failed: $e"),
          backgroundColor: OslerTheme.danger,
        ));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
      padding: EdgeInsets.all(16),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text("Search Medicines", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    Text("${_results.length} products loaded", style: TextStyle(fontSize: 12, color: OslerTheme.textSecondary)),
                  ],
                ),
              ),
              if (_isSyncing)
                SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
              else
                TextButton.icon(
                  onPressed: _syncShopify,
                  icon: Icon(Icons.sync, size: 16),
                  label: Text("Sync", style: TextStyle(fontSize: 12)),
                ),
              TextButton.icon(
                  onPressed: _showAllProducts,
                  icon: Icon(Icons.list, size: 16),
                  label: Text("All", style: TextStyle(fontSize: 12)),
                ),
            ],
          ),
          SizedBox(height: 10),
          TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: "Type medicine name (e.g. Ashwagandha)",
              prefixIcon: Icon(AppIcons.search),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onChanged: _onSearchChanged,
          ),
          SizedBox(height: 10),
          Expanded(
            child: _isLoading 
          ? Center(child: CircularProgressIndicator(color: OslerTheme.forestDeep))
              : ListView.builder(
                  itemCount: _results.length,
                  itemBuilder: (context, index) {
                    final item = _results[index];
                    return ListTile(
                      title: Text(item['medicine_name'] ?? item['title'] ?? 'Unknown'),
                      subtitle: Text("₹ ${item['price'] ?? (item['variants'] != null && (item['variants'] as List).isNotEmpty ? item['variants'][0]['price'] : '0')}"),
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

class DoctorSignaturePad extends StatefulWidget {
  final Function(Uint8List) onChanged;
  const DoctorSignaturePad({Key? key, required this.onChanged}) : super(key: key);

  @override
  _DoctorSignaturePadState createState() => _DoctorSignaturePadState();
}

class _DoctorSignaturePadState extends State<DoctorSignaturePad> {
  final List<Offset?> _points = [];

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanUpdate: (details) {
        setState(() {
          RenderBox renderBox = context.findRenderObject() as RenderBox;
          _points.add(renderBox.globalToLocal(details.globalPosition));
        });
      },
      onPanEnd: (details) async {
        _points.add(null);
        final bytes = await _captureSignature();
        if (bytes != null) {
          widget.onChanged(bytes);
        }
      },
      child: CustomPaint(
        painter: SignaturePainter(points: List.from(_points)),
        size: Size.infinite,
      ),
    );
  }

  Future<Uint8List?> _captureSignature() async {
    try {
      final recorder = ui.PictureRecorder();
      final canvas = Canvas(recorder, Rect.fromPoints(Offset(0, 0), Offset(500, 200)));
      
      final paint = Paint()
        ..color = Colors.black
        ..strokeCap = StrokeCap.round
        ..strokeWidth = 3.0;

      for (int i = 0; i < _points.length - 1; i++) {
        if (_points[i] != null && _points[i + 1] != null) {
          canvas.drawLine(_points[i]!, _points[i + 1]!, paint);
        }
      }

      final picture = recorder.endRecording();
      final img = await picture.toImage(500, 200);
      final ByteData? byteData = await img.toByteData(format: ui.ImageByteFormat.png);
      return byteData?.buffer.asUint8List();
    } catch (e) {
      return null;
    }
  }
}

class SignaturePainter extends CustomPainter {
  final List<Offset?> points;
  SignaturePainter({required this.points});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue.shade900
      ..strokeCap = StrokeCap.round
      ..strokeWidth = 3.0;

    for (int i = 0; i < points.length - 1; i++) {
      if (points[i] != null && points[i + 1] != null) {
        canvas.drawLine(points[i]!, points[i + 1]!, paint);
      }
    }
  }

  @override
  bool shouldRepaint(SignaturePainter oldDelegate) => true;
}
