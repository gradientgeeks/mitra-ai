import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_model.dart';
import '../providers/auth_provider.dart';
import 'main_navigation_screen.dart';

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  bool _isCompleting = false;

  // Form data
  AgeGroup? _selectedAgeGroup;
  String _mitraName = 'Mitra';
  Gender? _selectedGender;
  VoiceType? _selectedVoice;

  final TextEditingController _nameController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _nameController.text = _mitraName;
  }

  @override
  void dispose() {
    _pageController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  void _nextPage() {
    if (_currentPage < 3) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    } else {
      _completeOnboarding();
    }
  }

  void _previousPage() {
    if (_currentPage > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  Future<void> _completeOnboarding() async {
    if (_selectedAgeGroup == null || 
        _selectedGender == null || 
        _selectedVoice == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please complete all steps'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isCompleting = true;
    });

    try {
      final onboardingRequest = OnboardingRequest(
        name: 'User', // Default name since we don't collect it in this flow
        age: _getAgeFromGroup(_selectedAgeGroup!),
        gender: _selectedGender!.name,
        interests: [], // Empty for now, can be added later
        mitraName: _nameController.text.trim().isEmpty ? 'Mitra' : _nameController.text.trim(),
        preferredVoice: _selectedVoice!,
      );

      await ref.read(authControllerProvider.notifier).completeOnboarding(onboardingRequest);
      
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (context) => const MainNavigationScreen(),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error completing onboarding: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isCompleting = false;
        });
      }
    }
  }

  bool _canProceed() {
    switch (_currentPage) {
      case 0:
        return _selectedAgeGroup != null;
      case 1:
        return _nameController.text.trim().isNotEmpty;
      case 2:
        return _selectedGender != null;
      case 3:
        return _selectedVoice != null;
      default:
        return false;
    }
  }

  @override
  Widget build(BuildContext context) {
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
              'Welcome to Mitra',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: const Color(0xFF2C3E50),
              ),
            ),
          ],
        ),
        automaticallyImplyLeading: false,
      ),
      body: Column(
        children: [
          // Progress indicator
          Container(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: List.generate(4, (index) {
                return Expanded(
                  child: Container(
                    margin: EdgeInsets.only(right: index < 3 ? 8 : 0),
                    height: 4,
                    decoration: BoxDecoration(
                      color: index <= _currentPage
                          ? const Color(0xFF3498DB)
                          : const Color(0xFFE0E0E0),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                );
              }),
            ),
          ),
          
          // Page content
          Expanded(
            child: PageView(
              controller: _pageController,
              onPageChanged: (page) {
                setState(() {
                  _currentPage = page;
                });
              },
              children: [
                _buildAgeGroupPage(),
                _buildNamePage(),
                _buildGenderPage(),
                _buildVoicePage(),
              ],
            ),
          ),
          
          // Navigation buttons
          Container(
            padding: const EdgeInsets.all(24),
            child: Row(
              children: [
                if (_currentPage > 0)
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _previousPage,
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        side: const BorderSide(color: Color(0xFF3498DB)),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text(
                        'Back',
                        style: TextStyle(
                          color: Color(0xFF3498DB),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                if (_currentPage > 0) const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: (_canProceed() && !_isCompleting) ? _nextPage : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF3498DB),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 2,
                    ),
                    child: _isCompleting
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : Text(
                            _currentPage == 3 ? 'Complete Setup' : 'Continue',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
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

  Widget _buildAgeGroupPage() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 20),
          Icon(
            Icons.cake_outlined,
            size: 64,
            color: const Color(0xFF3498DB).withValues(alpha: 0.8),
          ),
          const SizedBox(height: 24),
          Text(
            'What\'s your age group?',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: const Color(0xFF2C3E50),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          Text(
            'This helps Mitra provide age-appropriate responses and guidance',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: const Color(0xFF7F8C8D),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),
          Expanded(
            child: ListView(
              children: AgeGroup.values.map((ageGroup) {
                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: InkWell(
                    onTap: () {
                      setState(() {
                        _selectedAgeGroup = ageGroup;
                      });
                    },
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: _selectedAgeGroup == ageGroup
                            ? const Color(0xFF3498DB).withValues(alpha: 0.1)
                            : Colors.white,
                        border: Border.all(
                          color: _selectedAgeGroup == ageGroup
                              ? const Color(0xFF3498DB)
                              : const Color(0xFFE0E0E0),
                          width: 2,
                        ),
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.05),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              ageGroup.displayName,
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                color: _selectedAgeGroup == ageGroup
                                    ? const Color(0xFF3498DB)
                                    : const Color(0xFF2C3E50),
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          if (_selectedAgeGroup == ageGroup)
                            const Icon(
                              Icons.check_circle,
                              color: Color(0xFF3498DB),
                              size: 24,
                            ),
                        ],
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNamePage() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 20),
          Icon(
            Icons.psychology_outlined,
            size: 64,
            color: const Color(0xFF3498DB).withOpacity(0.8),
          ),
          const SizedBox(height: 24),
          Text(
            'Customize your AI companion',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: const Color(0xFF2C3E50),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          Text(
            'Give your AI companion a personal name. This creates a more intimate and comfortable conversation experience.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: const Color(0xFF7F8C8D),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),
          Container(
            padding: const EdgeInsets.all(24),
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
                Text(
                  'AI Companion Name',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF2C3E50),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _nameController,
                  decoration: InputDecoration(
                    hintText: 'Enter a name (e.g., Mitra, Alex, Sam)',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: Color(0xFFE0E0E0)),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: Color(0xFFE0E0E0)),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: Color(0xFF3498DB), width: 2),
                    ),
                    contentPadding: const EdgeInsets.all(16),
                  ),
                  style: Theme.of(context).textTheme.bodyLarge,
                  onChanged: (value) {
                    setState(() {
                      _mitraName = value;
                    });
                  },
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF3498DB).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.lightbulb_outline,
                        color: Color(0xFF3498DB),
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Choose a name that feels comfortable and personal to you',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: const Color(0xFF3498DB),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Spacer(),
        ],
      ),
    );
  }

  Widget _buildGenderPage() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 20),
          Icon(
            Icons.person_outline,
            size: 64,
            color: const Color(0xFF3498DB).withOpacity(0.8),
          ),
          const SizedBox(height: 24),
          Text(
            'Choose your companion\'s persona',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: const Color(0xFF2C3E50),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          Text(
            'This affects how ${_nameController.text.isNotEmpty ? _nameController.text : 'Mitra'} communicates and responds to you',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: const Color(0xFF7F8C8D),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),
          Expanded(
            child: ListView(
              children: Gender.values.map((gender) {
                IconData icon;
                switch (gender) {
                  case Gender.male:
                    icon = Icons.man;
                    break;
                  case Gender.female:
                    icon = Icons.woman;
                    break;
                  case Gender.nonBinary:
                    icon = Icons.person;
                    break;
                }
                
                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: InkWell(
                    onTap: () {
                      setState(() {
                        _selectedGender = gender;
                      });
                    },
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: _selectedGender == gender
                            ? const Color(0xFF3498DB).withOpacity(0.1)
                            : Colors.white,
                        border: Border.all(
                          color: _selectedGender == gender
                              ? const Color(0xFF3498DB)
                              : const Color(0xFFE0E0E0),
                          width: 2,
                        ),
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.05),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          Icon(
                            icon,
                            color: _selectedGender == gender
                                ? const Color(0xFF3498DB)
                                : const Color(0xFF7F8C8D),
                            size: 28,
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Text(
                              gender.displayName,
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                color: _selectedGender == gender
                                    ? const Color(0xFF3498DB)
                                    : const Color(0xFF2C3E50),
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          if (_selectedGender == gender)
                            const Icon(
                              Icons.check_circle,
                              color: Color(0xFF3498DB),
                              size: 24,
                            ),
                        ],
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVoicePage() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 20),
          Icon(
            Icons.record_voice_over,
            size: 64,
            color: const Color(0xFF3498DB).withOpacity(0.8),
          ),
          const SizedBox(height: 24),
          Text(
            'Select ${_nameController.text.isNotEmpty ? _nameController.text : 'Mitra'}\'s voice',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: const Color(0xFF2C3E50),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          Text(
            'Choose a voice that feels comfortable for your conversations',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: const Color(0xFF7F8C8D),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),
          Expanded(
            child: ListView(
              children: VoiceType.values.map((voice) {
                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: InkWell(
                    onTap: () {
                      setState(() {
                        _selectedVoice = voice;
                      });
                    },
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: _selectedVoice == voice
                            ? const Color(0xFF3498DB).withOpacity(0.1)
                            : Colors.white,
                        border: Border.all(
                          color: _selectedVoice == voice
                              ? const Color(0xFF3498DB)
                              : const Color(0xFFE0E0E0),
                          width: 2,
                        ),
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.05),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: (_selectedVoice == voice
                                  ? const Color(0xFF3498DB)
                                  : const Color(0xFF7F8C8D)
                              ).withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Icon(
                              Icons.volume_up,
                              color: _selectedVoice == voice
                                  ? const Color(0xFF3498DB)
                                  : const Color(0xFF7F8C8D),
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  voice.displayName,
                                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    color: _selectedVoice == voice
                                        ? const Color(0xFF3498DB)
                                        : const Color(0xFF2C3E50),
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  _getVoiceDescription(voice),
                                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: const Color(0xFF7F8C8D),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            onPressed: () {
                              // TODO: Play voice sample
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Playing ${voice.displayName} sample...'),
                                  duration: const Duration(seconds: 1),
                                ),
                              );
                            },
                            icon: const Icon(
                              Icons.play_circle_outline,
                              color: Color(0xFF3498DB),
                            ),
                          ),
                          if (_selectedVoice == voice)
                            const Icon(
                              Icons.check_circle,
                              color: Color(0xFF3498DB),
                              size: 24,
                            ),
                        ],
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  int _getAgeFromGroup(AgeGroup ageGroup) {
    switch (ageGroup) {
      case AgeGroup.young:
        return 16; // Representative age for teens
      case AgeGroup.adult:
        return 30; // Representative age for adults
      case AgeGroup.senior:
        return 70; // Representative age for seniors
    }
  }

  String _getVoiceDescription(VoiceType voice) {
    switch (voice) {
      case VoiceType.femaleYoung:
        return 'Warm and empathetic voice';
      case VoiceType.femaleMature:
        return 'Gentle and soothing voice';
      case VoiceType.maleYoung:
        return 'Strong and supportive voice';
      case VoiceType.maleMature:
        return 'Deep and reassuring voice';
    }
  }
}
