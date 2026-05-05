import 'package:flutter/material.dart';
import '../app_styles.dart';

class AuthChoiceScreen extends StatelessWidget {
  const AuthChoiceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: AppStyles.pageBackground,
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 30),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                
                const Spacer(flex: 2),

                Container(
                  height: 200,
                  width: 200,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: [
                        AppStyles.primary.withOpacity(0.15),
                        AppStyles.accent.withOpacity(0.15),
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                  child: const Icon(
                    Icons.devices_rounded,
                    size: 90,
                    color: AppStyles.primary,
                  ),
                ),

                const SizedBox(height: 35),

                const Text(
                  "Identify Smarter.",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 30,
                    fontWeight: FontWeight.bold,
                    color: AppStyles.textDark,
                  ),
                ),

                const SizedBox(height: 12),

                const Text(
                  "The most advanced platform to recognize and manage your smart devices in one place.",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 15,
                    color: AppStyles.textLight,
                    height: 1.6,
                  ),
                ),

                const Spacer(flex: 3),

                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppStyles.primary,
                      padding: const EdgeInsets.symmetric(vertical: 18),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                      elevation: 2,
                    ),
                    onPressed: () =>
                        Navigator.pushNamed(context, '/login'),
                    child: const Text(
                      "Get Started",
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 12),

                TextButton(
                  onPressed: () =>
                      Navigator.pushNamed(context, '/signup'),
                  child: const Text(
                    "Create an account",
                    style: TextStyle(
                      color: AppStyles.primary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),

                const SizedBox(height: 10),
              ],
            ),
          ),
        ),
      ),
    );
  }
}