import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../app_styles.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> with SingleTickerProviderStateMixin {
  File? _image;
  bool _isScanning = false;
  late AnimationController _scannerController;

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

    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
        _isScanning = true;
      });

      Future.delayed(const Duration(seconds: 3), () {
        if (mounted) {
          setState(() => _isScanning = false);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("Printer Identified: HP LaserJet")),
          );
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text("Smart Scanner", style: TextStyle(color: Colors.white)),
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
                : const Center(child: Icon(Icons.camera_alt_outlined, color: Colors.white24, size: 80)),
          ),

          if (_image != null) _buildScannerOverlay(),

          Align(
            alignment: Alignment.bottomCenter,
            child: _buildControlPanel(),
          ),
        ],
      ),
    );
  }

  Widget _buildScannerOverlay() {
    return Stack(
      children: [
        ColorFiltered(
          colorFilter: ColorFilter.mode(Colors.black.withOpacity(0.5), BlendMode.srcOut),
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
                top: MediaQuery.of(context).size.height * 0.3 + (_scannerController.value * 280),
                left: MediaQuery.of(context).size.width * 0.5 - 140,
                child: Container(
                  width: 280,
                  height: 2,
                  decoration: BoxDecoration(
                    boxShadow: [
                      BoxShadow(color: AppStyles.primary.withOpacity(0.8), blurRadius: 10, spreadRadius: 2)
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
            _isScanning ? "Analyzing Components..." : "Identify Printer Part",
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _actionButton(Icons.photo_library, "Gallery", () => _pickImage(ImageSource.gallery)),
              _actionButton(Icons.camera_alt, "Camera", () => _pickImage(ImageSource.camera)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _actionButton(IconData icon, String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
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
    );
  }
}