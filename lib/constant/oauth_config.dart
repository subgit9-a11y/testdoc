/// Google OAuth client IDs for Google Sign-In.
///
/// These are PUBLIC identifiers (not secrets). They are safe to commit.
/// They are configured in the Google Cloud Console under
/// "Credentials" > "OAuth 2.0 Client IDs" and must match the package
/// name + SHA-1 of the app for each platform.
class OAuthConfig {
  /// iOS OAuth client ID (iOS app).
  static const String iosClientId =
      '298839588168-up4rcmclffgne2hnlemg7n4e29qtovn2.apps.googleusercontent.com';

  /// Android OAuth client ID.
  static const String androidClientId =
      '298839588168-6ut75u7g4rqc8grmujtcl4m7obnq3oml.apps.googleusercontent.com';

  /// Server (web) client ID — used for ID token verification on backend.
  static const String serverClientId =
      '298839588168-6ut75u7g4rqc8grmujtcl4m7obnq3oml.apps.googleusercontent.com';
}
