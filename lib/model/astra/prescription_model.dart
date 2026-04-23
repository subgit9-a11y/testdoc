/// Prescription models for Astra AI Healthcare
class AstraPrescription {
  final String? id;
  final String? prescriptionId;
  final String? doctorId;
  final String? patientId;
  final String? diagnosis;
  final List<MedicineItem>? medicines;
  final String? lifestyleAdvice;
  final String? dietaryRecommendations;
  final String? followUpDate;
  final String? notes;
  final String? status;
  final String? pdfUrl;
  final String? shopifyDraftOrderId;
  final bool? remindersCreated;
  final bool? whatsappSent;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  AstraPrescription({
    this.id,
    this.prescriptionId,
    this.doctorId,
    this.patientId,
    this.diagnosis,
    this.medicines,
    this.lifestyleAdvice,
    this.dietaryRecommendations,
    this.followUpDate,
    this.notes,
    this.status,
    this.pdfUrl,
    this.shopifyDraftOrderId,
    this.remindersCreated,
    this.whatsappSent,
    this.createdAt,
    this.updatedAt,
  });

  factory AstraPrescription.fromJson(Map<String, dynamic> json) {
    return AstraPrescription(
      id: json['id']?.toString(),
      prescriptionId: json['prescription_id']?.toString(),
      doctorId: json['doctor_id']?.toString(),
      patientId: json['patient_id']?.toString(),
      diagnosis: json['diagnosis'],
      medicines: json['medicines'] != null
          ? (json['medicines'] as List)
              .map((m) => MedicineItem.fromJson(m))
              .toList()
          : null,
      lifestyleAdvice: json['lifestyle_advice'],
      dietaryRecommendations: json['dietary_recommendations'],
      followUpDate: json['follow_up_date'],
      notes: json['notes'],
      status: json['status'],
      pdfUrl: json['pdf_url'],
      shopifyDraftOrderId: json['shopify_draft_order_id'],
      remindersCreated: json['reminders_created'],
      whatsappSent: json['whatsapp_sent'],
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
      if (prescriptionId != null) 'prescription_id': prescriptionId,
      if (doctorId != null) 'doctor_id': doctorId,
      if (patientId != null) 'patient_id': patientId,
      if (diagnosis != null) 'diagnosis': diagnosis,
      if (medicines != null) 'medicines': medicines!.map((m) => m.toJson()).toList(),
      if (lifestyleAdvice != null) 'lifestyle_advice': lifestyleAdvice,
      if (dietaryRecommendations != null) 'dietary_recommendations': dietaryRecommendations,
      if (followUpDate != null) 'follow_up_date': followUpDate,
      if (notes != null) 'notes': notes,
      if (status != null) 'status': status,
    };
  }
}

/// Medicine item in a prescription
class MedicineItem {
  final String? medicineName;
  final String? shopifyVariantId;
  final String? shopifyProductId;
  final String? dose;
  final String? schedule; // e.g., "1-0-1"
  final String? timing; // e.g., "After Food"
  final String? duration; // e.g., "7 days"
  final String? instructions;
  final int? quantity;
  final String? price;
  final bool? isAvailable;

  MedicineItem({
    this.medicineName,
    this.shopifyVariantId,
    this.shopifyProductId,
    this.dose,
    this.schedule,
    this.timing,
    this.duration,
    this.instructions,
    this.quantity,
    this.price,
    this.isAvailable,
  });

  factory MedicineItem.fromJson(Map<String, dynamic> json) {
    return MedicineItem(
      medicineName: json['medicine_name'] ?? json['name'],
      shopifyVariantId: json['shopify_variant_id']?.toString(),
      shopifyProductId: json['shopify_product_id']?.toString(),
      dose: json['dose'] ?? json['dosage'],
      schedule: json['schedule'],
      timing: json['timing'],
      duration: json['duration'],
      instructions: json['instructions'],
      quantity: json['quantity'],
      price: json['price']?.toString(),
      isAvailable: json['is_available'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (medicineName != null) 'medicine_name': medicineName,
      if (shopifyVariantId != null) 'shopify_variant_id': shopifyVariantId,
      if (shopifyProductId != null) 'shopify_product_id': shopifyProductId,
      if (dose != null) 'dose': dose,
      if (schedule != null) 'schedule': schedule,
      if (timing != null) 'timing': timing,
      if (duration != null) 'duration': duration,
      if (instructions != null) 'instructions': instructions,
      if (quantity != null) 'quantity': quantity,
    };
  }

  /// Get formatted schedule display
  String get scheduleDisplay {
    if (schedule != null) {
      final parts = schedule!.split('-');
      if (parts.length == 3) {
        List<String> times = [];
        if (parts[0] == '1') times.add('Morning');
        if (parts[1] == '1') times.add('Afternoon');
        if (parts[2] == '1') times.add('Night');
        return times.join(', ');
      }
    }
    return schedule ?? '';
  }
}

/// Prescription creation request
class CreatePrescriptionRequest {
  final String doctorId;
  final String patientId;
  final String diagnosis;
  final List<MedicineItem> medicines;
  final String? lifestyleAdvice;
  final String? dietaryRecommendations;
  final String? followUpDate;
  final String? notes;
  final bool autoProcess;

  CreatePrescriptionRequest({
    required this.doctorId,
    required this.patientId,
    required this.diagnosis,
    required this.medicines,
    this.lifestyleAdvice,
    this.dietaryRecommendations,
    this.followUpDate,
    this.notes,
    this.autoProcess = true,
  });

  Map<String, dynamic> toJson() {
    return {
      'doctor_id': doctorId,
      'patient_id': patientId,
      'diagnosis': diagnosis,
      'medicines': medicines.map((m) => m.toJson()).toList(),
      if (lifestyleAdvice != null) 'lifestyle_advice': lifestyleAdvice,
      if (dietaryRecommendations != null) 'dietary_recommendations': dietaryRecommendations,
      if (followUpDate != null) 'follow_up_date': followUpDate,
      if (notes != null) 'notes': notes,
      'auto_process': autoProcess,
    };
  }
}

/// Workflow result from unified prescription workflow
class WorkflowResult {
  final String? prescriptionId;
  final String? status;
  final String? pdfUrl;
  final String? shopifyDraftOrderUrl;
  final bool? remindersCreated;
  final bool? whatsappSent;
  final String? message;
  final List<String>? errors;

  WorkflowResult({
    this.prescriptionId,
    this.status,
    this.pdfUrl,
    this.shopifyDraftOrderUrl,
    this.remindersCreated,
    this.whatsappSent,
    this.message,
    this.errors,
  });

  factory WorkflowResult.fromJson(Map<String, dynamic> json) {
    return WorkflowResult(
      prescriptionId: json['prescription_id']?.toString(),
      status: json['status'],
      pdfUrl: json['pdf_url'],
      shopifyDraftOrderUrl: json['shopify_draft_order_url'],
      remindersCreated: json['reminders_created'],
      whatsappSent: json['whatsapp_sent'],
      message: json['message'],
      errors: json['errors'] != null
          ? List<String>.from(json['errors'])
          : null,
    );
  }

  bool get isSuccess => status == 'success' || status == 'completed';
  bool get hasErrors => errors != null && errors!.isNotEmpty;
}
