import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../app_styles.dart';

class SearchScreen extends StatefulWidget {
  final int userId;
  final String userName;
  final String userEmail;

  const SearchScreen({
    super.key,
    required this.userId,
    required this.userName,
    required this.userEmail,
  });

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final TextEditingController searchController = TextEditingController();

  List<dynamic> results = [];
  bool isSearching = false;
  bool isGenerating = false;
  String query = '';

  Future<void> searchDevices() async {
    query = searchController.text.trim();

    if (query.isEmpty) return;

    setState(() {
      isSearching = true;
      results = [];
    });

    try {
      final response = await http.get(
        Uri.parse('http://10.0.2.2:3000/devices/search?q=$query'),
      );

      final data = jsonDecode(response.body);

      setState(() {
        results = data['devices'] ?? [];
      });
    } catch (e) {
      setState(() {
        results = [];
      });
    }

    setState(() {
      isSearching = false;
    });
  }

  Future<void> generateWithAI() async {
    if (query.isEmpty) return;

    setState(() => isGenerating = true);

    try {
      final response = await http.post(
        Uri.parse('http://10.0.2.2:3000/generate-device-guide'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'deviceName': query}),
      );

      final data = jsonDecode(response.body);

      if (!mounted) return;

      if (data['success'] == true) {
        final device = data['device'];
        final deviceId = device['deviceid'];

        await http.post(
          Uri.parse('http://10.0.2.2:3000/user-progress/open-device'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'userId': widget.userId, 'deviceId': deviceId}),
        );

        Navigator.pushNamed(
          context,
          '/device-detail',
          arguments: {
            'deviceId': deviceId,
            'source': data['source'] == 'database'
                ? 'database'
                : 'ai_generated',
            'userId': widget.userId,
            'userName': widget.userName,
            'userEmail': widget.userEmail,
          },
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('AI generation failed. Try again.')),
      );
    }

    if (mounted) {
      setState(() => isGenerating = false);
    }
  }

  Future<void> openDevice(dynamic device) async {
    final deviceId = device['deviceid'];

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
    );
  }

  @override
  void dispose() {
    searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final hasSearched = query.isNotEmpty;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(22),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Smart Search",
            style: TextStyle(
              fontSize: 30,
              fontWeight: FontWeight.w900,
              color: AppStyles.textDark,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            "Search any device in the database, or generate a guide using AI.",
            style: TextStyle(
              fontSize: 15,
              color: AppStyles.textLight,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 24),

          Container(
            padding: const EdgeInsets.all(18),
            decoration: AppStyles.cardDecoration,
            child: Column(
              children: [
                TextField(
                  controller: searchController,
                  decoration: AppStyles.fieldDecoration(
                    "Search for a device...",
                    Icons.search_rounded,
                  ),
                  onSubmitted: (_) => searchDevices(),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    style: AppStyles.primaryButton,
                    onPressed: isSearching ? null : searchDevices,
                    icon: isSearching
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : const Icon(Icons.search_rounded),
                    label: const Text("Search"),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 28),

          if (isSearching) const Center(child: CircularProgressIndicator()),

          if (!isSearching && results.isNotEmpty) ...[
            const Text(
              "Search Results",
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.w900,
                color: AppStyles.textDark,
              ),
            ),
            const SizedBox(height: 16),
            for (final device in results) _deviceCard(device),
          ],

          if (!isSearching && hasSearched && results.isEmpty) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(22),
              decoration: AppStyles.cardDecoration,
              child: Column(
                children: [
                  const Icon(
                    Icons.auto_awesome_rounded,
                    size: 48,
                    color: AppStyles.primary,
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    "Device not found",
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w900,
                      color: AppStyles.textDark,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    "Generate a new AI guide for \"$query\" and save it to the database.",
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      color: AppStyles.textLight,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 18),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: AppStyles.primaryButton,
                      onPressed: isGenerating ? null : generateWithAI,
                      icon: isGenerating
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                color: Colors.white,
                                strokeWidth: 2,
                              ),
                            )
                          : const Icon(Icons.auto_awesome_rounded),
                      label: Text(
                        isGenerating ? "Generating..." : "Generate with AI",
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _deviceCard(dynamic device) {
    return InkWell(
      borderRadius: BorderRadius.circular(24),
      onTap: () => openDevice(device),
      child: Container(
        margin: const EdgeInsets.only(bottom: 14),
        padding: const EdgeInsets.all(16),
        decoration: AppStyles.cardDecoration,
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
                size: 30,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    device['devicename'] ?? 'Unknown Device',
                    style: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w900,
                      color: AppStyles.textDark,
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    device['guide_title'] ?? 'Device guide',
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppStyles.textLight,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.arrow_forward_ios_rounded,
              size: 16,
              color: AppStyles.textLight,
            ),
          ],
        ),
      ),
    );
  }
}
