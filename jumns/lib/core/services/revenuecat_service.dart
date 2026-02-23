import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

/// RevenueCat configuration — pass via --dart-define at build time:
///   flutter run \
///     --dart-define=RC_GOOGLE_API_KEY=goog_xxx \
///     --dart-define=RC_APPLE_API_KEY=appl_xxx
class RCConfig {
  static const String googleApiKey = String.fromEnvironment(
    'RC_GOOGLE_API_KEY',
    defaultValue: '',
  );
  static const String appleApiKey = String.fromEnvironment(
    'RC_APPLE_API_KEY',
    defaultValue: '',
  );
  // Entitlement identifier configured in RevenueCat
  static const String entitlementId = 'pro';
}

/// Wraps the RevenueCat Purchases SDK.
class RevenueCatService {
  bool _initialized = false;

  /// Initialize the SDK. Call once at app startup after auth is resolved.
  Future<void> init({String? userId}) async {
    if (_initialized) return;

    final apiKey = Platform.isIOS || Platform.isMacOS
        ? RCConfig.appleApiKey
        : RCConfig.googleApiKey;

    // Skip initialization if no API key is configured
    if (apiKey.isEmpty) return;

    await Purchases.setLogLevel(LogLevel.debug);

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
