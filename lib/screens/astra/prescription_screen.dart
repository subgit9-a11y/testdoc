import 'package:flutter/material.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/services/astra_api_service.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/widgets/osler_button.dart';
import 'package:doctro/widgets/osler_card.dart';
import 'package:doctro/widgets/osler_dropdown.dart';
import 'package:doctro/widgets/osler_modal.dart';
import 'package:doctro/widgets/osler_alert.dart';
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
  final String? prescriptionId;
  final Map<String, dynamic>? astraFillData;

  const PrescriptionScreen({
    Key? key,
    required this.patientId,
    required this.patientName,
    this.patientPhone,
    this.doctorId,
    this.prescriptionId,
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
    final List variants = (medicine['variants'] is List) ? medicine['variants'] : [];
    final Map<String, dynamic>? firstVariant = variants.isNotEmpty && variants.first is Map<String, dynamic>
        ? variants.first as Map<String, dynamic>
        : null;

    final dynamic variantId = medicine['shopify_variant_id'] ??
        medicine['variant_id'] ??
        medicine['id'] ??
        firstVariant?['id'];

    final dynamic variantPrice = medicine['price'] ?? firstVariant?['price'];

    setState(() {
      _medicines.add({
        "medicine_name": medicine['medicine_name'] ?? medicine['title'],
        "shopify_variant_id": variantId,
        "price": variantPrice,
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

  Future<void> _editMedicineDetails(int index) async {
    final med = _medicines[index];
    final TextEditingController dosageController =
        TextEditingController(text: (med['dosage'] ?? '1 tablet').toString());
    final TextEditingController durationController =
        TextEditingController(text: (med['duration_days'] ?? 5).toString());
    final Map<String, String> frequencyLabelToValue = const {
      'Once daily': 'once_daily',
      'Twice daily': 'twice_daily',
      'Thrice daily': 'thrice_daily',
    };
    final Map<String, String> frequencyValueToLabel = const {
      'once_daily': 'Once daily',
      'twice_daily': 'Twice daily',
      'thrice_daily': 'Thrice daily',
    };
    final rawFrequency = (med['frequency'] ?? 'twice_daily').toString().toLowerCase();
    String frequencyLabel = frequencyValueToLabel[rawFrequency] ?? 'Twice daily';

    await showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text("Edit Dosage"),
          content: StatefulBuilder(
            builder: (context, setLocalState) {
              return Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    controller: dosageController,
                    decoration: const InputDecoration(labelText: "Dosage (e.g. 1 tablet)"),
                  ),
const SizedBox(height: 10),
                  OslerDropdown(
                    label: '',
                    hint: "Select frequency",
                    value: frequencyLabel,
                    items: const ['Once daily', 'Twice daily', 'Thrice daily'],
                    onChanged: (v) {
                      if (v != null) {
                        setLocalState(() => frequencyLabel = v);
                      }
                    },
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: durationController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: "Duration (days)"),
                  ),
                ],
              );
            },
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text("Cancel")),
            TextButton(
              onPressed: () {
                final int parsedDays = int.tryParse(durationController.text.trim()) ?? 5;
                setState(() {
                  _medicines[index]['dosage'] = dosageController.text.trim().isEmpty
                      ? '1 tablet'
                      : dosageController.text.trim();
                  _medicines[index]['frequency'] = frequencyLabelToValue[frequencyLabel] ?? 'twice_daily';
                  _medicines[index]['duration_days'] = parsedDays < 1 ? 1 : parsedDays;
                });
                Navigator.pop(context);
              },
              child: const Text("Save"),
            ),
          ],
        );
      },
    );
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
      final String doctorId = (widget.doctorId != null && widget.doctorId!.isNotEmpty)
          ? widget.doctorId!
          : SharedPreferenceHelper.getString(Preferences.doctorId);
      if (doctorId.isEmpty || doctorId == 'N_A') {
        throw Exception("Doctor ID missing. Please re-login once.");
      }

      bool allHaveShopify = _medicines.every((m) => m['shopify_variant_id'] != null && m['shopify_variant_id'].toString().isNotEmpty);
      
      final payload = {
        "prescription_id": (widget.prescriptionId != null && widget.prescriptionId!.trim().isNotEmpty)
            ? widget.prescriptionId!.trim()
            : "draft_${DateTime.now().millisecondsSinceEpoch}",
        "doctor_id": doctorId,
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
        backgroundColor: allHaveShopify ? AyurezeTheme.forestDeep : AyurezeTheme.warning,
        duration: Duration(seconds: 4),
      ));
      
      Navigator.pop(context);
    } catch (e) {
      final String err = e.toString();
      String message = err
          .replaceFirst('Exception: ', '')
          .replaceFirst('AstraApiException: ', '')
          .trim();
      if (message.isEmpty) {
        message = "Submission failed. Please try again.";
      }
      if (err.contains("Doctor ID missing")) {
        message = "Doctor session missing. Please login again.";
      } else if (err.contains("unreachable") || err.contains("Network error") || err.contains("connection") || err.contains("timeout")) {
        message = "Astra server unreachable. Check internet/VPN and retry.";
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message)),
        );
      }
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Prescription for ${widget.patientName}"),
        backgroundColor: AyurezeTheme.canvas,
        foregroundColor: AyurezeTheme.textPrimary,
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
                      color: noShopify ? AyurezeTheme.warning.withOpacity(0.1) : AyurezeTheme.surface,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8.0),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: noShopify ? AyurezeTheme.warning : AyurezeTheme.forestDeep,
                            child: Text("${idx + 1}", style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Theme.of(context).colorScheme.onPrimary))),
                          title: Row(
                            children: [
                              Expanded(child: Text(med['medicine_name'] ?? 'Unknown', style: TextStyle(fontWeight: FontWeight.bold))),
                              if (noShopify)
                                Tooltip(
                                  message: "Not available for Auto-Cart",
                                   child: Icon(Icons.warning_amber_rounded, color: AyurezeTheme.warning, size: 20),
                                ),
                            ],
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "${med['dosage']} | ${((med['frequency'] ?? '').toString().replaceAll('_', ' '))} | ${med['duration_days']} days",
                              ),
                              Row(
                                children: [
                                  IconButton(
                                    icon: Icon(Icons.edit, size: 18, color: AyurezeTheme.forestDeep),
                                    tooltip: "Edit dosage",
                                    onPressed: () => _editMedicineDetails(idx),
                                  ),
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
                                     Text("₹ ${med['price']}", style: TextStyle(color: AyurezeTheme.forestDeep, fontWeight: FontWeight.bold)),
                                ],
                              ),
                            ],
                          ),
                          trailing: IconButton(
                            icon: Icon(AppIcons.delete, color: AyurezeTheme.danger),
                            onPressed: () => setState(() => _medicines.removeAt(idx)),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                  
                  SizedBox(height: 16),
                  
                  ElevatedButton.icon(
                    onPressed: _showSearchSheet,
                    icon: Icon(AppIcons.add, size: 18),
                    label: Text("Add Medicine"),
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(double.infinity, 45),
                      backgroundColor: AyurezeTheme.forestDeep.withOpacity(0.08),
                      foregroundColor: AyurezeTheme.forestDeep,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                        side: BorderSide(color: AyurezeTheme.forestDeep.withOpacity(0.2)),
                      ),
                    ),
                  ),
                  
                  SizedBox(height: 32),

                  Text("Doctor Digital Signature", style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AyurezeTheme.textPrimary)),
                  SizedBox(height: 12),
                  Container(
                    height: 160,
                    width: double.infinity,
                    decoration: AyurezeTheme.panelDecoration(),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(28),
                      child: DoctorSignaturePad(
                        onChanged: (bytes) {
                          setState(() {
                            _signatureBytes = bytes;
                          });
                        },
                      ),
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
                  
                  OslerButton(
                    text: "Submit & Automate (PDF + WhatsApp)",
                    isLoading: _isLoading,
                    onPressed: _submitPrescription,
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
      List results = await _astraApiService.getAvailableMedicines();
      if (results.isEmpty) {
        final all = await _astraApiService.getAllShopifyProducts();
        if (all['success'] == true && all['products'] is List) {
          results = List.from(all['products']);
        }
      }
      if (mounted) {
        setState(() => _results = results);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Failed to load medicines")));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _syncShopify() async {
    setState(() => _isSyncing = true);
    try {
      await _astraApiService.syncShopifyProducts();
      await _loadAvailableMedicines();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Shopify Sync Complete")));
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Sync failed")));
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
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Search failed")));
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
              const Text("Search Medicines", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              if (_isSyncing)
                SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
              else
                TextButton.icon(
                  onPressed: _syncShopify,
                  icon: Icon(Icons.sync, size: 16),
                  label: Text("Sync Shopify"),
                ),
            ],
          ),
          SizedBox(height: 10),
          TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: "Type medicine name",
              prefixIcon: Icon(AppIcons.search),
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
                      title: Text(item['medicine_name'] ?? item['title'] ?? 'Unknown'),
                      subtitle: Text("₹ ${item['price'] ?? '0'}"),
                      trailing: Icon(Icons.add_circle, color: Theme.of(context).colorScheme.primary),
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
