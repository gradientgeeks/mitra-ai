import 'package:flutter/material.dart';

enum ProblemCategory {
  anxiety('Anxiety', Icons.psychology_outlined),
  depression('Depression', Icons.sentiment_dissatisfied),
  stress('Stress', Icons.healing),
  relationships('Relationships', Icons.favorite),
  selfEsteem('Self-esteem', Icons.self_improvement),
  grief('Grief & Loss', Icons.mood_bad),
  trauma('Trauma', Icons.support),
  sleep('Sleep Issues', Icons.bedtime),
  work('Work/Career', Icons.work),
  family('Family Issues', Icons.family_restroom),
  addiction('Addiction', Icons.local_pharmacy),
  anger('Anger Management', Icons.sentiment_very_dissatisfied),
  identity('Identity', Icons.person_search),
  other('Other', Icons.help_outline);

  const ProblemCategory(this.displayName, this.icon);
  final String displayName;
  final IconData icon;
}

class ProblemCategorySelectionDialog extends StatefulWidget {
  final List<ProblemCategory> initialSelectedCategories;
  final Function(List<ProblemCategory>) onConfirm;

  const ProblemCategorySelectionDialog({
    super.key,
    required this.initialSelectedCategories,
    required this.onConfirm,
  });

  @override
  State<ProblemCategorySelectionDialog> createState() =>
      _ProblemCategorySelectionDialogState();
}

class _ProblemCategorySelectionDialogState
    extends State<ProblemCategorySelectionDialog> {
  late List<ProblemCategory> selectedCategories;

  @override
  void initState() {
    super.initState();
    selectedCategories = List.from(widget.initialSelectedCategories);
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: Container(
        constraints: BoxConstraints(
          maxHeight: MediaQuery.of(context).size.height * 0.7,
          maxWidth: MediaQuery.of(context).size.width * 0.9,
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Icon(
                  Icons.category_outlined,
                  color: const Color(0xFF3498DB),
                  size: 28,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'What would you like to focus on?',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF2C3E50),
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Select the areas you\'d like to discuss today (you can choose multiple)',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: const Color(0xFF7F8C8D),
                  ),
            ),
            const SizedBox(height: 20),

            // Categories List
            Flexible(
              child: GridView.builder(
                shrinkWrap: true,
                physics: const BouncingScrollPhysics(),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  childAspectRatio: 2.5,
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                ),
                itemCount: ProblemCategory.values.length,
                itemBuilder: (context, index) {
                  final category = ProblemCategory.values[index];
                  final isSelected = selectedCategories.contains(category);

                  return InkWell(
                    onTap: () {
                      setState(() {
                        if (isSelected) {
                          selectedCategories.remove(category);
                        } else {
                          selectedCategories.add(category);
                        }
                      });
                    },
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: isSelected
                            ? const Color(0xFF3498DB).withOpacity(0.1)
                            : Colors.grey.withOpacity(0.05),
                        border: Border.all(
                          color: isSelected
                              ? const Color(0xFF3498DB)
                              : Colors.grey.withOpacity(0.3),
                          width: 1.5,
                        ),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            category.icon,
                            color: isSelected
                                ? const Color(0xFF3498DB)
                                : const Color(0xFF7F8C8D),
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              category.displayName,
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(
                                    color: isSelected
                                        ? const Color(0xFF3498DB)
                                        : const Color(0xFF2C3E50),
                                    fontWeight: isSelected
                                        ? FontWeight.w600
                                        : FontWeight.w500,
                                  ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),

            const SizedBox(height: 24),

            // Action Buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      Navigator.of(context).pop();
                    },
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      side: const BorderSide(color: Color(0xFF7F8C8D)),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text(
                      'Cancel',
                      style: TextStyle(
                        color: Color(0xFF7F8C8D),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: selectedCategories.isNotEmpty
                        ? () {
                            widget.onConfirm(selectedCategories);
                            Navigator.of(context).pop();
                          }
                        : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF3498DB),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 2,
                    ),
                    child: Text(
                      selectedCategories.isEmpty
                          ? 'Select at least one'
                          : 'Continue (${selectedCategories.length})',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// Helper function to show the dialog
Future<List<ProblemCategory>?> showProblemCategoryDialog(
  BuildContext context, {
  List<ProblemCategory> initialSelected = const [],
}) async {
  List<ProblemCategory>? result;

  await showDialog<void>(
    context: context,
    barrierDismissible: false,
    builder: (BuildContext context) {
      return ProblemCategorySelectionDialog(
        initialSelectedCategories: initialSelected,
        onConfirm: (categories) {
          result = categories;
        },
      );
    },
  );

  return result;
}