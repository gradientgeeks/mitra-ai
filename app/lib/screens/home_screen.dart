import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';
import '../models/user_model.dart';
import '../widgets/profile_avatar.dart';
import 'login_screen.dart';
import 'chat_screen.dart';
import 'talk_screen.dart';

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
    final selectedCategory = ref.watch(currentProblemCategoryProvider);

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
                child: Row(
                  children: [
                    // Mitra Avatar
                    MitraProfileAvatar(
                      imageUrl: user?.preferences.mitraProfileImageUrl,
                      mitraName: user?.preferences.mitraName ?? 'Mitra',
                      size: 60,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Hi there! I\'m ${user?.preferences.mitraName ?? 'Mitra'}',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Your AI companion for mental wellness. How are you feeling today?',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: Colors.white.withOpacity(0.9),
                                ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // Problem Category Selection
              _buildProblemCategorySection(context, ref, selectedCategory),

              const SizedBox(height: 30),

              // Chat and Call Cards - Show only when category is selected
              if (selectedCategory != null && user != null)
                _buildMitraInteractionCards(context, ref, user, selectedCategory),

              // Instruction when no category selected
              if (selectedCategory == null)
                _buildSelectionPrompt(context),

              const SizedBox(height: 30),

              // Account Linking Reminder
              if (user?.isAnonymous == true)
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
            'Select what\'s on your mind to get personalized support from ${ref.watch(authControllerProvider).value?.backendUser?.preferences.mitraName ?? 'Mitra'}',
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
                  ref.read(currentProblemCategoryProvider.notifier).state =
                      isSelected ? null : category;
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? const Color(0xFF3498DB)
                        : const Color(0xFFF8F9FA),
                    borderRadius: BorderRadius.circular(25),
                    border: Border.all(
                      color: isSelected
                          ? const Color(0xFF3498DB)
                          : const Color(0xFFE0E0E0),
                      width: 1,
                    ),
                    boxShadow: isSelected ? [
                      BoxShadow(
                        color: const Color(0xFF3498DB).withOpacity(0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ] : [],
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (isSelected)
                        Container(
                          width: 16,
                          height: 16,
                          margin: const EdgeInsets.only(right: 8),
                          decoration: const BoxDecoration(
                            color: Colors.white,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.check,
                            size: 12,
                            color: Color(0xFF3498DB),
                          ),
                        ),
                      Text(
                        getProblemCategoryDisplayName(category),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: isSelected ? Colors.white : const Color(0xFF7F8C8D),
                              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                            ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
          if (selectedCategory != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF27AE60).withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: const Color(0xFF27AE60).withOpacity(0.3),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.lightbulb_outline,
                    size: 20,
                    color: const Color(0xFF27AE60),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      getProblemCategoryDescription(selectedCategory),
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
        ],
      ),
    );
  }

  Widget _buildSelectionPrompt(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFFE0E0E0),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Icon(
            Icons.arrow_upward,
            size: 32,
            color: const Color(0xFF7F8C8D),
          ),
          const SizedBox(height: 16),
          Text(
            'Please select how you\'re feeling',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: const Color(0xFF2C3E50),
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Choose from the options above to start your conversation with Mitra',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFF7F8C8D),
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildMitraInteractionCards(BuildContext context, WidgetRef ref, UserModel user, ProblemCategory selectedCategory) {
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
                color: const Color(0xFF3498DB),
                onTap: () => _navigateToChat(context, ref, selectedCategory),
                user: user,
                ref: ref,
              ),
            ),
            const SizedBox(width: 16),
            // Call Card
            Expanded(
              child: _buildInteractionCard(
                context: context,
                title: 'Talk to ${user.preferences.mitraName}',
                subtitle: 'Voice Conversation',
                icon: Icons.phone_outlined,
                color: const Color(0xFF27AE60),
                onTap: () => _navigateToCall(context, ref, selectedCategory),
                user: user,
                ref: ref,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF9B59B6).withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: const Color(0xFF9B59B6).withOpacity(0.3),
              width: 1,
            ),
          ),
          child: Row(
            children: [
              Icon(
                Icons.auto_awesome,
                color: const Color(0xFF9B59B6),
                size: 20,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Your conversation will be personalized for ${getProblemCategoryDisplayName(selectedCategory)}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: const Color(0xFF9B59B6),
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
              color: color.withOpacity(0.15),
              blurRadius: 20,
              offset: const Offset(0, 4),
            ),
          ],
          border: Border.all(
            color: color.withOpacity(0.2),
            width: 1,
          ),
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                size: 32,
                color: color,
              ),
            ),
            const SizedBox(height: 16),
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
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                'Start Now',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                    ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _navigateToChat(BuildContext context, WidgetRef ref, ProblemCategory category) {
    // Initialize chat session with selected problem category
    ref.read(chatControllerProvider.notifier).startChatSession(
      problemCategory: category,
    );

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const ChatScreen(),
      ),
    );
  }

  void _navigateToCall(BuildContext context, WidgetRef ref, ProblemCategory category) {
    // Initialize chat session for voice mode with selected problem category
    ref.read(chatControllerProvider.notifier).startChatSession(
      problemCategory: category,
    );

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const TalkScreen(),
      ),
    );
  }
}
