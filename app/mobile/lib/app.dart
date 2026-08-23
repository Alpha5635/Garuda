import 'dart:io';

import 'package:camera/camera.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:go_router/go_router.dart';
import 'package:path/path.dart' as path;
import 'package:permission_handler/permission_handler.dart';
import 'package:sqflite/sqflite.dart';
import 'package:uuid/uuid.dart';

import 'core/config/api_client.dart';

const ink = Color(0xFF17242A);
const teal = Color(0xFF007C78);
const paper = Color(0xFFF4F7F5);

final storeProvider = Provider<LocalStore>((ref) => LocalStore());
final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());
final inspectionsProvider =
    NotifierProvider<InspectionController, List<Inspection>>(
      InspectionController.new,
    );
final onlineProvider = StreamProvider<bool>((ref) async* {
  yield true;
  await for (final result in Connectivity().onConnectivityChanged) {
    yield result.any((item) => item != ConnectivityResult.none);
  }
});

class LabelSetuApp extends StatelessWidget {
  const LabelSetuApp({super.key});

  @override
  Widget build(BuildContext context) {
    final router = GoRouter(
      initialLocation: '/login',
      routes: [
        GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
        GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
        GoRoute(path: '/new', builder: (_, __) => const InspectionTypeScreen()),
        GoRoute(
          path: '/guidance/:type',
          builder: (_, state) =>
              GuidanceScreen(type: state.pathParameters['type']!),
        ),
        GoRoute(
          path: '/camera/:type',
          builder: (_, state) =>
              CaptureScreen(type: state.pathParameters['type']!),
        ),
        GoRoute(
          path: '/preview',
          builder: (_, state) =>
              PreviewScreen(imagePath: state.extra! as String),
        ),
        GoRoute(
          path: '/calibration',
          builder: (_, __) => const CalibrationScreen(),
        ),
        GoRoute(path: '/queue', builder: (_, __) => const QueueScreen()),
        GoRoute(path: '/history', builder: (_, __) => const HistoryScreen()),
      ],
    );
    return MaterialApp.router(
      title: 'LabelSetu',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: paper,
        colorScheme: ColorScheme.fromSeed(seedColor: teal),
        appBarTheme: const AppBarTheme(
          backgroundColor: paper,
          foregroundColor: ink,
          elevation: 0,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        ),
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
      routerConfig: router,
    );
  }
}

class Inspection {
  Inspection({
    required this.id,
    required this.key,
    required this.type,
    required this.createdAt,
    this.imagePath,
    this.captureTime,
    this.latitude,
    this.longitude,
    this.accuracy,
    this.calibration,
    this.status = 'draft',
    this.retryCount = 0,
    this.lastError,
    this.remoteId,
    this.jobId,
  });

  final String id;
  final String key;
  final String type;
  final DateTime createdAt;
  String? imagePath;
  DateTime? captureTime;
  double? latitude;
  double? longitude;
  double? accuracy;
  String? calibration;
  String status;
  int retryCount;
  String? lastError;
  String? remoteId;
  String? jobId;

  Map<String, Object?> toMap() => {
    'client_inspection_id': id,
    'idempotency_key': key,
    'inspection_type': type,
    'image_path': imagePath,
    'created_at': createdAt.toIso8601String(),
    'capture_time': captureTime?.toIso8601String(),
    'latitude': latitude,
    'longitude': longitude,
    'gps_accuracy': accuracy,
    'calibration_metadata': calibration,
    'status': status,
    'retry_count': retryCount,
    'last_error': lastError,
    'remote_id': remoteId,
    'job_id': jobId,
  };

  factory Inspection.fromMap(Map<String, Object?> map) => Inspection(
    id: map['client_inspection_id']! as String,
    key: map['idempotency_key']! as String,
    type: map['inspection_type']! as String,
    createdAt: DateTime.parse(map['created_at']! as String),
    imagePath: map['image_path'] as String?,
    captureTime: map['capture_time'] == null
        ? null
        : DateTime.parse(map['capture_time']! as String),
    latitude: map['latitude'] as double?,
    longitude: map['longitude'] as double?,
    accuracy: map['gps_accuracy'] as double?,
    calibration: map['calibration_metadata'] as String?,
    status: map['status']! as String,
    retryCount: map['retry_count']! as int,
    lastError: map['last_error'] as String?,
    remoteId: map['remote_id'] as String?,
    jobId: map['job_id'] as String?,
  );
}

class LocalStore {
  Database? _db;

  Future<Database> get db async {
    if (_db != null) return _db!;
    _db = await openDatabase(
      path.join(await getDatabasesPath(), 'labelsetu.db'),
      version: 2,
      onCreate: (database, _) => database.execute('''
          CREATE TABLE inspections (
            client_inspection_id TEXT PRIMARY KEY,
            idempotency_key TEXT,
            inspection_type TEXT,
            image_path TEXT,
            created_at TEXT,
            capture_time TEXT,
            latitude REAL,
            longitude REAL,
            gps_accuracy REAL,
            calibration_metadata TEXT,
            status TEXT,
            retry_count INTEGER,
            last_error TEXT
            ,remote_id TEXT
            ,job_id TEXT
          )
        '''),
      onUpgrade: (database, oldVersion, _) async {
        if (oldVersion < 2) {
          await database.execute('ALTER TABLE inspections ADD COLUMN remote_id TEXT');
          await database.execute('ALTER TABLE inspections ADD COLUMN job_id TEXT');
        }
      },
    );
    return _db!;
  }

  Future<void> save(Inspection item) async {
    await (await db).insert(
      'inspections',
      item.toMap(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Inspection>> all() async {
    final rows = await (await db).query(
      'inspections',
      orderBy: 'created_at DESC',
    );
    return rows.map(Inspection.fromMap).toList();
  }
}

class InspectionController extends Notifier<List<Inspection>> {
  late final LocalStore store;

  @override
  List<Inspection> build() {
    store = ref.read(storeProvider);
    ref.listen<AsyncValue<bool>>(onlineProvider, (_, next) {
      if (next.value == true) syncQueued();
    });
    load();
    return [];
  }

  Future<void> load() async => state = await store.all();

  Future<void> create(String type) async {
    final item = Inspection(
      id: const Uuid().v4(),
      key: const Uuid().v4(),
      type: type,
      createdAt: DateTime.now(),
    );
    await store.save(item);
    state = [item, ...state];
  }

  Future<void> update(Inspection item) async {
    await store.save(item);
    state = [...state];
  }

  Future<void> refreshProcessing() async {
    final api = ref.read(apiClientProvider);
    for (final item in [...state]) {
      if (item.jobId == null) continue;
      try {
        final job = await api.job(item.jobId!);
        item.status = job['status'] as String? ?? item.status;
        item.lastError = job['error_reason'] as String?;
        await store.save(item);
      } on ApiException catch (exception) {
        item.lastError = exception.message;
        await store.save(item);
      }
    }
    state = await store.all();
  }

  Future<void> syncQueued() async {
    final online = await Connectivity().checkConnectivity();
    if (!online.any((result) => result != ConnectivityResult.none)) return;
    for (final item in [...state]) {
      if (item.type != 'batch' || item.imagePath == null || item.status != 'draft') {
        continue;
      }
      try {
        final api = ref.read(apiClientProvider);
        final session = await api.createSession({
          'client_session_id': item.id,
          'idempotency_key': item.key,
          'latitude': item.latitude,
          'longitude': item.longitude,
          'gps_accuracy': item.accuracy,
          'metadata_json': {'calibration': item.calibration},
        });
        item.remoteId = session['id'] as String?;
        if (item.remoteId == null) continue;
        await api.uploadSessionImage(
          item.remoteId!,
          item.imagePath!,
          latitude: item.latitude,
          longitude: item.longitude,
        );
        item.status = 'processing';
        item.lastError = null;
        await store.save(item);
      } on ApiException catch (exception) {
        item.retryCount += 1;
        item.lastError = exception.message;
        await store.save(item);
      }
    }
    state = await store.all();
  }
}

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});
  @override
  ConsumerState<LoginScreen> createState() => _LoginState();
}

class _LoginState extends ConsumerState<LoginScreen> {
  final email = TextEditingController();
  final password = TextEditingController();
  bool loading = false;
  String? error;

  Future<void> signIn() async {
    setState(() {
      loading = true;
      error = null;
    });
    if (!mounted) return;
    if (email.text.trim().isEmpty || password.text.isEmpty) {
      setState(() {
        loading = false;
        error = 'Enter your email and password.';
      });
      return;
    }
    try {
      await ref
          .read(apiClientProvider)
          .loginAndVerify(email.text.trim(), password.text);
      if (mounted) context.go('/home');
    } on ApiException catch (exception) {
      if (mounted) {
        setState(() {
          loading = false;
          error = exception.statusCode == 401
              ? 'Invalid email or password. Verify the backend account and password.'
              : exception.message;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(28),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 440),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 58,
                  height: 58,
                  decoration: BoxDecoration(
                    color: teal,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Icon(
                    Icons.fact_check_outlined,
                    color: Colors.white,
                    size: 32,
                  ),
                ),
                const SizedBox(height: 30),
                Text(
                  'LabelSetu',
                  style: Theme.of(context).textTheme.displaySmall
                      ?.copyWith(fontWeight: FontWeight.w800, color: ink),
                ),
                const SizedBox(height: 8),
                Text(
                  'Field inspection client',
                  style: Theme.of(context).textTheme.titleMedium
                      ?.copyWith(color: Colors.black54),
                ),
                const SizedBox(height: 42),
                Text(
                  'Inspector sign in',
                  style: Theme.of(context).textTheme.headlineSmall
                      ?.copyWith(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 20),
                TextField(
                  controller: email,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    prefixIcon: Icon(Icons.alternate_email),
                  ),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: password,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Password',
                    prefixIcon: Icon(Icons.lock_outline),
                  ),
                ),
                if (error != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 14),
                    child: Text(
                      error!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 54,
                  child: FilledButton(
                    onPressed: loading ? null : signIn,
                    child: loading
                        ? const SizedBox(
                            width: 22,
                            height: 22,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Text('Sign in'),
                  ),
                ),
                const SizedBox(height: 18),
                const Text(
                  'Sign in uses the LabelSetu API. Captures can still be saved offline.',
                  style: TextStyle(color: Colors.black54),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}

class Shell extends ConsumerWidget {
  const Shell({required this.title, required this.body, super.key});
  final String title;
  final Widget body;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final online = ref.watch(onlineProvider).value ?? true;
    final selected = title == 'Home'
        ? 0
        : title == 'History'
        ? 3
        : title == 'Pending sync'
        ? 2
        : 1;
    return Scaffold(
      appBar: AppBar(
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
      ),
      body: body,
      bottomNavigationBar: NavigationBar(
        selectedIndex: selected,
        onDestinationSelected: (index) {
          if (index == 0) context.go('/home');
          if (index == 1) context.go('/new');
          if (index == 2) context.go('/queue');
          if (index == 3) context.go('/history');
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.add_circle_outline),
            label: 'New',
          ),
          NavigationDestination(
            icon: Icon(Icons.sync_outlined),
            label: 'Pending',
          ),
          NavigationDestination(icon: Icon(Icons.history), label: 'History'),
        ],
      ),
      persistentFooterButtons: [
        Row(
          children: [
            Icon(
              Icons.circle,
              size: 12,
              color: online ? Colors.green : Colors.orange,
            ),
            const SizedBox(width: 8),
            Text(
              online ? 'Online' : 'Offline',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ],
        ),
      ],
    );
  }
}

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final items = ref.watch(inspectionsProvider);
    return Shell(
      title: 'Home',
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 20),
        children: [
          Text(
            'Field inspection',
            style: Theme.of(context).textTheme.headlineMedium
                ?.copyWith(fontWeight: FontWeight.w800, color: ink),
          ),
          const SizedBox(height: 6),
          const Text(
            'Capture reliable evidence, even without connectivity.',
            style: TextStyle(color: Colors.black54),
          ),
          const SizedBox(height: 26),
          ActionCard(
            title: 'New inspection',
            subtitle: 'Start a product or shelf capture',
            onTap: () => context.go('/new'),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              MetricCard(
                label: 'Pending sync',
                value: '${items.where((i) => i.status != 'complete').length}',
                icon: Icons.sync_outlined,
              ),
              const SizedBox(width: 12),
              MetricCard(
                label: 'Completed',
                value: '${items.where((i) => i.status == 'complete').length}',
                icon: Icons.check_circle_outline,
              ),
            ],
          ),
          const SizedBox(height: 26),
          Text(
            'Today’s activity',
            style: Theme.of(context).textTheme.titleLarge
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 12),
          if (items.isEmpty)
            const EmptyState()
          else
            ...items.take(3).map((item) => InspectionTile(item: item)),
        ],
      ),
    );
  }
}

class ActionCard extends StatelessWidget {
  const ActionCard({
    required this.title,
    required this.subtitle,
    required this.onTap,
    super.key,
  });
  final String title, subtitle;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Card(
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            const CircleAvatar(
              radius: 26,
              backgroundColor: teal,
              child: Icon(Icons.add_a_photo_outlined, color: Colors.white),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(subtitle, style: const TextStyle(color: Colors.black54)),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios, size: 18),
          ],
        ),
      ),
    ),
  );
}

class MetricCard extends StatelessWidget {
  const MetricCard({
    required this.label,
    required this.value,
    required this.icon,
    super.key,
  });
  final String label, value;
  final IconData icon;
  @override
  Widget build(BuildContext context) => Expanded(
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: teal),
            const SizedBox(height: 12),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineMedium
                  ?.copyWith(fontWeight: FontWeight.w800),
            ),
            Text(label, style: const TextStyle(color: Colors.black54)),
          ],
        ),
      ),
    ),
  );
}

class EmptyState extends StatelessWidget {
  const EmptyState({super.key});
  @override
  Widget build(BuildContext context) => const Card(
    child: Padding(
      padding: EdgeInsets.all(24),
      child: Column(
        children: [
          Icon(Icons.assignment_outlined, size: 40, color: teal),
          SizedBox(height: 10),
          Text('No inspections yet'),
          SizedBox(height: 4),
          Text(
            'Your saved evidence will appear here.',
            style: TextStyle(color: Colors.black54),
          ),
        ],
      ),
    ),
  );
}

class StatusBadge extends StatelessWidget {
  const StatusBadge({required this.text, super.key});
  final String text;
  @override
  Widget build(BuildContext context) => Chip(
    label: Text(text == 'draft' ? 'Saved offline' : text),
    visualDensity: VisualDensity.compact,
    side: BorderSide.none,
    backgroundColor: const Color(0xFFE5F2EF),
  );
}

class InspectionTile extends StatelessWidget {
  const InspectionTile({required this.item, super.key});
  final Inspection item;
  @override
  Widget build(BuildContext context) => Card(
    child: ListTile(
      leading: const CircleAvatar(
        backgroundColor: Color(0xFFE0F1EF),
        child: Icon(Icons.description_outlined, color: teal),
      ),
      title: Text(
        item.type == 'batch' ? 'Batch / shelf scan' : 'Single product',
      ),
      subtitle: Text(item.id.substring(0, 8).toUpperCase()),
      trailing: StatusBadge(text: item.status),
    ),
  );
}

class InspectionTypeScreen extends ConsumerWidget {
  const InspectionTypeScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) => Shell(
    title: 'New inspection',
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          'What are you capturing?',
          style: Theme.of(context).textTheme.headlineSmall
              ?.copyWith(fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 8),
        const Text(
          'Choose the evidence type. Product detection happens later on the backend.',
        ),
        const SizedBox(height: 24),
        ChoiceCard(
          icon: Icons.inventory_2_outlined,
          title: 'Single product',
          text: 'Capture one complete product label.',
          onTap: () => begin(context, ref, 'single'),
        ),
        const SizedBox(height: 14),
        ChoiceCard(
          icon: Icons.view_module_outlined,
          title: 'Batch / shelf scan',
          text: 'Capture an entire shelf or display with multiple products.',
          onTap: () => begin(context, ref, 'batch'),
        ),
      ],
    ),
  );
  void begin(BuildContext context, WidgetRef ref, String type) async {
    await ref.read(inspectionsProvider.notifier).create(type);
    if (context.mounted) context.go('/guidance/$type');
  }
}

class ChoiceCard extends StatelessWidget {
  const ChoiceCard({
    required this.icon,
    required this.title,
    required this.text,
    required this.onTap,
    super.key,
  });
  final IconData icon;
  final String title, text;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Card(
    child: InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Icon(icon, size: 32, color: teal),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(text),
                ],
              ),
            ),
            const Icon(Icons.chevron_right),
          ],
        ),
      ),
    ),
  );
}

class GuidanceScreen extends StatelessWidget {
  const GuidanceScreen({required this.type, super.key});
  final String type;
  @override
  Widget build(BuildContext context) {
    final batch = type == 'batch';
    final tips = batch
        ? [
            'Keep products visible',
            'Avoid severe overlap',
            'Keep camera steady',
            'Capture enough resolution',
          ]
        : [
            'Keep package inside frame',
            'Keep text readable',
            'Avoid glare',
            'Keep camera steady',
            'Use calibration reference when required',
          ];
    return Scaffold(
      appBar: AppBar(title: const Text('Capture guidance')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Icon(
            batch ? Icons.view_module_outlined : Icons.inventory_2_outlined,
            size: 52,
            color: teal,
          ),
          const SizedBox(height: 18),
          Text(
            batch
                ? 'Capture the complete shelf/display'
                : 'Capture the complete product label',
            style: Theme.of(context).textTheme.headlineSmall
                ?.copyWith(fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 22),
          ...tips.map(
            (tip) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: teal),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(tip, style: const TextStyle(fontSize: 16)),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 26),
          SizedBox(
            height: 54,
            child: FilledButton.icon(
              onPressed: () => context.go('/camera/$type'),
              icon: const Icon(Icons.camera_alt_outlined),
              label: const Text('Open camera'),
            ),
          ),
        ],
      ),
    );
  }
}

class CaptureScreen extends StatefulWidget {
  const CaptureScreen({required this.type, super.key});
  final String type;
  @override
  State<CaptureScreen> createState() => _CaptureState();
}

class _CaptureState extends State<CaptureScreen> {
  CameraController? controller;
  String? error;
  bool flash = false;

  @override
  void initState() {
    super.initState();
    open();
  }

  Future<void> open() async {
    final permission = await Permission.camera.request();
    if (!permission.isGranted) {
      setState(
        () => error = 'Camera permission is required to capture evidence.',
      );
      return;
    }
    try {
      final cameras = await availableCameras();
      final rear = cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );
      final camera = CameraController(
        rear,
        ResolutionPreset.max,
        enableAudio: false,
      );
      await camera.initialize();
      if (mounted) setState(() => controller = camera);
    } catch (_) {
      if (mounted) setState(() => error = 'Unable to open the camera.');
    }
  }

  Future<void> take() async {
    final image = await controller!.takePicture();
    if (mounted) context.go('/preview', extra: image.path);
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (error != null)
      return Scaffold(
        appBar: AppBar(title: const Text('Camera')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(28),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.no_photography_outlined, size: 54),
                const SizedBox(height: 16),
                Text(error!, textAlign: TextAlign.center),
                const SizedBox(height: 20),
                FilledButton(
                  onPressed: context.pop,
                  child: const Text('Go back'),
                ),
              ],
            ),
          ),
        ),
      );
    if (controller == null || !controller!.value.isInitialized)
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        title: Text(
          widget.type == 'batch' ? 'Shelf capture' : 'Product capture',
        ),
        actions: [
          IconButton(
            tooltip: 'Toggle flash',
            onPressed: () async {
              flash = !flash;
              await controller!.setFlashMode(
                flash ? FlashMode.torch : FlashMode.off,
              );
              setState(() {});
            },
            icon: Icon(flash ? Icons.flash_on : Icons.flash_off),
          ),
        ],
      ),
      body: Stack(
        fit: StackFit.expand,
        children: [
          CameraPreview(controller!),
          Center(
            child: Container(
              width: MediaQuery.sizeOf(context).width * .82,
              height: MediaQuery.sizeOf(context).height * .55,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.white, width: 2),
                borderRadius: BorderRadius.circular(14),
              ),
            ),
          ),
          Align(
            alignment: Alignment.bottomCenter,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 30),
              child: FloatingActionButton.large(
                backgroundColor: Colors.white,
                foregroundColor: teal,
                onPressed: take,
                child: const Icon(Icons.camera_alt),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class PreviewScreen extends ConsumerStatefulWidget {
  const PreviewScreen({required this.imagePath, super.key});
  final String imagePath;

  @override
  ConsumerState<PreviewScreen> createState() => _PreviewScreenState();
}

class _PreviewScreenState extends ConsumerState<PreviewScreen> {
  bool uploading = false;

  Future<void> _directAnalyzeAndUpload() async {
    setState(() => uploading = true);
    final items = ref.read(inspectionsProvider);
    if (items.isEmpty) return;
    final item = items.first;
    item.captureTime = DateTime.now();

    try {
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.always ||
          permission == LocationPermission.whileInUse) {
        final position = await Geolocator.getCurrentPosition();
        item.latitude = position.latitude;
        item.longitude = position.longitude;
        item.accuracy = position.accuracy;
      }
    } catch (_) {}

    await ref.read(inspectionsProvider.notifier).update(item);

    try {
      final api = ref.read(apiClientProvider);
      if (item.type == 'batch') {
        final session = await api.createSession({
          'session_name': 'Shelf Inspection ${DateTime.now().toLocal().toString().split(".")[0]}',
          'location': 'Mobile Inspection Site',
          'client_session_id': item.id,
          'idempotency_key': item.key,
          'latitude': item.latitude,
          'longitude': item.longitude,
          'gps_accuracy': item.accuracy,
          'metadata_json': {'source': 'mobile_direct_capture'},
        });
        item.remoteId = session['id'] as String?;
        await api.uploadSessionImage(
          item.remoteId!,
          item.imagePath!,
          latitude: item.latitude,
          longitude: item.longitude,
        );
        item.status = 'completed';
      } else {
        final inspection = await api.createInspection({
          'title': 'Product Inspection - ${DateTime.now().toLocal().toString().split(".")[0]}',
          'product_name': 'Packaged Commodity',
          'product_category': 'Packaged Goods',
          'market_location': 'Retail Store',
          'metadata_json': {
            'client_inspection_id': item.id,
            'idempotency_key': item.key,
            'inspection_type': item.type,
            'capture_time': item.captureTime?.toIso8601String(),
            'latitude': item.latitude,
            'longitude': item.longitude,
            'gps_accuracy': item.accuracy,
          },
        });
        item.remoteId = inspection['id'] as String?;
        final job = await api.uploadInspectionImage(
          item.remoteId!,
          item.imagePath!,
          latitude: item.latitude,
          longitude: item.longitude,
        );
        item.jobId = job['id'] as String?;
        item.status = job['status'] as String? ?? 'completed';
      }
      await ref.read(inspectionsProvider.notifier).update(item);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            backgroundColor: Color(0xFF0F766E),
            content: Text('✅ Analyzed & Stored live on website!'),
          ),
        );
        context.go('/queue');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: Colors.red.shade700,
            content: Text('Upload error: $e'),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => uploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final file = File(widget.imagePath);
    return Scaffold(
      appBar: AppBar(title: const Text('Review & Analyze')),
      body: Stack(
        children: [
          Column(
            children: [
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(14),
                    child: Image.file(
                      file,
                      fit: BoxFit.contain,
                      width: double.infinity,
                    ),
                  ),
                ),
              ),
              FutureBuilder<int>(
                future: file.length(),
                builder: (_, snapshot) => Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Captured Evidence'),
                      Text(
                        snapshot.hasData
                            ? '${(snapshot.data! / 1024).round()} KB'
                            : 'Reading file...',
                      ),
                    ],
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    Expanded(
                      flex: 1,
                      child: OutlinedButton.icon(
                        onPressed: uploading ? null : context.pop,
                        icon: const Icon(Icons.refresh),
                        label: const Text('Retake'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      flex: 2,
                      child: FilledButton.icon(
                        style: FilledButton.styleFrom(
                          backgroundColor: const Color(0xFF0F766E),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        onPressed: uploading ? null : _directAnalyzeAndUpload,
                        icon: uploading
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Icon(Icons.cloud_upload),
                        label: Text(
                          uploading ? 'Analyzing...' : 'Analyze & Store on Web',
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (uploading)
            Container(
              color: Colors.black54,
              child: const Center(
                child: Card(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 16),
                        Text(
                          'Analyzing Label with AI...',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        SizedBox(height: 6),
                        Text('Syncing results to live website'),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class CalibrationScreen extends ConsumerStatefulWidget {
  const CalibrationScreen({super.key});
  @override
  ConsumerState<CalibrationScreen> createState() => _CalibrationState();
}

class _CalibrationState extends ConsumerState<CalibrationScreen> {
  String method = 'No calibration';
  final width = TextEditingController();
  final height = TextEditingController();
  bool saving = false;
  Future<void> save() async {
    setState(() => saving = true);
    final items = ref.read(inspectionsProvider);
    if (items.isEmpty) return;
    final item = items.first;
    item.calibration =
        '$method${method == 'Manual package dimension' ? ' (${width.text} mm x ${height.text} mm)' : ''}';
    item.captureTime = DateTime.now();
    try {
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied)
        permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.always ||
          permission == LocationPermission.whileInUse) {
        final position = await Geolocator.getCurrentPosition();
        item.latitude = position.latitude;
        item.longitude = position.longitude;
        item.accuracy = position.accuracy;
      } else {
        item.lastError = 'GPS permission denied';
      }
    } catch (_) {
      item.lastError = 'GPS unavailable';
    }
    await ref.read(inspectionsProvider.notifier).update(item);
    var message = 'Uploading & analyzing...';
    if (item.imagePath != null) {
      try {
        final api = ref.read(apiClientProvider);
        if (item.type == 'batch') {
          final session = await api.createSession({
            'session_name': 'Shelf Inspection ${DateTime.now().toLocal().toString().split(".")[0]}',
            'location': 'Mobile Inspection Site',
            'client_session_id': item.id,
            'idempotency_key': item.key,
            'latitude': item.latitude,
            'longitude': item.longitude,
            'gps_accuracy': item.accuracy,
            'metadata_json': {'calibration': item.calibration},
          });
          item.remoteId = session['id'] as String?;
          await api.uploadSessionImage(
            item.remoteId!,
            item.imagePath!,
            latitude: item.latitude,
            longitude: item.longitude,
          );
          item.status = 'completed';
        } else {
          final inspection = await api.createInspection({
            'title': 'Product Inspection - ${DateTime.now().toLocal().toString().split(".")[0]}',
            'product_name': 'Packaged Commodity',
            'product_category': 'Packaged Goods',
            'market_location': 'Retail Store',
            'metadata_json': {
              'client_inspection_id': item.id,
              'idempotency_key': item.key,
              'inspection_type': item.type,
              'capture_time': item.captureTime?.toIso8601String(),
              'latitude': item.latitude,
              'longitude': item.longitude,
              'gps_accuracy': item.accuracy,
              'calibration': item.calibration,
            },
          });
          item.remoteId = inspection['id'] as String?;
          final job = await api.uploadInspectionImage(
            item.remoteId!,
            item.imagePath!,
            latitude: item.latitude,
            longitude: item.longitude,
          );
          item.jobId = job['id'] as String?;
          item.status = job['status'] as String? ?? 'completed';
        }
        await ref.read(inspectionsProvider.notifier).update(item);
        message = 'Analyzed & Uploaded directly to website!';
      } on ApiException catch (exception) {
        item.lastError = exception.message;
        item.retryCount += 1;
        await ref.read(inspectionsProvider.notifier).update(item);
        message = 'Upload failed: ${exception.message}';
      } catch (e) {
        item.lastError = e.toString();
        await ref.read(inspectionsProvider.notifier).update(item);
        message = 'Error connecting to backend: $e';
      }
    }
    if (mounted) {
      setState(() => saving = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      context.go('/queue');
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Calibration metadata')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text(
          'Record a reference for backend measurement. No measurements or compliance decisions are made on the device.',
        ),
        const SizedBox(height: 20),
        DropdownButtonFormField<String>(
          initialValue: method,
          decoration: const InputDecoration(labelText: 'Reference method'),
          items:
              const [
                    '50 mm ArUco reference',
                    'QR / reference',
                    'Known reference',
                    'Manual package dimension',
                    'No calibration',
                  ]
                  .map(
                    (item) => DropdownMenuItem(value: item, child: Text(item)),
                  )
                  .toList(),
          onChanged: (value) => setState(() => method = value!),
        ),
        if (method == 'Manual package dimension')
          Padding(
            padding: const EdgeInsets.only(top: 14),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: width,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Width (mm)'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: height,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Height (mm)'),
                  ),
                ),
              ],
            ),
          ),
        const SizedBox(height: 24),
        const Card(
          child: ListTile(
            leading: Icon(Icons.location_on_outlined, color: teal),
            title: Text('GPS and capture time'),
            subtitle: Text(
              'Location is requested at save time and is never invented.',
            ),
          ),
        ),
        const SizedBox(height: 24),
        SizedBox(
          height: 54,
          child: FilledButton(
            onPressed: saving ? null : save,
            child: saving
                ? const CircularProgressIndicator(color: Colors.white)
                : const Text('Save inspection'),
          ),
        ),
      ],
    ),
  );
}

class QueueScreen extends ConsumerStatefulWidget {
  const QueueScreen({super.key});
  @override
  ConsumerState<QueueScreen> createState() => _QueueState();
}

class _QueueState extends ConsumerState<QueueScreen> {
  @override
  void initState() {
    super.initState();
    Future<void>.microtask(
      () async {
        await ref.read(inspectionsProvider.notifier).syncQueued();
        await ref.read(inspectionsProvider.notifier).refreshProcessing();
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final items = ref.watch(inspectionsProvider);
    return Shell(
      title: 'Pending sync',
      body: items.isEmpty
          ? const EmptyState()
          : ListView(
              padding: const EdgeInsets.all(20),
              children: items
                  .map(
                    (item) => Card(
                      child: ListTile(
                        title: Text(item.id.substring(0, 8).toUpperCase()),
                        subtitle: Text(
                          '${item.createdAt.toLocal()}\n${item.status == 'draft' ? 'Waiting for network' : item.status}',
                        ),
                        isThreeLine: true,
                        trailing: StatusBadge(text: item.status),
                      ),
                    ),
                  )
                  .toList(),
            ),
    );
  }
}

class HistoryScreen extends ConsumerStatefulWidget {
  const HistoryScreen({super.key});
  @override
  ConsumerState<HistoryScreen> createState() => _HistoryState();
}

class _HistoryState extends ConsumerState<HistoryScreen> {
  late final Future<List<Map<String, dynamic>>> history;

  @override
  void initState() {
    super.initState();
    history = ref.read(apiClientProvider).inspections();
  }

  @override
  Widget build(BuildContext context) => Shell(
    title: 'History',
    body: FutureBuilder<List<Map<String, dynamic>>>(
      future: history,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        final remoteItems = snapshot.data ?? const <Map<String, dynamic>>[];
        if (remoteItems.isEmpty) return const EmptyState();
        return ListView(
          padding: const EdgeInsets.all(20),
          children: remoteItems.map((item) => Card(
            child: ListTile(
              title: Text(item['inspection_number'] as String? ?? 'Inspection'),
              subtitle: Text(
                '${item['created_at'] ?? ''}\n${item['product_name'] ?? 'Product pending'}',
              ),
              isThreeLine: true,
              trailing: StatusBadge(text: item['status'] as String? ?? 'unknown'),
            ),
          )).toList(),
        );
      },
    ),
  );
}
