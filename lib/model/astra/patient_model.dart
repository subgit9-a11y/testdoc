/// Patient model for Astra AI Healthcare
class AstraPatient {
  final String? id;
  final String? patientId;
  final String? name;
  final String? phone;
  final String? email;
  final int? age;
  final String? gender;
  final String? dateOfBirth;
  final String? address;
  final String? city;
  final String? state;
  final String? pincode;
  final List<String>? allergies;
  final List<String>? chronicConditions;
  final String? bloodGroup;
  final double? height;
  final double? weight;
  final String? profileImageUrl;
  final String? patientCode;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  AstraPatient({
    this.id,
    this.patientId,
    this.name,
    this.phone,
    this.email,
    this.age,
    this.gender,
    this.dateOfBirth,
    this.address,
    this.city,
    this.state,
    this.pincode,
    this.allergies,
    this.chronicConditions,
    this.bloodGroup,
    this.height,
    this.weight,
    this.profileImageUrl,
    this.patientCode,
    this.createdAt,
    this.updatedAt,
  });

  factory AstraPatient.fromJson(Map<String, dynamic> json) {
    return AstraPatient(
      id: json['id']?.toString(),
      patientId: json['patient_id']?.toString(),
      name: json['name'],
      phone: json['phone'],
      email: json['email'],
      age: json['age'],
      gender: json['gender'],
      dateOfBirth: json['date_of_birth'],
      address: json['address'],
      city: json['city'],
      state: json['state'],
      pincode: json['pincode'],
      allergies: json['allergies'] != null 
          ? List<String>.from(json['allergies']) 
          : null,
      chronicConditions: json['chronic_conditions'] != null 
          ? List<String>.from(json['chronic_conditions']) 
          : null,
      bloodGroup: json['blood_group'],
      height: json['height']?.toDouble(),
      weight: json['weight']?.toDouble(),
      profileImageUrl: json['profile_image_url'],
      patientCode: json['patient_code'],
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
      if (patientId != null) 'patient_id': patientId,
      if (name != null) 'name': name,
      if (phone != null) 'phone': phone,
      if (email != null) 'email': email,
      if (age != null) 'age': age,
      if (gender != null) 'gender': gender,
      if (dateOfBirth != null) 'date_of_birth': dateOfBirth,
      if (address != null) 'address': address,
      if (city != null) 'city': city,
      if (state != null) 'state': state,
      if (pincode != null) 'pincode': pincode,
      if (allergies != null) 'allergies': allergies,
      if (chronicConditions != null) 'chronic_conditions': chronicConditions,
      if (bloodGroup != null) 'blood_group': bloodGroup,
      if (height != null) 'height': height,
      if (weight != null) 'weight': weight,
      if (profileImageUrl != null) 'profile_image_url': profileImageUrl,
      if (patientCode != null) 'patient_code': patientCode,
    };
  }

  /// Get full name with title
  String get displayName => name ?? 'Unknown Patient';

  /// Get BMI if height and weight are available
  double? get bmi {
    if (height != null && weight != null && height! > 0) {
      final heightInMeters = height! / 100;
      return weight! / (heightInMeters * heightInMeters);
    }
    return null;
  }

  /// Check if patient has any allergies
  bool get hasAllergies => allergies != null && allergies!.isNotEmpty;

  /// Check if patient has chronic conditions
  bool get hasChronicConditions => 
      chronicConditions != null && chronicConditions!.isNotEmpty;
}

/// Patient registration request
class PatientRegistrationRequest {
  final String name;
  final String phone;
  final String? email;
  final int? age;
  final String? gender;
  final String? dateOfBirth;
  final String? address;
  final String? city;
  final String? state;
  final String? pincode;
  final List<String>? allergies;
  final List<String>? chronicConditions;
  final String? bloodGroup;

  PatientRegistrationRequest({
    required this.name,
    required this.phone,
    this.email,
    this.age,
    this.gender,
    this.dateOfBirth,
    this.address,
    this.city,
    this.state,
    this.pincode,
    this.allergies,
    this.chronicConditions,
    this.bloodGroup,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'phone': phone,
      if (email != null) 'email': email,
      if (age != null) 'age': age,
      if (gender != null) 'gender': gender,
      if (dateOfBirth != null) 'date_of_birth': dateOfBirth,
      if (address != null) 'address': address,
      if (city != null) 'city': city,
      if (state != null) 'state': state,
      if (pincode != null) 'pincode': pincode,
      if (allergies != null) 'allergies': allergies,
      if (chronicConditions != null) 'chronic_conditions': chronicConditions,
      if (bloodGroup != null) 'blood_group': bloodGroup,
    };
  }
}

/// Patient search result
class PatientSearchResult {
  final List<AstraPatient> patients;
  final int total;
  final int page;
  final int limit;

  PatientSearchResult({
    required this.patients,
    required this.total,
    required this.page,
    required this.limit,
  });

  factory PatientSearchResult.fromJson(Map<String, dynamic> json) {
    return PatientSearchResult(
      patients: (json['patients'] as List? ?? [])
          .map((p) => AstraPatient.fromJson(p))
          .toList(),
      total: json['total'] ?? 0,
      page: json['page'] ?? 1,
      limit: json['limit'] ?? 20,
    );
  }
}
