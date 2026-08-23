# LabelSetu Mobile

Stage 1 Flutter Android field-inspection client. Inspection drafts and original camera evidence are stored locally. The app does not connect directly to PostgreSQL, Redis, or S3 and performs no OCR, computer vision, measurement, or compliance calculation.

## Run

```powershell
flutter pub get
flutter analyze
flutter test
flutter devices
flutter run
```

Authentication is a local mock for Stage 1. Enter any non-empty email and password. The API base URL in `.env.example` is reserved for Stage 2 and contains no secrets.# mobile

A new Flutter project.

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Learn Flutter](https://docs.flutter.dev/get-started/learn-flutter)
- [Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Flutter learning resources](https://docs.flutter.dev/reference/learning-resources)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.
