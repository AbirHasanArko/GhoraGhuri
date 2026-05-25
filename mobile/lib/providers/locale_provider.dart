import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

final localeProvider = StateNotifierProvider<LocaleNotifier, String>((ref) {
  return LocaleNotifier();
});

class LocaleNotifier extends StateNotifier<String> {
  LocaleNotifier() : super('bn') {
    _loadLocale();
  }

  static const _key = 'selected_locale';

  Future<void> _loadLocale() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(_key);
    if (saved != null) {
      state = saved;
    }
  }

  Future<void> toggle() async {
    final newLocale = state == 'bn' ? 'en' : 'bn';
    state = newLocale;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, newLocale);
  }

  void setLocale(String locale) async {
    state = locale;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, locale);
  }
}
