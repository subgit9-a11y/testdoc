import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class DoctorListScreen extends StatefulWidget {
  const DoctorListScreen({super.key});

  @override
  _DoctorListScreenState createState() => _DoctorListScreenState();
}

class _DoctorListScreenState extends State<DoctorListScreen> {
  List<dynamic> _doctors = [];
  List<dynamic> _filteredDoctors = [];
  bool _isLoading = true;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchDoctors();
  }

  Future<void> _fetchDoctors() async {
    // Placeholder until dedicated API endpoint is finalized.
    setState(() {
      _doctors = [];
      _filteredDoctors = [];
      _isLoading = false;
    });
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
                ? const Center(child: CircularProgressIndicator(color: Colors.cyanAccent))
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
          backgroundImage: (doc.image != null && doc.image!.isNotEmpty)
              ? NetworkImage(doc.image!)
              : const AssetImage("assets/images/no_image.jpg") as ImageProvider,
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
