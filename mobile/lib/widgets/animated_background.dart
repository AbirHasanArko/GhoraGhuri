import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../config/theme.dart';

class AnimatedBackground extends StatelessWidget {
  const AnimatedBackground({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Stack(
      children: [
        // Base background
        Container(
          color: Theme.of(context).scaffoldBackgroundColor,
        ),
        // Animated Blob 1 (Top Right)
        Positioned(
          top: -100,
          right: -100,
          child: Container(
            width: 300,
            height: 300,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isDark 
                  ? GhoraGhuriTheme.primaryTeal.withOpacity(0.3)
                  : GhoraGhuriTheme.primaryTeal.withOpacity(0.15),
            ),
          ).animate(onPlay: (controller) => controller.repeat(reverse: true))
           .scaleXY(begin: 0.8, end: 1.2, duration: 6.seconds, curve: Curves.easeInOut)
           .move(begin: const Offset(20, 20), end: const Offset(-20, -20), duration: 8.seconds),
        ),
        // Animated Blob 2 (Bottom Left)
        Positioned(
          bottom: -50,
          left: -100,
          child: Container(
            width: 250,
            height: 250,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isDark
                  ? GhoraGhuriTheme.accentAmber.withOpacity(0.2)
                  : GhoraGhuriTheme.accentAmber.withOpacity(0.1),
            ),
          ).animate(onPlay: (controller) => controller.repeat(reverse: true))
           .scaleXY(begin: 1.1, end: 0.9, duration: 7.seconds, curve: Curves.easeInOut)
           .move(begin: const Offset(-30, 0), end: const Offset(30, -30), duration: 9.seconds),
        ),
        // Heavy blur overlay to blend the blobs
        Positioned.fill(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 80, sigmaY: 80),
            child: Container(color: Colors.transparent),
          ),
        ),
      ],
    );
  }
}
