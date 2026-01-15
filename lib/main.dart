import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const TrainAlertApp());
}

class TrainAlertApp extends StatelessWidget {
  const TrainAlertApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '通学圏鉄道運行情報',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 2,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
