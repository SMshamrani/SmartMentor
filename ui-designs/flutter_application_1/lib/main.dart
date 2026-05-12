import 'package:flutter/material.dart';

import 'screens/splash_screen.dart';
import 'screens/auth_choice_screen.dart';
import 'screens/login_screen.dart';
import 'screens/signup_screen.dart';
import 'screens/home_screen.dart';
import 'screens/device_detail_screen.dart';
import 'screens/guided_mode_screen.dart';

void main() {
  runApp(const SmartMentorApp());
}

class SmartMentorApp extends StatelessWidget {
  const SmartMentorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SmartMentor',
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/welcome': (context) => const AuthChoiceScreen(),
        '/login': (context) => const LoginScreen(),
        '/signup': (context) => const SignupScreen(),

        '/home': (context) {
          final args =
              ModalRoute.of(context)!.settings.arguments
                  as Map<String, dynamic>?;

          return HomeScreen(
            userId: args?['userid'] ?? args?['userId'] ?? 1,
            userName: args?['name'] ?? 'User',
            userEmail: args?['email'] ?? '',
          );
        },

        '/device-detail': (context) => const DeviceDetailScreen(),
        '/guided-mode': (context) => const GuidedModeScreen(),
      },
    );
  }
}
