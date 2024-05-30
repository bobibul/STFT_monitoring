import 'package:firebase_database/firebase_database.dart';

class DatabaseSvc {
  FirebaseDatabase database = FirebaseDatabase.instance;

  void readDB() {
    DatabaseReference startCountRef = FirebaseDatabase.instance.ref('/');
    startCountRef.onValue.listen((DatabaseEvent event) {
      final data = event.snapshot.value as Map<dynamic, dynamic>;
    });
  }
}
