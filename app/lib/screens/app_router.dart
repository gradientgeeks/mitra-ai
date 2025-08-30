import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../screens/login_screen.dart';
import '../screens/onboarding_screen.dart';
import '../screens/main_navigation_screen.dart';

class AppRouter extends ConsumerWidget {
  const AppRouter({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);

    return authState.when(
      data: (state) {
        print('📱 AppRouter - Auth state: isAuthenticated=${state.isAuthenticated}, hasBackendUser=${state.hasBackendUser}, needsOnboarding=${state.needsOnboarding}, isLoading=${state.isLoading}, error=${state.error}');
        
        // Not authenticated - show login screen
        if (!state.isAuthenticated) {
          print('📱 Showing LoginScreen - not authenticated');
          return const LoginScreen();
        }

        // Authenticated but still loading backend user - show loading
        if (state.isAuthenticated && !state.hasBackendUser && state.isLoading) {
          print('📱 Showing loading - authenticated but loading backend user');
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }

        // Authenticated but backend user doesn't exist - show login (error state)
        if (state.isAuthenticated && !state.hasBackendUser && !state.isLoading) {
          print('📱 Showing LoginScreen - authenticated but no backend user');
          return const LoginScreen();
        }

        // Authenticated but needs onboarding
        if (state.needsOnboarding) {
          print('📱 Showing OnboardingScreen - needs onboarding');
          return const OnboardingScreen();
        }

        // Authenticated and onboarded - show main app
        print('📱 Showing MainNavigationScreen - fully authenticated');
        return const MainNavigationScreen();
      },
      loading: () {
        print('📱 AppRouter - Loading state');
        return const Scaffold(
          body: Center(
            child: CircularProgressIndicator(),
          ),
        );
      },
      error: (error, stack) {
        print('📱 AppRouter - Error state: $error');
        return Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.error_outline,
                  size: 64,
                  color: Colors.red,
                ),
                const SizedBox(height: 16),
                Text(
                  'Something went wrong',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  error.toString(),
                  style: Theme.of(context).textTheme.bodyMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () {
                    ref.invalidate(authControllerProvider);
                  },
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
