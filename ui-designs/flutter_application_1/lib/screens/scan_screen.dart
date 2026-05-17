import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

import '../app_styles.dart';

class ScanScreen extends StatefulWidget {
  final int userId;
  final String userName;
  final String userEmail;

  const ScanScreen({
    super.key,
    required this.userId,
    required this.userName,
    required this.userEmail,
  });

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen>
    with SingleTickerProviderStateMixin {
  File? _image;
  bool _isScanning = false;
  String? _deviceModel;
  String? _source;

  late AnimationController _scannerController;

  final String apiUrl = 'http://10.0.2.2:3000/scan-printer';

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
      _deviceModel = null;
      _source = null;
    });

    await _scanDevice(_image!);
  }

  Future<void> _scanDevice(File imageFile) async {
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
        _deviceModel = data['printer_model'] ?? 'UNKNOWN';
        _source = data['source'] ?? 'unknown';
      });

      final int? deviceId = data['device']?['deviceid'] ?? data['device_id'];

      if (deviceId != null) {
        await http.post(
          Uri.parse('http://10.0.2.2:3000/user-progress/open-device'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'userId': widget.userId, 'deviceId': deviceId}),
        );

        if (!mounted) return;

        Navigator.pushReplacementNamed(
          context,
          '/device-detail',
          arguments: {
            'deviceId': deviceId,
            'source': _source,
            'userId': widget.userId,
            'userName': widget.userName,
            'userEmail': widget.userEmail,
          },
        );
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Device Identified: $_deviceModel')),
      );
    } catch (error) {
      if (!mounted) return;

      setState(() {
        _isScanning = false;
      });

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Scan failed. Please try again.')));
    }
  }

  void _showScanSearchSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(22),
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 50,
                height: 5,
                decoration: BoxDecoration(
                  color: AppStyles.primaryLight,
                  borderRadius: BorderRadius.circular(20),
                ),
              ),
              const SizedBox(height: 22),
              const Text(
                "Search Device",
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w900,
                  color: AppStyles.textDark,
                ),
              ),
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: AppStyles.cardDecoration.copyWith(
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const TextField(
                  decoration: InputDecoration(
                    hintText: "Type device name or model...",
                    border: InputBorder.none,
                    icon: Icon(Icons.search_rounded, color: AppStyles.primary),
                  ),
                ),
              ),
              const SizedBox(height: 18),
              const Text(
                "Manual database search will be connected later. For now, use camera or gallery scan to identify devices with AI.",
                textAlign: TextAlign.center,
                style: TextStyle(color: AppStyles.textLight, height: 1.5),
              ),
              const SizedBox(height: 14),
            ],
          ),
        );
      },
    );
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
        actions: [
          IconButton(
            icon: const Icon(Icons.search_rounded, color: Colors.white),
            onPressed: _showScanSearchSheet,
          ),
        ],
      ),
      body: Stack(
        children: [
          Container(
            width: double.infinity,
            height: double.infinity,
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [AppStyles.textDark, Color(0xFF111827)],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
            ),
            child: _image != null
                ? Center(
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 400),
                      margin: const EdgeInsets.fromLTRB(22, 100, 22, 220),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(34),
                        boxShadow: [
                          BoxShadow(
                            color: AppStyles.primary.withOpacity(0.35),
                            blurRadius: 35,
                            offset: const Offset(0, 18),
                          ),
                        ],
                      ),
                      clipBehavior: Clip.antiAlias,
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          Container(color: Colors.black),
                          Image.file(_image!, fit: BoxFit.contain),
                          Container(
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  Colors.transparent,
                                  Colors.black.withOpacity(0.15),
                                ],
                                begin: Alignment.topCenter,
                                end: Alignment.bottomCenter,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  )
                : Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(30),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.white.withOpacity(0.05),
                          border: Border.all(color: Colors.white12, width: 1.5),
                        ),
                        child: const Icon(
                          Icons.document_scanner_rounded,
                          color: Colors.white70,
                          size: 85,
                        ),
                      ),
                      const SizedBox(height: 26),
                      const Text(
                        "AI Device Scanner",
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 28,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 12),
                      const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 40),
                        child: Text(
                          "Capture or upload a device image and let SmartMentor identify it instantly using AI.",
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Colors.white60,
                            fontSize: 15,
                            height: 1.6,
                          ),
                        ),
                      ),
                    ],
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
        Center(
          child: Container(
            width: 250,
            height: 250,
            margin: const EdgeInsets.only(bottom: 60),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(28),
              border: Border.all(
                color: Colors.white.withOpacity(0.9),
                width: 2,
              ),
              boxShadow: [
                BoxShadow(
                  color: AppStyles.primary.withOpacity(0.35),
                  blurRadius: 24,
                  spreadRadius: 3,
                ),
              ],
            ),
          ),
        ),
        if (_isScanning)
          AnimatedBuilder(
            animation: _scannerController,
            builder: (context, child) {
              return Positioned(
                top:
                    MediaQuery.of(context).size.height * 0.28 +
                    (_scannerController.value * 250),
                left: MediaQuery.of(context).size.width * 0.5 - 125,
                child: Container(
                  width: 250,
                  height: 3,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: AppStyles.primary.withOpacity(0.9),
                        blurRadius: 14,
                        spreadRadius: 3,
                      ),
                    ],
                    gradient: const LinearGradient(
                      colors: [
                        Colors.transparent,
                        AppStyles.primary,
                        Colors.transparent,
                      ],
                    ),
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
                ? "Analyzing Device..."
                : _deviceModel != null
                ? "Device Identified"
                : "Scan Your Device",
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          if (_deviceModel != null) ...[
            const SizedBox(height: 12),
            Text(
              _deviceModel!,
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
