import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/user_model.dart';

class MitraProfileAvatar extends StatelessWidget {
  final String? imageUrl;
  final String mitraName;
  final double size;
  final Gender? mitraGender;

  const MitraProfileAvatar({
    super.key,
    this.imageUrl,
    required this.mitraName,
    this.size = 40,
    this.mitraGender,
  });

  @override
  Widget build(BuildContext context) {
    // If no image URL is provided, show a fallback avatar
    if (imageUrl == null || imageUrl!.isEmpty) {
      return _buildFallbackAvatar();
    }

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipOval(
        child: CachedNetworkImage(
          imageUrl: imageUrl!,
          width: size,
          height: size,
          fit: BoxFit.cover,
          httpHeaders: const {
            // Add headers to help with CORS and caching
            'Access-Control-Allow-Origin': '*',
          },
          placeholder: (context, url) => _buildLoadingAvatar(),
          errorWidget: (context, url, error) {
            // Log the error for debugging
            debugPrint('Failed to load Mitra profile image: $error');
            debugPrint('Image URL: $url');

            // Show fallback avatar on error
            return _buildFallbackAvatar();
          },
          // Enable memory caching
          memCacheWidth: (size * MediaQuery.of(context).devicePixelRatio).round(),
          memCacheHeight: (size * MediaQuery.of(context).devicePixelRatio).round(),
          // Set cache duration
          cacheManager: null, // Use default cache manager
        ),
      ),
    );
  }

  Widget _buildLoadingAvatar() {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: _getMitraColor().withOpacity(0.1),
      ),
      child: Center(
        child: SizedBox(
          width: size * 0.4,
          height: size * 0.4,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(_getMitraColor()),
          ),
        ),
      ),
    );
  }

  Widget _buildFallbackAvatar() {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: _getMitraColor(),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Center(
        child: Text(
          mitraName.isNotEmpty ? mitraName[0].toUpperCase() : 'M',
          style: TextStyle(
            fontSize: size * 0.4,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ),
    );
  }

  Color _getMitraColor() {
    switch (mitraGender) {
      case Gender.female:
        return const Color(0xFFE91E63); // Pink
      case Gender.male:
        return const Color(0xFF2196F3); // Blue
      case Gender.non_binary:
        return const Color(0xFF9C27B0); // Purple
      case Gender.prefer_not_to_say:
        return const Color(0xFF607D8B); // Blue Grey
      case null:
        return const Color(0xFF3498DB); // Default blue
    }
  }
}

class CircularMitraAvatar extends StatelessWidget {
  final String? imageUrl;
  final String mitraName;
  final double size;
  final Gender? mitraGender;
  final VoidCallback? onTap;

  const CircularMitraAvatar({
    super.key,
    this.imageUrl,
    required this.mitraName,
    this.size = 60,
    this.mitraGender,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final avatar = MitraProfileAvatar(
      imageUrl: imageUrl,
      mitraName: mitraName,
      size: size,
      mitraGender: mitraGender,
    );

    if (onTap != null) {
      return GestureDetector(
        onTap: onTap,
        child: avatar,
      );
    }

    return avatar;
  }
}

// Alternative avatar widget that tries to handle CORS issues more gracefully
class RobustMitraAvatar extends StatefulWidget {
  final String? imageUrl;
  final String mitraName;
  final double size;
  final Gender? mitraGender;

  const RobustMitraAvatar({
    super.key,
    this.imageUrl,
    required this.mitraName,
    this.size = 40,
    this.mitraGender,
  });

  @override
  State<RobustMitraAvatar> createState() => _RobustMitraAvatarState();
}

class _RobustMitraAvatarState extends State<RobustMitraAvatar> {
  bool _hasError = false;

  @override
  Widget build(BuildContext context) {
    if (widget.imageUrl == null || widget.imageUrl!.isEmpty || _hasError) {
      return _buildFallbackAvatar();
    }

    return Container(
      width: widget.size,
      height: widget.size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipOval(
        child: Image.network(
          widget.imageUrl!,
          width: widget.size,
          height: widget.size,
          fit: BoxFit.cover,
          loadingBuilder: (context, child, loadingProgress) {
            if (loadingProgress == null) return child;
            return _buildLoadingAvatar();
          },
          errorBuilder: (context, error, stackTrace) {
            debugPrint('Error loading Mitra profile image: $error');

            // Set error state to prevent repeated attempts
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                setState(() {
                  _hasError = true;
                });
              }
            });

            return _buildFallbackAvatar();
          },
          // Add cache headers
          headers: const {
            'Cache-Control': 'max-age=3600',
          },
        ),
      ),
    );
  }

  Widget _buildLoadingAvatar() {
    return Container(
      width: widget.size,
      height: widget.size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: _getMitraColor().withOpacity(0.1),
      ),
      child: Center(
        child: SizedBox(
          width: widget.size * 0.4,
          height: widget.size * 0.4,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(_getMitraColor()),
          ),
        ),
      ),
    );
  }

  Widget _buildFallbackAvatar() {
    return Container(
      width: widget.size,
      height: widget.size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: _getMitraColor(),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Center(
        child: Text(
          widget.mitraName.isNotEmpty ? widget.mitraName[0].toUpperCase() : 'M',
          style: TextStyle(
            fontSize: widget.size * 0.4,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ),
    );
  }

  Color _getMitraColor() {
    switch (widget.mitraGender) {
      case Gender.female:
        return const Color(0xFFE91E63); // Pink
      case Gender.male:
        return const Color(0xFF2196F3); // Blue
      case Gender.non_binary:
        return const Color(0xFF9C27B0); // Purple
      case Gender.prefer_not_to_say:
        return const Color(0xFF607D8B); // Blue Grey
      case null:
        return const Color(0xFF3498DB); // Default blue
    }
  }
}
