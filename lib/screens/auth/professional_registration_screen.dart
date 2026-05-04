import 'dart:io';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:image_picker/image_picker.dart';
import 'package:doctro/screens/auth/profile_complete_screen.dart';
import 'package:doctro/screens/auth/registration_success_screen.dart';
import 'package:doctro/services/supabase_service.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/model/register.dart';
import 'package:intl/intl.dart';

class ProfessionalRegistrationScreen extends StatefulWidget {
  final Map<String, dynamic>? personalData;

  const ProfessionalRegistrationScreen({Key? key, this.personalData}) : super(key: key);

  @override
  _ProfessionalRegistrationScreenState createState() => _ProfessionalRegistrationScreenState();
}

class _ProfessionalRegistrationScreenState extends State<ProfessionalRegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  
  // Controllers
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _dobController = TextEditingController();
  final TextEditingController _licenseController = TextEditingController();
  final TextEditingController _educationController = TextEditingController();
  final TextEditingController _experienceController = TextEditingController();
  final TextEditingController _feesController = TextEditingController();
  final TextEditingController _videoFeesController = TextEditingController();
  final TextEditingController _descController = TextEditingController();
  final TextEditingController _languageController = TextEditingController();
  final TextEditingController _revenueModelController = TextEditingController();
  
  String? _genderSelect;
  String? _selectedRevenueModel;
  List<String> _revenueModels = ["Commission", "Subscription"];
  List<String> _genders = ["Male", "Female", "Other"];
  
  File? _certificateImage;
  String? _existingCertificateUrl;
  File? _idProofImage;
  String? _existingIdProofUrl;

  final ImagePicker _picker = ImagePicker();
  bool _isLoading = false;

  // Set fixed values as they are removed from UI
  String? _selectedTreatmentId = "1"; // Default or null if backend allows
  String? _selectedCategoryId = "1"; // Default or null if backend allows

  final SupabaseService _supabaseService = SupabaseService();

  @override
  void initState() {
    super.initState();
    _fetchTreatments();
    
    if (widget.personalData != null) {
      String rawDob = widget.personalData!['dob'] ?? "";
      if (rawDob.isNotEmpty) {
        try {
          // If signup passes yyyy-MM-dd reformat it
          if (rawDob.contains("-") && rawDob.indexOf("-") == 4) {
             DateTime d = DateFormat('yyyy-MM-dd').parse(rawDob);
             _dobController.text = DateFormat('dd-MM-yyyy').format(d);
          } else {
             _dobController.text = rawDob;
          }
        } catch (e) {
          _dobController.text = rawDob;
        }
      }
      _nameController.text = widget.personalData!['name'] ?? "";
      _emailController.text = widget.personalData!['email'] ?? "";
      _phoneController.text = widget.personalData!['phone'] ?? "";
      _genderSelect = widget.personalData!['gender'];
    }

    if (SharedPreferenceHelper.getBoolean(Preferences.is_logged_in)) {
      _fetchProfileDetails();
    }
  }

  Future<void> _fetchProfileDetails() async {
    setState(() => _isLoading = true);
    try {
      final response = await RestClient(await RetroApi().dioData(context)).doctorProfile();
      if (response.success == true && response.data != null) {
        final data = response.data!;
        setState(() {
          _nameController.text = data.name ?? "";
          _emailController.text = data.email ?? "";
          _phoneController.text = data.phone ?? "";
          
          if (data.dob != null && data.dob!.contains("-")) {
            try {
              if (data.dob!.indexOf("-") == 4) {
                 _dobController.text = DateFormat('dd-MM-yyyy').format(DateFormat('yyyy-MM-dd').parse(data.dob!));
              } else {
                 _dobController.text = data.dob!;
              }
            } catch (e) {
              _dobController.text = data.dob!;
            }
          } else {
            _dobController.text = data.dob ?? "";
          }
          _genderSelect = data.gender;
          
          _licenseController.text = data.hospitalId ?? "";
          _educationController.text = data.education ?? "";
          _experienceController.text = data.experience ?? "";
          _feesController.text = data.appointmentFees ?? "";
          _videoFeesController.text = data.videoAppointmentFees ?? "";
          _descController.text = data.desc ?? "";
          _languageController.text = data.language ?? "";
          _selectedTreatmentId = data.treatmentId?.toString();
          _selectedCategoryId = data.categoryId?.toString();
          _existingCertificateUrl = data.certificate;
        });
        
        if (_selectedTreatmentId != null) {
          _fetchCategories(_selectedTreatmentId!);
        }
      }
    } catch (e) {
      print("Error fetching profile details: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _fetchTreatments() async {
    // Removed treatment fetching as Clinical Expertise is removed from UI
  }

  Future<void> _fetchCategories(String id) async {
    // Removed category fetching
  }

  Future<void> _pickImage(bool isCertificate) async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      setState(() {
        if (isCertificate) {
          _certificateImage = File(image.path);
          _existingCertificateUrl = null;
        } else {
          _idProofImage = File(image.path);
          _existingIdProofUrl = null;
        }
      });
    }
  }

  Future<void> _submitData() async {
    if (!_formKey.currentState!.validate() || 
        _licenseController.text.isEmpty || 
        _videoFeesController.text.isEmpty) {
      Fluttertoast.showToast(msg: "Please fill all required fields");
      return;
    }
    
    if ((_certificateImage == null && _existingCertificateUrl == null) || 
        (_idProofImage == null && _existingIdProofUrl == null)) {
      Fluttertoast.showToast(msg: "Both Medical Certificate and ID Proof are required");
      return;
    }

    Map<String, dynamic> combinedData = widget.personalData != null ? Map.from(widget.personalData!) : {};
    
    combinedData.addAll({
      "name": _nameController.text,
      "email": _emailController.text,
      "phone": _phoneController.text,
      "dob": _dobController.text.isNotEmpty ? DateFormat('yyyy-MM-dd').format(DateFormat('dd-MM-yyyy').parse(_dobController.text)) : "",
      "gender": _genderSelect,
      "treatment_id": int.tryParse(_selectedTreatmentId ?? ""),
      "category_id": int.tryParse(_selectedCategoryId ?? ""),
      "treatment": _selectedTreatmentId, // User recommended field
      "category": _selectedCategoryId, // User recommended field
      "education": _educationController.text,
      "experience": _experienceController.text,
      "appointment_fees": _feesController.text,
      "clinic_fee": _feesController.text, // User recommended field
      "video_appointment_fees": _videoFeesController.text,
      "video_fee": _videoFeesController.text, // User recommended field
      "hospital_id": _licenseController.text,
      "license_number": _licenseController.text, // User recommended field
      "based_on": _selectedRevenueModel ?? "",
      "language": _languageController.text,
      "desc": _descController.text,
      "certificate": _existingCertificateUrl ?? "",
      "id_proof": _existingIdProofUrl ?? "",
    });
    
    if (_certificateImage != null) combinedData["certificate_path"] = _certificateImage!.path;
    if (_idProofImage != null) combinedData["id_proof_path"] = _idProofImage!.path;

    if (widget.personalData != null) {
      _finalizeRegistration(combinedData);
    } else {
      _updateProfile(combinedData);
    }
  }

  Future<void> _finalizeRegistration(Map<String, dynamic> combinedData) async {
    setState(() => _isLoading = true);
    try {
      // 1. Generate Unique ID
      String uniqueId = _supabaseService.generateDoctorID();
      
      // 2. Upload Documents to Supabase
      String? certUrl;
      String? idUrl;
      
      if (combinedData['certificate_path'] != null) {
        certUrl = await _supabaseService.uploadProfilePhoto(File(combinedData['certificate_path']), "${uniqueId}_cert");
      }
      if (combinedData['id_proof_path'] != null) {
        idUrl = await _supabaseService.uploadProfilePhoto(File(combinedData['id_proof_path']), "${uniqueId}_idproof");
      }

      // 3. Prepare Final Data
      Map<String, dynamic> finalData = Map.from(combinedData);
      finalData.addAll({
        "unique_id": uniqueId,
        "is_face_verified": 1, // Face verification bypassed as requested
        "certificate": certUrl ?? "",
        "id_proof": idUrl ?? "",
        "is_filled": 1,
      });

      // 4. Register in Legacy MySQL Backend
      final response = await RestClient(await RetroApi().dioData(context)).registerRequest(finalData);

      if (response.success == true) {
        // 5. Sync to Supabase
        try {
          await _supabaseService.saveDoctorProfile(
            doctorId: uniqueId,
            name: combinedData['name'] ?? '',
            email: combinedData['email'] ?? '',
            phone: combinedData['phone'] ?? '',
            gender: combinedData['gender'] ?? '',
            dob: combinedData['dob'] ?? '',
            photoUrl: "", // No photo captured without face scan
            isFaceVerified: true,
          );
        } catch (e) {
          debugPrint("Supabase Sync Error: $e");
        }

        // 6. Save Preferences & Navigate
      if (response.success == true) {
        _savePreferences(response);
        Navigator.pushAndRemoveUntil(
          context,
          MaterialPageRoute(
            builder: (context) => RegistrationSuccessScreen(
              doctorName: combinedData['name'] ?? '',
              doctorId: response.data?.uniqueId ?? uniqueId,
              email: combinedData['email'] ?? '',
            ),
          ),
          (route) => false,
        );
      }
      } else {
        Fluttertoast.showToast(msg: response.msg ?? "Registration failed");
      }
    } catch (e, stack) {
      if (e is DioException) {
        debugPrint("Registration Request Data: ${e.requestOptions.data}");
        debugPrint("Registration Error Status: ${e.response?.statusCode}");
        debugPrint("Registration Error Response: ${e.response?.data}");
        
        String errorMsg = "Registration failed";
        if (e.response?.data is Map) {
          errorMsg = e.response?.data['msg'] ?? e.response?.data['message'] ?? errorMsg;
        }
        Fluttertoast.showToast(msg: errorMsg);
      } else {
        debugPrint("Non-Dio Error during registration: $e");
        debugPrint("Stacktrace: $stack");
        Fluttertoast.showToast(msg: "An unexpected error occurred: $e");
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _savePreferences(Register response) {
    if (response.data == null) return;
    final data = response.data!;
    
    SharedPreferenceHelper.setBoolean(Preferences.is_logged_in, true);
    SharedPreferenceHelper.setString(Preferences.auth_token, response.token ?? "");
    SharedPreferenceHelper.setString(Preferences.refresh_token, response.refreshToken ?? "");
    SharedPreferenceHelper.setString(Preferences.name, data.name ?? "");
    SharedPreferenceHelper.setString(Preferences.email, data.email ?? "");
    SharedPreferenceHelper.setString(Preferences.phone_no, data.phone ?? "");
    SharedPreferenceHelper.setString(Preferences.gender, data.gender ?? "");
    SharedPreferenceHelper.setString(Preferences.dob, data.dob ?? "");
    SharedPreferenceHelper.setString(Preferences.uniqueId, data.uniqueId ?? "");
    SharedPreferenceHelper.setString(Preferences.image, data.image ?? "");
    SharedPreferenceHelper.setString(Preferences.doctorId, data.id?.toString() ?? "");
  }

  Future<void> _updateProfile(Map<String, dynamic> profileData) async {
    setState(() => _isLoading = true);
    try {
      String doctorId = SharedPreferenceHelper.getString(Preferences.uniqueId);
      if (doctorId == 'N_A' || doctorId.isEmpty) {
        doctorId = SharedPreferenceHelper.getString(Preferences.doctorId);
      }
      
      String? certUrl = _existingCertificateUrl;
      String? idProofUrl = _existingIdProofUrl;
      
      if (_certificateImage != null) {
        certUrl = await _supabaseService.uploadProfilePhoto(_certificateImage!, "${doctorId}_cert");
      }
      if (_idProofImage != null) {
        idProofUrl = await _supabaseService.uploadProfilePhoto(_idProofImage!, "${doctorId}_idproof");
      }
      
      Map<String, dynamic> body = Map.from(profileData);
      body["certificate"] = certUrl ?? "";
      body["id_proof"] = idProofUrl ?? "";
      body["is_filled"] = 1;

      final response = await RestClient(await RetroApi().dioData(context)).updateProfile(body);

      if (response.success == true) {
        Fluttertoast.showToast(msg: "Clinical Profile Updated");
        Navigator.pop(context);
      } else {
        Fluttertoast.showToast(msg: response.msg ?? "Update failed");
      }
    } catch (e, stack) {
      if (e is DioException) {
        debugPrint("Update Request Data: ${e.requestOptions.data}");
        debugPrint("Update Error Status: ${e.response?.statusCode}");
        debugPrint("Update Error Response: ${e.response?.data}");
        
        String errorMsg = "Profile update failed";
        if (e.response?.data is Map) {
          errorMsg = e.response?.data['msg'] ?? e.response?.data['message'] ?? errorMsg;
        }
        Fluttertoast.showToast(msg: errorMsg);
      } else {
        debugPrint("Non-Dio Error during update: $e");
        debugPrint("Stacktrace: $stack");
        Fluttertoast.showToast(msg: "An error occurred: $e");
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFBFBFE),
      appBar: AppBar(
        title: Text("Clinical Profile", style: TextStyle(color: purple, fontWeight: FontWeight.w800, fontSize: 22)),
        backgroundColor: Colors.white,
        elevation: 0.5,
        centerTitle: true,
        leading: IconButton(icon: Icon(Icons.arrow_back_ios_new, color: purple, size: 20), onPressed: () => Navigator.pop(context)),
      ),
      body: _isLoading 
        ? Center(child: CircularProgressIndicator(color: purple))
        : SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 25),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSectionHeader("Personal Information", Icons.person_outline),
                  const SizedBox(height: 15),
                  widget.personalData != null 
                    ? _buildPersonalSummaryCard()
                    : Column(
                        children: [
                          _buildTextField("Full Name", _nameController, Icons.badge_outlined),
                          _buildTextField("Email Address", _emailController, Icons.email_outlined),
                          _buildTextField("Phone Number", _phoneController, AppIcons.phone, isNumber: true),
                          Row(
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    _buildLabel("Gender"),
                                    _buildGenericDropdown(_genders, (val) => setState(() => _genderSelect = val), _genderSelect),
                                  ],
                                ),
                              ),
                              const SizedBox(width: 15),
                              Expanded(child: _buildTextField("Date of Birth", _dobController, Icons.cake_outlined, isReadOnly: true, onTap: () => _selectDate(context))),
                            ],
                          ),
                        ],
                      ),

                  const SizedBox(height: 10),
                  
                  const SizedBox(height: 35),
                  _buildSectionHeader("Professional Credentials", Icons.badge_outlined),
                  const SizedBox(height: 15),
                  _buildTextField("Medical Registration / License Number", _licenseController, Icons.verified_user_outlined),
                  _buildTextField("Medical Education (e.g. BAMS, MD)", _educationController, Icons.school_outlined),
                  _buildTextField("Years of Experience", _experienceController, Icons.history, isNumber: true),
                  
                  const SizedBox(height: 35),
                  _buildSectionHeader("Consultation Rates", Icons.account_balance_wallet_outlined),
                  const SizedBox(height: 15),
                    Row(
                      children: [
                        Expanded(child: _buildTextField("Audio call fee (₹)", _feesController, Icons.phone_android_outlined, isNumber: true)),
                        const SizedBox(width: 15),
                        Expanded(child: _buildTextField("Video call fee (₹)", _videoFeesController, Icons.videocam_outlined, isNumber: true)),
                      ],
                    ),
                    const SizedBox(height: 10),
                    _buildLabel("Revenue Model"),
                    _buildGenericDropdown(_revenueModels, (val) => setState(() => _selectedRevenueModel = val), _selectedRevenueModel),

                  const SizedBox(height: 35),
                  _buildSectionHeader("Practice Details", Icons.description_outlined),
                  const SizedBox(height: 15),
                  _buildTextField("Languages Spoken (e.g. English, Hindi)", _languageController, Icons.translate),
                  _buildTextField("Professional Bio / Description", _descController, Icons.article_outlined, maxLines: 3),
                  
                  const SizedBox(height: 35),
                  _buildSectionHeader("Verification Documents", Icons.cloud_upload_outlined),
                  const SizedBox(height: 15),
                  
                  _buildLabel("Medical Degree / Certificate"),
                  _buildUploadBox(
                    onTap: () => _pickImage(true),
                    file: _certificateImage,
                    url: _existingCertificateUrl,
                    placeholder: "Upload Medical Certificate",
                  ),
                  
                  const SizedBox(height: 25),
                  
                  _buildLabel("Identification Proof (Aadhar / PAN / DL)"),
                  _buildUploadBox(
                    onTap: () => _pickImage(false),
                    file: _idProofImage,
                    url: _existingIdProofUrl,
                    placeholder: "Upload ID Proof",
                  ),
                  
                  const SizedBox(height: 45),
                  SizedBox(
                    width: double.infinity,
                    height: 58,
                    child: ElevatedButton(
                      onPressed: _submitData,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: purple,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                        elevation: 0,
                      ),
                      child: Text(widget.personalData != null ? "Complete Registration" : "Save Profile Details", 
                        style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: Colors.white)),
                    ),
                  ),
                  const SizedBox(height: 30),
                ],
              ),
            ),
          ),
    );
  }

  Widget _buildUploadBox({required VoidCallback onTap, File? file, String? url, required String placeholder}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 160,
        width: double.infinity,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: purple.withOpacity(0.1), width: 2),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10, spreadRadius: 0)],
        ),
        child: file != null
          ? ClipRRect(
              borderRadius: BorderRadius.circular(18),
              child: Image.file(file, fit: BoxFit.cover),
            )
          : url != null && url.isNotEmpty
            ? ClipRRect(
                borderRadius: BorderRadius.circular(18),
                child: Image.network(url, fit: BoxFit.cover),
              )
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.add_a_photo_outlined, size: 40, color: purple.withOpacity(0.4)),
                  const SizedBox(height: 10),
                  Text(placeholder, style: TextStyle(color: purple, fontWeight: FontWeight.w600, fontSize: 13)),
                  const SizedBox(height: 4),
                  const Text("Tap to select image/PDF", style: TextStyle(color: Colors.grey, fontSize: 10)),
                ],
              ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, color: purple, size: 22),
        const SizedBox(width: 10),
        Text(title, style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Colors.black87.withOpacity(0.8))),
      ],
    );
  }

  Widget _buildLabel(String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, left: 4),
      child: Text(label, style: TextStyle(fontWeight: FontWeight.w700, color: Colors.black54, fontSize: 13)),
    );
  }

  Widget _buildDropdown(List<dynamic> items, Function(String?) onChanged, String? value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 4),
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.2)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.01), blurRadius: 5, spreadRadius: 0)],
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          isExpanded: true,
          icon: Icon(Icons.keyboard_arrow_down, color: purple),
          hint: const Text("Select option", style: TextStyle(fontSize: 14, color: Colors.grey)),
          items: items.map((item) {
            return DropdownMenuItem<String>(
              value: item.id.toString(),
              child: Text(item.name ?? "", style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }

  Widget _buildGenericDropdown(List<String> items, Function(String?) onChanged, String? value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 4),
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.2)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.01), blurRadius: 5, spreadRadius: 0)],
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          isExpanded: true,
          icon: Icon(Icons.keyboard_arrow_down, color: purple),
          hint: const Text("Select", style: TextStyle(fontSize: 14, color: Colors.grey)),
          items: items.map((item) {
            return DropdownMenuItem<String>(
              value: item,
              child: Text(item, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }

  Widget _buildTextField(String label, TextEditingController controller, IconData icon, {bool isNumber = false, int maxLines = 1, bool isReadOnly = false, VoidCallback? onTap}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildLabel(label),
          TextFormField(
            controller: controller,
            maxLines: maxLines,
            readOnly: isReadOnly,
            onTap: onTap,
            keyboardType: isNumber ? TextInputType.number : TextInputType.text,
            style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
            decoration: InputDecoration(
              prefixIcon: Icon(icon, color: purple.withOpacity(0.7), size: 20),
              filled: true,
              fillColor: Colors.white,
              contentPadding: const EdgeInsets.symmetric(vertical: 18, horizontal: 20),
              enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: Colors.grey.withOpacity(0.2))),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: purple, width: 1.5)),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
              errorBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: Colors.redAccent)),
            ),
            validator: (value) => value == null || value.isEmpty ? "Required" : null,
          ),
        ],
      ),
    );
  }

  Future<void> _selectDate(BuildContext context) async {
    DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _dobController.text.isNotEmpty 
          ? DateFormat('dd-MM-yyyy').parse(_dobController.text)
          : DateTime.now().subtract(const Duration(days: 365 * 25)),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: ThemeData.light().copyWith(
            primaryColor: purple,
            colorScheme: ColorScheme.light(
              primary: purple,
              onPrimary: Colors.white,
              surface: Colors.white,
              onSurface: purple,
            ),
            dialogBackgroundColor: Colors.white,
            textButtonTheme: TextButtonThemeData(
              style: TextButton.styleFrom(foregroundColor: purple),
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        _dobController.text = DateFormat('dd-MM-yyyy').format(picked);
      });
    }
  }

  Widget _buildPersonalSummaryCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: purple.withOpacity(0.05),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: purple.withOpacity(0.1)),
      ),
      child: Column(
        children: [
          _buildSummaryRow(Icons.person, "Name", _nameController.text),
          const Divider(height: 20),
          _buildSummaryRow(Icons.email, "Email", _emailController.text),
          const Divider(height: 20),
          _buildSummaryRow(Icons.cake, "DOB", _dobController.text),
          const Divider(height: 20),
          _buildSummaryRow(Icons.wc, "Gender", _genderSelect ?? "Not selected"),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 18, color: purple),
        const SizedBox(width: 12),
        Text("$label: ", style: TextStyle(color: Colors.grey[600], fontSize: 13)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
      ],
    );
  }

  void _showSuccessDialog(BuildContext context, {required String name, required String email, required String uniqueId}) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          elevation: 0,
          backgroundColor: Colors.transparent,
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.rectangle,
              borderRadius: BorderRadius.circular(24),
              boxShadow: const [
                BoxShadow(color: Colors.black26, blurRadius: 10.0, offset: Offset(0.0, 10.0)),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 80,
                  height: 80,
                  decoration: const BoxDecoration(
                    color: Colors.green,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.check, color: Colors.white, size: 50),
                ),
                const SizedBox(height: 24),
                const Text(
                  "Registration Successful!",
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                const Text(
                  "Your professional profile has been created. Please keep your credentials safe.",
                  style: TextStyle(color: Colors.grey),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey[50],
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.grey[200]!),
                  ),
                  child: Column(
                    children: [
                      _buildDetailRow("Doctor ID", uniqueId, isBold: true),
                      const Divider(height: 24),
                      _buildDetailRow("Name", name),
                      const SizedBox(height: 8),
                      _buildDetailRow("Email", email),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pushAndRemoveUntil(
                         context,
                         MaterialPageRoute(builder: (context) => ProfileCompleteScreen()),
                         (route) => false,
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: purple,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Text("Continue", style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildDetailRow(String label, String value, {bool isBold = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            value,
            style: TextStyle(
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              fontSize: 14,
              color: isBold ? purple : Colors.black87,
            ),
            textAlign: TextAlign.right,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}
