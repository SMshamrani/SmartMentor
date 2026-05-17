import 'package:flutter/material.dart';
import '../app_styles.dart';

class AppLogo extends StatelessWidget {
  final double size;

  const AppLogo({super.key, this.size = 120});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: const LinearGradient(
          colors: [AppStyles.primary, AppStyles.primaryDark],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
            color: AppStyles.primary.withOpacity(0.35),
            blurRadius: 30,
            spreadRadius: 2,
            offset: const Offset(0, 14),
          ),
        ],
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Main glowing circle
          Container(
            width: size * 0.72,
            height: size * 0.72,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white.withOpacity(0.12),
            ),
          ),

          // Smart device icon
          Icon(Icons.devices_rounded, color: Colors.white, size: size * 0.40),

          // AI sparkle top right
          Positioned(
            top: size * 0.16,
            right: size * 0.14,
            child: Container(
              padding: EdgeInsets.all(size * 0.045),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.white.withOpacity(0.7),
                    blurRadius: 12,
                  ),
                ],
              ),
              child: Icon(
                Icons.auto_awesome_rounded,
                color: AppStyles.primary,
                size: size * 0.15,
              ),
            ),
          ),

          // Small connected AI nodes
          Positioned(
            bottom: size * 0.18,
            left: size * 0.23,
            child: Row(
              children: [
                _dot(size * 0.05),
                SizedBox(width: size * 0.03),
                Container(
                  width: size * 0.12,
                  height: size * 0.02,
                  color: Colors.white.withOpacity(0.8),
                ),
                SizedBox(width: size * 0.03),
                _dot(size * 0.05),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _dot(double size) {
    return Container(
      width: size,
      height: size,
      decoration: const BoxDecoration(
        shape: BoxShape.circle,
        color: Colors.white,
      ),
    );
  }
}
