import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../app_styles.dart';

class DeviceDetailScreen extends StatefulWidget {
  const DeviceDetailScreen({super.key});

  @override
  State<DeviceDetailScreen> createState() => _DeviceDetailScreenState();
}

class _DeviceDetailScreenState extends State<DeviceDetailScreen> {
  bool _isLoading = true;
  bool _loaded = false;
  bool resume = false;

  int progress = 0;
  int deviceId = 0;
  int userId = 1;
  int guideId = 0;
  int currentStep = 0;

  String userName = 'User';
  String userEmail = '';

  String deviceName = '';
  String guideTitle = '';
  String source = '';

  List<dynamic> steps = [];

 @override
void didChangeDependencies() {
  super.didChangeDependencies();

  if (_loaded) return;
  _loaded = true;

  final args =
      ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;

  deviceId = args?['deviceId'] ?? 0;
  userId = args?['userId'] ?? 1;
  userName = args?['userName'] ?? 'User';
  userEmail = args?['userEmail'] ?? '';
  source = args?['source'] ?? 'database';
  currentStep = args?['currentStep'] ?? 0;
  progress = args?['progressPercent'] ?? 0;
  
  resume = args?['resume'] ?? false;

  _loadGuide();
}
  Future<void> _loadGuide() async {
    try {
      final response = await http.get(
        Uri.parse('http://10.0.2.2:3000/devices/$deviceId/guide'),
      );

      final data = jsonDecode(response.body);

      setState(() {
        deviceName = data['device']['devicename'];
        guideId = data['guide']['guideid'];
        guideTitle = data['guide']['title'];
        steps = data['steps'];

        if (resume && steps.isNotEmpty) {
        currentStep =
             ((progress / 100) * steps.length).floor();

      if (currentStep >= steps.length) {
        currentStep = steps.length - 1;
  }
}

        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: AppStyles.pageBackground,
        child: SafeArea(
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(22),
                      child: Row(
                        children: [
                          CircleAvatar(
                            backgroundColor: AppStyles.primaryLight,
                            child: IconButton(
                              icon: const Icon(Icons.arrow_back),
                              color: AppStyles.primary,
                              onPressed: () => Navigator.pop(context),
                            ),
                          ),
                          const Spacer(),
                          const Text(
                            'Device Guide',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                              color: AppStyles.textDark,
                            ),
                          ),
                          const Spacer(),
                          CircleAvatar(
                            backgroundColor: AppStyles.primary,
                            child: IconButton(
                              icon: const Icon(
                                Icons.home_rounded,
                                color: Colors.white,
                              ),
                              onPressed: () {
                                Navigator.pop(context);
                              },
                            ),
                          ),
                        ],
                      ),
                    ),
                    Expanded(
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.symmetric(horizontal: 22),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(26),
                              decoration: BoxDecoration(
                                gradient: const LinearGradient(
                                  colors: [
                                    AppStyles.primary,
                                    AppStyles.primaryDark,
                                  ],
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                ),
                                borderRadius: BorderRadius.circular(32),
                                boxShadow: [
                                  BoxShadow(
                                    color: AppStyles.primary.withOpacity(0.28),
                                    blurRadius: 30,
                                    offset: const Offset(0, 14),
                                  ),
                                ],
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Icon(
                                    Icons.print_rounded,
                                    color: Colors.white,
                                    size: 58,
                                  ),
                                  const SizedBox(height: 20),
                                  Text(
                                    deviceName,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 26,
                                      fontWeight: FontWeight.w900,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    guideTitle,
                                    style: TextStyle(
                                      color: Colors.white.withOpacity(0.85),
                                      fontSize: 15,
                                    ),
                                  ),
                                  const SizedBox(height: 18),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 14,
                                      vertical: 8,
                                    ),
                                    decoration: BoxDecoration(
                                      color: Colors.white.withOpacity(0.18),
                                      borderRadius: BorderRadius.circular(20),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 26),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton.icon(
                                style: AppStyles.primaryButton,
                                onPressed: () {
                                  

                                  Navigator.pushNamed(
                                    context,
                                    '/guided-mode',
                                    arguments: {
                                      'userId': userId,
                                      'userName': userName,
                                      'userEmail': userEmail,
                                      'deviceId': deviceId,
                                      'deviceName': deviceName,
                                      'guideTitle': guideTitle,
                                      'guideId': guideId,
                                      'steps': steps,
                                      'progressPercent': progress,
                                       resume: progress > 0 && progress < 100,
                                      'currentStep': currentStep,
                                    },
                                  );
                                },
                                icon: const Icon(Icons.play_arrow_rounded),
                                label: const Text('Start Guided Mode'),
                              ),
                            ),
                            const SizedBox(height: 28),
                            const Text(
                              'Smart Guide Preview',
                              style: TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.w900,
                                color: AppStyles.textDark,
                              ),
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              'Preview the steps below, or start guided mode for a step-by-step experience.',
                              style: TextStyle(
                                color: AppStyles.textLight,
                                fontSize: 15,
                                height: 1.5,
                              ),
                            ),
                            const SizedBox(height: 20),
                            for (int i = 0; i < steps.length; i++)
                              _StepCard(
                                number: steps[i]['stepnumber'],
                                text: steps[i]['description'],
                              ),
                            const SizedBox(height: 30),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}

class _StepCard extends StatelessWidget {
  final int number;
  final String text;

  const _StepCard({required this.number, required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: AppStyles.cardDecoration,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            backgroundColor: AppStyles.primaryLight,
            child: Text(
              '$number',
              style: const TextStyle(
                color: AppStyles.primary,
                fontWeight: FontWeight.w900,
              ),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                fontSize: 15,
                height: 1.5,
                color: AppStyles.textDark,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
