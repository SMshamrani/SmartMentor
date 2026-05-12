import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../app_styles.dart';
import 'scan_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  final int userId;
  final String userName;
  final String userEmail;

  const HomeScreen({
    super.key,
    required this.userId,
    required this.userName,
    required this.userEmail,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  List<dynamic> recentDevices = [];
  bool isLoadingRecent = true;

  @override
  void initState() {
    super.initState();
    _loadRecentDevices();
  }

  Future<void> _loadRecentDevices() async {
    try {
      final response = await http.get(
        Uri.parse('http://10.0.2.2:3000/users/${widget.userId}/recent-devices'),
      );

      final data = jsonDecode(response.body);

      if (!mounted) return;

      setState(() {
        recentDevices = data['devices'] ?? [];
        isLoadingRecent = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => isLoadingRecent = false);
    }
  }

  String _formatTimeAgo(String? dateString) {
    if (dateString == null) return 'Recently';

    final date = DateTime.tryParse(dateString);
    if (date == null) return 'Recently';

    final diff = DateTime.now().difference(date.toLocal());

    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes} min ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays == 1) return 'Yesterday';
    return '${diff.inDays} days ago';
  }

  List<dynamic> get unfinishedDevices {
    return recentDevices.where((device) {
      final progress = device['progresspercent'] ?? 0;
      return progress > 0 && progress < 100;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final firstLetter = widget.userName.isNotEmpty
        ? widget.userName[0].toUpperCase()
        : "U";

    return Scaffold(
      backgroundColor: AppStyles.background,
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text(
          "SmartMentor",
          style: TextStyle(
            color: AppStyles.textDark,
            fontWeight: FontWeight.w900,
            fontSize: 24,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.notifications_none_rounded,
              color: AppStyles.textDark,
            ),
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
          ),
        ],
      ),
      body: Container(
        decoration: AppStyles.pageBackground,
        child: _currentIndex == 2
            ? _buildContinueScreen()
            : SingleChildScrollView(
                padding: const EdgeInsets.all(22),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Hello, ${widget.userName}! 👋",
                      style: const TextStyle(
                        fontSize: 30,
                        fontWeight: FontWeight.w900,
                        color: AppStyles.textDark,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      "Scan, learn, and fix your printer with AI guidance.",
                      style: TextStyle(
                        fontSize: 15,
                        color: AppStyles.textLight,
                      ),
                    ),
                    const SizedBox(height: 28),
                    _buildScanCard(),
                    const SizedBox(height: 34),
                    Row(
                      children: const [
                        Text(
                          "Recent Devices",
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w900,
                            color: AppStyles.textDark,
                          ),
                        ),
                        Spacer(),
                        Icon(Icons.history_rounded, color: AppStyles.primary),
                      ],
                    ),
                    const SizedBox(height: 16),
                    _buildRecentList(showOnlyUnfinished: false),
                  ],
                ),
              ),
      ),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  Widget _buildContinueScreen() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(22),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Continue Learning",
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w900,
              color: AppStyles.textDark,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            "Complete guides you already started.",
            style: TextStyle(fontSize: 15, color: AppStyles.textLight),
          ),
          const SizedBox(height: 24),
          _buildRecentList(showOnlyUnfinished: true),
        ],
      ),
    );
  }

  Widget _buildRecentList({required bool showOnlyUnfinished}) {
    final list = showOnlyUnfinished ? unfinishedDevices : recentDevices;

    if (isLoadingRecent) {
      return const Center(child: CircularProgressIndicator());
    }

    if (list.isEmpty) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: AppStyles.cardDecoration,
        child: Text(
          showOnlyUnfinished
              ? "No unfinished guides yet. Start a guide and it will appear here."
              : "No recent printers yet. Scan a printer to see it here.",
          style: const TextStyle(color: AppStyles.textLight, height: 1.5),
        ),
      );
    }

    return Column(
      children: [
        for (final device in list)
          _buildRecentPrinterItem(
            device['deviceid'],
            device['devicename'] ?? 'Unknown Printer',
            device['guide_title'] ?? 'Printer guide',
            _formatTimeAgo(device['last_opened']),
            device['status'] ?? 'opened',
            device['progresspercent'] ?? 0,
          ),
      ],
    );
  }

  Widget _buildScanCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(26),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppStyles.primary, AppStyles.primaryDark],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(32),
        boxShadow: [
          BoxShadow(
            color: AppStyles.primary.withOpacity(0.28),
            blurRadius: 28,
            offset: const Offset(0, 14),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Identify Printer",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  "Take a photo and let SmartMentor find the right guide.",
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 14,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 22),
                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: AppStyles.primary,
                    elevation: 0,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 18,
                      vertical: 13,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const ScanScreen(),
                      ),
                    ).then((_) => _loadRecentDevices());
                  },
                  icon: const Icon(Icons.camera_alt_rounded),
                  label: const Text(
                    "Start Scanning",
                    style: TextStyle(fontWeight: FontWeight.w800),
                  ),
                ),
              ],
            ),
          ),
          Icon(
            Icons.print_rounded,
            size: 78,
            color: Colors.white.withOpacity(0.25),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentPrinterItem(
    int deviceId,
    String title,
    String subtitle,
    String time,
    String source,
    int progressPercent,
  ) {
    return InkWell(
      borderRadius: BorderRadius.circular(24),
      onTap: () async {
        await http.post(
          Uri.parse('http://10.0.2.2:3000/user-progress/open-device'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'userId': widget.userId, 'deviceId': deviceId}),
        );

        if (!mounted) return;

        Navigator.pushNamed(
          context,
          '/device-detail',
          arguments: {
            'deviceId': deviceId,
            'source': source,
            'userId': widget.userId,
          },
        ).then((_) => _loadRecentDevices());
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(14),
        decoration: AppStyles.cardDecoration.copyWith(
          borderRadius: BorderRadius.circular(24),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppStyles.primaryLight,
                borderRadius: BorderRadius.circular(18),
              ),
              child: const Icon(
                Icons.print_rounded,
                color: AppStyles.primary,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontWeight: FontWeight.w900,
                      fontSize: 17,
                      color: AppStyles.textDark,
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    subtitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppStyles.textLight,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    time,
                    style: const TextStyle(
                      color: AppStyles.textLight,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            SizedBox(
              width: 48,
              height: 48,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CircularProgressIndicator(
                    value: progressPercent / 100,
                    strokeWidth: 5,
                    backgroundColor: AppStyles.primaryLight,
                    color: AppStyles.primary,
                  ),
                  Text(
                    '$progressPercent%',
                    style: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w900,
                      color: AppStyles.textDark,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomNav() {
    return Container(
      margin: const EdgeInsets.fromLTRB(20, 0, 20, 30),
      height: 70,
      decoration: BoxDecoration(
        color: AppStyles.textDark,
        borderRadius: BorderRadius.circular(26),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.22),
            blurRadius: 24,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _navIcon(Icons.home_rounded, 0),
          _navIcon(Icons.document_scanner_rounded, 1),
          _navIcon(Icons.playlist_add_check_rounded, 2),
          _navIcon(Icons.settings_rounded, 3),
        ],
      ),
    );
  }

  Widget _navIcon(IconData icon, int index) {
    final isSelected = _currentIndex == index;

    return GestureDetector(
      onTap: () {
        if (index == 3) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SettingsScreen(
                userName: widget.userName,
                userEmail: widget.userEmail,
              ),
            ),
          );
          return;
        }

        if (index == 1) {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const ScanScreen()),
          ).then((_) => _loadRecentDevices());
          return;
        }

        setState(() {
          _currentIndex = index;
        });
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected
              ? AppStyles.primary.withOpacity(0.22)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(18),
        ),
        child: Icon(
          icon,
          color: isSelected ? AppStyles.primary : Colors.white54,
          size: 27,
        ),
      ),
    );
  }
}
