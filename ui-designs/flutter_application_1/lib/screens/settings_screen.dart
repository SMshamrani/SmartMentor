import 'package:flutter/material.dart';
import '../app_styles.dart';

class SettingsScreen extends StatelessWidget {
  final String userName;
  final String userEmail;

  const SettingsScreen({
    super.key,
    required this.userName,
    required this.userEmail,
  });

  @override
  Widget build(BuildContext context) {
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
                      "Settings",
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: AppStyles.textDark,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 25),

                // 👤 Profile Card
                Container(
                  padding: const EdgeInsets.all(25),
                  decoration: AppStyles.cardDecoration,
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 45,
                        backgroundColor: AppStyles.primary.withOpacity(0.1),
                        child: Text(
                          userName.isNotEmpty ? userName[0].toUpperCase() : "U",
                          style: const TextStyle(
                            fontSize: 30,
                            fontWeight: FontWeight.bold,
                            color: AppStyles.primary,
                          ),
                        ),
                      ),

                      const SizedBox(height: 15),

                      Text(
                        userName,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: AppStyles.textDark,
                        ),
                      ),

                      const SizedBox(height: 5),

                      Text(
                        userEmail.isNotEmpty ? userEmail : "No email",
                        style: const TextStyle(
                          fontSize: 13,
                          color: AppStyles.textLight,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 25),

                // ⚙️ Account Section
                _section("Account", [
                  _tile(Icons.person, "Edit Profile"),
                  _tile(Icons.lock, "Change Password"),
                  _tile(Icons.notifications, "Notifications"),
                ]),

                const SizedBox(height: 20),

                // 🚪 Logout
                Container(
                  decoration: AppStyles.cardDecoration,
                  child: ListTile(
                    onTap: () =>
                        Navigator.pushReplacementNamed(context, '/login'),

                    leading: const Icon(Icons.logout, color: Colors.red),

                    title: const Text(
                      "Logout",
                      style: TextStyle(
                        color: Colors.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 30),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ================= Section =================

  Widget _section(String title, List<Widget> tiles) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 8),
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.bold,
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

  // ================= Tile =================

  Widget _tile(IconData icon, String title) {
    return ListTile(
      leading: Icon(icon, color: AppStyles.textDark),

      title: Text(title, style: const TextStyle(color: AppStyles.textDark)),

      trailing: const Icon(
        Icons.arrow_forward_ios,
        size: 14,
        color: AppStyles.textLight,
      ),
    );
  }
}
