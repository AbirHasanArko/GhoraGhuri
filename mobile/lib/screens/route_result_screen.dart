import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/theme.dart';
import '../l10n/translations.dart';
import '../providers/locale_provider.dart';

class RouteResultScreen extends ConsumerWidget {
  const RouteResultScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final locale = ref.watch(localeProvider);

    // Demo route result data
    final steps = [
      _StepData('bus', 'মিরপুর ১০', 'কাজীপাড়া', 'বাস (মিরপুর-গুলিস্তান রুট)', 8, 8, 1200),
      _StepData('bus', 'কাজীপাড়া', 'ফার্মগেট', 'বাস (মিরপুর-গুলিস্তান রুট)', 16, 10, 2200),
      _StepData('walking', 'ফার্মগেট', 'সায়েন্স ল্যাব', 'হাঁটুন', 12, 0, 1500),
      _StepData('rickshaw', 'সায়েন্স ল্যাব', 'ধানমন্ডি ২৭', 'রিকশা', 10, 20, 900),
    ];
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          Translations.tr('route_result', locale),
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
      body: Column(
        children: [
          // ── Summary Card ───────────────────────────────
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [
                  GhoraGhuriTheme.primaryTeal,
                  GhoraGhuriTheme.primaryTealDark,
                ],
              ),
              borderRadius: const BorderRadius.vertical(
                bottom: Radius.circular(24),
              ),
            ),
            child: SafeArea(
              top: false,
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _SummaryItem('সময়', '37-55', 'মিনিট', Icons.schedule),
                      _SummaryItem('ভাড়া', '৳30-42', 'টাকা', Icons.payments),
                      _SummaryItem('বদল', '2', 'বার', Icons.swap_horiz),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.verified, color: GhoraGhuriTheme.success, size: 16),
                        const SizedBox(width: 6),
                        Text(
                          'নির্ভরযোগ্যতা: 73%',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.9),
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // ── Steps ──────────────────────────────────────
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(20),
              itemCount: steps.length,
              itemBuilder: (context, index) {
                final step = steps[index];
                final isLast = index == steps.length - 1;

                return IntrinsicHeight(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Timeline
                      SizedBox(
                        width: 40,
                        child: Column(
                          children: [
                            Container(
                              width: 32,
                              height: 32,
                              decoration: BoxDecoration(
                                color: GhoraGhuriTheme.transportModeColor(step.mode),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Icon(
                                GhoraGhuriTheme.transportModeIcon(step.mode),
                                color: Colors.white,
                                size: 18,
                              ),
                            ),
                            if (!isLast)
                              Expanded(
                                child: Container(
                                  width: 2,
                                  color: Colors.grey.shade300,
                                ),
                              ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      // Step content
                      Expanded(
                        child: Container(
                          margin: EdgeInsets.only(bottom: isLast ? 0 : 16),
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Theme.of(context).cardTheme.color ?? Colors.white,
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: Colors.grey.shade200),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                step.instruction,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 14,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${step.from} → ${step.to}',
                                style: TextStyle(
                                  color: Colors.grey.shade600,
                                  fontSize: 13,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Wrap(
                                spacing: 12,
                                children: [
                                  _InfoChip(Icons.schedule, '${step.duration} মিনিট'),
                                  if (step.fare > 0)
                                    _InfoChip(Icons.payments, '৳${step.fare}'),
                                  _InfoChip(Icons.straighten, '${(step.distance / 1000).toStringAsFixed(1)} কিমি'),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),

          // ── Charge notice ──────────────────────────────
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: GhoraGhuriTheme.accentAmber.withOpacity(0.1),
              border: Border(
                top: BorderSide(color: Colors.grey.shade200),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.info_outline, color: GhoraGhuriTheme.accentAmber, size: 20),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    'রুট ফি ৳2.00 আপনার মোবাইল ব্যালেন্স থেকে কাটা হয়েছে',
                    style: TextStyle(fontSize: 12),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StepData {
  final String mode;
  final String from;
  final String to;
  final String instruction;
  final int duration;
  final int fare;
  final int distance;

  _StepData(this.mode, this.from, this.to, this.instruction,
      this.duration, this.fare, this.distance);
}

class _SummaryItem extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final IconData icon;

  const _SummaryItem(this.label, this.value, this.unit, this.icon);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: Colors.white.withOpacity(0.7), size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        Text(
          '$label ($unit)',
          style: TextStyle(
            fontSize: 11,
            color: Colors.white.withOpacity(0.7),
          ),
        ),
      ],
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip(this.icon, this.label);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: Colors.grey),
        const SizedBox(width: 4),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey.shade700)),
      ],
    );
  }
}
