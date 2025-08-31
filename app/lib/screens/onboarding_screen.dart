import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
<<<<<<< HEAD
import '../models/user_model.dart';
import '../providers/auth_provider.dart';
=======
import '../providers/auth_provider.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
>>>>>>> feat/voice
import 'main_navigation_screen.dart';

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

<<<<<<< HEAD
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
=======
class _OnboardingScreenState extends ConsumerState<OnboardingScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  final PageController _pageController = PageController();
  int _currentPage = 0;
  bool _isLoading = false;

  // Form data
  AgeGroup? _selectedAgeGroup;
  int? _birthYear;
  String _mitraName = 'Mitra';
  Gender _selectedGender = Gender.female;
  VoiceOption _selectedVoice = VoiceOption.puck;
  String _selectedLanguage = 'en';
  bool _notificationEnabled = true;
  bool _meditationReminders = false;
  bool _journalReminders = false;

  // Controllers
  final TextEditingController _mitraNameController = TextEditingController(text: 'Mitra');
  final TextEditingController _birthYearController = TextEditingController();

  // Options data
  OnboardingOptions? _options;
>>>>>>> feat/voice

  @override
  void initState() {
    super.initState();
<<<<<<< HEAD
    _nameController.text = _mitraName;
=======
    _initializeAnimations();
    _loadOnboardingOptions();
  }

  void _initializeAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOutCubic,
    ));

    _animationController.forward();
  }

  Future<void> _loadOnboardingOptions() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final options = await apiService.getOnboardingOptions();
      setState(() {
        _options = options;
      });
    } catch (e) {
      // Handle error - show default options
      print('Error loading onboarding options: $e');
    }
>>>>>>> feat/voice
  }

  @override
  void dispose() {
<<<<<<< HEAD
    _pageController.dispose();
    _nameController.dispose();
=======
    _animationController.dispose();
    _pageController.dispose();
    _mitraNameController.dispose();
    _birthYearController.dispose();
>>>>>>> feat/voice
    super.dispose();
  }

  void _nextPage() {
<<<<<<< HEAD
    if (_currentPage < 3) {
=======
    if (_currentPage < 4) {
>>>>>>> feat/voice
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

<<<<<<< HEAD
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
=======
  bool _canProceed() {
    switch (_currentPage) {
      case 0:
        return _selectedAgeGroup != null;
      case 1:
        return _mitraName.isNotEmpty;
      case 2:
        return true; // Gender selection is optional with default
      case 3:
        return true; // Voice selection is optional with default
      case 4:
        return true; // Preferences are optional
      default:
        return false;
    }
  }

  Future<void> _completeOnboarding() async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
    });

    try {
      await ref.read(authControllerProvider.notifier).completeOnboarding(
        ageGroup: _selectedAgeGroup!,
        birthYear: _birthYear,
        mitraName: _mitraName,
        mitraGender: _selectedGender,
        preferredVoice: _selectedVoice,
        language: _selectedLanguage,
        notificationEnabled: _notificationEnabled,
        meditationReminders: _meditationReminders,
        journalReminders: _journalReminders,
      );

      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const MainNavigationScreen()),
>>>>>>> feat/voice
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
<<<<<<< HEAD
            content: Text('Error completing onboarding: $e'),
=======
            content: Text('Failed to complete onboarding: $e'),
>>>>>>> feat/voice
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
<<<<<<< HEAD
          _isCompleting = false;
=======
          _isLoading = false;
>>>>>>> feat/voice
        });
      }
    }
  }

<<<<<<< HEAD
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

=======
>>>>>>> feat/voice
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
<<<<<<< HEAD
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
=======
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.all(20.0),
              child: FadeTransition(
                opacity: _fadeAnimation,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    if (_currentPage > 0)
                      IconButton(
                        onPressed: _previousPage,
                        icon: const Icon(Icons.arrow_back, color: Color(0xFF7F8C8D)),
                      )
                    else
                      const SizedBox(width: 48),
                    Text(
                      'Let\'s personalize Mitra for you',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: const Color(0xFF2C3E50),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      '${_currentPage + 1}/5',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: const Color(0xFF7F8C8D),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Progress indicator
            FadeTransition(
              opacity: _fadeAnimation,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0),
                child: LinearProgressIndicator(
                  value: (_currentPage + 1) / 5,
                  backgroundColor: const Color(0xFFE8E8E8),
                  valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF3498DB)),
                ),
              ),
            ),

            // Page content
            Expanded(
              child: PageView(
                controller: _pageController,
                onPageChanged: (index) {
                  setState(() {
                    _currentPage = index;
                  });
                  _animationController.reset();
                  _animationController.forward();
                },
                children: [
                  _buildAgeGroupPage(),
                  _buildPersonalizationPage(),
                  _buildGenderPage(),
                  _buildVoicePage(),
                  _buildPreferencesPage(),
                ],
              ),
            ),

            // Continue button
            FadeTransition(
              opacity: _fadeAnimation,
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _canProceed() && !_isLoading ? _nextPage : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF3498DB),
                      foregroundColor: Colors.white,
>>>>>>> feat/voice
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 2,
                    ),
<<<<<<< HEAD
                    child: _isCompleting
=======
                    child: _isLoading
>>>>>>> feat/voice
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
<<<<<<< HEAD
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : Text(
                            _currentPage == 3 ? 'Complete Setup' : 'Continue',
                            style: const TextStyle(
                              color: Colors.white,
=======
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : Text(
                            _currentPage == 4 ? 'Complete Setup' : 'Continue',
                            style: const TextStyle(
                              fontSize: 16,
>>>>>>> feat/voice
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                  ),
                ),
<<<<<<< HEAD
              ],
            ),
          ),
        ],
=======
              ),
            ),
          ],
        ),
>>>>>>> feat/voice
      ),
    );
  }

  Widget _buildAgeGroupPage() {
<<<<<<< HEAD
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
=======
    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 40),
              Text(
                'What\'s your age group?',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: const Color(0xFF2C3E50),
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'This helps us provide age-appropriate content and support.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: const Color(0xFF7F8C8D),
                ),
              ),
              const SizedBox(height: 40),
              Expanded(
                child: ListView(
                  children: [
                    _buildAgeGroupOption(AgeGroup.teen, '13-17 years', 'Teen'),
                    _buildAgeGroupOption(AgeGroup.young_adult, '18-24 years', 'Young Adult'),
                    _buildAgeGroupOption(AgeGroup.adult, '25-34 years', 'Adult'),
                    _buildAgeGroupOption(AgeGroup.mature_adult, '35+ years', 'Mature Adult'),
                  ],
                ),
              ),
              if (_selectedAgeGroup != null) ...[
                const SizedBox(height: 20),
                TextField(
                  controller: _birthYearController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Birth Year (Optional)',
                    hintText: 'e.g. 1995',
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (value) {
                    _birthYear = int.tryParse(value);
                  },
                ),
              ],
            ],
          ),
        ),
>>>>>>> feat/voice
      ),
    );
  }

<<<<<<< HEAD
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
=======
  Widget _buildAgeGroupOption(AgeGroup ageGroup, String subtitle, String title) {
    final isSelected = _selectedAgeGroup == ageGroup;
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
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF3498DB).withOpacity(0.1) : Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? const Color(0xFF3498DB) : const Color(0xFFE8E8E8),
              width: 2,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 20,
                height: 20,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: isSelected ? const Color(0xFF3498DB) : const Color(0xFFBDC3C7),
                    width: 2,
                  ),
                  color: isSelected ? const Color(0xFF3498DB) : Colors.transparent,
                ),
                child: isSelected
                    ? const Icon(
                        Icons.check,
                        size: 12,
                        color: Colors.white,
                      )
                    : null,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: const Color(0xFF2C3E50),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: const Color(0xFF7F8C8D),
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

  Widget _buildPersonalizationPage() {
    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 40),
              Text(
                'What should we call your AI companion?',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: const Color(0xFF2C3E50),
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Choose a name that feels comfortable and personal to you.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: const Color(0xFF7F8C8D),
                ),
              ),
              const SizedBox(height: 40),
              TextField(
                controller: _mitraNameController,
                decoration: const InputDecoration(
                  labelText: 'AI Companion Name',
                  hintText: 'e.g. Mitra, Sakhi, Friend',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person),
                ),
                onChanged: (value) {
                  setState(() {
                    _mitraName = value;
                  });
                },
              ),
              const SizedBox(height: 30),
              if (_options?.sampleMitraNames != null) ...[
                Text(
                  'Popular choices:',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: const Color(0xFF2C3E50),
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _options!.sampleMitraNames.map((name) {
                    return InkWell(
                      onTap: () {
                        setState(() {
                          _mitraName = name;
                          _mitraNameController.text = name;
                        });
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        decoration: BoxDecoration(
                          color: _mitraName == name 
                              ? const Color(0xFF3498DB).withOpacity(0.1)
                              : Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: _mitraName == name 
                                ? const Color(0xFF3498DB)
                                : const Color(0xFFE8E8E8),
                          ),
                        ),
                        child: Text(
                          name,
                          style: TextStyle(
                            color: _mitraName == name 
                                ? const Color(0xFF3498DB)
                                : const Color(0xFF7F8C8D),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            ],
          ),
        ),
>>>>>>> feat/voice
      ),
    );
  }

  Widget _buildGenderPage() {
<<<<<<< HEAD
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
=======
    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 40),
              Text(
                'How would you like $_mitraName to be?',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: const Color(0xFF2C3E50),
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'This affects the personality and communication style.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: const Color(0xFF7F8C8D),
                ),
              ),
              const SizedBox(height: 40),
              Expanded(
                child: ListView(
                  children: [
                    _buildGenderOption(Gender.female, 'Feminine', 'Nurturing and empathetic communication'),
                    _buildGenderOption(Gender.male, 'Masculine', 'Direct and supportive communication'),
                    _buildGenderOption(Gender.non_binary, 'Non-binary', 'Balanced and inclusive communication'),
                    _buildGenderOption(Gender.prefer_not_to_say, 'Neutral', 'Adaptive communication style'),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGenderOption(Gender gender, String title, String description) {
    final isSelected = _selectedGender == gender;
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
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF3498DB).withOpacity(0.1) : Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? const Color(0xFF3498DB) : const Color(0xFFE8E8E8),
              width: 2,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 20,
                height: 20,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: isSelected ? const Color(0xFF3498DB) : const Color(0xFFBDC3C7),
                    width: 2,
                  ),
                  color: isSelected ? const Color(0xFF3498DB) : Colors.transparent,
                ),
                child: isSelected
                    ? const Icon(
                        Icons.check,
                        size: 12,
                        color: Colors.white,
                      )
                    : null,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: const Color(0xFF2C3E50),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      description,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: const Color(0xFF7F8C8D),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
>>>>>>> feat/voice
      ),
    );
  }

  Widget _buildVoicePage() {
<<<<<<< HEAD
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
=======
    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 40),
              Text(
                'Choose $_mitraName\'s voice',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: const Color(0xFF2C3E50),
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Select the voice that feels most comfortable for conversations.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: const Color(0xFF7F8C8D),
                ),
              ),
              const SizedBox(height: 40),
              Expanded(
                child: ListView(
                  children: VoiceOption.values.map((voice) {
                    return _buildVoiceOption(voice);
                  }).toList(),
                ),
              ),
            ],
          ),
        ),
>>>>>>> feat/voice
      ),
    );
  }

<<<<<<< HEAD
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
=======
  Widget _buildVoiceOption(VoiceOption voice) {
    final isSelected = _selectedVoice == voice;
    final voiceName = voice.name.substring(0, 1).toUpperCase() + voice.name.substring(1);
    
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
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF3498DB).withOpacity(0.1) : Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? const Color(0xFF3498DB) : const Color(0xFFE8E8E8),
              width: 2,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 20,
                height: 20,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: isSelected ? const Color(0xFF3498DB) : const Color(0xFFBDC3C7),
                    width: 2,
                  ),
                  color: isSelected ? const Color(0xFF3498DB) : Colors.transparent,
                ),
                child: isSelected
                    ? const Icon(
                        Icons.check,
                        size: 12,
                        color: Colors.white,
                      )
                    : null,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      voiceName,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: const Color(0xFF2C3E50),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      'AI-generated voice option',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: const Color(0xFF7F8C8D),
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: () {
                  // TODO: Play voice sample
                },
                icon: const Icon(
                  Icons.play_circle_outline,
                  color: Color(0xFF3498DB),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPreferencesPage() {
    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 40),
              Text(
                'Final preferences',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: const Color(0xFF2C3E50),
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'You can change these anytime in settings.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: const Color(0xFF7F8C8D),
                ),
              ),
              const SizedBox(height: 40),
              Expanded(
                child: ListView(
                  children: [
                    _buildPreferenceSwitch(
                      'Enable Notifications',
                      'Get reminders and supportive messages',
                      _notificationEnabled,
                      (value) => setState(() => _notificationEnabled = value),
                    ),
                    _buildPreferenceSwitch(
                      'Meditation Reminders',
                      'Daily reminders to practice mindfulness',
                      _meditationReminders,
                      (value) => setState(() => _meditationReminders = value),
                    ),
                    _buildPreferenceSwitch(
                      'Journal Reminders',
                      'Gentle prompts to reflect and write',
                      _journalReminders,
                      (value) => setState(() => _journalReminders = value),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF27AE60).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: const Color(0xFF27AE60).withOpacity(0.3),
                  ),
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.privacy_tip,
                      color: Color(0xFF27AE60),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Your privacy is important. All conversations are confidential and secure.',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
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
      ),
    );
  }

  Widget _buildPreferenceSwitch(
    String title,
    String subtitle,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: const Color(0xFF2C3E50),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: const Color(0xFF7F8C8D),
                    ),
                  ),
                ],
              ),
            ),
            Switch(
              value: value,
              onChanged: onChanged,
              activeColor: const Color(0xFF3498DB),
            ),
          ],
        ),
      ),
    );
  }
}
>>>>>>> feat/voice
