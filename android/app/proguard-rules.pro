# Proguard rules for Ayureze Doctor App
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# Firebase
-keep class com.google.firebase.** { *; }

# Razorpay
-keep class com.razorpay.** {*;}
-dontwarn com.razorpay.**

# Agora
-keep class io.agora.** { *; }
-dontwarn io.agora.**
