import 'package:flutter/material.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/services/astra_api_service.dart';

/// Widget to display Astra Fill health intake records submitted by patient
/// This shows symptoms, vitals, medical history that patient filled in their app
class AstraFillDisplayWidget extends StatefulWidget {
  final String patientId;
  final Map<String, dynamic>? preloadedData;

  const AstraFillDisplayWidget({
    Key? key,
    required this.patientId,
    this.preloadedData,
  }) : super(key: key);

  @override
  _AstraFillDisplayWidgetState createState() => _AstraFillDisplayWidgetState();
}

class _AstraFillDisplayWidgetState extends State<AstraFillDisplayWidget> {
  final AstraApiService _astraService = AstraApiService();
  Map<String, dynamic>? _astraFillData;
  bool _isLoading = true;
  bool _isExpanded = true;

  @override
  void initState() {
    super.initState();
    if (widget.preloadedData != null && widget.preloadedData!.isNotEmpty) {
      _astraFillData = widget.preloadedData;
      _isLoading = false;
    } else {
      _loadAstraFillData();
    }
  }

  Future<void> _loadAstraFillData() async {
    try {
      final data = await _astraService.getLatestAstraFill(widget.patientId);
      if (mounted) {
        setState(() {
          _astraFillData = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return _buildLoadingCard();
    }

    if (_astraFillData == null || _astraFillData!.isEmpty) {
      return _buildNoDataCard();
    }

    return _buildAstraFillCard();
  }

  Widget _buildLoadingCard() {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            SizedBox(
              width: 20, height: 20,
              child: CircularProgressIndicator(strokeWidth: 2, color: purple),
            ),
            SizedBox(width: 12),
            Text("Loading patient's health intake...", style: TextStyle(color: hintColor)),
          ],
        ),
      ),
    );
  }

  Widget _buildNoDataCard() {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.grey.shade100,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.info_outline, color: hintColor, size: 20),
            SizedBox(width: 12),
            Expanded(
              child: Text(
                "No health intake data available. Patient hasn't filled Astra form yet.",
                style: TextStyle(color: hintColor, fontSize: 13),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAstraFillCard() {
    // Standardize data from the NEW upgraded Astra Fill 20-parameter model Response
    final chiefComplaint = _astraFillData?['primary_complaint'] ?? _astraFillData?['chief_complaint'] ?? '';
    final duration = _astraFillData?['duration'] ?? '';
    final severityDetails = _astraFillData?['severity_clues'] ?? '';
    final timing = _astraFillData?['pattern_or_timing'] ?? '';
    
    // Ayurvedic / Lifestyle Parameters
    final sleepDetails = _astraFillData?['sleep'] ?? '';
    final appetiteDetails = _astraFillData?['appetite'] ?? '';
    final bowelDetails = _astraFillData?['bowel'] ?? '';
    final micturitionDetails = _astraFillData?['micturition'] ?? '';
    
    // Medical History
    final pastHistory = _astraFillData?['past_history'] ?? '';
    final previousTreatment = _astraFillData?['previous_treatment'] ?? '';
    
    // Boolean Flags
    final hasDiabetes = _astraFillData?['history_of_diabetes'] == true;
    final hasThyroid = _astraFillData?['history_of_thyroid'] == true;
    final hasBp = _astraFillData?['history_of_blood_pressure'] == true;
    
    // Legacy support handles
    final rawSymptoms = _astraFillData?['extracted_symptoms'] ?? _astraFillData?['symptoms'];
    final List<String> symptoms = rawSymptoms is List ? List<String>.from(rawSymptoms) : (rawSymptoms != null ? [rawSymptoms.toString()] : []);
    final currentMedications = _astraFillData?['current_medications'] ?? [];
    final timestamp = _astraFillData?['created_at'] ?? _astraFillData?['timestamp'] ?? '';
    final severityScore = _astraFillData?['severity_score'];

    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [purple.withOpacity(0.05), Colors.white],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            InkWell(
              onTap: () => setState(() => _isExpanded = !_isExpanded),
              borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
              child: Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: purple.withOpacity(0.1),
                  borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: purple,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(Icons.auto_awesome, color: Colors.white, size: 20),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Astra AI Health Intake",
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: purple,
                            ),
                          ),
                          if (timestamp.isNotEmpty)
                            Text(
                              "Submitted by patient",
                              style: TextStyle(fontSize: 12, color: hintColor),
                            ),
                        ],
                      ),
                    ),
                    if (severityScore != null)
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: _getSeverityColor(severityScore),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          "Severity: $severityScore/10",
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    SizedBox(width: 8),
                    Icon(
                      _isExpanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                      color: purple,
                    ),
                  ],
                ),
              ),
            ),

            // Expandable Content
            if (_isExpanded)
              Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Chief Complaint
                    if (chiefComplaint.toString().isNotEmpty)
                      _buildSection(
                        icon: Icons.report_problem_outlined,
                        title: "Primary Complaint",
                        content: chiefComplaint.toString(),
                        iconColor: Colors.orange,
                      ),
                      
                    // Severity & Timing
                    if (severityDetails.toString().isNotEmpty || timing.toString().isNotEmpty)
                      _buildSection(
                        icon: Icons.timeline,
                        title: "Pattern & Severity",
                        content: "${severityDetails.toString().isNotEmpty ? 'Severity: $severityDetails\n' : ''}"
                                 "${timing.toString().isNotEmpty ? 'Timing: $timing' : ''}",
                        iconColor: Colors.redAccent,
                      ),

                    // Duration
                    if (duration.toString().isNotEmpty)
                      _buildSection(
                        icon: Icons.schedule,
                        title: "Duration",
                        content: duration.toString(),
                        iconColor: Colors.blue,
                      ),

                    // Lifestyle & Ayurvedic Parameters
                    if (sleepDetails.toString().isNotEmpty || appetiteDetails.toString().isNotEmpty || bowelDetails.toString().isNotEmpty || micturitionDetails.toString().isNotEmpty)
                      _buildSection(
                        icon: Icons.self_improvement,
                        title: "Lifestyle & Ashtavidha Pariksha",
                        content: "${sleepDetails.toString().isNotEmpty ? '• Sleep: $sleepDetails\n' : ''}"
                                 "${appetiteDetails.toString().isNotEmpty ? '• Appetite: $appetiteDetails\n' : ''}"
                                 "${bowelDetails.toString().isNotEmpty ? '• Bowel: $bowelDetails\n' : ''}"
                                 "${micturitionDetails.toString().isNotEmpty ? '• Urine: $micturitionDetails' : ''}".trim(),
                        iconColor: Colors.green,
                      ),

                    // Medical Flags
                    if (hasDiabetes || hasThyroid || hasBp || pastHistory.toString().isNotEmpty)
                      _buildSection(
                        icon: Icons.history,
                        title: "Medical History",
                        content: "${hasDiabetes ? '⚠️ Diabetes\n' : ''}"
                                 "${hasThyroid ? '⚠️ Thyroid\n' : ''}"
                                 "${hasBp ? '⚠️ Blood Pressure\n' : ''}"
                                 "${pastHistory.toString().isNotEmpty ? 'Details: $pastHistory' : ''}".trim(),
                        iconColor: Colors.purple,
                      ),
                      
                    // Previous Treatment
                    if (previousTreatment.toString().isNotEmpty)
                      _buildSection(
                        icon: Icons.medication_liquid,
                        title: "Previous Treatment",
                        content: previousTreatment.toString(),
                        iconColor: Colors.teal,
                      ),

                    // Current Medications (Legacy/Standard)
                    if (currentMedications != null && (currentMedications as List).isNotEmpty)
                      _buildChipsSection(
                        icon: Icons.medication_outlined,
                        title: "Current Medications",
                        items: List<String>.from(currentMedications),
                        chipColor: Colors.green.shade50,
                        textColor: Colors.green.shade700,
                      ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({
    required IconData icon,
    required String title,
    required String content,
    required Color iconColor,
  }) {
    return Padding(
      padding: EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(icon, color: iconColor, size: 18),
          ),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: TextStyle(fontSize: 12, color: hintColor)),
                SizedBox(height: 4),
                Text(
                  content,
                  style: TextStyle(fontSize: 14, color: cardText, fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChipsSection({
    required IconData icon,
    required String title,
    required List<String> items,
    required Color chipColor,
    required Color textColor,
  }) {
    return Padding(
      padding: EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: textColor, size: 18),
              SizedBox(width: 8),
              Text(title, style: TextStyle(fontSize: 12, color: hintColor)),
            ],
          ),
          SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: items.map((item) => Container(
              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: chipColor,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: textColor.withOpacity(0.3)),
              ),
              child: Text(
                item,
                style: TextStyle(color: textColor, fontSize: 13, fontWeight: FontWeight.w500),
              ),
            )).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildVitalsSection(Map vitals) {
    return Padding(
      padding: EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.monitor_heart_outlined, color: Colors.red, size: 18),
              SizedBox(width: 8),
              Text("Vitals", style: TextStyle(fontSize: 12, color: hintColor)),
            ],
          ),
          SizedBox(height: 8),
          Container(
            padding: EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                if (vitals['blood_pressure'] != null)
                  _buildVitalItem("BP", vitals['blood_pressure'].toString(), Icons.favorite),
                if (vitals['heart_rate'] != null)
                  _buildVitalItem("HR", "${vitals['heart_rate']} bpm", Icons.monitor_heart),
                if (vitals['temperature'] != null)
                  _buildVitalItem("Temp", "${vitals['temperature']}°F", Icons.thermostat),
                if (vitals['oxygen_saturation'] != null || vitals['spo2'] != null)
                  _buildVitalItem("SpO2", "${vitals['oxygen_saturation'] ?? vitals['spo2']}%", Icons.air),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVitalItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.blue.shade700, size: 20),
        SizedBox(height: 4),
        Text(label, style: TextStyle(fontSize: 10, color: hintColor)),
        Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: cardText)),
      ],
    );
  }

  Widget _buildMedicalHistorySection(Map history) {
    List<String> conditions = [];
    
    if (history['conditions'] != null) {
      if (history['conditions'] is List) {
        conditions.addAll(List<String>.from(history['conditions']));
      } else {
        conditions.add(history['conditions'].toString());
      }
    }
    if (history['chronic_conditions'] != null) {
      if (history['chronic_conditions'] is List) {
        conditions.addAll(List<String>.from(history['chronic_conditions']));
      } else {
        conditions.add(history['chronic_conditions'].toString());
      }
    }
    if (history['past_surgeries'] != null) {
      if (history['past_surgeries'] is List) {
        conditions.addAll((history['past_surgeries'] as List).map((s) => "Surgery: $s"));
      } else {
        conditions.add("Surgery: ${history['past_surgeries'].toString()}");
      }
    }

    if (conditions.isEmpty) return SizedBox.shrink();

    return _buildChipsSection(
      icon: Icons.history,
      title: "Medical History",
      items: conditions,
      chipColor: Colors.purple.shade50,
      textColor: Colors.purple.shade700,
    );
  }

  Color _getSeverityColor(dynamic score) {
    int severity = score is int ? score : int.tryParse(score.toString()) ?? 0;
    if (severity <= 3) return Colors.green;
    if (severity <= 6) return Colors.orange;
    return Colors.red;
  }
}


/// Compact version for inline display (e.g., in prescription screen)
class AstraFillCompactWidget extends StatelessWidget {
  final Map<String, dynamic>? astraFillData;

  const AstraFillCompactWidget({Key? key, this.astraFillData}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (astraFillData == null || astraFillData!.isEmpty) {
      return SizedBox.shrink();
    }

    final rawSymptoms = astraFillData?['extracted_symptoms'] ?? 
                        astraFillData?['symptoms'];
    final List<String> symptoms = rawSymptoms is List 
        ? List<String>.from(rawSymptoms)
        : (rawSymptoms != null ? [rawSymptoms.toString()] : []);
    final severityScore = astraFillData?['severity_score'];

    return Card(
      color: purple.withOpacity(0.08),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.auto_awesome, color: purple, size: 18),
                SizedBox(width: 8),
                Text(
                  "Astra AI Summary",
                  style: TextStyle(fontWeight: FontWeight.bold, color: purple, fontSize: 14),
                ),
                Spacer(),
                if (severityScore != null)
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _getSeverityColor(severityScore),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      "$severityScore/10",
                      style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ),
              ],
            ),
            if (symptoms != null) ...[
              SizedBox(height: 8),
              Text(
                "Symptoms: ${symptoms is List ? symptoms.join(', ') : symptoms.toString()}",
                style: TextStyle(fontSize: 13, color: cardText),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getSeverityColor(dynamic score) {
    int severity = score is int ? score : int.tryParse(score.toString()) ?? 0;
    if (severity <= 3) return Colors.green;
    if (severity <= 6) return Colors.orange;
    return Colors.red;
  }
}
