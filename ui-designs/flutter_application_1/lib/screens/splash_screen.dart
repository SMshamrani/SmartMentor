import 'dart:async';

import 'package:flutter/material.dart';

import '../app_styles.dart';
import '../widgets/app_logo.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  late AnimationController _logoController;

  late Animation<double> _logoScale;

  late AnimationController _fadeController;

  late Animation<double> _fadeAnimation;

  late AnimationController _pulseController;

  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();

    _logoController = AnimationController(
      vsync: this,

      duration: const Duration(milliseconds: 1400),
    );

    _logoScale = CurvedAnimation(
      parent: _logoController,

      curve: Curves.elasticOut,
    );

    _fadeController = AnimationController(
      vsync: this,

      duration: const Duration(milliseconds: 1000),
    );

    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(_fadeController);

    _pulseController = AnimationController(
      vsync: this,

      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _logoController.forward();

    Future.delayed(const Duration(milliseconds: 500), () {
      _fadeController.forward();
    });

    Timer(const Duration(seconds: 4), () {
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/welcome');
      }
    });
  }

  @override
  void dispose() {
    _logoController.dispose();

    _fadeController.dispose();

    _pulseController.dispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,

        decoration: AppStyles.pageBackground,

        child: Stack(
          children: [
            Positioned(
              top: -120,
              right: -80,
              child: _glowCircle(260, AppStyles.primary.withOpacity(0.12)),
            ),

            Positioned(
              bottom: -100,
              left: -60,
              child: _glowCircle(220, AppStyles.primaryDark.withOpacity(0.10)),
            ),

            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,

                children: [
                  ScaleTransition(
                    scale: _logoScale,

                    child: AnimatedBuilder(
                      animation: _pulseAnimation,

                      builder: (context, child) {
                        return Transform.scale(
                          scale: _pulseAnimation.value,

                          child: const AppLogo(size: 145),
                        );
                      },
                    ),
                  ),

                  const SizedBox(height: 36),

                  FadeTransition(
                    opacity: _fadeAnimation,

                    child: const Text(
                      "SmartMentor",

                      style: TextStyle(
                        fontSize: 40,
                        fontWeight: FontWeight.w900,
                        color: AppStyles.textDark,
                        letterSpacing: -1.2,
                      ),
                    ),
                  ),

                  const SizedBox(height: 12),

                  FadeTransition(
                    opacity: _fadeAnimation,

                    child: const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 40),

                      child: Text(
                        "AI-powered guidance for smarter device troubleshooting and learning.",

                        textAlign: TextAlign.center,

                        style: TextStyle(
                          color: AppStyles.textLight,
                          fontSize: 16,
                          height: 1.6,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 42),

                  FadeTransition(
                    opacity: _fadeAnimation,

                    child: SizedBox(
                      width: 34,
                      height: 34,

                      child: CircularProgressIndicator(
                        strokeWidth: 3,

                        color: AppStyles.primary,

                        backgroundColor: AppStyles.primaryLight,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _glowCircle(double size, Color color) {
    return Container(
      width: size,
      height: size,

      decoration: BoxDecoration(shape: BoxShape.circle, color: color),
    );
  }
}
