import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/theme.dart';
import '../l10n/translations.dart';
import '../providers/locale_provider.dart';

class ContributeScreen extends ConsumerWidget {
  const ContributeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final locale = ref.watch(localeProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          Translations.tr('contribute_title', locale),
          style: TextStyle(
            color: isDark ? Colors.white : GhoraGhuriTheme.primaryTeal,
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: IconThemeData(
          color: isDark ? Colors.white : GhoraGhuriTheme.primaryTeal,
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Earnings banner ──────────────────────────
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [GhoraGhuriTheme.accentAmber, GhoraGhuriTheme.accentAmberDark],
                ),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Column(
                children: [
                  const Icon(Icons.monetization_on, color: Colors.white, size: 36),
                  const SizedBox(height: 8),
                  const Text(
                    'আজকের আয়',
                    style: TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                  const Text(
                    '12 যাত্রী কয়েন',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    '≈ ৳1.20',
                    style: TextStyle(color: Colors.white.withOpacity(0.8)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // ── Contribution options ─────────────────────
            _ContributeOption(
              icon: Icons.gps_fixed,
              title: Translations.tr('share_live_gps', locale),
              subtitle: 'GPS Track',
              description: Translations.tr('gps_desc', locale),
              reward: '5 Coins/km',
              color: GhoraGhuriTheme.primaryTeal,
              onTap: () {
                // TODO: Start GPS tracking
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('জিপিএস ট্র্যাকিং শুরু হচ্ছে...')),
                );
              },
            ),
            const SizedBox(height: 12),

            _ContributeOption(
              icon: Icons.people_alt,
              title: Translations.tr('report_crowd', locale),
              subtitle: 'Crowd Report',
              description: Translations.tr('crowd_desc', locale),
              reward: '2 Coins',
              color: GhoraGhuriTheme.warning,
              onTap: () => _showCrowdDialog(context, locale),
            ),
            const SizedBox(height: 12),

            _ContributeOption(
              icon: Icons.verified_user,
              title: 'রুট যাচাই',
              subtitle: 'Verify Route',
              description: 'বিদ্যমান রুটের তথ্য যাচাই করুন',
              reward: '5 কয়েন',
              color: GhoraGhuriTheme.success,
              onTap: () {
                // TODO: Route verification flow
              },
            ),
            const SizedBox(height: 12),

            _ContributeOption(
              icon: Icons.add_location,
              title: 'স্টপ রিপোর্ট',
              subtitle: 'Stop Report',
              description: 'নতুন বাস স্টপ/রিকশা স্ট্যান্ড যুক্ত করুন',
              reward: '3 কয়েন',
              color: GhoraGhuriTheme.info,
              onTap: () {
                // TODO: Stop report flow
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showCrowdDialog(BuildContext context, String locale) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'ভিড়ের অবস্থা',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _CrowdButton('কম', '🟢', 'low', context),
                  _CrowdButton('মাঝারি', '🟡', 'medium', context),
                  _CrowdButton('বেশি', '🟠', 'high', context),
                  _CrowdButton('অত্যন্ত', '🔴', 'extreme', context),
                ],
              ),
              const SizedBox(height: 24),
            ],
          ),
        );
      },
    );
  }

  Widget _CrowdButton(String label, String emoji, String level, BuildContext context) {
    return GestureDetector(
      onTap: () {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('ভিড় রিপোর্ট জমা হয়েছে — 2 কয়েন অর্জিত! $emoji')),
        );
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        decoration: BoxDecoration(
          color: Colors.grey.shade100,
          borderRadius: BorderRadius.circular(14),
        ),
        child: Column(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 28)),
            const SizedBox(height: 4),
            Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}

class _ContributeOption extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final String description;
  final String reward;
  final Color color;
  final VoidCallback onTap;

  const _ContributeOption({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.description,
    required this.reward,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Theme.of(context).cardTheme.color ?? Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.grey.shade200),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                  Text(subtitle, style: TextStyle(fontSize: 12, color: Colors.grey.shade500)),
                  const SizedBox(height: 4),
                  Text(description, style: TextStyle(fontSize: 13, color: Colors.grey.shade600)),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: GhoraGhuriTheme.accentAmber.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                reward,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: GhoraGhuriTheme.accentAmberDark,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
