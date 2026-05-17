import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../app_styles.dart';
import '../widgets/app_logo.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController emailController = TextEditingController();

  final TextEditingController passwordController = TextEditingController();

  bool _isLoading = false;

  Future<void> login() async {
    setState(() => _isLoading = true);

    final url = Uri.parse('http://10.0.2.2:3000/login');

    try {
      final response = await http.post(
        url,

        headers: {'Content-Type': 'application/json'},

        body: jsonEncode({
          'email': emailController.text.trim(),

          'password': passwordController.text.trim(),
        }),
      );

      final data = jsonDecode(response.body);

      if (!mounted) return;

      if (response.statusCode == 200) {
        final user = data['user'];

        Navigator.pushReplacementNamed(
          context,

          '/home',

          arguments: {
            'userid': user['userid'],

            'name': user['name'] ?? 'User',

            'email': user['email'] ?? '',
          },
        );

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['message'] ?? "Login successful ✔")),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['message'] ?? "Login failed ❌")),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Connection error ❌")));
    }

    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: AppStyles.pageBackground,

        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(28),

              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,

                children: [
                  AppLogo(size: 120),

                  const SizedBox(height: 28),

                  const Text(
                    "Welcome Back",

                    style: TextStyle(
                      fontSize: 30,
                      fontWeight: FontWeight.w900,
                      color: AppStyles.textDark,
                    ),
                  ),

                  const SizedBox(height: 10),

                  const Text(
                    "Sign in to continue your AI-powered device guidance experience.",

                    textAlign: TextAlign.center,

                    style: TextStyle(
                      color: AppStyles.textLight,
                      fontSize: 15,
                      height: 1.6,
                    ),
                  ),

                  const SizedBox(height: 34),

                  Container(
                    padding: const EdgeInsets.all(24),

                    decoration: AppStyles.cardDecoration,

                    child: Column(
                      children: [
                        TextField(
                          controller: emailController,

                          decoration: AppStyles.fieldDecoration(
                            "Email",

                            Icons.email_outlined,
                          ),
                        ),

                        const SizedBox(height: 18),

                        TextField(
                          controller: passwordController,

                          obscureText: true,

                          decoration: AppStyles.fieldDecoration(
                            "Password",

                            Icons.lock_outline,
                          ),
                        ),

                        const SizedBox(height: 28),

                        SizedBox(
                          width: double.infinity,

                          child: ElevatedButton(
                            style: AppStyles.primaryButton,

                            onPressed: _isLoading ? null : login,

                            child: _isLoading
                                ? const SizedBox(
                                    width: 24,
                                    height: 24,

                                    child: CircularProgressIndicator(
                                      color: Colors.white,
                                      strokeWidth: 2.5,
                                    ),
                                  )
                                : const Text(
                                    "Sign In",

                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                          ),
                        ),

                        const SizedBox(height: 16),

                        TextButton(
                          onPressed: () {
                            Navigator.pushNamed(context, '/signup');
                          },

                          child: const Text(
                            "Create an account",

                            style: TextStyle(
                              color: AppStyles.primary,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
