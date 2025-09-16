import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:app/services/api_service.dart';
import 'package:app/models/chat_models.dart';
import 'flashcard_screen.dart';

// Mock data for now
final journalEntriesProvider = FutureProvider<List<JournalEntry>>((ref) async {
  return [
    JournalEntry(
      id: "1",
      userId: "1",
      title: "A Good Day",
      content: "Today was a good day. I felt happy and productive.",
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
      is_private: true,
      tags: ["happy", "productive"],
    ),
    JournalEntry(
      id: "2",
      userId: "1",
      title: "A Tough Day",
      content: "Today was a bit tough. I felt stressed and anxious.",
      createdAt: DateTime.now().subtract(const Duration(days: 1)),
      updatedAt: DateTime.now().subtract(const Duration(days: 1)),
      is_private: true,
      tags: ["stressed", "anxious"],
    ),
  ];
});

class JournalScreen extends ConsumerWidget {
  const JournalScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final journalEntries = ref.watch(journalEntriesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Personal Journal'),
      ),
      body: journalEntries.when(
        data: (entries) => ListView.builder(
          itemCount: entries.length,
          itemBuilder: (context, index) {
            final entry = entries[index];
            return ListTile(
              title: Text(entry.title ?? 'No Title'),
              subtitle: Text(
                entry.content,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              trailing: IconButton(
                icon: const Icon(Icons.style),
                onPressed: () async {
                  try {
                    final apiService = ApiService();
                    final flashcardResponse = await apiService.generateFlashcards(entry.id);
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (context) => FlashcardScreen(
                          flashcards: flashcardResponse.flashcards,
                        ),
                      ),
                    );
                  } catch (e) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Error generating flashcards: $e'),
                      ),
                    );
                  }
                },
              ),
            );
          },
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(child: Text('Error: $error')),
      ),
    );
  }
}

// A mock JournalEntry class to make the code runnable
class JournalEntry {
  final String id;
  final String userId;
  final String? title;
  final String content;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool is_private;
  final List<String> tags;

  const JournalEntry({
    required this.id,
    required this.userId,
    this.title,
    required this.content,
    required this.createdAt,
    required this.updatedAt,
    required this.is_private,
    required this.tags,
  });
}
