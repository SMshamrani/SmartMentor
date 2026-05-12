import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

import '../app_styles.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen>
    with SingleTickerProviderStateMixin {
  File? _image;
  bool _isScanning = false;
  String? _printerModel;
  String? _source;

  late AnimationController _scannerController;

  // لو تشغلين على Windows/Web خليه localhost
  //final String apiUrl = 'http://localhost:3000/scan-printer';

  // لو تشغلين على جوال حقيقي بدليه بـ IP جهازك:
  final String apiUrl = 'http://10.0.2.2:3000/scan-printer';
  final int userId = 1;

  @override
  void initState() {
    super.initState();

    _scannerController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _scannerController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: source);

    if (pickedFile == null) return;

    setState(() {
      _image = File(pickedFile.path);
      _isScanning = true;
      _printerModel = null;
      _source = null;
    });

    await _scanPrinter(_image!);
  }

  Future<void> _scanPrinter(File imageFile) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse(apiUrl));

      request.files.add(
        await http.MultipartFile.fromPath('image', imageFile.path),
      );

      final streamedResponse = await request.send();
      final responseBody = await streamedResponse.stream.bytesToString();
      final data = jsonDecode(responseBody);

      if (!mounted) return;

      setState(() {
        _isScanning = false;
        _printerModel = data['printer_model'] ?? 'UNKNOWN';
        _source = data['source'] ?? 'unknown';
      });

      final int? deviceId = data['device']?['deviceid'] ?? data['device_id'];

      if (deviceId != null) {
        // =========================
        // SAVE USER ACTIVITY
        // =========================

        await http.post(
          Uri.parse('http://10.0.2.2:3000/user-progress/open-device'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'userId': userId, 'deviceId': deviceId}),
        );

        // =========================
        // OPEN DEVICE DETAILS
        // =========================

        if (!mounted) return;

        Navigator.pushNamed(
          context,
          '/device-detail',
          arguments: {'deviceId': deviceId, 'source': _source},
        );
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Printer Identified: $_printerModel')),
      );
    } catch (error) {
      if (!mounted) return;

      setState(() {
        _isScanning = false;
      });

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Scan failed: $error')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text(
          "Smart Scanner",
          style: TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Stack(
        children: [
          Container(
            width: double.infinity,
            height: double.infinity,
            color: Colors.black,
            child: _image != null
                ? Image.file(_image!, fit: BoxFit.cover)
                : const Center(
                    child: Icon(
                      Icons.camera_alt_outlined,
                      color: Colors.white24,
                      size: 80,
                    ),
                  ),
          ),

          if (_image != null) _buildScannerOverlay(),

          Align(alignment: Alignment.bottomCenter, child: _buildControlPanel()),
        ],
      ),
    );
  }

  Widget _buildScannerOverlay() {
    return Stack(
      children: [
        ColorFiltered(
          colorFilter: ColorFilter.mode(
            Colors.black.withOpacity(0.5),
            BlendMode.srcOut,
          ),
          child: Stack(
            children: [
              Container(decoration: const BoxDecoration(color: Colors.black)),
              Center(
                child: Container(
                  width: 280,
                  height: 280,
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
              ),
            ],
          ),
        ),

        if (_isScanning)
          AnimatedBuilder(
            animation: _scannerController,
            builder: (context, child) {
              return Positioned(
                top:
                    MediaQuery.of(context).size.height * 0.3 +
                    (_scannerController.value * 280),
                left: MediaQuery.of(context).size.width * 0.5 - 140,
                child: Container(
                  width: 280,
                  height: 2,
                  decoration: BoxDecoration(
                    boxShadow: [
                      BoxShadow(
                        color: AppStyles.primary.withOpacity(0.8),
                        blurRadius: 10,
                        spreadRadius: 2,
                      ),
                    ],
                    color: AppStyles.primary,
                  ),
                ),
              );
            },
          ),
      ],
    );
  }

  Widget _buildControlPanel() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 30, horizontal: 20),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(30)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            _isScanning
                ? "Analyzing Printer..."
                : _printerModel != null
                ? "Printer Identified"
                : "Scan Your Printer",
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),

          if (_printerModel != null) ...[
            const SizedBox(height: 12),
            Text(
              _printerModel!,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: AppStyles.primary,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              _source == 'database'
                  ? 'Found in Database'
                  : _source == 'llm_saved_to_database'
                  ? 'Generated by AI and Saved'
                  : 'Detected by AI',
              style: const TextStyle(color: AppStyles.textLight),
            ),
          ],

          const SizedBox(height: 20),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _actionButton(
                Icons.photo_library,
                "Gallery",
                _isScanning ? null : () => _pickImage(ImageSource.gallery),
              ),
              _actionButton(
                Icons.camera_alt,
                "Camera",
                _isScanning ? null : () => _pickImage(ImageSource.camera),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _actionButton(IconData icon, String label, VoidCallback? onTap) {
    return InkWell(
      onTap: onTap,
      child: Opacity(
        opacity: onTap == null ? 0.4 : 1,
        child: Column(
          children: [
            CircleAvatar(
              radius: 30,
              backgroundColor: AppStyles.primary.withOpacity(0.1),
              child: Icon(icon, color: AppStyles.primary),
            ),
            const SizedBox(height: 8),
            Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }
}
