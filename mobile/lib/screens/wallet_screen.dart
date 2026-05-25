import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/theme.dart';
import '../l10n/translations.dart';
import '../providers/locale_provider.dart';

class WalletScreen extends ConsumerWidget {
  const WalletScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final locale = ref.watch(localeProvider);
    final transactions = [
      _TxnData('contribution_reward', Translations.tr('txn_crowd', locale), 2, '10:30 AM'),
      _TxnData('contribution_reward', Translations.tr('txn_gps', locale), 11, '9:15 AM'),
      _TxnData('route_charge', Translations.tr('txn_route', locale), -20, Translations.tr('yesterday', locale)),
      _TxnData('contribution_reward', Translations.tr('txn_verify', locale), 5, Translations.tr('yesterday', locale)),
      _TxnData('bonus', Translations.tr('txn_bonus', locale), 50, Translations.tr('date_may23', locale)),
    ];
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          Translations.tr('wallet_title', locale),
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
          // ── Balance Card ───────────────────────────────
          Container(
            width: double.infinity,
            margin: const EdgeInsets.all(20),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  GhoraGhuriTheme.primaryTeal,
                  GhoraGhuriTheme.primaryTealDark,
                  Color(0xFF063D3F),
                ],
              ),
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: GhoraGhuriTheme.primaryTeal.withOpacity(0.3),
                  blurRadius: 20,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: Column(
              children: [
                Text(
                  Translations.tr('total_balance', locale),
                  style: const TextStyle(color: Colors.white70, fontSize: 14),
                ),
                const SizedBox(height: 8),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.monetization_on, color: GhoraGhuriTheme.accentAmber, size: 32),
                    SizedBox(width: 8),
                    Text(
                      '148',
                      style: TextStyle(
                        fontSize: 48,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
                Text(
                  '≈ ৳14.80',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 20),
                Row(
                  children: [
                    Expanded(
                      child: _WalletStat(Translations.tr('earned', locale), '198', GhoraGhuriTheme.success),
                    ),
                    Container(width: 1, height: 40, color: Colors.white24),
                    Expanded(
                      child: _WalletStat(Translations.tr('spent', locale), '50', GhoraGhuriTheme.error),
                    ),
                    Container(width: 1, height: 40, color: Colors.white24),
                    Expanded(
                      child: _WalletStat(Translations.tr('redeemed', locale), '৳0', GhoraGhuriTheme.accentAmber),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(Translations.tr('recharge_msg', locale))),
                          );
                        },
                        icon: const Icon(Icons.add_card),
                        label: Text(Translations.tr('recharge_now', locale)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: GhoraGhuriTheme.primaryTeal.withOpacity(0.8),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                            side: const BorderSide(color: Colors.white30),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(Translations.tr('redeem_error', locale))),
                          );
                        },
                        icon: const Icon(Icons.phone_android),
                        label: Text(Translations.tr('redeem_now', locale)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: GhoraGhuriTheme.accentAmber,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // ── Transaction history ────────────────────────
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              children: [
                Text(
                  Translations.tr('recent_transactions', locale),
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () {},
                  child: Text(Translations.tr('view_all', locale)),
                ),
              ],
            ),
          ),

          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              itemCount: transactions.length,
              itemBuilder: (context, index) {
                final txn = transactions[index];
                final isPositive = txn.amount > 0;

                return Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardTheme.color ?? Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey.shade200),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: (isPositive
                              ? GhoraGhuriTheme.success
                              : GhoraGhuriTheme.error)
                              .withOpacity(0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(
                          isPositive ? Icons.arrow_downward : Icons.arrow_upward,
                          color: isPositive ? GhoraGhuriTheme.success : GhoraGhuriTheme.error,
                          size: 18,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              txn.description,
                              style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 13),
                            ),
                            Text(
                              txn.time,
                              style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                            ),
                          ],
                        ),
                      ),
                      Text(
                        '${isPositive ? '+' : ''}${txn.amount} ${Translations.tr('coins_label', locale)}',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: isPositive ? GhoraGhuriTheme.success : GhoraGhuriTheme.error,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _TxnData {
  final String type;
  final String description;
  final int amount;
  final String time;
  _TxnData(this.type, this.description, this.amount, this.time);
}

class _WalletStat extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  const _WalletStat(this.label, this.value, this.color);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 18)),
        Text(label, style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 11)),
      ],
    );
  }
}
