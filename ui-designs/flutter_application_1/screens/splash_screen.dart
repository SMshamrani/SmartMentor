import 'dart:async';
import 'package:flutter/material.dart';
import '../app_styles.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..forward();

    _scale = CurvedAnimation(parent: _controller, curve: Curves.elasticOut);

    Timer(const Duration(seconds: 3), () {
      if (mounted) Navigator.pushReplacementNamed(context, '/welcome');
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        decoration: AppStyles.pageBackground,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ScaleTransition(
              scale: _scale,
              child: Container(
                padding: const EdgeInsets.all(25),
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [BoxShadow(color: AppStyles.primary.withOpacity(0.2), blurRadius: 40)],
                ),
                child: const Icon(Icons.auto_awesome, size: 80, color: AppStyles.primary),
              ),
            ),
            const SizedBox(height: 30),
            const Text(
              'SmartMentor',
              style: TextStyle(fontSize: 36, fontWeight: FontWeight.w900, color: AppStyles.textDark, letterSpacing: -1),
            ),
            const Text('AI-Powered Device Intelligence', style: TextStyle(color: AppStyles.textLight, fontSize: 16)),
          ],
        ),
      ),
    );
  }
}