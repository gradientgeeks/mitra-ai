import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../models/user_model.dart';
import 'login_screen.dart';
import 'chat_screen.dart';
import 'talk_screen.dart';

// Provider for selected problem category
final selectedProblemCategoryProvider = StateProvider<ProblemCategory?>((ref) => null);

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);
    
    return authState.when(
      data: (state) => _buildHomeContent(context, ref, state.backendUser),
      loading: () => const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      ),
      error: (error, stack) => Scaffold(
        body: Center(
          child: Text('Error: $error'),
        ),
      ),
    );
  }

  Widget _buildHomeContent(BuildContext context, WidgetRef ref, UserModel? user) {
    final selectedCategory = ref.watch(selectedProblemCategoryProvider);

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
            Text(
              'Mitra',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF2C3E50),
                  ),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () async {
              await ref.read(authControllerProvider.notifier).signOut();
              if (context.mounted) {
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (context) => const LoginScreen()),
                );
              }
            },
            icon: const Icon(
              Icons.logout,
              color: Color(0xFF7F8C8D),
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Message
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      const Color(0xFF3498DB),
                      const Color(0xFF2980B9),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF3498DB).withOpacity(0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Welcome to your safe space',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'You\'re signed in anonymously. Your privacy is protected.',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Colors.white.withOpacity(0.9),
                          ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // Problem Category Selection
              _buildProblemCategorySection(context, ref, selectedCategory),

              const SizedBox(height: 30),

              // Chat and Call Cards
              if (user != null) _buildMitraInteractionCards(context, ref, user, selectedCategory),

              const SizedBox(height: 30),

              // Account Linking Reminder
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF3498DB).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: const Color(0xFF3498DB).withOpacity(0.3),
                    width: 1,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.link,
                      color: const Color(0xFF3498DB),
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Link your account in Settings to secure your data',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: const Color(0xFF3498DB),
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
      ),
    );
  }

  Widget _buildProblemCategorySection(BuildContext context, WidgetRef ref, ProblemCategory? selectedCategory) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.psychology_outlined,
                color: const Color(0xFF3498DB),
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'How are you feeling today?',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFF2C3E50),
                    ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            'Select what\'s on your mind to get personalized support',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFF7F8C8D),
                ),
          ),
          const SizedBox(height: 20),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: ProblemCategory.values.map((category) {
              final isSelected = selectedCategory == category;
              return GestureDetector(
                onTap: () {
                  ref.read(selectedProblemCategoryProvider.notifier).state =
                      isSelected ? null : category;
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? const Color(0xFF3498DB)
                        : const Color(0xFFF8F9FA),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: isSelected
                          ? const Color(0xFF3498DB)
                          : const Color(0xFFE0E0E0),
                      width: 1,
                    ),
                  ),
                  child: Text(
                    _getProblemCategoryDisplayName(category),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: isSelected ? Colors.white : const Color(0xFF7F8C8D),
                          fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                        ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildMitraInteractionCards(BuildContext context, WidgetRef ref, UserModel user, ProblemCategory? selectedCategory) {
    return Column(
      children: [
        Row(
          children: [
            // Chat Card
            Expanded(
              child: _buildInteractionCard(
                context: context,
                title: 'Chat with ${user.preferences.mitraName}',
                subtitle: 'Text Conversation',
                icon: Icons.chat_bubble_outline,
                activeIcon: Icons.chat_bubble,
                color: const Color(0xFF3498DB),
                onTap: () => _navigateToChat(context, selectedCategory),
                user: user,
                ref: ref,
              ),
            ),
            const SizedBox(width: 16),
            // Call Card
            Expanded(
              child: _buildInteractionCard(
                context: context,
                title: 'Call ${user.preferences.mitraName}',
                subtitle: 'Voice Conversation',
                icon: Icons.phone_outlined,
                activeIcon: Icons.phone,
                color: const Color(0xFF27AE60),
                onTap: () => _navigateToCall(context, selectedCategory),
                user: user,
                ref: ref,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (selectedCategory != null)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF27AE60).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: const Color(0xFF27AE60).withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: const Color(0xFF27AE60),
                  size: 20,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Your conversation will be personalized for ${_getProblemCategoryDisplayName(selectedCategory)}',
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
    );
  }

  Widget _buildInteractionCard({
    required BuildContext context,
    required String title,
    required String subtitle,
    required IconData icon,
    required IconData activeIcon,
    required Color color,
    required VoidCallback onTap,
    required UserModel user,
    required WidgetRef ref,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 20,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          children: [
            Icon(
              icon,
              size: 32,
              color: color,
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: const Color(0xFF2C3E50),
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: const Color(0xFF7F8C8D),
                  ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  void _navigateToChat(BuildContext context, ProblemCategory? category) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const ChatScreen(),
        settings: RouteSettings(
          arguments: {'problemCategory': category},
        ),
      ),
    );
  }

  void _navigateToCall(BuildContext context, ProblemCategory? category) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const TalkScreen(),
        settings: RouteSettings(
          arguments: {'problemCategory': category},
        ),
      ),
    );
  }

  String _getProblemCategoryDisplayName(ProblemCategory category) {
    switch (category) {
      case ProblemCategory.stress_anxiety:
        return 'Stress & Anxiety';
      case ProblemCategory.depression_sadness:
        return 'Depression & Sadness';
      case ProblemCategory.relationship_issues:
        return 'Relationships';
      case ProblemCategory.academic_pressure:
        return 'Academic Pressure';
      case ProblemCategory.career_confusion:
        return 'Career Confusion';
      case ProblemCategory.family_problems:
        return 'Family Issues';
      case ProblemCategory.social_anxiety:
        return 'Social Anxiety';
      case ProblemCategory.self_esteem:
        return 'Self-Esteem';
      case ProblemCategory.sleep_issues:
        return 'Sleep Issues';
      case ProblemCategory.anger_management:
        return 'Anger Management';
      case ProblemCategory.addiction_habits:
        return 'Addiction & Habits';
      case ProblemCategory.grief_loss:
        return 'Grief & Loss';
      case ProblemCategory.identity_crisis:
        return 'Identity Crisis';
      case ProblemCategory.loneliness:
        return 'Loneliness';
      case ProblemCategory.general_wellness:
        return 'General Wellness';
    }
  }

  Widget _buildStatCard(
    BuildContext context,
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 4),
          Text(
            value,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            title,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
