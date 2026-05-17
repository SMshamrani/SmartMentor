import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../app_styles.dart';
import 'scan_screen.dart';
import 'search_screen.dart';

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
  List<dynamic> searchedDevices = [];
  List<dynamic> notifications = [];

  bool isLoadingRecent = true;
  bool isSearchingDatabase = false;
  bool isLoadingNotifications = false;

  bool _showSearch = false;
  String _searchQuery = '';

  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadRecentDevices();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
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

  Future<void> _searchDevicesFromDatabase(String query) async {
    if (query.trim().isEmpty) {
      setState(() {
        searchedDevices = [];
        isSearchingDatabase = false;
      });
      return;
    }

    try {
      setState(() {
        isSearchingDatabase = true;
      });

      final response = await http.get(
        Uri.parse('http://10.0.2.2:3000/devices/search?q=$query'),
      );

      final data = jsonDecode(response.body);

      if (!mounted) return;

      setState(() {
        searchedDevices = data['devices'] ?? [];
        isSearchingDatabase = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        searchedDevices = [];
        isSearchingDatabase = false;
      });
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

  List<dynamic> _filterDevices(List<dynamic> devices) {
    if (_searchQuery.trim().isEmpty) return devices;

    if (searchedDevices.isNotEmpty) return searchedDevices;

    final query = _searchQuery.toLowerCase();

    return devices.where((device) {
      final name = (device['devicename'] ?? '').toString().toLowerCase();
      final guide = (device['guide_title'] ?? '').toString().toLowerCase();

      return name.contains(query) || guide.contains(query);
    }).toList();
  }

  void _openSettings() {
    Navigator.pushNamed(
      context,
      '/settings',
      arguments: {
        'userId': widget.userId,
        'userName': widget.userName,
        'userEmail': widget.userEmail,
      },
    );
  }

  void _openScan() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ScanScreen(
          userId: widget.userId,
          userName: widget.userName,
          userEmail: widget.userEmail,
        ),
      ),
    ).then((_) => _loadRecentDevices());
  }

  Future<void> _showNotificationsSheet() async {
    try {
      setState(() {
        isLoadingNotifications = true;
      });

      final response = await http.get(
        Uri.parse('http://10.0.2.2:3000/users/${widget.userId}/notifications'),
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
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(22),
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 50,
                height: 5,
                decoration: BoxDecoration(
                  color: AppStyles.primaryLight,
                  borderRadius: BorderRadius.circular(20),
                ),
              ),
              const SizedBox(height: 22),
              const Text(
                "Notifications",
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w900,
                  color: AppStyles.textDark,
                ),
              ),
              const SizedBox(height: 20),
              if (isLoadingNotifications) const CircularProgressIndicator(),
              if (!isLoadingNotifications && notifications.isEmpty)
                const Padding(
                  padding: EdgeInsets.all(20),
                  child: Text(
                    "No notifications yet.",
                    style: TextStyle(color: AppStyles.textLight),
                  ),
                ),
              if (!isLoadingNotifications)
                ...notifications.map((notification) {
                  return _notificationTile(
                    _notificationIcon(notification['type']),
                    notification['title'] ?? 'Notification',
                    notification['message'] ?? '',
                  );
                }).toList(),
            ],
          ),
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

  Widget _notificationTile(IconData icon, String title, String subtitle) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppStyles.primaryLight,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: AppStyles.primary,
            child: Icon(icon, color: Colors.white, size: 20),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: AppStyles.textDark,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: const TextStyle(
                    color: AppStyles.textLight,
                    fontSize: 13,
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
            icon: Icon(
              _showSearch ? Icons.close_rounded : Icons.search_rounded,
              color: AppStyles.textDark,
            ),
            onPressed: () {
              setState(() {
                _showSearch = !_showSearch;

                if (!_showSearch) {
                  _searchQuery = '';

                  searchedDevices = [];

                  _searchController.clear();
                }
              });
            },
          ),

          Padding(
            padding: const EdgeInsets.only(right: 4, left: 2),
            child: Stack(
              children: [
                Container(
                  margin: const EdgeInsets.only(top: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.75),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 10,
                      ),
                    ],
                  ),
                  child: IconButton(
                    icon: const Icon(
                      Icons.notifications_none_rounded,
                      color: AppStyles.textDark,
                    ),
                    onPressed: _showNotificationsSheet,
                  ),
                ),

                Positioned(
                  right: 10,
                  top: 10,
                  child: Container(
                    width: 10,
                    height: 10,
                    decoration: const BoxDecoration(
                      color: Colors.redAccent,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
              ],
            ),
          ),

          Padding(
            padding: const EdgeInsets.only(right: 22, left: 6),
            child: InkWell(
              borderRadius: BorderRadius.circular(100),
              onTap: _openSettings,
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
          ),
        ],
      ),
      body: Container(
        decoration: AppStyles.pageBackground,
        child: _currentIndex == 2
            ? SearchScreen(
                userId: widget.userId,
                userName: widget.userName,
                userEmail: widget.userEmail,
              )
            : _currentIndex == 3
            ? _buildContinueScreen()
            : SingleChildScrollView(
                padding: const EdgeInsets.all(22),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (_showSearch) _buildSearchField(),
                    if (_showSearch) const SizedBox(height: 20),
                    Text(
                      "Hello, ${widget.userName}!",
                      style: const TextStyle(
                        fontSize: 30,
                        fontWeight: FontWeight.w900,
                        color: AppStyles.textDark,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      "Scan, learn, and manage your smart devices with AI guidance.",
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

  Widget _buildSearchField() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: AppStyles.cardDecoration.copyWith(
        borderRadius: BorderRadius.circular(22),
      ),
      child: TextField(
        controller: _searchController,
        onChanged: (value) async {
          setState(() {
            _searchQuery = value;
          });

          await _searchDevicesFromDatabase(value);
        },
        decoration: InputDecoration(
          hintText: "Search devices in database...",
          border: InputBorder.none,
          icon: const Icon(Icons.search_rounded, color: AppStyles.primary),
          suffixIcon: isSearchingDatabase
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: Padding(
                    padding: EdgeInsets.all(12),
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                )
              : null,
        ),
      ),
    );
  }

  Widget _buildContinueScreen() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(22),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_showSearch) _buildSearchField(),
          if (_showSearch) const SizedBox(height: 20),
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
            "Complete device guides you already started.",
            style: TextStyle(fontSize: 15, color: AppStyles.textLight),
          ),
          const SizedBox(height: 24),
          _buildRecentList(showOnlyUnfinished: true),
        ],
      ),
    );
  }

  Widget _buildRecentList({required bool showOnlyUnfinished}) {
    final baseList = showOnlyUnfinished ? unfinishedDevices : recentDevices;
    final list = _filterDevices(baseList);

    if (isLoadingRecent) {
      return const Center(child: CircularProgressIndicator());
    }

    if (isSearchingDatabase) {
      return const Center(child: CircularProgressIndicator());
    }

    if (list.isEmpty) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: AppStyles.cardDecoration,
        child: Text(
          _searchQuery.isNotEmpty
              ? "No devices found in database."
              : showOnlyUnfinished
              ? "No unfinished guides yet. Start a guide and it will appear here."
              : "No recent devices yet. Scan a device to see it here.",
          style: const TextStyle(color: AppStyles.textLight, height: 1.5),
        ),
      );
    }

    return Column(
      children: [
        for (final device in list)
          _buildRecentDeviceItem(
            device['deviceid'],
            device['devicename'] ?? 'Unknown Device',
            device['guide_title'] ?? 'Device guide',
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
                  "Identify Device",
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
                  onPressed: _openScan,
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
            Icons.devices_rounded,
            size: 78,
            color: Colors.white.withOpacity(0.25),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentDeviceItem(
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
            'source': 'database',
            'userId': widget.userId,
            'userName': widget.userName,
            'userEmail': widget.userEmail,
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
                Icons.devices_rounded,
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
          _navIcon(Icons.search_rounded, 2),
          _navIcon(Icons.playlist_add_check_rounded, 3),
          _navIcon(Icons.settings_rounded, 4),
        ],
      ),
    );
  }

  Widget _navIcon(IconData icon, int index) {
    final isSelected = _currentIndex == index;

    return GestureDetector(
      onTap: () {
        if (index == 4) {
          _openSettings();
          return;
        }

        if (index == 1) {
          _openScan();
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
