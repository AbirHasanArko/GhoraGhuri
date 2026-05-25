import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/theme.dart';
import '../l10n/translations.dart';
import '../providers/locale_provider.dart';

class RouteScreen extends ConsumerStatefulWidget {
  const RouteScreen({super.key});

  @override
  ConsumerState<RouteScreen> createState() => _RouteScreenState();
}

class _RouteScreenState extends ConsumerState<RouteScreen> {
  final _originController = TextEditingController();
  final _destController = TextEditingController();
  String _optimizeMode = 'time';
  bool _loading = false;

  final List<Map<String, String>> _recentSearches = [
    {'from_bn': 'মিরপুর ১০', 'to_bn': 'ধানমন্ডি ২৭', 'from': 'Mirpur 10', 'to': 'Dhanmondi 27'},
    {'from_bn': 'গুলশান ১', 'to_bn': 'মতিঝিল', 'from': 'Gulshan 1', 'to': 'Motijheel'},
    {'from_bn': 'উত্তরা', 'to_bn': 'ফার্মগেট', 'from': 'Uttara', 'to': 'Farmgate'},
  ];

  Future<void> _searchRoute() async {
    if (_originController.text.isEmpty || _destController.text.isEmpty) return;
    setState(() => _loading = true);
    await Future.delayed(const Duration(seconds: 2));
    setState(() => _loading = false);
    if (mounted) {
      Navigator.pushNamed(context, '/route-result');
    }
  }

  @override
  Widget build(BuildContext context) {
    final locale = ref.watch(localeProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          Translations.tr('find_route_title', locale),
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
            // ── Route inputs ─────────────────────────────
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Theme.of(context).cardTheme.color ?? Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 15,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                children: [
                  TextField(
                    controller: _originController,
                    decoration: InputDecoration(
                      labelText: Translations.tr('starting_point', locale),
                      hintText: 'মিরপুর ১০ / Mirpur 10',
                      prefixIcon: const Icon(Icons.my_location, color: GhoraGhuriTheme.success),
                    ),
                  ),
                  const SizedBox(height: 12),
                  // Swap button
                  Center(
                    child: IconButton(
                      icon: const Icon(Icons.swap_vert, color: GhoraGhuriTheme.primaryTeal),
                      onPressed: () {
                        final temp = _originController.text;
                        _originController.text = _destController.text;
                        _destController.text = temp;
                      },
                    ),
                  ),
                  const SizedBox(height: 4),
                  TextField(
                    controller: _destController,
                    decoration: InputDecoration(
                      labelText: Translations.tr('destination', locale),
                      hintText: 'ধানমন্ডি ২৭ / Dhanmondi 27',
                      prefixIcon: const Icon(Icons.location_on, color: GhoraGhuriTheme.error),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // ── Optimization Chips ───────────────────────
            Row(
              children: [
                _OptChip(
                  label: Translations.tr('fastest', locale),
                  icon: Icons.speed,
                  isSelected: _optimizeMode == 'time',
                  onTap: () => setState(() => _optimizeMode = 'time'),
                ),
                const SizedBox(width: 8),
                _OptChip(
                  label: Translations.tr('cheapest', locale),
                  icon: Icons.savings,
                  isSelected: _optimizeMode == 'cost',
                  onTap: () => setState(() => _optimizeMode = 'cost'),
                ),
                const SizedBox(width: 8),
                _OptChip(
                  label: Translations.tr('comfortable', locale),
                  icon: Icons.weekend,
                  isSelected: _optimizeMode == 'comfort',
                  onTap: () => setState(() => _optimizeMode = 'comfort'),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // ── Search Button ────────────────────────────
            ElevatedButton.icon(
              onPressed: _loading ? null : _searchRoute,
              icon: _loading
                  ? const SizedBox(
                      height: 20, width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.search),
              label: Text(_loading ? Translations.tr('loading', locale) : Translations.tr('find_route_title', locale)),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 18),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
              ),
            ),
            const SizedBox(height: 32),

            // ── Recent Searches ──────────────────────────
            Text(
              Translations.tr('recent_searches', locale),
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            ...(_recentSearches.map((s) => _RecentSearchTile(
              fromBn: s['from_bn']!,
              toBn: s['to_bn']!,
              from: s['from']!,
              to: s['to']!,
              locale: locale,
              onTap: () {
                _originController.text = s['from_bn']!;
                _destController.text = s['to_bn']!;
              },
            ))),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _originController.dispose();
    _destController.dispose();
    super.dispose();
  }
}

class _OptChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;

  const _OptChip({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected
                ? GhoraGhuriTheme.primaryTeal
                : Colors.grey.shade100,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected
                  ? GhoraGhuriTheme.primaryTeal
                  : Colors.grey.shade300,
            ),
          ),
          child: Column(
            children: [
              Icon(
                icon,
                color: isSelected ? Colors.white : Colors.grey,
                size: 20,
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: isSelected ? Colors.white : Colors.grey.shade700,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RecentSearchTile extends StatelessWidget {
  final String fromBn;
  final String toBn;
  final String from;
  final String to;
  final String locale;
  final VoidCallback onTap;

  const _RecentSearchTile({
    required this.fromBn,
    required this.toBn,
    required this.from,
    required this.to,
    required this.locale,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardTheme.color ?? Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade200),
        ),
        child: Row(
          children: [
            const Icon(Icons.history, color: Colors.grey, size: 20),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    locale == 'bn' ? '$fromBn → $toBn' : '$from → $to',
                    style: const TextStyle(fontWeight: FontWeight.w500),
                  ),
                  Text(
                    locale == 'bn' ? '$from → $to' : '$fromBn → $toBn',
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios, size: 14, color: Colors.grey),
          ],
        ),
      ),
    );
  }
}
