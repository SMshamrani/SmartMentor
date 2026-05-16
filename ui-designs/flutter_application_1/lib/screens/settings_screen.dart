import 'package:flutter/material.dart';

import '../app_styles.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final args =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>?;

    final String userName = args?['userName'] ?? 'User';

    final String userEmail = args?['userEmail'] ?? '';

    return Scaffold(
      backgroundColor: AppStyles.background,

      body: Container(
        decoration: AppStyles.pageBackground,

        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 20),

            child: Column(
              children: [
                const SizedBox(height: 20),

                // ===== HEADER =====
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(
                        Icons.arrow_back_ios,
                        color: AppStyles.textDark,
                      ),

                      onPressed: () => Navigator.pop(context),
                    ),

                    const SizedBox(width: 5),

                    const Text(
                      "Profile",

                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w900,
                        color: AppStyles.textDark,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 28),

                // ===== PROFILE CARD =====
                Container(
                  width: double.infinity,

                  padding: const EdgeInsets.all(28),

                  decoration: AppStyles.cardDecoration,

                  child: Column(
                    children: [
                      Container(
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,

                          boxShadow: [
                            BoxShadow(
                              color: AppStyles.primary.withOpacity(0.28),

                              blurRadius: 20,

                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),

                        child: CircleAvatar(
                          radius: 50,

                          backgroundColor: AppStyles.primary,

                          child: Text(
                            userName.isNotEmpty
                                ? userName[0].toUpperCase()
                                : "U",

                            style: const TextStyle(
                              fontSize: 34,
                              fontWeight: FontWeight.w900,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),

                      const SizedBox(height: 18),

                      Text(
                        userName,

                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.w900,
                          color: AppStyles.textDark,
                        ),
                      ),

                      const SizedBox(height: 6),

                      Text(
                        userEmail.isNotEmpty ? userEmail : "No Email",

                        style: const TextStyle(
                          fontSize: 14,
                          color: AppStyles.textLight,
                        ),
                      ),

                      const SizedBox(height: 18),

                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 10,
                        ),

                        decoration: BoxDecoration(
                          color: AppStyles.primary.withOpacity(0.12),

                          borderRadius: BorderRadius.circular(30),
                        ),

                        child: const Text(
                          "SmartMentor User",

                          style: TextStyle(
                            color: AppStyles.primary,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                // ===== ACCOUNT =====
                _section("Account", [
                  _tile(Icons.person_outline, "Edit Profile"),

                  _tile(Icons.lock_outline, "Change Password"),

                  _tile(Icons.notifications_none, "Notifications"),
                ]),

                const SizedBox(height: 22),

                // ===== ABOUT =====
                _section("About", [
                  _tile(Icons.info_outline, "About SmartMentor"),

                  _tile(Icons.star_outline, "Rate Application"),
                ]),

                const SizedBox(height: 22),

                // ===== LOGOUT =====
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

                    leading: const Icon(
                      Icons.logout_rounded,
                      color: Colors.red,
                    ),

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
      ),
    );
  }

  // ===== SECTION =====

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

  // ===== TILE =====

  Widget _tile(IconData icon, String title) {
    return ListTile(
      leading: Icon(icon, color: AppStyles.textDark),

      title: Text(
        title,

        style: const TextStyle(
          color: AppStyles.textDark,
          fontWeight: FontWeight.w600,
        ),
      ),

      trailing: const Icon(
        Icons.arrow_forward_ios,
        size: 14,
        color: AppStyles.textLight,
      ),
    );
  }
}
