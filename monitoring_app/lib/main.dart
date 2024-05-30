import 'dart:async';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '구멍가공 모니터링',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: '구멍가공 모니터링'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _counter = 0;
  late Timer _timer;
  String latest_key = '1';
  String elapsed_time = '00:00';
  String current_state = '시작 전';
  DatabaseReference databaseReference = FirebaseDatabase.instance.ref('/');
  DatabaseReference ref = FirebaseDatabase.instance.ref();

  void _connectToDatabase() {
    FirebaseDatabase database = FirebaseDatabase.instance;
    _timer = Timer.periodic(Duration(seconds: 1), (timer) {
      setState(() {
        databaseReference.onValue.listen((DatabaseEvent event) {
          final data = event.snapshot.value as Map<dynamic, dynamic>;
          List<dynamic> sortedKeys = data.keys.toList()..sort();
          latest_key = sortedKeys.last;
          elapsed_time = data[latest_key]['경과된 시간'];
          current_state = data[latest_key]['현 상태'];
        });
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Row(
              children: [
                const Text(
                  '경과 시간:',
                  style: TextStyle(fontSize: 24),
                ),
                Text(
                  elapsed_time,
                  style: TextStyle(fontSize: 24),
                ),
              ],
              mainAxisAlignment: MainAxisAlignment.center,
            ),
            Row(
              children: [
                Text(
                  '현재 상태: ',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                Text(
                  current_state,
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
              ],
              mainAxisAlignment: MainAxisAlignment.center,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _connectToDatabase,
        tooltip: 'Increment',
        child: const Icon(Icons.connect_without_contact),
      ),
    );
  }
}
