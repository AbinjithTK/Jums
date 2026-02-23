class UserSettings {
  final String id;
  final String userId;
  final String agentName;
  final String agentBehavior;
  final bool onboardingCompleted;
  final String timezone;
  final DateTime? createdAt;

  const UserSettings({
    required this.id,
    required this.userId,
    this.agentName = 'Jumns',
    this.agentBehavior = 'friendly',
    this.onboardingCompleted = false,
    this.timezone = 'UTC',
    this.createdAt,
  });

  factory UserSettings.fromJson(Map<String, dynamic> json) => UserSettings(
        id: json['id'] as String? ?? '',
        userId: json['userId'] as String? ?? '',
        agentName: json['agentName'] as String? ?? 'Jumns',
        agentBehavior: json['agentBehavior'] as String? ?? 'friendly',
        onboardingCompleted: json['onboardingCompleted'] as bool? ?? false,
        timezone: json['timezone'] as String? ?? 'UTC',
        createdAt: json['createdAt'] != null
            ? DateTime.tryParse(json['createdAt'] as String)
            : null,
      );

  /// Emoji for the current personality.
  String get personalityEmoji => switch (agentBehavior.toLowerCase()) {
        'coach' => '💪',
        'professional' => '📋',
        'zen' => '🧘',
        'creative' => '✨',
        _ => '😊',
      };

  /// Human-readable personality label.
  String get personalityLabel => switch (agentBehavior.toLowerCase()) {
        'coach' => 'Coach',
        'professional' => 'Professional',
        'zen' => 'Zen',
        'creative' => 'Creative',
        _ => 'Friendly',
      };
}

class SubscriptionStatus {
  final String plan;
  final bool isPro;
  final String? expiresAt;

  const SubscriptionStatus({
    this.plan = 'free',
    this.isPro = false,
    this.expiresAt,
  });

  factory SubscriptionStatus.fromJson(Map<String, dynamic> json) =>
      SubscriptionStatus(
        plan: json['plan'] as String? ?? 'free',
        isPro: json['isPro'] as bool? ?? json['entitled'] as bool? ?? false,
        expiresAt: json['expiresAt'] as String?,
      );
}
