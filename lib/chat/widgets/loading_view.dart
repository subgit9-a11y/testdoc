import 'package:flutter/material.dart';



class LoadingView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      child: Center(
        child: CircularProgressIndicator(
          color: Theme.of(context).colorScheme.primary,
        ),
      ),
      color: Theme.of(context).colorScheme.surface.withOpacity(0.8),
    );
  }
}
