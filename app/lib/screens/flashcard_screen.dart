import 'package:flutter/material.dart';
import 'package:flutter_card_swiper/flutter_card_swiper.dart';
import '../models/chat_models.dart';

class FlashcardScreen extends StatelessWidget {
  final List<Flashcard> flashcards;

  const FlashcardScreen({super.key, required this.flashcards});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Flashcards'),
      ),
      body: Center(
        child: SizedBox(
          height: 400,
          width: 300,
          child: CardSwiper(
            cardsCount: flashcards.length,
            cardBuilder: (context, index, percentThresholdX, percentThresholdY) {
              final card = flashcards[index];
              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Front',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 16),
                      Text(card.front),
                      const SizedBox(height: 32),
                      const Divider(),
                      const SizedBox(height: 32),
                      Text(
                        'Back',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 16),
                      Text(card.back),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}
