import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'jumns_colors.dart';

/// Charcoal Sketch theme — handwritten fonts, wobbly borders, paper texture.
ThemeData jumnsTheme() {
  // Gloria Hallelujah = display/headings, Patrick Hand = body text
  final displayFont = GoogleFonts.gloriaHallelujahTextTheme();
  final bodyFont = GoogleFonts.patrickHandTextTheme();

  final textTheme = bodyFont.copyWith(
    displayLarge: displayFont.displayLarge?.copyWith(color: JumnsColors.charcoal),
    displayMedium: displayFont.displayMedium?.copyWith(color: JumnsColors.charcoal),
    displaySmall: displayFont.displaySmall?.copyWith(color: JumnsColors.charcoal),
    headlineLarge: displayFont.headlineLarge?.copyWith(color: JumnsColors.charcoal),
    headlineMedium: displayFont.headlineMedium?.copyWith(color: JumnsColors.charcoal),
    headlineSmall: displayFont.headlineSmall?.copyWith(color: JumnsColors.charcoal),
    titleLarge: displayFont.titleLarge?.copyWith(
      fontWeight: FontWeight.w700,
      color: JumnsColors.charcoal,
    ),
    titleMedium: displayFont.titleMedium?.copyWith(
      fontWeight: FontWeight.w700,
      color: JumnsColors.charcoal,
    ),
    titleSmall: displayFont.titleSmall?.copyWith(
      fontWeight: FontWeight.w700,
      color: JumnsColors.charcoal,
    ),
    bodyLarge: bodyFont.bodyLarge?.copyWith(color: JumnsColors.charcoal),
    bodyMedium: bodyFont.bodyMedium?.copyWith(color: JumnsColors.charcoal),
    bodySmall: bodyFont.bodySmall?.copyWith(color: JumnsColors.ink),
    labelLarge: bodyFont.labelLarge?.copyWith(color: JumnsColors.charcoal),
    labelMedium: bodyFont.labelMedium?.copyWith(color: JumnsColors.charcoal),
    labelSmall: bodyFont.labelSmall?.copyWith(color: JumnsColors.charcoal),
  );

  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    scaffoldBackgroundColor: JumnsColors.paper,
    colorScheme: const ColorScheme.light(
      surface: JumnsColors.surface,
      surfaceContainer: JumnsColors.paperDark,
      primary: JumnsColors.charcoal,
      onPrimary: JumnsColors.paper,
      secondary: JumnsColors.lavender,
      tertiary: JumnsColors.coral,
      onSurface: JumnsColors.charcoal,
      onSurfaceVariant: JumnsColors.ink,
      outline: JumnsColors.ink,
      error: JumnsColors.error,
    ),
    textTheme: textTheme,
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      foregroundColor: JumnsColors.charcoal,
      elevation: 0,
      scrolledUnderElevation: 0,
    ),
    cardTheme: CardThemeData(
      color: JumnsColors.surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: JumnsColors.ink, width: 2),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: JumnsColors.surface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(20),
        borderSide: const BorderSide(color: JumnsColors.ink, width: 2),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(20),
        borderSide: const BorderSide(color: JumnsColors.ink, width: 2),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(20),
        borderSide: const BorderSide(color: JumnsColors.charcoal, width: 2.5),
      ),
      hintStyle: TextStyle(
        color: JumnsColors.ink.withAlpha(100),
        fontFamily: GoogleFonts.architectsDaughter().fontFamily,
        fontWeight: FontWeight.w700,
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: JumnsColors.charcoal,
        foregroundColor: JumnsColors.paper,
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        textStyle: TextStyle(
          fontWeight: FontWeight.w700,
          fontSize: 15,
          fontFamily: GoogleFonts.architectsDaughter().fontFamily,
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: JumnsColors.charcoal,
        side: const BorderSide(color: JumnsColors.ink, width: 2),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
      ),
    ),
    dividerTheme: const DividerThemeData(
      color: JumnsColors.ink,
      thickness: 2,
      space: 1,
    ),
    dialogTheme: DialogThemeData(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      backgroundColor: JumnsColors.paper,
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: JumnsColors.charcoal,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
  );
}
