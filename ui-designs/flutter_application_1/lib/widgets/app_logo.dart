import 'package:flutter/material.dart';

import '../app_styles.dart';

class AppLogo extends StatelessWidget {
  final double size;

  const AppLogo({super.key, this.size = 110});

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

            blurRadius: 28,

            offset: const Offset(0, 12),
          ),
        ],
      ),

      child: Stack(
        alignment: Alignment.center,

        children: [
          Icon(Icons.print_rounded, color: Colors.white, size: size * 0.42),

          Positioned(
            right: size * 0.20,

            top: size * 0.20,

            child: Container(
              padding: EdgeInsets.all(size * 0.055),

              decoration: const BoxDecoration(
                color: Colors.white,

                shape: BoxShape.circle,
              ),

              child: Icon(
                Icons.auto_awesome_rounded,

                color: AppStyles.primary,

                size: size * 0.18,
              ),
            ),
          ),

          Positioned(
            bottom: size * 0.18,

            child: Container(
              width: size * 0.42,

              height: size * 0.07,

              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.75),

                borderRadius: BorderRadius.circular(20),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
