import 'dart:convert';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../app_styles.dart';

class GuidedModeScreen extends StatefulWidget {
  const GuidedModeScreen({super.key});

  @override
  State<GuidedModeScreen> createState() => _GuidedModeScreenState();
}

class _GuidedModeScreenState extends State<GuidedModeScreen>
    with SingleTickerProviderStateMixin {
  int userId = 1;
  int deviceId = 0;
  int guideId = 0;
  int startIndex = 0;

  String userName = 'User';
  String userEmail = '';

  String deviceName = '';
  String guideTitle = '';

  List<dynamic> steps = [];

  int currentIndex = 0;
  int completedSteps = 0;

  bool _saving = false;
  int selectedRating = 0;

  final TextEditingController reviewController = TextEditingController();

  late AnimationController _partyController;

  double get progress {
    if (steps.isEmpty) return 0;
    return completedSteps / steps.length;
  }

  int get progressPercent {
    return (progress * 100).round();
  }

  @override
  void initState() {
    super.initState();


    _partyController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );
  }

  @override
  void dispose() {
    reviewController.dispose();
    _partyController.dispose();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

   final args = (ModalRoute.of(context)?.settings.arguments as Map)
    .cast<String, dynamic>();
    
    userId = args['userId'] ?? 1;
    userName = args['userName'] ?? 'User';
    userEmail = args['userEmail'] ?? '';

    deviceId = args['deviceId'];
    guideId = args['guideId'] ?? 0;

    deviceName = args['deviceName'] ?? 'Printer';
    guideTitle = args['guideTitle'] ?? 'Guided Mode';
    steps = args['steps'] ?? [];

  if (steps.isNotEmpty) {
  currentIndex = (args['currentStep'] ?? 0)
      .clamp(0, steps.length - 1);

  completedSteps = currentIndex;
}

 else {
  startIndex = 0;
  currentIndex = 0;
  completedSteps = 0;
}
  }

  Future<void> _saveProgress({
    required int percent,
    required String status,
  }) async {
    setState(() => _saving = true);

    try {
      await http.post(
        Uri.parse('http://10.0.2.2:3000/user-progress/update'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'userId': userId,
          'deviceId': deviceId,
          'progressPercent': percent,
          'status': status,
          'currentStep': currentIndex,
        }),
      );
    } catch (_) {}

    if (mounted) {
      setState(() => _saving = false);
    }
  }

  Future<void> _submitFeedback() async {
    if (selectedRating == 0) return;

    try {
      await http.post(
        Uri.parse('http://10.0.2.2:3000/feedback'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'userId': userId,
          'guideId': guideId,
          'rating': selectedRating,
          'comment': reviewController.text.trim(),
        }),
      );
    } catch (_) {}
  }



  void _previousStep() {
    if (currentIndex == 0) return;

    setState(() {
      currentIndex--;
      completedSteps = currentIndex + 1;
    });
  }
  Future<void> _nextStep() async {
  final nextStep = currentIndex + 1;

  final isLastStep = currentIndex >= steps.length - 1;

  if (isLastStep) {
    setState(() {
      completedSteps = steps.length;
    });

    await _saveProgress(percent: 100, status: 'completed');

    _partyController.forward(from: 0);

    _showCompletedDialog();
    return;
  }

  setState(() {
    currentIndex = nextStep;
    completedSteps = nextStep;
  });

  final nextPercent =
    steps.isEmpty ? 0 : ((nextStep / steps.length) * 100).round();

  await _saveProgress(
    percent: nextPercent,
    status: 'in_progress',
  );
}
  void _goHome() {
    Navigator.pushNamedAndRemoveUntil(
      context,
      '/home',
      (route) => false,
      arguments: {'userid': userId, 'name': userName, 'email': userEmail},
    );
  }

  void _showCompletedDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return Stack(
              children: [
                AnimatedBuilder(
                  animation: _partyController,
                  builder: (context, child) {
                    return CustomPaint(
                      painter: _ConfettiPainter(_partyController.value),
                      child: const SizedBox.expand(),
                    );
                  },
                ),
                AlertDialog(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(28),
                  ),
                  title: const Text(
                    'Guide Completed!',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontWeight: FontWeight.w900),
                  ),
                  content: SingleChildScrollView(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Text(
                          'Great job! You completed all steps successfully.',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: AppStyles.textLight,
                            height: 1.5,
                          ),
                        ),
                        const SizedBox(height: 20),
                        Container(
                          padding: const EdgeInsets.all(18),
                          decoration: const BoxDecoration(
                            color: AppStyles.primaryLight,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.celebration_rounded,
                            color: AppStyles.primary,
                            size: 52,
                          ),
                        ),
                        const SizedBox(height: 22),
                        const Text(
                          'Rate this guide',
                          style: TextStyle(
                            fontWeight: FontWeight.w800,
                            color: AppStyles.textDark,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: List.generate(5, (index) {
                            final star = index + 1;

                            return IconButton(
                              onPressed: () {
                                setDialogState(() {
                                  selectedRating = star;
                                });
                              },
                              icon: Icon(
                                selectedRating >= star
                                    ? Icons.star_rounded
                                    : Icons.star_border_rounded,
                                color: Colors.amber,
                                size: 34,
                              ),
                            );
                          }),
                        ),
                        const SizedBox(height: 12),
                        TextField(
                          controller: reviewController,
                          maxLines: 3,
                          decoration: InputDecoration(
                            hintText: 'Write your feedback...',
                            filled: true,
                            fillColor: AppStyles.primaryLight,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(18),
                              borderSide: BorderSide.none,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  actionsAlignment: MainAxisAlignment.center,
                  actions: [
                    ElevatedButton.icon(
                      style: AppStyles.primaryButton,

                      onPressed: () async {
                        await _submitFeedback();

                        if (!mounted) return;

                        Navigator.pop(context);
                        _goHome();
                        
                      },

                      icon: const Icon(Icons.check_circle_rounded),

                      label: const Text('Finish'),
                    ),
                  ],
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final safeIndex = currentIndex.clamp(0, steps.length - 1);
    final currentStep = steps.isNotEmpty ? steps[safeIndex] : null;

    return Scaffold(
      body: Container(
        decoration: AppStyles.pageBackground,
        child: SafeArea(
          child: steps.isEmpty
              ? const Center(child: Text('No steps available'))
              : Padding(
                  padding: const EdgeInsets.all(22),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          CircleAvatar(
                            backgroundColor: AppStyles.primaryLight,
                            child: IconButton(
                              icon: const Icon(Icons.close_rounded),
                              color: AppStyles.primary,
                              onPressed: () => Navigator.pop(context),
                            ),
                          ),

                          const SizedBox(width: 14),

                          Expanded(
                            child: Text(
                              deviceName,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w900,
                                color: AppStyles.textDark,
                              ),
                            ),
                          ),

                          const SizedBox(width: 10),

                          CircleAvatar(
                            backgroundColor: AppStyles.primary,
                            child: IconButton(
                              icon: const Icon(
                                Icons.home_rounded,
                                color: Colors.white,
                              ),
                              onPressed: _goHome,
                            ),
                          ),
                        ],
                      ),
                      
                      const SizedBox(height: 24),
                      Container(
                        padding: const EdgeInsets.all(22),
                        decoration: AppStyles.cardDecoration,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Progress $progressPercent%',
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w800,
                                color: AppStyles.textDark,
                              ),
                            ),
                            const SizedBox(height: 12),
                            ClipRRect(
                              borderRadius: BorderRadius.circular(20),
                              child: LinearProgressIndicator(
                                value: progress,
                                minHeight: 12,
                                backgroundColor: AppStyles.primaryLight,
                                color: AppStyles.primary,
                              ),
                            ),
                            const SizedBox(height: 14),
                            Text(
                              'Step ${currentIndex + 1} of ${steps.length}',
                              style: const TextStyle(
                                color: AppStyles.textLight,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 26),
                      Expanded(
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(28),
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              colors: [
                                AppStyles.primary,
                                AppStyles.primaryDark,
                              ],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            ),
                            borderRadius: BorderRadius.circular(34),
                            boxShadow: [
                              BoxShadow(
                                color: AppStyles.primary.withOpacity(0.25),
                                blurRadius: 30,
                                offset: const Offset(0, 14),
                              ),
                            ],
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              CircleAvatar(
                                radius: 30,
                                backgroundColor: Colors.white.withOpacity(0.2),
                                child: Text(
                                  '${currentStep['stepnumber']}',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 22,
                                    fontWeight: FontWeight.w900,
                                  ),
                                ),
                              ),
                              const SizedBox(height: 28),
                              const Text(
                                'Your next step',
                                style: TextStyle(
                                  color: Colors.white70,
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              const SizedBox(height: 12),
                              Expanded(
                                child: SingleChildScrollView(
                                  child: Text(
                                    currentStep['description'],
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 24,
                                      height: 1.45,
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: currentIndex == 0
                                  ? null
                                  : _previousStep,
                              icon: const Icon(Icons.arrow_back_rounded),
                              label: const Text('Back'),
                              style: OutlinedButton.styleFrom(
                                foregroundColor: AppStyles.primary,
                                side: const BorderSide(
                                  color: AppStyles.primary,
                                  width: 1.4,
                                ),
                                padding: const EdgeInsets.symmetric(
                                  vertical: 16,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(18),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _saving ? null : _nextStep,
                              style: AppStyles.primaryButton,
                              icon: _saving
                                  ? const SizedBox(
                                      width: 18,
                                      height: 18,
                                      child: CircularProgressIndicator(
                                        color: Colors.white,
                                        strokeWidth: 2,
                                      ),
                                    )
                                  : Icon(
                                      currentIndex == steps.length - 1
                                          ? Icons.check_circle_rounded
                                          : Icons.arrow_forward_rounded,
                                    ),
                              label: Text(
                                currentIndex == steps.length - 1
                                    ? 'Finish'
                                    : 'Next',
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
        ),
      ),
    );
  }
}

class _ConfettiPainter extends CustomPainter {
  final double progress;

  _ConfettiPainter(this.progress);

  final Random random = Random(4);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint();

    final colors = [
      AppStyles.primary,
      Colors.amber,
      Colors.pinkAccent,
      Colors.greenAccent,
      Colors.deepPurpleAccent,
    ];

    for (int i = 0; i < 70; i++) {
      final x = random.nextDouble() * size.width;
      final startY = -random.nextDouble() * size.height;
      final y = startY + (progress * size.height * 1.4);

      paint.color = colors[i % colors.length].withOpacity(
        (1 - progress).clamp(0.0, 1.0),
      );

      canvas.drawCircle(Offset(x, y), 4 + random.nextDouble() * 4, paint);
    }
  }

  @override
  bool shouldRepaint(covariant _ConfettiPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}
