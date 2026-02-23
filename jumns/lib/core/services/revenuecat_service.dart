import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

/// RevenueCat configuration.
/// The SDK auto-detects the platform and uses the correct API key.
class RCConfig {
  // Google Play Store API key (from RevenueCat dashboard)
  static const String googleApiKey = 'goog_kcZEKrSaBmOExbSLzeQxZjGLfHc';
  // Apple App Store API key (from RevenueCat dashboard)
  static const String appleApiKey = 'appl_itpKRhMuBPKqCzrRbCHZkPCLyMl';
  // Entitlement identifier configured in RevenueCat
  static const String entitlementId = 'pro';
}

/// Wraps the RevenueCat Purchases SDK.
class RevenueCatService {
  bool _initialized = false;

  /// Initialize the SDK. Call once at app startup after auth is resolved.
  Future<void> init({String? userId}) async {
    if (_initialized) return;

    await Purchases.setLogLevel(LogLevel.debug);

    final apiKey = Platform.isIOS || Platform.isMacOS
        ? RCConfig.appleApiKey
        : RCConfig.googleApiKey;

    final config = PurchasesConfiguration(apiKey)
      ..appUserID = userId
      ..purchasesAreCompletedBy =
          const PurchasesAreCompletedByRevenueCat();

    await Purchases.configure(config);
    _initialized = true;
  }

  /// Log in a specific user (call after Cognito sign-in).
  Future<CustomerInfo> logIn(String userId) async {
    final result = await Purchases.logIn(userId);
    return result.customerInfo;
  }

  /// Log out (call on sign-out).
  Future<CustomerInfo> logOut() async {
    return await Purchases.logOut();
  }

  /// Fetch current offerings (packages + prices).
  Future<Offerings> getOfferings() async {
    return await Purchases.getOfferings();
  }

  /// Purchase a package.
  Future<CustomerInfo> purchasePackage(Package package) async {
    final params = PurchaseParams.package(package);
    final result = await Purchases.purchase(params);
    return result.customerInfo;
  }

  /// Check if user has pro entitlement.
  Future<bool> hasProAccess() async {
    final info = await Purchases.getCustomerInfo();
    return info.entitlements.active.containsKey(RCConfig.entitlementId);
  }

  /// Get full customer info.
  Future<CustomerInfo> getCustomerInfo() async {
    return await Purchases.getCustomerInfo();
  }

  /// Restore purchases (device transfer / reinstall).
  Future<CustomerInfo> restorePurchases() async {
    return await Purchases.restorePurchases();
  }
}

final revenueCatServiceProvider =
    Provider<RevenueCatService>((ref) => RevenueCatService());
