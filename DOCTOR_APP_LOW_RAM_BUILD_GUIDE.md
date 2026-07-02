# 📱 Ayureze Doctor App - Low RAM Build Guide

This guide is specifically tailored for building the release APK of the **Ayureze Doctor App** on laptops with low RAM (e.g., 4GB or 8GB). 

By restricting Gradle's maximum memory allocation and disabling parallel execution, your laptop will not freeze or crash during the intense APK compilation process.

---

## 🛠️ Required Versions

Based on your actual source code config (`pubspec.yaml` and `build.gradle`), ensure you have these exact versions installed on your System:

1. **Flutter SDK**: `Version 3.22.0` or newer (Required for new Android 36 SDK paths)
2. **Dart SDK**: `>= 3.4.4` (Comes bundled with Flutter 3.22+)
3. **Java/JDK Version**: `Java 17` (Used by Gradle to compile). *Note: The app source code compiles backward to Java Version 1.8 (`JavaVersion.VERSION_1_8`), but Gradle itself requires JDK 17 to run Android API 36.*

---

## 🚀 Step 1: Optimize Gradle for Low RAM

Before running any Flutter commands, we need to instruct Android Studio/Gradle to use less memory so it doesn't crash your laptop.

1. Open your code editor and navigate to:
   `ayureze_doctor-development / android / gradle.properties`
   *(If the file does not exist, create it).*
2. Add or replace the contents with the following exact lines:

```properties
org.gradle.jvmargs=-Xmx1024m -XX:MaxPermSize=512m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8
org.gradle.parallel=false
org.gradle.daemon=true
org.gradle.configureondemand=true
android.enableJetifier=true
android.useAndroidX=true
```

> **Why this helps:** `-Xmx1024m` restricts Java to exactly 1GB of RAM maximum. `org.gradle.parallel=false` stops it from trying to compile 4 things at once, taking pressure off your CPU and RAM.

---

## 🧹 Step 2: Clean the Workspace

Open your terminal or command prompt inside the specifically `ayureze_doctor-development` folder.

Clear out all old cached heavy files to free up disk space and memory:
```bash
flutter clean
flutter pub get
```

---

## 📦 Step 3: Build the Release APK

Now, execute the build command. Since you have low RAM, we want to build a "split ABI" apk or a standard release APK which is specifically smaller.

Run this simple command:
```bash
flutter build apk --release
```

*Note: This process may take 5 to 10 minutes on a low-RAM machine because we turned off parallel compilation. Let it sit, do not open browsers or Android Studio while it is building!*

### 📥 Where to find your APK:
Once it successfully says `✓ Built build\app\outputs\flutter-apk\app-release.apk`, you can find your App ready to be transferred to your Android phone here:
`ayureze_doctor-development\build\app\outputs\flutter-apk\app-release.apk`
