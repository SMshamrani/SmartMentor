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

  bool showManualInput = false;

  final TextEditingController manualDeviceController = TextEditingController();

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
    manualDeviceController.dispose();
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

      showManualInput = false;
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

      if (_deviceModel == null || _deviceModel == 'UNKNOWN') {
        setState(() {
          showManualInput = true;
        });

        return;
      }

      final int? deviceId = data['device']?['deviceid'] ?? data['device_id'];

      // Save scanned image to DeviceImages table
      if (deviceId != null) {
        final request2 = http.MultipartRequest(
          'POST',
          Uri.parse('http://10.0.2.2:3000/device-images'),
        );
        request2.fields['deviceId'] = deviceId.toString();
        request2.fields['deviceName'] = _deviceModel ?? 'device';
        request2.fields['imageNumber'] = '1';
        request2.files.add(
          await http.MultipartFile.fromPath('image', imageFile.path),
        );
        await request2.send();
      }

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

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Scan failed. Please try again.')),
      );
    }
  }

  Future<void> generateManualGuide() async {
    final deviceName = manualDeviceController.text.trim();

    if (deviceName.isEmpty) return;

    setState(() => _isScanning = true);

    try {
      final response = await http.post(
        Uri.parse('http://10.0.2.2:3000/generate-device-guide'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'deviceName': deviceName}),
      );

      final data = jsonDecode(response.body);

      if (!mounted) return;

      final device = data['device'];

      final deviceId = device['deviceid'];

      Navigator.pushReplacementNamed(
        context,
        '/device-detail',
        arguments: {
          'deviceId': deviceId,
          'source': 'ai_generated',
          'userId': widget.userId,
          'userName': widget.userName,
          'userEmail': widget.userEmail,
        },
      );
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Failed to generate guide')));
    }

    if (mounted) {
      setState(() => _isScanning = false);
    }
  }

  String _getStatusTitle() {
    if (_isScanning) {
      return "Analyzing Device...";
    }

    if (_deviceModel == 'UNKNOWN') {
      return "Device Not Recognized";
    }

    if (_deviceModel != null) {
      return "Device Identified";
    }

    return "Scan Your Device";
  }

  String _getSourceText() {
    if (_deviceModel == 'UNKNOWN') {
      return "You can enter the device manually and generate an AI guide.";
    }

    if (_source == 'database') {
      return 'Found in Database';
    }

    if (_source == 'llm_saved_to_database') {
      return 'Generated by AI and Saved';
    }

    return 'Detected by AI';
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
            _getStatusTitle(),

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
              _getSourceText(),

              textAlign: TextAlign.center,

              style: const TextStyle(color: AppStyles.textLight),
            ),
          ],

          const SizedBox(height: 20),

          if (showManualInput) ...[
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),

              decoration: AppStyles.cardDecoration.copyWith(
                borderRadius: BorderRadius.circular(20),
              ),

              child: TextField(
                controller: manualDeviceController,

                enabled: !_isScanning,

                decoration: const InputDecoration(
                  hintText: "Enter device name manually",
                  border: InputBorder.none,
                  icon: Icon(Icons.edit_rounded, color: AppStyles.primary),
                ),
              ),
            ),

            const SizedBox(height: 14),

            SizedBox(
              width: double.infinity,

              child: ElevatedButton(
                onPressed: _isScanning ? null : generateManualGuide,

                style: ElevatedButton.styleFrom(
                  backgroundColor: AppStyles.primary,

                  padding: const EdgeInsets.symmetric(vertical: 15),

                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(18),
                  ),
                ),

                child: _isScanning
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2.5,
                        ),
                      )
                    : const Text(
                        "Generate AI Guide",
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
              ),
            ),

            const SizedBox(height: 18),
          ],

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
