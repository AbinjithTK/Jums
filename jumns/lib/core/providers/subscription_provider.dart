import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:purchases_flutter/purchases_flutter.dart';
import '../services/revenuecat_service.dart';

/// Subscription state for the app.
class SubscriptionState {
  final bool isPro;
  final bool isLoading;
  final String? error;
  final Offerings? offerings;
  final String? activeProduct;
  final String? expirationDate;
  final bool willRenew;

  const SubscriptionState({
    this.isPro = false,
    this.isLoading = false,
    this.error,
    this.offerings,
    this.activeProduct,
    this.expirationDate,
    this.willRenew = true,
  });

  SubscriptionState copyWith({
    bool? isPro,
    bool? isLoading,
    String? error,
    Offerings? offerings,
    String? activeProduct,
    String? expirationDate,
    bool? willRenew,
  }) =>
      SubscriptionState(
        isPro: isPro ?? this.isPro,
        isLoading: isLoading ?? this.isLoading,
        error: error,
        offerings: offerings ?? this.offerings,
        activeProduct: activeProduct ?? this.activeProduct,
        expirationDate: expirationDate ?? this.expirationDate,
        willRenew: willRenew ?? this.willRenew,
      );
}

class SubscriptionNotifier extends StateNotifier<SubscriptionState> {
  final RevenueCatService _rc;

  SubscriptionNotifier(this._rc) : super(const SubscriptionState());

  /// Load offerings and check current entitlement.
  Future<void> load() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final offerings = await _rc.getOfferings();
      final info = await _rc.getCustomerInfo();
      final proEntitlement =
          info.entitlements.active[RCConfig.entitlementId];

      state = state.copyWith(
        isLoading: false,
        offerings: offerings,
        isPro: proEntitlement != null,
        activeProduct: proEntitlement?.productIdentifier,
        expirationDate: proEntitlement?.expirationDate,
        willRenew: proEntitlement?.willRenew ?? true,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  /// Purchase a package (monthly or annual).
  Future<bool> purchase(Package package) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final info = await _rc.purchasePackage(package);
      final proEntitlement =
          info.entitlements.active[RCConfig.entitlementId];

      state = state.copyWith(
        isLoading: false,
        isPro: proEntitlement != null,
        activeProduct: proEntitlement?.productIdentifier,
        expirationDate: proEntitlement?.expirationDate,
        willRenew: proEntitlement?.willRenew ?? true,
      );
      return proEntitlement != null;
    } on PlatformException catch (e) {
      final code = PurchasesErrorHelper.getErrorCode(e);
      if (code == PurchasesErrorCode.purchaseCancelledError) {
        state = state.copyWith(isLoading: false);
        return false;
      }
      state = state.copyWith(
          isLoading: false, error: e.message ?? 'Purchase failed');
      return false;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }

  /// Restore purchases.
  Future<void> restore() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final info = await _rc.restorePurchases();
      final proEntitlement =
          info.entitlements.active[RCConfig.entitlementId];

      state = state.copyWith(
        isLoading: false,
        isPro: proEntitlement != null,
        activeProduct: proEntitlement?.productIdentifier,
        expirationDate: proEntitlement?.expirationDate,
        willRenew: proEntitlement?.willRenew ?? true,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final subscriptionNotifierProvider =
    StateNotifierProvider<SubscriptionNotifier, SubscriptionState>((ref) {
  return SubscriptionNotifier(ref.watch(revenueCatServiceProvider));
});
