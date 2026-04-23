/// AI Response models for Astra Brain
class AIChatResponse {
  final String? response;
  final String? intent;
  final String? capability;
  final double? confidence;
  final Map<String, dynamic>? metadata;
  final List<String>? suggestedActions;
  final String? sessionId;

  AIChatResponse({
    this.response,
    this.intent,
    this.capability,
    this.confidence,
    this.metadata,
    this.suggestedActions,
    this.sessionId,
  });

  factory AIChatResponse.fromJson(Map<String, dynamic> json) {
    return AIChatResponse(
      response: json['response'],
      intent: json['intent'],
      capability: json['capability'],
      confidence: json['confidence']?.toDouble(),
      metadata: json['metadata'],
      suggestedActions: json['suggested_actions'] != null
          ? List<String>.from(json['suggested_actions'])
          : null,
      sessionId: json['session_id'],
    );
  }
}

/// AI Chat Request
class AIChatRequest {
  final String q;
  final String userId;
  final String? profileId;
  final Map<String, dynamic>? userMetadata;
  final String? sessionId;
  final String? context;

  AIChatRequest({
    required this.q,
    required this.userId,
    this.profileId,
    this.userMetadata,
    this.sessionId,
    this.context,
  });

  Map<String, dynamic> toJson() {
    return {
      'q': q,
      'user_id': userId,
      if (profileId != null) 'profile_id': profileId,
      if (userMetadata != null) 'user_metadata': userMetadata,
      if (sessionId != null) 'session_id': sessionId,
      if (context != null) 'context': context,
    };
  }
}

/// Doctor Summary Response from AI
class DoctorSummaryResponse {
  final String? summary;
  final String? clinicalNotes;
  final List<String>? keyFindings;
  final List<String>? recommendations;
  final String? differentialDiagnosis;
  final String? riskAssessment;

  DoctorSummaryResponse({
    this.summary,
    this.clinicalNotes,
    this.keyFindings,
    this.recommendations,
    this.differentialDiagnosis,
    this.riskAssessment,
  });

  factory DoctorSummaryResponse.fromJson(Map<String, dynamic> json) {
    return DoctorSummaryResponse(
      summary: json['summary'],
      clinicalNotes: json['clinical_notes'],
      keyFindings: json['key_findings'] != null
          ? List<String>.from(json['key_findings'])
          : null,
      recommendations: json['recommendations'] != null
          ? List<String>.from(json['recommendations'])
          : null,
      differentialDiagnosis: json['differential_diagnosis'],
      riskAssessment: json['risk_assessment'],
    );
  }
}

/// Safety Analysis Response
class SafetyAnalysisResponse {
  final bool? isSafe;
  final List<String>? warnings;
  final List<DrugInteraction>? interactions;
  final List<String>? contraindications;
  final String? overallRisk;
  final String? recommendation;

  SafetyAnalysisResponse({
    this.isSafe,
    this.warnings,
    this.interactions,
    this.contraindications,
    this.overallRisk,
    this.recommendation,
  });

  factory SafetyAnalysisResponse.fromJson(Map<String, dynamic> json) {
    return SafetyAnalysisResponse(
      isSafe: json['is_safe'],
      warnings: json['warnings'] != null
          ? List<String>.from(json['warnings'])
          : null,
      interactions: json['interactions'] != null
          ? (json['interactions'] as List)
              .map((i) => DrugInteraction.fromJson(i))
              .toList()
          : null,
      contraindications: json['contraindications'] != null
          ? List<String>.from(json['contraindications'])
          : null,
      overallRisk: json['overall_risk'],
      recommendation: json['recommendation'],
    );
  }
}

/// Drug Interaction Details
class DrugInteraction {
  final String? drug1;
  final String? drug2;
  final String? severity; // "mild", "moderate", "severe"
  final String? description;
  final String? recommendation;

  DrugInteraction({
    this.drug1,
    this.drug2,
    this.severity,
    this.description,
    this.recommendation,
  });

  factory DrugInteraction.fromJson(Map<String, dynamic> json) {
    return DrugInteraction(
      drug1: json['drug1'] ?? json['drug_1'],
      drug2: json['drug2'] ?? json['drug_2'],
      severity: json['severity'],
      description: json['description'],
      recommendation: json['recommendation'],
    );
  }
}

/// Medication Schedule Extraction Response
class ScheduleExtractionResponse {
  final List<ExtractedMedicine>? medicines;
  final String? rawText;
  final double? confidence;
  final List<String>? warnings;

  ScheduleExtractionResponse({
    this.medicines,
    this.rawText,
    this.confidence,
    this.warnings,
  });

  factory ScheduleExtractionResponse.fromJson(Map<String, dynamic> json) {
    return ScheduleExtractionResponse(
      medicines: json['medicines'] != null
          ? (json['medicines'] as List)
              .map((m) => ExtractedMedicine.fromJson(m))
              .toList()
          : null,
      rawText: json['raw_text'],
      confidence: json['confidence']?.toDouble(),
      warnings: json['warnings'] != null
          ? List<String>.from(json['warnings'])
          : null,
    );
  }
}

/// Extracted Medicine from AI
class ExtractedMedicine {
  final String? name;
  final String? dose;
  final String? frequency;
  final String? timing;
  final String? duration;
  final String? instructions;
  final double? confidence;

  ExtractedMedicine({
    this.name,
    this.dose,
    this.frequency,
    this.timing,
    this.duration,
    this.instructions,
    this.confidence,
  });

  factory ExtractedMedicine.fromJson(Map<String, dynamic> json) {
    return ExtractedMedicine(
      name: json['name'] ?? json['medicine_name'],
      dose: json['dose'] ?? json['dosage'],
      frequency: json['frequency'],
      timing: json['timing'],
      duration: json['duration'],
      instructions: json['instructions'],
      confidence: json['confidence']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (name != null) 'medicine_name': name,
      if (dose != null) 'dose': dose,
      if (frequency != null) 'frequency': frequency,
      if (timing != null) 'timing': timing,
      if (duration != null) 'duration': duration,
      if (instructions != null) 'instructions': instructions,
    };
  }
}

/// Profile Analysis Response
class ProfileAnalysisResponse {
  final String? riskLevel;
  final List<String>? healthRisks;
  final List<String>? recommendations;
  final Map<String, dynamic>? lifestyleScore;
  final String? summary;

  ProfileAnalysisResponse({
    this.riskLevel,
    this.healthRisks,
    this.recommendations,
    this.lifestyleScore,
    this.summary,
  });

  factory ProfileAnalysisResponse.fromJson(Map<String, dynamic> json) {
    return ProfileAnalysisResponse(
      riskLevel: json['risk_level'],
      healthRisks: json['health_risks'] != null
          ? List<String>.from(json['health_risks'])
          : null,
      recommendations: json['recommendations'] != null
          ? List<String>.from(json['recommendations'])
          : null,
      lifestyleScore: json['lifestyle_score'],
      summary: json['summary'],
    );
  }
}

/// Wellness Recommendation Response
class WellnessRecommendation {
  final String? category;
  final String? recommendation;
  final String? priority;
  final List<String>? tips;
  final String? ayurvedicAdvice;

  WellnessRecommendation({
    this.category,
    this.recommendation,
    this.priority,
    this.tips,
    this.ayurvedicAdvice,
  });

  factory WellnessRecommendation.fromJson(Map<String, dynamic> json) {
    return WellnessRecommendation(
      category: json['category'],
      recommendation: json['recommendation'],
      priority: json['priority'],
      tips: json['tips'] != null ? List<String>.from(json['tips']) : null,
      ayurvedicAdvice: json['ayurvedic_advice'],
    );
  }
}

/// Shop Assist Response
class ShopAssistResponse {
  final List<ProductRecommendation>? recommendations;
  final String? message;
  final double? totalPrice;
  final String? checkoutUrl;

  ShopAssistResponse({
    this.recommendations,
    this.message,
    this.totalPrice,
    this.checkoutUrl,
  });

  factory ShopAssistResponse.fromJson(Map<String, dynamic> json) {
    return ShopAssistResponse(
      recommendations: json['recommendations'] != null
          ? (json['recommendations'] as List)
              .map((r) => ProductRecommendation.fromJson(r))
              .toList()
          : null,
      message: json['message'],
      totalPrice: json['total_price']?.toDouble(),
      checkoutUrl: json['checkout_url'],
    );
  }
}

/// Product Recommendation from AI
class ProductRecommendation {
  final String? productId;
  final String? variantId;
  final String? name;
  final String? description;
  final double? price;
  final String? imageUrl;
  final bool? inStock;
  final String? reason;
  final double? matchScore;

  ProductRecommendation({
    this.productId,
    this.variantId,
    this.name,
    this.description,
    this.price,
    this.imageUrl,
    this.inStock,
    this.reason,
    this.matchScore,
  });

  factory ProductRecommendation.fromJson(Map<String, dynamic> json) {
    return ProductRecommendation(
      productId: json['product_id']?.toString(),
      variantId: json['variant_id']?.toString() ?? json['shopify_variant_id']?.toString(),
      name: json['name'] ?? json['medicine_name'],
      description: json['description'],
      price: json['price']?.toDouble(),
      imageUrl: json['image_url'],
      inStock: json['in_stock'] ?? json['is_available'],
      reason: json['reason'],
      matchScore: json['match_score']?.toDouble(),
    );
  }
}
