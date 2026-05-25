import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../config/theme.dart';
import '../l10n/translations.dart';
import '../providers/locale_provider.dart';
import '../widgets/glass_card.dart';
import '../widgets/animated_background.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _phoneController = TextEditingController();
  final _otpController = TextEditingController();
  bool _otpSent = false;
  bool _loading = false;
  String? _referenceNo;

  Future<void> _requestOtp() async {
    if (_phoneController.text.length < 11) return;

    setState(() => _loading = true);

    // TODO: Call API - POST /api/v1/auth/otp/request
    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _otpSent = true;
      _loading = false;
      _referenceNo = 'demo-ref';
    });
  }

  Future<void> _verifyOtp() async {
    if (_otpController.text.length < 4) return;

    setState(() => _loading = true);

    // TODO: Call API - POST /api/v1/auth/otp/verify
    await Future.delayed(const Duration(seconds: 2));

    setState(() => _loading = false);

    if (mounted) {
      Navigator.pushReplacementNamed(context, '/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final locale = ref.watch(localeProvider);

    return Scaffold(
      extendBodyBehindAppBar: true,
      body: Stack(
        children: [
          const AnimatedBackground(),
          SafeArea(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // ── Header Branding ──────────────────────────
                const SizedBox(height: 60),
                const Icon(Icons.explore, size: 56, color: GhoraGhuriTheme.primaryTeal)
                    .animate().scale(duration: 600.ms, curve: Curves.easeOutBack),
                const SizedBox(height: 12),
                const Text(
                  'GHORAGHURI',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ).animate().fade(delay: 200.ms).slideY(),
                const SizedBox(height: 4),
                Text(
                  Translations.tr('login_header', locale),
                  style: TextStyle(
                    fontSize: 16,
                    color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.8),
                  ),
                  textAlign: TextAlign.center,
                ).animate().fade(delay: 300.ms).slideY(),
                const SizedBox(height: 40),

                // ── Login Card ─────────────────────────────
                Expanded(
                  child: GlassCard(
                    margin: const EdgeInsets.symmetric(horizontal: 20),
                    padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 40),
                    borderRadius: 32,
                    child: SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const SizedBox(height: 16),
                          Text(
                            _otpSent
                                ? Translations.tr('enter_otp', locale)
                                : Translations.tr('enter_phone', locale),
                            style: Theme.of(context).textTheme.headlineMedium,
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            _otpSent
                                ? Translations.tr('enter_otp_subtitle', locale)
                                : Translations.tr('enter_phone_subtitle', locale),
                            style: Theme.of(context).textTheme.bodyMedium,
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 32),

                          if (!_otpSent) ...[
                            // Phone input
                            TextField(
                              controller: _phoneController,
                              keyboardType: TextInputType.phone,
                              maxLength: 11,
                              inputFormatters: [
                                FilteringTextInputFormatter.digitsOnly,
                              ],
                              decoration: InputDecoration(
                                labelText: Translations.tr('phone_label', locale),
                                hintText: '01XXXXXXXXX',
                                prefixIcon: const Icon(Icons.phone_android),
                                prefixText: '+880 ',
                                counterText: '',
                              ),
                            ),
                            const SizedBox(height: 24),
                            ElevatedButton(
                              onPressed: _loading ? null : _requestOtp,
                              child: _loading
                                  ? const SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        color: Colors.white,
                                      ),
                                    )
                                  : Text(Translations.tr('send_otp', locale)),
                            ),
                          ] else ...[
                            // OTP input
                            TextField(
                              controller: _otpController,
                              keyboardType: TextInputType.number,
                              maxLength: 6,
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                fontSize: 28,
                                letterSpacing: 12,
                                fontWeight: FontWeight.bold,
                              ),
                              inputFormatters: [
                                FilteringTextInputFormatter.digitsOnly,
                              ],
                              decoration: const InputDecoration(
                                hintText: '• • • • • •',
                                counterText: '',
                              ),
                            ),
                            const SizedBox(height: 24),
                            ElevatedButton(
                              onPressed: _loading ? null : _verifyOtp,
                              child: _loading
                                  ? const SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        color: Colors.white,
                                      ),
                                    )
                                  : Text(Translations.tr('verify_otp', locale)),
                            ),
                            const SizedBox(height: 16),
                            TextButton(
                              onPressed: () {
                                setState(() {
                                  _otpSent = false;
                                  _otpController.clear();
                                });
                              },
                              child: Text(Translations.tr('change_number', locale)),
                            ),
                          ],
                        ],
                      ),
                    ),
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
  void dispose() {
    _phoneController.dispose();
    _otpController.dispose();
    super.dispose();
  }
}
