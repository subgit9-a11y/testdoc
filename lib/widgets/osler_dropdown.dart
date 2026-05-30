import 'package:flutter/material.dart';
import 'package:doctro/theme/ayureze_theme.dart';

class OslerDropdown extends StatelessWidget {
  final String label;
  final String hint;
  final String? value;
  final List<String> items;
  final ValueChanged<String?> onChanged;
  final String? Function(String?)? validator;
  final IconData? prefixIcon;

  const OslerDropdown({
    super.key,
    required this.label,
    required this.hint,
    required this.value,
    required this.items,
    required this.onChanged,
    this.validator,
    this.prefixIcon,
  });

  @override
  Widget build(BuildContext context) {
    final String? safeValue = (value != null && items.contains(value)) ? value : null;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label.isNotEmpty) ...[
          Text(
            label,
            style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
          ),
          const SizedBox(height: 8),
        ],
        DropdownButtonFormField<String>(
          value: safeValue,
          hint: Text(hint, style: TextStyle(color: AyurezeTheme.textSecondary)),
          decoration: InputDecoration(
            filled: true,
            fillColor: AyurezeTheme.oslerGray10,
            contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
            prefixIcon: prefixIcon != null ? Icon(prefixIcon, size: 20, color: AyurezeTheme.healingGreen100) : null,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: const BorderSide(color: Colors.transparent),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide(color: AyurezeTheme.healingGreen50, width: 2),
            ),
          ),
          items: items.map((String item) => DropdownMenuItem(value: item, child: Text(item))).toList(),
          onChanged: onChanged,
          validator: validator,
        ),
      ],
    );
  }
}
