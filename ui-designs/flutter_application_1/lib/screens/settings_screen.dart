import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../app_styles.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  List<dynamic> notifications = [];
  bool isLoadingNotifications = false;

  void _showAboutSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.8,
          minChildSize: 0.5,
          maxChildSize: 0.9,
          builder: (context, scrollController) {
            return Container(
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
              ),
              child: ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(32),
                ),
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.all(24),
                  children: [
                    Center(
                      child: Container(
                        width: 50,
                        height: 5,
                        decoration: BoxDecoration(
                          color: const Color.fromARGB(255, 234, 255, 252),
                          borderRadius: BorderRadius.circular(20),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    Center(
                      child: Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: AppStyles.primary.withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.auto_awesome_rounded,
                          size: 50,
                          color: AppStyles.primary,
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    const Center(
                      child: Text(
                        "About SmartMentor",
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.w900,
                          color: AppStyles.textDark,
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    const Text(
                      "SmartMentor is your AI-powered interactive guide designed to simplify how you interact with devices and printers.",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: AppStyles.textDark,
                        height: 1.5,
                      ),
                    ),
                    const SizedBox(height: 10),
                    const Text(
                      "Using advanced AI (VLM & LLM), it transforms how you troubleshoot, learn, and master technical equipment instantly.",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 13,
                        color: AppStyles.textLight,
                        height: 1.5,
                      ),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      "Key Features",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                        color: AppStyles.primary,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildFeatureItem(
                      Icons.center_focus_strong_rounded,
                      "Smart Recognition",
                      "Instant device identification via photo capture.",
                    ),
                    _buildFeatureItem(
                      Icons.lightbulb_outline_rounded,
                      "AI Troubleshooting",
                      "Step-by-step interactive guidance tailored to your device.",
                    ),
                    _buildFeatureItem(
                      Icons.track_changes_rounded,
                      "Progress Tracking",
                      "Easily monitor your history and learning journey.",
                    ),
                    const SizedBox(height: 20),
                    const Text(
                      "Making tech guidance seamless and accessible to everyone!",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: AppStyles.primary,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                    const SizedBox(height: 28),
                    const Center(
                      child: Text(
                        "Version 1.0.0",
                        style: TextStyle(
                          fontSize: 12,
                          color: AppStyles.textLight,
                          letterSpacing: 1,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildFeatureItem(IconData icon, String title, String description) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppStyles.primaryLight,
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppStyles.primary.withOpacity(0.12),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: AppStyles.primary, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: AppStyles.textDark,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppStyles.textLight,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showNotificationsSheet(int userId) async {
    if (isLoadingNotifications) return;

    try {
      setState(() {
        isLoadingNotifications = true;
      });

      final response = await http.get(
        Uri.parse('http://10.0.2.2:3000/users/$userId/notifications'),
      );

      final data = jsonDecode(response.body);
      notifications = data['notifications'] ?? [];
    } catch (e) {
      notifications = [];
    }

    if (!mounted) return;

    setState(() {
      isLoadingNotifications = false;
    });

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.85,
          minChildSize: 0.4,
          maxChildSize: 0.95,
          builder: (context, scrollController) {
            return Container(
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
              ),
              child: ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(32),
                ),
                child: ListView.builder(
                  controller: scrollController,
                  padding: const EdgeInsets.all(22),
                  itemCount: isLoadingNotifications
                      ? 1
                      : (notifications.isEmpty ? 1 : notifications.length + 1),
                  itemBuilder: (context, i) {
                    if (i == 0) {
                      return Column(
                        children: [
                          Container(
                            width: 50,
                            height: 5,
                            decoration: BoxDecoration(
                              color: const Color.fromARGB(255, 234, 255, 252),
                              borderRadius: BorderRadius.circular(20),
                            ),
                          ),
                          const SizedBox(height: 20),
                          const Text(
                            "Notifications",
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.w900,
                              color: AppStyles.textDark,
                            ),
                          ),
                          const SizedBox(height: 20),
                          if (isLoadingNotifications)
                            const Padding(
                              padding: EdgeInsets.all(20),
                              child: Center(child: CircularProgressIndicator()),
                            ),
                          if (!isLoadingNotifications && notifications.isEmpty)
                            const Padding(
                              padding: EdgeInsets.all(20),
                              child: Center(
                                child: Text("No notifications yet."),
                              ),
                            ),
                        ],
                      );
                    }

                    final n = notifications[i - 1];

                    return Container(
                      margin: const EdgeInsets.only(bottom: 14),
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: AppStyles.primaryLight,
                        borderRadius: BorderRadius.circular(22),
                      ),
                      child: Row(
                        children: [
                          CircleAvatar(
                            backgroundColor: AppStyles.primary,
                            child: Icon(
                              _notificationIcon(n['type']),
                              color: Colors.white,
                              size: 20,
                            ),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  n['title'] ?? 'Notification',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w900,
                                    color: AppStyles.textDark,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  n['message'] ?? '',
                                  style: const TextStyle(
                                    fontSize: 13,
                                    color: AppStyles.textLight,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            );
          },
        );
      },
    );
  }

  IconData _notificationIcon(String? type) {
    switch (type) {
      case 'Device guide completed':
        return Icons.verified_rounded;
      case 'New AI guide generated':
        return Icons.auto_awesome_rounded;
      case 'Incomplete guide reminder':
        return Icons.playlist_add_check_rounded;
      case 'Feedback submitted':
        return Icons.star_rounded;
      case 'Recently scanned device':
        return Icons.history_rounded;
      default:
        return Icons.notifications_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final args =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>?;

    final int userId = args?['userId'] ?? 0;
    final String userName = args?['userName'] ?? 'User';
    final String userEmail = args?['userEmail'] ?? '';

    return Scaffold(
      backgroundColor: AppStyles.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            children: [
              const SizedBox(height: 20),
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back_ios),
                    onPressed: () => Navigator.pop(context),
                  ),
                  const Text(
                    "Profile",
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
                  ),
                ],
              ),
              const SizedBox(height: 28),

              // Profile Card
              Container(
                padding: const EdgeInsets.all(28),
                decoration: AppStyles.cardDecoration,
                child: Column(
                  children: [
                    CircleAvatar(
                      radius: 50,
                      backgroundColor: AppStyles.primary,
                      child: Text(
                        userName.isNotEmpty ? userName[0] : "U",
                        style: const TextStyle(
                          fontSize: 34,
                          color: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(height: 18),
                    Text(
                      userName,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(userEmail),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // Account Section (ONLY Notifications)
              _section("Account", [
                ListTile(
                  leading: const Icon(Icons.notifications_none_rounded),
                  title: const Text("Notifications"),
                  trailing: isLoadingNotifications
                      ? const CircularProgressIndicator(strokeWidth: 2)
                      : const Icon(Icons.arrow_forward_ios, size: 14),
                  onTap: () => _showNotificationsSheet(userId),
                ),
              ]),

              const SizedBox(height: 22),

              // About
              _section("About", [
                ListTile(
                  leading: const Icon(Icons.info_outline),
                  title: const Text("About SmartMentor"),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                  onTap: _showAboutSheet,
                ),
              ]),

              const SizedBox(height: 22),

              // Logout
              Container(
                decoration: AppStyles.cardDecoration,
                child: ListTile(
                  onTap: () {
                    Navigator.pushNamedAndRemoveUntil(
                      context,
                      '/login',
                      (route) => false,
                    );
                  },
                  leading: const Icon(Icons.logout_rounded, color: Colors.red),
                  title: const Text(
                    "Logout",
                    style: TextStyle(
                      color: Colors.red,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 35),
            ],
          ),
        ),
      ),
    );
  }

  Widget _section(String title, List<Widget> tiles) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 8),
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: AppStyles.primary,
            ),
          ),
        ),
        Container(
          decoration: AppStyles.cardDecoration,
          child: Column(children: tiles),
        ),
      ],
    );
  }
}
