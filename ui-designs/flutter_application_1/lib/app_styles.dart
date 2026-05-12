import 'package:flutter/material.dart';

class AppStyles {
  static const Color primary = Color(0xFF4F8CFF);

  static const Color primaryDark = Color(0xFF2563EB);

  static const Color primaryLight = Color(0xFFEAF2FF);

  static const Color accent = Color(0xFF7C5CFF);

  static const Color textDark = Color(0xFF111827);

  static const Color textLight = Color(0xFF6B7280);

  static const Color background = Color(0xFFF8FAFC);

  static BoxDecoration pageBackground = const BoxDecoration(
    gradient: LinearGradient(
      colors: [Color(0xFFF8FBFF), Color(0xFFEFF4FF)],

      begin: Alignment.topCenter,
      end: Alignment.bottomCenter,
    ),
  );

  static BoxDecoration cardDecoration = BoxDecoration(
    color: Colors.white,

    borderRadius: BorderRadius.circular(28),

    boxShadow: [
      BoxShadow(
        color: Colors.black.withOpacity(0.05),

        blurRadius: 24,

        offset: const Offset(0, 10),
      ),
    ],
  );

  static ButtonStyle primaryButton = ElevatedButton.styleFrom(
    backgroundColor: primary,

    foregroundColor: Colors.white,

    elevation: 0,

    padding: const EdgeInsets.symmetric(vertical: 16),

    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
  );

  static InputDecoration fieldDecoration(String hint, IconData icon) {
    return InputDecoration(
      hintText: hint,

      hintStyle: const TextStyle(color: textLight),

      prefixIcon: Icon(icon, color: primary),

      filled: true,

      fillColor: Colors.white,

      contentPadding: const EdgeInsets.symmetric(vertical: 18, horizontal: 18),

      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),

        borderSide: BorderSide.none,
      ),

      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),

        borderSide: BorderSide.none,
      ),

      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),

        borderSide: const BorderSide(color: primary, width: 1.7),
      ),
    );
  }
}
