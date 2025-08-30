import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:url_launcher/url_launcher.dart';

class MarkdownMessage extends StatelessWidget {
  final String markdown;
  final bool isUser;
  final VoidCallback? onTap;

  const MarkdownMessage({
    super.key,
    required this.markdown,
    required this.isUser,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxWidth: MediaQuery.of(context).size.width * 0.85,
      ),
      child: MarkdownBody(
        data: markdown,
        selectable: true,
        styleSheet: MarkdownStyleSheet(
          p: TextStyle(
            color: isUser ? const Color(0xFF303030) : const Color(0xFF303030),
            fontSize: 16,
            height: 1.4,
          ),
          h1: TextStyle(
            color: isUser ? const Color(0xFF1976D2) : const Color(0xFF1976D2),
            fontSize: 24,
            fontWeight: FontWeight.bold,
            height: 1.3,
          ),
          h2: TextStyle(
            color: isUser ? const Color(0xFF1976D2) : const Color(0xFF1976D2),
            fontSize: 20,
            fontWeight: FontWeight.bold,
            height: 1.3,
          ),
          h3: TextStyle(
            color: isUser ? const Color(0xFF1976D2) : const Color(0xFF1976D2),
            fontSize: 18,
            fontWeight: FontWeight.w600,
            height: 1.3,
          ),
          strong: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Color(0xFF1565C0),
          ),
          em: const TextStyle(
            fontStyle: FontStyle.italic,
          ),
          code: TextStyle(
            backgroundColor: isUser
                ? const Color(0xFFE8F5E8)
                : const Color(0xFFF5F5F5),
            color: const Color(0xFFD32F2F),
            fontFamily: 'monospace',
            fontSize: 14,
          ),
          codeblockDecoration: BoxDecoration(
            color: isUser
                ? const Color(0xFFE8F5E8)
                : const Color(0xFFF8F9FA),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFFE0E0E0)),
          ),
          codeblockPadding: const EdgeInsets.all(12),
          blockquote: TextStyle(
            color: const Color(0xFF666666),
            fontStyle: FontStyle.italic,
          ),
          blockquoteDecoration: BoxDecoration(
            border: Border(
              left: BorderSide(
                color: const Color(0xFF1976D2),
                width: 3,
              ),
            ),
          ),
          blockquotePadding: const EdgeInsets.only(left: 16),
          listBullet: const TextStyle(
            color: Color(0xFF1976D2),
            fontWeight: FontWeight.bold,
          ),
          listIndent: 24,
          a: const TextStyle(
            color: Color(0xFF1976D2),
            decoration: TextDecoration.underline,
          ),
        ),
        onTapLink: (text, href, title) async {
          if (href != null) {
            final uri = Uri.parse(href);
            if (await canLaunchUrl(uri)) {
              await launchUrl(uri, mode: LaunchMode.externalApplication);
            }
          }
        },
        imageBuilder: (uri, title, alt) {
          return Container(
            margin: const EdgeInsets.symmetric(vertical: 8),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                uri.toString(),
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  return Container(
                    height: 200,
                    alignment: Alignment.center,
                    child: CircularProgressIndicator(
                      value: loadingProgress.expectedTotalBytes != null
                          ? loadingProgress.cumulativeBytesLoaded /
                              loadingProgress.expectedTotalBytes!
                          : null,
                    ),
                  );
                },
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    height: 200,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.broken_image, size: 48, color: Colors.grey),
                        const SizedBox(height: 8),
                        Text(
                          alt ?? 'Failed to load image',
                          style: const TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          );
        },
      ),
    );
  }
}

// Extension to add markdown styling for different message types
extension MarkdownMessageStyles on MarkdownMessage {
  static Widget resource({
    required String title,
    required String description,
    required String content,
    VoidCallback? onTap,
  }) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFF3E5F5), Color(0xFFE8EAF6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.auto_awesome,
                color: Color(0xFF7B1FA2),
                size: 20,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: Color(0xFF7B1FA2),
                  ),
                ),
              ),
            ],
          ),
          if (description.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              description,
              style: const TextStyle(
                fontSize: 14,
                color: Color(0xFF666666),
              ),
            ),
          ],
          const SizedBox(height: 12),
          MarkdownMessage(
            markdown: content,
            isUser: false,
            onTap: onTap,
          ),
        ],
      ),
    );
  }
}
