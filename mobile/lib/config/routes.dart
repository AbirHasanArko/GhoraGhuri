import 'package:flutter/material.dart';
import '../screens/splash_screen.dart';
import '../screens/login_screen.dart';
import '../screens/home_screen.dart';
import '../screens/route_screen.dart';
import '../screens/route_result_screen.dart';
import '../screens/contribute_screen.dart';
import '../screens/wallet_screen.dart';
import '../screens/about_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String home = '/home';
  static const String findRoute = '/find-route';
  static const String routeResult = '/route-result';
  static const String contribute = '/contribute';
  static const String wallet = '/wallet';
  static const String about = '/about';

  static Map<String, WidgetBuilder> get routes => {
    splash: (_) => const SplashScreen(),
    login: (_) => const LoginScreen(),
    home: (_) => const HomeScreen(),
    findRoute: (_) => const RouteScreen(),
    routeResult: (_) => const RouteResultScreen(),
    contribute: (context) => const ContributeScreen(),
    wallet: (context) => const WalletScreen(),
    about: (context) => const AboutScreen(),
  };
}
