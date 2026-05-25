import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// GhoraGhuri Design System
/// Inspired by Bangladesh's water/rivers (teal) and rickshaw culture (amber)
class GhoraGhuriTheme {
  // ── Brand Colors ───────────────────────────────────────
  static const Color primaryTeal = Color(0xFF0D7377);
  static const Color primaryTealDark = Color(0xFF095B5E);
  static const Color primaryTealLight = Color(0xFF1A9CA0);
  static const Color accentAmber = Color(0xFFF5A623);
  static const Color accentAmberDark = Color(0xFFE09112);

  // ── Surface Colors ─────────────────────────────────────
  static const Color backgroundLight = Color(0xFFF8FAFB);
  static const Color surfaceLight = Color(0xFFFFFFFF);
  static const Color backgroundDark = Color(0xFF1A1F36);
  static const Color surfaceDark = Color(0xFF252B48);

  // ── Semantic Colors ────────────────────────────────────
  static const Color success = Color(0xFF2ECC71);
  static const Color warning = Color(0xFFF39C12);
  static const Color error = Color(0xFFE74C3C);
  static const Color info = Color(0xFF3498DB);

  // ── Transport Mode Colors ──────────────────────────────
  static const Color busColor = Color(0xFF2980B9);
  static const Color rickshawColor = Color(0xFF27AE60);
  static const Color cngColor = Color(0xFFF39C12);
  static const Color walkingColor = Color(0xFF95A5A6);
  static const Color legunaColor = Color(0xFF8E44AD);
  static const Color launchColor = Color(0xFF1ABC9C);

  // ── Light Theme ────────────────────────────────────────
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryTeal,
        primary: primaryTeal,
        secondary: accentAmber,
        surface: surfaceLight,
        brightness: Brightness.light,
      ),
      scaffoldBackgroundColor: backgroundLight,
      appBarTheme: AppBarTheme(
        backgroundColor: primaryTeal,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 2,
        shadowColor: Colors.black12,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryTeal,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.grey.shade50,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey.shade300),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey.shade300),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: primaryTeal, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      ),
      textTheme: GoogleFonts.interTextTheme().copyWith(
        headlineLarge: GoogleFonts.inter(
          fontSize: 32,
          fontWeight: FontWeight.bold,
          color: const Color(0xFF1A1F36),
        ),
        headlineMedium: GoogleFonts.inter(
          fontSize: 24,
          fontWeight: FontWeight.w600,
          color: const Color(0xFF1A1F36),
        ),
        bodyLarge: GoogleFonts.inter(
          fontSize: 16,
          color: const Color(0xFF4A4A4A),
        ),
        bodyMedium: GoogleFonts.inter(
          fontSize: 14,
          color: const Color(0xFF6B6B6B),
        ),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Colors.white,
        selectedItemColor: primaryTeal,
        unselectedItemColor: Colors.grey,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
    );
  }

  // ── Dark Theme ─────────────────────────────────────────
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryTealLight,
        primary: primaryTealLight,
        secondary: accentAmber,
        surface: surfaceDark,
        brightness: Brightness.dark,
      ),
      scaffoldBackgroundColor: backgroundDark,
      appBarTheme: AppBarTheme(
        backgroundColor: surfaceDark,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 4,
        shadowColor: Colors.black38,
        color: surfaceDark,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryTealLight,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
    );
  }

  /// Get color for a transport mode
  static Color transportModeColor(String mode) {
    switch (mode) {
      case 'bus':
        return busColor;
      case 'rickshaw':
        return rickshawColor;
      case 'cng':
        return cngColor;
      case 'walking':
        return walkingColor;
      case 'leguna':
        return legunaColor;
      case 'launch':
        return launchColor;
      default:
        return primaryTeal;
    }
  }

  /// Get icon for a transport mode
  static IconData transportModeIcon(String mode) {
    switch (mode) {
      case 'bus':
        return Icons.directions_bus;
      case 'rickshaw':
        return Icons.pedal_bike;
      case 'cng':
        return Icons.electric_rickshaw;
      case 'walking':
        return Icons.directions_walk;
      case 'leguna':
        return Icons.airport_shuttle;
      case 'launch':
        return Icons.directions_boat;
      case 'train':
        return Icons.train;
      case 'tempo':
        return Icons.local_shipping;
      default:
        return Icons.directions;
    }
  }
}
