/// Doctor model for Astra AI Healthcare
class AstraDoctor {
  final String? id;
  final String? doctorId;
  final String? name;
  final String? email;
  final String? phone;
  final String? specialization;
  final List<String>? qualifications;
  final int? experienceYears;
  final double? consultationFee;
  final List<String>? availableDays;
  final LocationModel? location;
  final String? profileImageUrl;
  final String? registrationNumber;
  final String? bio;
  final double? rating;
  final int? totalConsultations;
  final bool? isActive;
  final bool? isVerified;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  AstraDoctor({
    this.id,
    this.doctorId,
    this.name,
    this.email,
    this.phone,
    this.specialization,
    this.qualifications,
    this.experienceYears,
    this.consultationFee,
    this.availableDays,
    this.location,
    this.profileImageUrl,
    this.registrationNumber,
    this.bio,
    this.rating,
    this.totalConsultations,
    this.isActive,
    this.isVerified,
    this.createdAt,
    this.updatedAt,
  });

  factory AstraDoctor.fromJson(Map<String, dynamic> json) {
    return AstraDoctor(
      id: json['id']?.toString(),
      doctorId: json['doctor_id']?.toString(),
      name: json['name'],
      email: json['email'],
      phone: json['phone'],
      specialization: json['specialization'],
      qualifications: json['qualifications'] != null
          ? List<String>.from(json['qualifications'])
          : null,
      experienceYears: json['experience_years'],
      consultationFee: json['consultation_fee']?.toDouble(),
      availableDays: json['available_days'] != null
          ? List<String>.from(json['available_days'])
          : null,
      location: json['location'] != null
          ? LocationModel.fromJson(json['location'])
          : null,
      profileImageUrl: json['profile_image_url'],
      registrationNumber: json['registration_number'],
      bio: json['bio'],
      rating: json['rating']?.toDouble(),
      totalConsultations: json['total_consultations'],
      isActive: json['is_active'],
      isVerified: json['is_verified'],
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
      if (doctorId != null) 'doctor_id': doctorId,
      if (name != null) 'name': name,
      if (email != null) 'email': email,
      if (phone != null) 'phone': phone,
      if (specialization != null) 'specialization': specialization,
      if (qualifications != null) 'qualifications': qualifications,
      if (experienceYears != null) 'experience_years': experienceYears,
      if (consultationFee != null) 'consultation_fee': consultationFee,
      if (availableDays != null) 'available_days': availableDays,
      if (location != null) 'location': location!.toJson(),
      if (profileImageUrl != null) 'profile_image_url': profileImageUrl,
      if (registrationNumber != null) 'registration_number': registrationNumber,
      if (bio != null) 'bio': bio,
    };
  }

  /// Get display name with title
  String get displayName => name != null ? 'Dr. $name' : 'Doctor';

  /// Get qualifications as comma-separated string
  String get qualificationsDisplay =>
      qualifications?.join(', ') ?? '';
}

/// Location model for geolocation
class LocationModel {
  final double? latitude;
  final double? longitude;
  final String? city;
  final String? state;
  final String? country;
  final String? address;
  final String? pincode;

  LocationModel({
    this.latitude,
    this.longitude,
    this.city,
    this.state,
    this.country,
    this.address,
    this.pincode,
  });

  factory LocationModel.fromJson(Map<String, dynamic> json) {
    return LocationModel(
      latitude: json['latitude']?.toDouble(),
      longitude: json['longitude']?.toDouble(),
      city: json['city'],
      state: json['state'],
      country: json['country'],
      address: json['address'],
      pincode: json['pincode'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (latitude != null) 'latitude': latitude,
      if (longitude != null) 'longitude': longitude,
      if (city != null) 'city': city,
      if (state != null) 'state': state,
      if (country != null) 'country': country,
      if (address != null) 'address': address,
      if (pincode != null) 'pincode': pincode,
    };
  }

  /// Get formatted address
  String get formattedAddress {
    List<String> parts = [];
    if (address != null) parts.add(address!);
    if (city != null) parts.add(city!);
    if (state != null) parts.add(state!);
    if (pincode != null) parts.add(pincode!);
    return parts.join(', ');
  }
}

/// Doctor registration request
class RegisterDoctorRequest {
  final String name;
  final String email;
  final String phone;
  final String specialization;
  final List<String>? qualifications;
  final int? experienceYears;
  final double? consultationFee;
  final List<String>? availableDays;
  final LocationModel? location;
  final String? registrationNumber;
  final String? bio;

  RegisterDoctorRequest({
    required this.name,
    required this.email,
    required this.phone,
    required this.specialization,
    this.qualifications,
    this.experienceYears,
    this.consultationFee,
    this.availableDays,
    this.location,
    this.registrationNumber,
    this.bio,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'email': email,
      'phone': phone,
      'specialization': specialization,
      if (qualifications != null) 'qualifications': qualifications,
      if (experienceYears != null) 'experience_years': experienceYears,
      if (consultationFee != null) 'consultation_fee': consultationFee,
      if (availableDays != null) 'available_days': availableDays,
      if (location != null) 'location': location!.toJson(),
      if (registrationNumber != null) 'registration_number': registrationNumber,
      if (bio != null) 'bio': bio,
    };
  }
}

/// Doctor update request
class UpdateDoctorRequest {
  final String? name;
  final String? specialization;
  final List<String>? qualifications;
  final int? experienceYears;
  final double? consultationFee;
  final List<String>? availableDays;
  final LocationModel? location;
  final String? bio;
  final bool? isActive;

  UpdateDoctorRequest({
    this.name,
    this.specialization,
    this.qualifications,
    this.experienceYears,
    this.consultationFee,
    this.availableDays,
    this.location,
    this.bio,
    this.isActive,
  });

  Map<String, dynamic> toJson() {
    return {
      if (name != null) 'name': name,
      if (specialization != null) 'specialization': specialization,
      if (qualifications != null) 'qualifications': qualifications,
      if (experienceYears != null) 'experience_years': experienceYears,
      if (consultationFee != null) 'consultation_fee': consultationFee,
      if (availableDays != null) 'available_days': availableDays,
      if (location != null) 'location': location!.toJson(),
      if (bio != null) 'bio': bio,
      if (isActive != null) 'is_active': isActive,
    };
  }
}
