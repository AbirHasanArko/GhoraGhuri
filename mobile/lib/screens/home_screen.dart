import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../config/theme.dart';
import '../l10n/translations.dart';
import '../providers/locale_provider.dart';
import '../providers/theme_provider.dart';
import '../widgets/glass_card.dart';
import '../widgets/animated_background.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final locale = ref.watch(localeProvider);
    final themeMode = ref.watch(themeProvider);
    final isDark = themeMode == ThemeMode.dark;

    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: Text(
          Translations.tr('app_name_bn', locale),
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
        actionsIconTheme: IconThemeData(
          color: isDark ? Colors.white : GhoraGhuriTheme.primaryTeal,
        ),
        actions: [
          // Language toggle
          IconButton(
            icon: const Icon(Icons.language),
            tooltip: 'বাংলা / English',
            onPressed: () {
              ref.read(localeProvider.notifier).toggle();
            },
          ),
          // Wallet
          IconButton(
            icon: const Icon(Icons.account_balance_wallet),
            onPressed: () => Navigator.pushNamed(context, '/wallet'),
          ),
        ],
      ),
      drawer: Drawer(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor.withOpacity(0.9),
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(color: GhoraGhuriTheme.primaryTeal),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  const Icon(Icons.explore, size: 48, color: Colors.white),
                  const SizedBox(height: 12),
                  Text(
                    Translations.tr('app_name_en', locale),
                    style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
            ListTile(
              leading: Icon(isDark ? Icons.light_mode : Icons.dark_mode),
              title: const Text('Toggle Theme'),
              onTap: () {
                ref.read(themeProvider.notifier).toggleTheme();
              },
            ),
            ListTile(
              leading: const Icon(Icons.info_outline),
              title: Text(Translations.tr('about_app', locale)),
              onTap: () {
                Navigator.pop(context);
                Navigator.pushNamed(context, '/about');
              },
            ),
          ],
        ),
      ),
      body: Stack(
        children: [
          const AnimatedBackground(),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
              // ── Greeting ────────────────────────────────
              const SizedBox(height: 16),
              Text(
                Translations.tr('where_to', locale),
                style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ).animate().fade(duration: 500.ms).slideY(begin: -0.2),
              const SizedBox(height: 4),
              Text(
                Translations.tr('where_to_en', locale),
                style: Theme.of(context).textTheme.bodyMedium,
              ).animate().fade(delay: 200.ms).slideY(begin: -0.2),
              const SizedBox(height: 32),

              // ── Mode Cards ──────────────────────────────
              Expanded(
                child: Column(
                  children: [
                    // Find Route Card
                    Expanded(
                      child: _ModeCard(
                        icon: Icons.route,
                        title: Translations.tr('find_route_title', locale),
                        subtitle: Translations.tr('find_route_subtitle', locale),
                        description: Translations.tr('find_route_desc', locale),
                        onTap: () => Navigator.pushNamed(context, '/find-route'),
                      ).animate().fade(delay: 300.ms).scale(begin: const Offset(0.95, 0.95)),
                    ),
                    const SizedBox(height: 16),
                    // Contribute Card
                    Expanded(
                      child: _ModeCard(
                        icon: Icons.volunteer_activism,
                        title: Translations.tr('contribute_title', locale),
                        subtitle: Translations.tr('contribute_subtitle', locale),
                        description: Translations.tr('contribute_desc', locale),
                        onTap: () => Navigator.pushNamed(context, '/contribute'),
                      ).animate().fade(delay: 400.ms).scale(begin: const Offset(0.95, 0.95)),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // ── Quick Stats ─────────────────────────────
              GlassCard(
                padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _StatItem(
                      icon: Icons.monetization_on,
                      value: '150',
                      label: Translations.tr('stat_coins', locale),
                      color: GhoraGhuriTheme.accentAmber,
                    ),
                    _StatItem(
                      icon: Icons.map,
                      value: '12',
                      label: Translations.tr('stat_routes', locale),
                      color: GhoraGhuriTheme.primaryTeal,
                    ),
                    _StatItem(
                      icon: Icons.star,
                      value: '4.2',
                      label: Translations.tr('stat_rating', locale),
                      color: GhoraGhuriTheme.success,
                    ),
                  ],
                ),
              ).animate().fade(delay: 500.ms).slideY(begin: 0.2),
            ],
          ),
        ),
      ),
      ],
      ),
    );
  }
}

class _ModeCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final String description;
  final VoidCallback onTap;

  const _ModeCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.description,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: GlassCard(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, size: 24, color: Theme.of(context).colorScheme.primary),
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            Text(
              subtitle,
              style: TextStyle(
                fontSize: 13,
                color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.8),
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            Expanded(
              child: Text(
                description,
                style: TextStyle(
                  fontSize: 12,
                  color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            Align(
              alignment: Alignment.bottomRight,
              child: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.arrow_forward,
                  color: Theme.of(context).colorScheme.primary,
                  size: 16,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color color;

  const _StatItem({
    required this.icon,
    required this.value,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }
}
