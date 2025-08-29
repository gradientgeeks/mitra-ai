import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../models/user_model.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(userDocumentProvider);

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Row(
          children: [
            Image.asset(
              'assets/images/mitra_logo.png',
              width: 32,
              height: 32,
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Mitra',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: const Color(0xFF2C3E50),
                      ),
                ),
                Text(
                  'Your AI Companion',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: const Color(0xFF7F8C8D),
                      ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.settings_outlined,
              color: Color(0xFF2C3E50),
            ),
            onPressed: () {
              // Navigate to settings
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome message
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFF3498DB),
                    Color(0xFF2980B9),
                  ],
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF3498DB).withValues(alpha: 0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  userAsync.when(
                    data: (user) => Text(
                      user?.isOnboardingCompleted == true
                          ? 'Welcome back!'
                          : 'Hello there!',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    loading: () => Text(
                      'Hello there!',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    error: (_, __) => Text(
                      'Hello there!',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Ready to chat with your AI companion?',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.white.withValues(alpha: 0.9),
                        ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // User info card
            userAsync.when(
              data: (user) => Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.black.withValues(alpha: 0.05),
                    width: 1,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Your Profile',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: const Color(0xFF2C3E50),
                          ),
                    ),
                    const SizedBox(height: 12),
                    if (user?.isOnboardingCompleted == true) ...[
                      _buildInfoRow(
                        context,
                        icon: Icons.person_outline,
                        label: 'Profile Complete',
                        value: '✓',
                        valueColor: const Color(0xFF27AE60),
                      ),
                      const SizedBox(height: 8),
                      _buildInfoRow(
                        context,
                        icon: Icons.psychology_outlined,
                        label: 'AI Name',
                        value: user?.preferences.mitraName ?? 'Mitra',
                      ),
                      const SizedBox(height: 8),
                      _buildInfoRow(
                        context,
                        icon: Icons.volume_up_outlined,
                        label: 'Voice',
                        value: user?.preferences.preferredVoice.displayName ?? 'Default',
                      ),
                    ] else ...[
                      Row(
                        children: [
                          const Icon(
                            Icons.shield_outlined,
                            size: 20,
                            color: Color(0xFF27AE60),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Anonymous User',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: const Color(0xFF27AE60),
                                  fontWeight: FontWeight.w500,
                                ),
                          ),
                        ],
                      ),
                    ],
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(
                          Icons.timer_outlined,
                          size: 20,
                          color: Color(0xFF7F8C8D),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Session ${user?.totalSessions ?? 0}',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: const Color(0xFF7F8C8D),
                              ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (_, __) => Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.black.withValues(alpha: 0.05),
                    width: 1,
                  ),
                ),
                child: const Text('Unable to load profile'),
              ),
            ),

            const SizedBox(height: 24),

            // Action buttons
            Expanded(
              child: Column(
                children: [
                  // Text chat button
                  _buildActionButton(
                    context,
                    icon: Icons.chat_bubble_outline,
                    title: 'Text Chat',
                    subtitle: 'Start a conversation with Mitra',
                    gradient: const LinearGradient(
                      colors: [Color(0xFF9B59B6), Color(0xFF8E44AD)],
                    ),
                    onTap: () {
                      // Navigate to text chat
                    },
                  ),

                  const SizedBox(height: 16),

                  // Voice chat button
                  _buildActionButton(
                    context,
                    icon: Icons.mic_outlined,
                    title: 'Voice Chat',
                    subtitle: 'Talk naturally with Mitra',
                    gradient: const LinearGradient(
                      colors: [Color(0xFF3498DB), Color(0xFF2980B9)],
                    ),
                    onTap: () {
                      // Navigate to voice chat
                    },
                  ),

                  const SizedBox(height: 16),

                  // Wellness check button
                  _buildActionButton(
                    context,
                    icon: Icons.favorite_outline,
                    title: 'Wellness Check',
                    subtitle: 'Quick mood and wellness assessment',
                    gradient: const LinearGradient(
                      colors: [Color(0xFF27AE60), Color(0xFF229954)],
                    ),
                    onTap: () {
                      // Navigate to wellness check
                    },
                  ),
                ],
              ),
            ),

            // Privacy reminder
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF27AE60).withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: const Color(0xFF27AE60).withValues(alpha: 0.3),
                  width: 1,
                ),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.security,
                    color: Color(0xFF27AE60),
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Your conversations are private and secure',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: const Color(0xFF27AE60),
                            fontWeight: FontWeight.w500,
                          ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
    Color? valueColor,
  }) {
    return Row(
      children: [
        Icon(
          icon,
          size: 20,
          color: const Color(0xFF7F8C8D),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: const Color(0xFF7F8C8D),
              ),
        ),
        const Spacer(),
        Text(
          value,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: valueColor ?? const Color(0xFF2C3E50),
                fontWeight: FontWeight.w500,
              ),
        ),
      ],
    );
  }

  Widget _buildActionButton(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required Gradient gradient,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: gradient,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.1),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                color: Colors.white,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.white.withValues(alpha: 0.9),
                        ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.arrow_forward_ios,
              color: Colors.white,
              size: 16,
            ),
          ],
        ),
      ),
    );
  }
}
