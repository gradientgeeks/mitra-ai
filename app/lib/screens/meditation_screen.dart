import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:app/services/api_service.dart';
import '../models/chat_models.dart' as chat_models;

// Provider to manage meditation state
final meditationStateProvider = StateProvider<MeditationState>((ref) => MeditationState.idle);
final selectedMeditationProvider = StateProvider<MeditationTypeModel?>((ref) => null);
final meditationTimerProvider = StateProvider<int>((ref) => 0);
final generatedMeditationProvider = StateProvider<chat_models.MeditationResponse?>((ref) => null);

enum MeditationState {
  idle,
  playing,
  paused,
  completed,
}

class MeditationTypeModel {
  final String id;
  final String title;
  final String description;
  final int duration; // in minutes
  final IconData icon;
  final Color color;
  final String category;

  const MeditationTypeModel({
    required this.id,
    required this.title,
    required this.description,
    required this.duration,
    required this.icon,
    required this.color,
    required this.category,
  });
}

class MeditationScreen extends ConsumerStatefulWidget {
  const MeditationScreen({super.key});

  @override
  ConsumerState<MeditationScreen> createState() => _MeditationScreenState();
}

class _MeditationScreenState extends ConsumerState<MeditationScreen>
    with TickerProviderStateMixin {
  late AnimationController _breathingController;
  late Animation<double> _breathingAnimation;

  final List<MeditationTypeModel> _meditationTypes = [
    MeditationTypeModel(
      id: 'breathing_basic',
      title: 'Basic Breathing',
      description: 'Simple 4-7-8 breathing technique for relaxation',
      duration: 5,
      icon: Icons.air,
      color: const Color(0xFF3498DB),
      category: 'Breathing',
    ),
    MeditationTypeModel(
      id: 'breathing_deep',
      title: 'Deep Breathing',
      description: 'Extended breathing exercises for deep relaxation',
      duration: 10,
      icon: Icons.spa,
      color: const Color(0xFF27AE60),
      category: 'Breathing',
    ),
    MeditationTypeModel(
      id: 'body_scanning',
      title: 'Body Scan',
      description: 'Progressive relaxation through body awareness',
      duration: 15,
      icon: Icons.self_improvement,
      color: const Color(0xFF9B59B6),
      category: 'Mindfulness',
    ),
    MeditationTypeModel(
      id: 'mindfulness',
      title: 'Mindfulness',
      description: 'Present moment awareness and acceptance',
      duration: 12,
      icon: Icons.psychology,
      color: const Color(0xFFE67E22),
      category: 'Mindfulness',
    ),
    MeditationTypeModel(
      id: 'stress_relief',
      title: 'Stress Relief',
      description: 'Release tension and calm your mind',
      duration: 8,
      icon: Icons.healing,
      color: const Color(0xFFE74C3C),
      category: 'Wellness',
    ),
    MeditationTypeModel(
      id: 'sleep_prep',
      title: 'Sleep Preparation',
      description: 'Gentle meditation to prepare for restful sleep',
      duration: 20,
      icon: Icons.bedtime,
      color: const Color(0xFF34495E),
      category: 'Sleep',
    ),
    MeditationTypeModel(
      id: 'anxiety_relief',
      title: 'Anxiety Relief',
      description: 'Calming techniques to ease anxious thoughts',
      duration: 12,
      icon: Icons.favorite,
      color: const Color(0xFFFF6B9D),
      category: 'Wellness',
    ),
    MeditationTypeModel(
      id: 'focus_concentration',
      title: 'Focus & Concentration',
      description: 'Improve mental clarity and concentration',
      duration: 10,
      icon: Icons.center_focus_strong,
      color: const Color(0xFF1ABC9C),
      category: 'Performance',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _breathingController = AnimationController(
      duration: const Duration(seconds: 8),
      vsync: this,
    );
    _breathingAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _breathingController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _breathingController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final selectedMeditation = ref.watch(selectedMeditationProvider);
    final meditationState = ref.watch(meditationStateProvider);

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
                  'Guided Meditation',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: const Color(0xFF2C3E50),
                      ),
                ),
                Text(
                  'Find your inner peace',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: const Color(0xFF7F8C8D),
                      ),
                ),
              ],
            ),
          ],
        ),
        leading: selectedMeditation != null
            ? IconButton(
                onPressed: () {
                  ref.read(selectedMeditationProvider.notifier).state = null;
                  ref.read(meditationStateProvider.notifier).state = MeditationState.idle;
                  _breathingController.reset();
                },
                icon: const Icon(Icons.arrow_back),
              )
            : null,
      ),
      body: selectedMeditation == null
          ? _buildMeditationLibrary()
          : _buildMeditationPlayer(selectedMeditation, meditationState),
    );
  }

  Widget _buildMeditationLibrary() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Welcome card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  const Color(0xFF9B59B6),
                  const Color(0xFF8E44AD),
                ],
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF9B59B6).withOpacity(0.3),
                  blurRadius: 12,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.self_improvement,
                      size: 40,
                      color: Colors.white,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Guided Meditations',
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                          Text(
                            'AI-powered sessions for every need',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: Colors.white.withOpacity(0.9),
                                ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 30),

          // Quick start section
          Text(
            'Quick Start',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF2C3E50),
                ),
          ),

          const SizedBox(height: 16),

          Row(
            children: [
              Expanded(
                child: _buildQuickStartCard(
                  'Breathing Exercise',
                  '5 min session',
                  Icons.air,
                  const Color(0xFF3498DB),
                  () => _startMeditation(_meditationTypes[0]),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickStartCard(
                  'Stress Relief',
                  '8 min session',
                  Icons.healing,
                  const Color(0xFFE74C3C),
                  () => _startMeditation(_meditationTypes[4]),
                ),
              ),
            ],
          ),

          const SizedBox(height: 30),

          // All meditations
          Text(
            'All Meditations',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF2C3E50),
                ),
          ),

          const SizedBox(height: 16),

          // Group meditations by category
          ..._buildMeditationsByCategory(),
        ],
      ),
    );
  }

  Widget _buildQuickStartCard(
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.2)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                icon,
                color: color,
                size: 24,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF2C3E50),
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: const Color(0xFF7F8C8D),
                  ),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildMeditationsByCategory() {
    final categories = <String, List<MeditationTypeModel>>{};

    for (final meditation in _meditationTypes) {
      categories.putIfAbsent(meditation.category, () => []).add(meditation);
    }

    return categories.entries.map((entry) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 12, top: 20),
            child: Text(
              entry.key,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF2C3E50),
                  ),
            ),
          ),
          ...entry.value.map((meditation) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildMeditationCard(meditation),
              )),
        ],
      );
    }).toList();
  }

  Widget _buildMeditationCard(MeditationTypeModel meditation) {
    return GestureDetector(
      onTap: () => _startMeditation(meditation),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: meditation.color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                meditation.icon,
                color: meditation.color,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    meditation.title,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF2C3E50),
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    meditation.description,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: const Color(0xFF7F8C8D),
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${meditation.duration} minutes',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: meditation.color,
                          fontWeight: FontWeight.w500,
                        ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.play_circle_outline,
              color: meditation.color,
              size: 28,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMeditationPlayer(MeditationTypeModel meditation, MeditationState state) {
    final generatedMeditation = ref.watch(generatedMeditationProvider);

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        children: [
          // Meditation info card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: meditation.color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: meditation.color.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Column(
              children: [
                Icon(
                  meditation.icon,
                  size: 48,
                  color: meditation.color,
                ),
                const SizedBox(height: 12),
                Text(
                  meditation.title,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: const Color(0xFF2C3E50),
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  meditation.description,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: const Color(0xFF7F8C8D),
                      ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),

          const SizedBox(height: 40),

          // Breathing visualization (for breathing exercises)
          if (meditation.id.contains('breathing'))
            Expanded(
              child: Center(
                child: AnimatedBuilder(
                  animation: _breathingAnimation,
                  builder: (context, child) {
                    return Transform.scale(
                      scale: _breathingAnimation.value,
                      child: Container(
                        width: 200,
                        height: 200,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: RadialGradient(
                            colors: [
                              meditation.color.withOpacity(0.3),
                              meditation.color.withOpacity(0.1),
                              meditation.color.withOpacity(0.05),
                            ],
                          ),
                        ),
                        child: Center(
                          child: Container(
                            width: 120,
                            height: 120,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: meditation.color.withOpacity(0.2),
                            ),
                            child: Icon(
                              Icons.air,
                              size: 60,
                              color: meditation.color,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            )
          else
            Expanded(
              child: Center(
                child: generatedMeditation == null
                    ? const CircularProgressIndicator()
                    : SingleChildScrollView(
                        child: Text(generatedMeditation.script),
                      ),
              ),
            ),

          // Control buttons
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (state == MeditationState.playing) ...[
                IconButton(
                  onPressed: _pauseMeditation,
                  icon: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: meditation.color,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.pause,
                      color: Colors.white,
                      size: 32,
                    ),
                  ),
                ),
              ] else ...[
                IconButton(
                  onPressed: _playMeditation,
                  icon: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: meditation.color,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.play_arrow,
                      color: Colors.white,
                      size: 32,
                    ),
                  ),
                ),
              ],
              const SizedBox(width: 20),
              IconButton(
                onPressed: _stopMeditation,
                icon: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF7F8C8D),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.stop,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),

          // Duration display
          Text(
            '${meditation.duration} minutes',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: const Color(0xFF7F8C8D),
                  fontWeight: FontWeight.w500,
                ),
          ),

          const SizedBox(height: 20),

          // Privacy reminder
          Container(
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
                  Icons.shield_outlined,
                  color: const Color(0xFF27AE60),
                  size: 20,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Your meditation sessions are completely private',
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
    );
  }

  void _startMeditation(MeditationTypeModel meditation) async {
    ref.read(selectedMeditationProvider.notifier).state = meditation;
    ref.read(meditationStateProvider.notifier).state = MeditationState.idle;

    try {
      final apiService = ApiService();
      final generatedMeditation = await apiService.generateMeditation(
        type: meditation.id,
        duration: meditation.duration,
        focusArea: meditation.title,
      );
      ref.read(generatedMeditationProvider.notifier).state = generatedMeditation;
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error generating meditation: $e'),
        ),
      );
    }
  }

  void _playMeditation() {
    ref.read(meditationStateProvider.notifier).state = MeditationState.playing;
    final selectedMeditation = ref.read(selectedMeditationProvider);

    if (selectedMeditation?.id.contains('breathing') == true) {
      _breathingController.repeat();
    }

    // Here you would integrate with actual meditation audio/guidance
    _simulateMeditationProgress();
  }

  void _pauseMeditation() {
    ref.read(meditationStateProvider.notifier).state = MeditationState.paused;
    _breathingController.stop();
  }

  void _stopMeditation() {
    ref.read(meditationStateProvider.notifier).state = MeditationState.idle;
    ref.read(selectedMeditationProvider.notifier).state = null;
    _breathingController.reset();
  }

  void _simulateMeditationProgress() {
    // This would be replaced with actual meditation logic
    final selectedMeditation = ref.read(selectedMeditationProvider);
    if (selectedMeditation != null) {
      Future.delayed(Duration(minutes: selectedMeditation.duration), () {
        if (mounted) {
          ref.read(meditationStateProvider.notifier).state = MeditationState.completed;
          _showCompletionDialog();
        }
      });
    }
  }

  void _showCompletionDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Meditation Complete'),
        content: const Text('Great job! You\'ve completed your meditation session. How do you feel?'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _stopMeditation();
            },
            child: const Text('Finish'),
          ),
        ],
      ),
    );
  }
}
