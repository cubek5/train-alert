import 'package:flutter/material.dart';
import 'dart:async';
import '../models/train_info.dart';
import '../services/train_info_service.dart';
import '../services/notification_service.dart';
import '../widgets/train_info_card.dart';
import 'settings_screen.dart' deferred as settings;

/// メイン画面: 列車運行情報一覧
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TrainInfoService _trainInfoService = TrainInfoService();
  final NotificationService _notificationService = NotificationService();

  List<TrainInfo> _trainInfoList = [];
  bool _isLoading = true;
  String? _errorMessage;
  DateTime? _lastUpdateTime;
  Timer? _autoRefreshTimer;
  bool _notificationEnabled = true;
  bool _isFirstLoad = true; // 初回読み込みかどうか
  int _retryCount = 0; // リトライ回数

  @override
  void initState() {
    super.initState();
    _initializeServices();
    _loadTrainInfo();
    _startAutoRefresh();
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    super.dispose();
  }

  /// サービスを初期化
  Future<void> _initializeServices() async {
    await _notificationService.initialize();
    final enabled = await _notificationService.isNotificationEnabled();
    setState(() {
      _notificationEnabled = enabled;
    });
  }

  /// 列車運行情報を読み込み
  Future<void> _loadTrainInfo() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // 初回読み込み時は自動リトライを使用
      final trainInfoList = _isFirstLoad
          ? await _trainInfoService.fetchTrainInfoWithRetry(maxRetries: 3)
          : await _trainInfoService.fetchTrainInfo();
      
      setState(() {
        _trainInfoList = trainInfoList;
        _lastUpdateTime = DateTime.now();
        _isLoading = false;
        _isFirstLoad = false; // 初回読み込み完了
        _retryCount = 0;
      });

      // 運行障害がある場合、通知を送信
      for (var trainInfo in trainInfoList) {
        if (!trainInfo.isNormal && !trainInfo.isError) {
          await _notificationService.notifyTrainIssue(trainInfo);
        } else {
          _notificationService.resetNotification(trainInfo);
        }
      }
    } catch (e) {
      _retryCount++;
      
      // エラーメッセージを詳細に
      String errorMsg;
      if (_isFirstLoad) {
        errorMsg = 'サーバー起動中です...\n'
            '初回アクセス時は1分ほどかかる場合があります\n'
            'しばらくお待ちください';
      } else {
        errorMsg = '運行情報の取得に失敗しました\n'
            'ネットワーク接続を確認してください';
      }
      
      setState(() {
        _errorMessage = errorMsg;
        _isLoading = false;
      });
      
      // 初回読ま込み時のみ、自動リトライ（3回まで）
      if (_isFirstLoad && _retryCount < 3) {
        await Future.delayed(const Duration(seconds: 15));
        if (mounted) {
          _loadTrainInfo();
        }
      }
    }
  }

  /// 自動更新を開始（5分ごと）
  void _startAutoRefresh() {
    _autoRefreshTimer = Timer.periodic(
      const Duration(minutes: 5),
      (timer) {
        _loadTrainInfo();
      },
    );
  }

  /// 通知設定を切り替え
  Future<void> _toggleNotification(bool value) async {
    await _notificationService.setNotificationEnabled(value);
    setState(() {
      _notificationEnabled = value;
    });

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(value ? '通知を有効にしました' : '通知を無効にしました'),
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('列車運行情報'),
        actions: [
          // 通知設定トグル
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8.0),
            child: Row(
              children: [
                Icon(
                  _notificationEnabled ? Icons.notifications : Icons.notifications_off,
                  size: 20,
                ),
                Switch(
                  value: _notificationEnabled,
                  onChanged: _toggleNotification,
                ),
              ],
            ),
          ),
          // 通知設定画面へ（遅延読み込み）
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () async {
              // 設定画面を動的に読み込み
              await settings.loadLibrary();
              if (!mounted) return;
              await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => settings.SettingsScreen(),
                ),
              );
              // 設定画面から戻ってきたら情報を再読み込み
              _loadTrainInfo();
            },
          ),
          // 更新ボタン
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _loadTrainInfo,
          ),
        ],
      ),
      body: SafeArea(
        child: _buildBody(),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _trainInfoList.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 24),
            Text(
              _isFirstLoad
                  ? '運行情報を読み込んでいます...\n初回は少し時間がかかります'
                  : '更新中...',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
            if (_retryCount > 0) ...[
              const SizedBox(height: 12),
              Text(
                '再試行中... ($_retryCount/3)',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[500],
                ),
              ),
            ],
          ],
        ),
      );
    }

    if (_errorMessage != null && _trainInfoList.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              style: const TextStyle(fontSize: 16),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadTrainInfo,
              child: const Text('再試行'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadTrainInfo,
      child: Column(
        children: [
          // 更新時刻表示
          if (_lastUpdateTime != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(8.0),
              color: Colors.grey[200],
              child: Text(
                '最終更新: ${_formatUpdateTime(_lastUpdateTime!)}',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 12),
              ),
            ),
          // 路線別情報一覧
          Expanded(
            child: ListView.builder(
              itemCount: _trainInfoList.length,
              itemBuilder: (context, index) {
                return TrainInfoCard(trainInfo: _trainInfoList[index]);
              },
            ),
          ),
        ],
      ),
    );
  }

  /// 更新時刻をフォーマット
  String _formatUpdateTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}
