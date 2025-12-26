import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/train_info.dart';

/// 列車運行障害時の通知サービス
class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();

  bool _initialized = false;
  Set<String> _notifiedLines = {};

  /// 通知サービスを初期化
  Future<void> initialize() async {
    if (_initialized) return;

    const initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    const initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
    );

    await _notifications.initialize(initializationSettings);
    _initialized = true;

    // 過去に通知済みの路線を読み込み
    await _loadNotifiedLines();
  }

  /// 通知が有効かどうかを確認
  Future<bool> isNotificationEnabled() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool('notification_enabled') ?? true;
  }

  /// 通知の有効/無効を設定
  Future<void> setNotificationEnabled(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('notification_enabled', enabled);

    if (!enabled) {
      // 通知を無効にした場合、通知済み路線をクリア
      _notifiedLines.clear();
      await _saveNotifiedLines();
    }
  }

  /// 運行障害を通知
  Future<void> notifyTrainIssue(TrainInfo trainInfo) async {
    if (!_initialized) return;

    final enabled = await isNotificationEnabled();
    if (!enabled) return;

    // 平常運転の場合は通知しない
    if (trainInfo.isNormal || trainInfo.isError) {
      return;
    }

    // すでに通知済みの場合はスキップ
    final lineKey = '${trainInfo.company}_${trainInfo.line}';
    if (_notifiedLines.contains(lineKey)) {
      return;
    }

    // 通知を送信
    String title = '${trainInfo.company} ${trainInfo.line}';
    String body = trainInfo.status;

    if (trainInfo.hasDelay) {
      body += ' (約${trainInfo.delayMinutes}分遅れ)';
    }

    const androidDetails = AndroidNotificationDetails(
      'train_alert_channel',
      '列車運行通知',
      channelDescription: '列車運行に乱れが発生した際の通知',
      importance: Importance.high,
      priority: Priority.high,
    );

    const notificationDetails = NotificationDetails(android: androidDetails);

    await _notifications.show(
      lineKey.hashCode,
      title,
      body,
      notificationDetails,
    );

    // 通知済みとして記録
    _notifiedLines.add(lineKey);
    await _saveNotifiedLines();
  }

  /// 運行が正常に戻った場合、通知済み状態をリセット
  void resetNotification(TrainInfo trainInfo) {
    if (trainInfo.isNormal) {
      final lineKey = '${trainInfo.company}_${trainInfo.line}';
      _notifiedLines.remove(lineKey);
      _saveNotifiedLines();
    }
  }

  /// 通知済み路線を保存
  Future<void> _saveNotifiedLines() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList('notified_lines', _notifiedLines.toList());
  }

  /// 通知済み路線を読み込み
  Future<void> _loadNotifiedLines() async {
    final prefs = await SharedPreferences.getInstance();
    final lines = prefs.getStringList('notified_lines') ?? [];
    _notifiedLines = lines.toSet();
  }

  /// すべての通知をクリア
  Future<void> clearAllNotifications() async {
    _notifiedLines.clear();
    await _saveNotifiedLines();
  }
}
