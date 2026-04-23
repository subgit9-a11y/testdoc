import 'package:flutter/material.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

class DoctorListScreen extends StatefulWidget {
  @override
  _DoctorListScreenState createState() => _DoctorListScreenState();
}

class _DoctorListScreenState extends State<DoctorListScreen> {
  List<dynamic> _doctors = [];
  List<dynamic> _filteredDoctors = [];
  bool _isLoading = true;
  TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchDoctors();
  }

  Future<void> _fetchDoctors() async {
    try {
      // Re-using existing treatment logic to fetch doctors if available or create a specific endpoint
      // Assuming a generic endpoint or fetching from existing model
      final response = await RestClient(await RetroApi().dioData(context)).apiAllDoctors(); 
      if (response.success == true) {
        setState(() {
          _doctors = response.data!;
          _filteredDoctors = _doctors;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
      print("Error: $e");
    }
  }

  void _filterDoctors(String query) {
    setState(() {
      _filteredDoctors = _doctors
          .where((doc) => doc.name!.toLowerCase().contains(query.toLowerCase()) || 
                          doc.uniqueId!.toLowerCase().contains(query.toLowerCase()))
          .toList();
    });
  }

  Future<void> _downloadPDF(String id) async {
    final url = "https://ayureze.org/doctor_profile_pdf/$id";
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
    } else {
      throw 'Could not launch $url';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F0F),
      appBar: AppBar(
        title: const Text("Medical Registry", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              onChanged: _filterDoctors,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: "Search Doctors...",
                hintStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
                prefixIcon: const Icon(Icons.search, color: Colors.cyanAccent),
                filled: true,
                fillColor: Colors.white.withOpacity(0.05),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(30), borderSide: BorderSide.none),
              ),
            ),
          ),
          Expanded(
            child: _isLoading
                ? const Center(child: SpinKitPulse(color: Colors.cyanAccent, size: 50.0))
                : ListView.builder(
                    itemCount: _filteredDoctors.length,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemBuilder: (context, index) {
                      final doc = _filteredDoctors[index];
                      return _buildDoctorCard(doc);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildDoctorCard(dynamic doc) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.03),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.1)),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(12),
        leading: CircleAvatar(
          radius: 30,
          backgroundImage: NetworkImage(doc.image ?? 'https://via.placeholder.com/150'),
        ),
        title: Text(
          doc.name ?? "Unknown",
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(doc.uniqueId ?? "ID: ---", style: const TextStyle(color: Colors.cyanAccent, fontSize: 12)),
            const SizedBox(height: 4),
            Text(doc.treatmentName ?? "General", style: TextStyle(color: Colors.white.withOpacity(0.6))),
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.picture_as_pdf, color: Colors.redAccent),
          onPressed: () => _downloadPDF(doc.id.toString()),
        ),
      ),
    );
  }
}
