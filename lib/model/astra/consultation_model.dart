/// Consultation model for Astra AI Healthcare
class Consultation {
  final String? id;
  final String? consultationId;
  final String? doctorId;
  final String? patientId;
  final String? chiefComplaint;
  final List<String>? symptoms;
  final String? diagnosis;
  final String? prescriptionId;
  final String? notes;
  final String? status;
  final String? type; // "in-person", "video", "chat"
  final String? vitals;
  final DateTime? consultationDate;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  Consultation({
    this.id,
    this.consultationId,
    this.doctorId,
    this.patientId,
    this.chiefComplaint,
    this.symptoms,
    this.diagnosis,
    this.prescriptionId,
    this.notes,
    this.status,
    this.type,
    this.vitals,
    this.consultationDate,
    this.createdAt,
    this.updatedAt,
  });

  factory Consultation.fromJson(Map<String, dynamic> json) {
    return Consultation(
      id: json['id']?.toString(),
      consultationId: json['consultation_id']?.toString(),
      doctorId: json['doctor_id']?.toString(),
      patientId: json['patient_id']?.toString(),
      chiefComplaint: json['chief_complaint'],
      symptoms: json['symptoms'] != null
          ? List<String>.from(json['symptoms'])
          : null,
      diagnosis: json['diagnosis'],
      prescriptionId: json['prescription_id']?.toString(),
      notes: json['notes'],
      status: json['status'],
      type: json['type'] ?? json['consultation_type'],
      vitals: json['vitals'],
      consultationDate: json['consultation_date'] != null
          ? DateTime.parse(json['consultation_date'])
          : null,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      if (consultationId != null) 'consultation_id': consultationId,
      if (doctorId != null) 'doctor_id': doctorId,
      if (patientId != null) 'patient_id': patientId,
      if (chiefComplaint != null) 'chief_complaint': chiefComplaint,
      if (symptoms != null) 'symptoms': symptoms,
      if (diagnosis != null) 'diagnosis': diagnosis,
      if (prescriptionId != null) 'prescription_id': prescriptionId,
      if (notes != null) 'notes': notes,
      if (status != null) 'status': status,
      if (type != null) 'type': type,
      if (vitals != null) 'vitals': vitals,
      if (consultationDate != null)
        'consultation_date': consultationDate!.toIso8601String(),
    };
  }
}

/// Consultation creation request
class CreateConsultationRequest {
  final String doctorId;
  final String patientId;
  final String chiefComplaint;
  final List<String>? symptoms;
  final String? diagnosis;
  final String? notes;
  final String type;
  final VitalsData? vitals;

  CreateConsultationRequest({
    required this.doctorId,
    required this.patientId,
    required this.chiefComplaint,
    this.symptoms,
    this.diagnosis,
    this.notes,
    this.type = 'in-person',
    this.vitals,
  });

  Map<String, dynamic> toJson() {
    return {
      'doctor_id': doctorId,
      'patient_id': patientId,
      'chief_complaint': chiefComplaint,
      if (symptoms != null) 'symptoms': symptoms,
      if (diagnosis != null) 'diagnosis': diagnosis,
      if (notes != null) 'notes': notes,
      'type': type,
      if (vitals != null) 'vitals': vitals!.toJson(),
    };
  }
}

/// Vitals data for consultation
class VitalsData {
  final double? temperature;
  final String? bloodPressure;
  final int? pulseRate;
  final int? respiratoryRate;
  final double? oxygenSaturation;
  final double? weight;
  final double? height;
  final String? bloodSugar;

  VitalsData({
    this.temperature,
    this.bloodPressure,
    this.pulseRate,
    this.respiratoryRate,
    this.oxygenSaturation,
    this.weight,
    this.height,
    this.bloodSugar,
  });

  factory VitalsData.fromJson(Map<String, dynamic> json) {
    return VitalsData(
      temperature: json['temperature']?.toDouble(),
      bloodPressure: json['blood_pressure'],
      pulseRate: json['pulse_rate'],
      respiratoryRate: json['respiratory_rate'],
      oxygenSaturation: json['oxygen_saturation']?.toDouble(),
      weight: json['weight']?.toDouble(),
      height: json['height']?.toDouble(),
      bloodSugar: json['blood_sugar'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (temperature != null) 'temperature': temperature,
      if (bloodPressure != null) 'blood_pressure': bloodPressure,
      if (pulseRate != null) 'pulse_rate': pulseRate,
      if (respiratoryRate != null) 'respiratory_rate': respiratoryRate,
      if (oxygenSaturation != null) 'oxygen_saturation': oxygenSaturation,
      if (weight != null) 'weight': weight,
      if (height != null) 'height': height,
      if (bloodSugar != null) 'blood_sugar': bloodSugar,
    };
  }

  /// Get BMI if height and weight available
  double? get bmi {
    if (height != null && weight != null && height! > 0) {
      final heightInMeters = height! / 100;
      return weight! / (heightInMeters * heightInMeters);
    }
    return null;
  }
}

/// AI-extracted health intake from patient conversation
class HealthIntake {
  final String? patientId;
  final List<String>? extractedSymptoms;
  final String? chiefComplaint;
  final String? duration;
  final String? severity;
  final List<String>? associatedSymptoms;
  final String? medicalHistory;
  final List<String>? currentMedications;
  final List<String>? allergies;
  final String? aiSummary;
  final DateTime? extractedAt;

  HealthIntake({
    this.patientId,
    this.extractedSymptoms,
    this.chiefComplaint,
    this.duration,
    this.severity,
    this.associatedSymptoms,
    this.medicalHistory,
    this.currentMedications,
    this.allergies,
    this.aiSummary,
    this.extractedAt,
  });

  factory HealthIntake.fromJson(Map<String, dynamic> json) {
    return HealthIntake(
      patientId: json['patient_id']?.toString(),
      extractedSymptoms: json['extracted_symptoms'] != null
          ? List<String>.from(json['extracted_symptoms'])
          : null,
      chiefComplaint: json['chief_complaint'],
      duration: json['duration'],
      severity: json['severity'],
      associatedSymptoms: json['associated_symptoms'] != null
          ? List<String>.from(json['associated_symptoms'])
          : null,
      medicalHistory: json['medical_history'],
      currentMedications: json['current_medications'] != null
          ? List<String>.from(json['current_medications'])
          : null,
      allergies: json['allergies'] != null
          ? List<String>.from(json['allergies'])
          : null,
      aiSummary: json['ai_summary'],
      extractedAt: json['extracted_at'] != null
          ? DateTime.parse(json['extracted_at'])
          : null,
    );
  }
}
