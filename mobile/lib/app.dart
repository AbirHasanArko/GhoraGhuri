import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'config/theme.dart';
import 'config/routes.dart';
import 'providers/theme_provider.dart';

class GhoraGhuriApp extends ConsumerWidget {
  const GhoraGhuriApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);

    return MaterialApp(
      title: 'GhoraGhuri (ঘোরাঘুরি)',
      debugShowCheckedModeBanner: false,
      theme: GhoraGhuriTheme.lightTheme,
      darkTheme: GhoraGhuriTheme.darkTheme,
      themeMode: themeMode,
      initialRoute: AppRoutes.splash,
      routes: AppRoutes.routes,
    );
  }
}
