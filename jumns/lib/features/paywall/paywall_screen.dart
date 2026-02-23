import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:purchases_flutter/purchases_flutter.dart';
import '../../core/providers/subscription_provider.dart';
import '../../core/theme/jumns_colors.dart';
import '../../core/theme/charcoal_decorations.dart';

class PaywallScreen extends ConsumerStatefulWidget {
  const PaywallScreen({super.key});

  @override
  ConsumerState<PaywallScreen> createState() => _PaywallScreenState();
}

class _PaywallScreenState extends ConsumerState<PaywallScreen> {
  int _selectedIndex = 1;

  @override
  void initState() {
    super.initState();
    Future.microtask(
        () => ref.read(subscriptionNotifierProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final sub = ref.watch(subscriptionNotifierProvider);
    final offering = sub.offerings?.current;
    final monthly = offering?.monthly;
    final annual = offering?.annual;
    final packages = <Package?>[monthly, annual];

    return Scaffold(
      backgroundColor: JumnsColors.paper,
      body: SafeArea(
        child: Column(
          children: [
            Align(
              alignment: Alignment.topLeft,
              child: IconButton(
                icon: const Icon(Icons.close, color: JumnsColors.charcoal),
                onPressed: () => Navigator.of(context).pop(),
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Column(
                  children: [
                    const SizedBox(height: 8),
                    // Icon blob
                    Stack(
                      alignment: Alignment.center,
                      children: [
                        Transform.rotate(
                          angle: 6 * math.pi / 180,
                          child: Container(
                            width: 90,
                            height: 90,
                            decoration: BoxDecoration(
                              color: JumnsColors.amber.withAlpha(100),
                              borderRadius: const BorderRadius.only(
                                topLeft: Radius.elliptical(64, 55),
                                topRight: Radius.elliptical(36, 58),
                                bottomLeft: Radius.elliptical(27, 42),
                                bottomRight: Radius.elliptical(73, 45),
                              ),
                            ),
                          ),
                        ),
                        BlobShape(
                          color: JumnsColors.lavender,
                          size: 72,
                          child: const Icon(Icons.auto_awesome,
                              color: JumnsColors.charcoal, size: 36),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Text('Unlock Jumns Pro',
                        style: GoogleFonts.gloriaHallelujah(
                            color: JumnsColors.charcoal,
                            fontSize: 28,
                            fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Text('Supercharge your AI assistant',
                        style: GoogleFonts.architectsDaughter(
                            color: JumnsColors.ink.withAlpha(150),
                            fontSize: 16)),
                    const SizedBox(height: 28),

                    // Feature list
                    ..._proFeatures.map((f) => Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: Row(
                            children: [
                              Icon(Icons.check_circle,
                                  color: JumnsColors.mint, size: 20),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(f,
                                    style: GoogleFonts.patrickHand(
                                        color: JumnsColors.charcoal,
                                        fontSize: 15)),
                              ),
                            ],
                          ),
                        )),
                    const SizedBox(height: 24),

                    if (sub.isLoading && offering == null)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 32),
                        child: CircularProgressIndicator(),
                      )
                    else ...[
                      _PlanCard(
                        title: 'Monthly',
                        price: monthly?.storeProduct.priceString ?? '\$9.99',
                        subtitle: 'per month',
                        isSelected: _selectedIndex == 0,
                        onTap: () => setState(() => _selectedIndex = 0),
                      ),
                      const SizedBox(height: 12),
                      _PlanCard(
                        title: 'Annual',
                        price: annual?.storeProduct.priceString ?? '\$79.99',
                        subtitle: 'per year',
                        badge: 'SAVE 33%',
                        isSelected: _selectedIndex == 1,
                        onTap: () => setState(() => _selectedIndex = 1),
                      ),
                      const SizedBox(height: 28),

                      if (sub.error != null && offering == null)
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(12),
                          margin: const EdgeInsets.only(bottom: 16),
                          decoration: BoxDecoration(
                            color: JumnsColors.paperDark.withAlpha(80),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Row(
                            children: [
                              Icon(Icons.info_outline,
                                  color: JumnsColors.ink.withAlpha(150),
                                  size: 18),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'In-app purchases are not available on this device.',
                                  style: GoogleFonts.patrickHand(
                                      color: JumnsColors.ink.withAlpha(150),
                                      fontSize: 13),
                                ),
                              ),
                            ],
                          ),
                        )
                      else if (sub.error != null)
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(12),
                          margin: const EdgeInsets.only(bottom: 16),
                          decoration: BoxDecoration(
                            color: JumnsColors.error.withAlpha(20),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                                color: JumnsColors.error.withAlpha(60)),
                          ),
                          child: Text(
                            'Something went wrong. Please try again later.',
                            style: const TextStyle(
                                color: JumnsColors.error, fontSize: 13),
                          ),
                        ),

                      SizedBox(
                        width: double.infinity,
                        height: 52,
                        child: ElevatedButton(
                          onPressed: sub.isLoading ||
                                  (sub.error != null && offering == null)
                              ? null
                              : () => _purchase(packages[_selectedIndex]),
                          child: sub.isLoading
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: JumnsColors.paper))
                              : Text(
                                  _selectedIndex == 1
                                      ? 'Subscribe Annually'
                                      : 'Subscribe Monthly',
                                  style: const TextStyle(fontSize: 17)),
                        ),
                      ),
                    ],

                    const SizedBox(height: 12),
                    TextButton(
                      onPressed: sub.isLoading ? null : _restore,
                      child: Text('Restore Purchase',
                          style: GoogleFonts.architectsDaughter(
                              color: JumnsColors.ink.withAlpha(150))),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        TextButton(
                          onPressed: () {},
                          child: Text('Terms',
                              style: GoogleFonts.architectsDaughter(
                                  color: JumnsColors.ink.withAlpha(100),
                                  fontSize: 11)),
                        ),
                        Text('·',
                            style: TextStyle(
                                color: JumnsColors.ink.withAlpha(100))),
                        TextButton(
                          onPressed: () {},
                          child: Text('Privacy',
                              style: GoogleFonts.architectsDaughter(
                                  color: JumnsColors.ink.withAlpha(100),
                                  fontSize: 11)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _purchase(Package? package) async {
    if (package == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text('Purchases not available on this device.')),
        );
      }
      return;
    }
    final success = await ref
        .read(subscriptionNotifierProvider.notifier)
        .purchase(package);
    if (success && mounted) {
      Navigator.of(context).pop(true);
    }
  }

  Future<void> _restore() async {
    await ref.read(subscriptionNotifierProvider.notifier).restore();
    final isPro = ref.read(subscriptionNotifierProvider).isPro;
    if (isPro && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Pro access restored!')),
      );
      Navigator.of(context).pop(true);
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No active subscription found')),
      );
    }
  }

  static const _proFeatures = [
    'Unlimited AI messages',
    'Unlimited goals & tasks',
    'Advanced AI memory',
    'All skills & MCP tools',
    'Voice mode',
    'Priority AI responses',
  ];
}

class _PlanCard extends StatelessWidget {
  final String title;
  final String price;
  final String subtitle;
  final String? badge;
  final bool isSelected;
  final VoidCallback onTap;

  const _PlanCard({
    required this.title,
    required this.price,
    required this.subtitle,
    this.badge,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: isSelected
            ? charcoalBorderDecoration()
            : BoxDecoration(
                color: JumnsColors.surface,
                borderRadius: kCharcoalRadius,
                border: Border.all(
                    color: JumnsColors.ink.withAlpha(60), width: 1.5),
              ),
        child: Row(
          children: [
            // Radio indicator
            Container(
              width: 22,
              height: 22,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: isSelected
                      ? JumnsColors.charcoal
                      : JumnsColors.ink.withAlpha(100),
                  width: 2,
                ),
              ),
              child: isSelected
                  ? Center(
                      child: Container(
                        width: 12,
                        height: 12,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: JumnsColors.charcoal,
                        ),
                      ),
                    )
                  : null,
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(title,
                          style: GoogleFonts.architectsDaughter(
                              color: JumnsColors.charcoal,
                              fontSize: 16,
                              fontWeight: FontWeight.w700)),
                      if (badge != null) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: JumnsColors.charcoal,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(badge!,
                              style: GoogleFonts.architectsDaughter(
                                  color: JumnsColors.paper,
                                  fontSize: 10,
                                  fontWeight: FontWeight.w700)),
                        ),
                      ],
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(subtitle,
                      style: GoogleFonts.patrickHand(
                          color: JumnsColors.ink.withAlpha(130),
                          fontSize: 13)),
                ],
              ),
            ),
            Text(price,
                style: GoogleFonts.gloriaHallelujah(
                    color: JumnsColors.charcoal,
                    fontSize: 18,
                    fontWeight: FontWeight.w700)),
          ],
        ),
      ),
    );
  }
}
