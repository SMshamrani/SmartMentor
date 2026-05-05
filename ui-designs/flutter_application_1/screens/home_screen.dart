import 'package:flutter/material.dart';
import '../app_styles.dart';
import 'scan_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  final String userName;

  const HomeScreen({super.key, required this.userName});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    String firstLetter =
        widget.userName.isNotEmpty ? widget.userName[0].toUpperCase() : "U";

    return Scaffold(
      backgroundColor: AppStyles.background,

      // ================= AppBar =================
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text(
          "SmartMentor",
          style: TextStyle(
            color: AppStyles.textDark,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_none,
                color: AppStyles.textDark),
            onPressed: () {},
          ),
          Padding(
            padding: const EdgeInsets.only(right: 15),
            child: CircleAvatar(
              backgroundColor: AppStyles.primary,
              child: Text(
                firstLetter,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          )
        ],
      ),

      // ================= Body =================
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Hello, ${widget.userName}! 👋",
              style: const TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.bold,
                color: AppStyles.textDark,
              ),
            ),
            const Text(
              "What would you like to fix today?",
              style: TextStyle(fontSize: 14, color: Colors.grey),
            ),
            const SizedBox(height: 25),

            // 🔵 Scan Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(25),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppStyles.primary, Color(0xFF8E8CD8)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(30),
                boxShadow: [
                  BoxShadow(
                    color: AppStyles.primary.withOpacity(0.3),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  )
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [
                        const Text(
                          "Identify Printer",
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 5),
                        Text(
                          "Scan your printer or components for instant help",
                          style: TextStyle(
                            color:
                                Colors.white.withOpacity(0.9),
                            fontSize: 13,
                          ),
                        ),
                        const SizedBox(height: 20),
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.white,
                            foregroundColor:
                                AppStyles.primary,
                            shape: RoundedRectangleBorder(
                              borderRadius:
                                  BorderRadius.circular(12),
                            ),
                          ),
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) =>
                                    const ScanScreen(),
                              ),
                            );
                          },
                          child: const Text("Start Scanning"),
                        )
                      ],
                    ),
                  ),
                  const Icon(Icons.print_outlined,
                      size: 70, color: Colors.white24),
                ],
              ),
            ),

            const SizedBox(height: 35),
            const Text(
              "Recent Devices",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 15),

            _buildRecentPrinterItem(
                "HP LaserJet Pro", "Toner replacement guide", "2h ago"),
            _buildRecentPrinterItem(
                "Epson EcoTank", "Paper jam fixed", "Yesterday"),
            _buildRecentPrinterItem(
                "Canon PIXMA", "Network setup", "3 days ago"),
          ],
        ),
      ),

      // ================= Bottom Nav =================
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  // ================= Recent Devices =================
  Widget _buildRecentPrinterItem(
      String title, String subtitle, String time) {
    return Container(
      margin: const EdgeInsets.only(bottom: 15),
      padding: const EdgeInsets.all(12),
      decoration: AppStyles.cardDecoration.copyWith(
        borderRadius: BorderRadius.circular(22),
      ),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppStyles.primary.withOpacity(0.1),
            borderRadius: BorderRadius.circular(15),
          ),
          child: const Icon(Icons.print_outlined,
              color: AppStyles.primary),
        ),
        title: Text(title,
            style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle:
            Text(subtitle, style: const TextStyle(fontSize: 12)),
        trailing: Text(time,
            style: const TextStyle(color: Colors.grey, fontSize: 11)),
      ),
    );
  }

  // ================= Bottom Nav =================
  Widget _buildBottomNav() {
    return Container(
      margin: const EdgeInsets.fromLTRB(20, 0, 20, 30),
      height: 70,
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E),
        borderRadius: BorderRadius.circular(25),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          )
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _navIcon(Icons.home_rounded, 0),
          _navIcon(Icons.document_scanner_rounded, 1),
          _navIcon(Icons.history_rounded, 2),
          _navIcon(Icons.settings_rounded, 3), // ⚙️
        ],
      ),
    );
  }

  // ================= Navigation =================
  Widget _navIcon(IconData icon, int index) {
    bool isSelected = _currentIndex == index;

    return GestureDetector(
      onTap: () {
        if (index == 3) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SettingsScreen(
                userName: widget.userName,
                userEmail: "example@email.com",
              ),
            ),
          );
          return;
        }

        setState(() => _currentIndex = index);

        if (index == 1) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const ScanScreen(),
            ),
          );
        }
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: isSelected
              ? AppStyles.primary.withOpacity(0.2)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(15),
        ),
        child: Icon(
          icon,
          color: isSelected ? AppStyles.primary : Colors.white54,
          size: 26,
        ),
      ),
    );
  }
}