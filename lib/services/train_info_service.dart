import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../models/train_info.dart';

/// 列車運行情報を取得するAPIサービス
class TrainInfoService {
  // RenderでデプロイしたバックエンドAPIのURL
  static const String _baseUrl = 'https://train-alert.onrender.com';
  
  /// すべての列車運行情報を取得
  Future<List<TrainInfo>> fetchTrainInfo() async {
    try {
      final url = '$_baseUrl/api/train-info';
      if (kDebugMode) {
        debugPrint('API URLにアクセス: $url');
      }
      
      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Accept': 'application/json',
        },
      ).timeout(
        const Duration(seconds: 10),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> jsonData = json.decode(response.body);
        final List<dynamic> data = jsonData['data'] as List<dynamic>;

        if (kDebugMode) {
          debugPrint('API取得成功: ${data.length}件の路線情報');
        }

        return data.map((item) => TrainInfo.fromJson(item)).toList();
      } else {
        if (kDebugMode) {
          debugPrint('APIエラー: ステータスコード ${response.statusCode}');
        }
        throw Exception('運行情報の取得に失敗しました: ${response.statusCode}');
      }
    } catch (e) {
      if (kDebugMode) {
        debugPrint('運行情報取得エラー: $e');
      }
      rethrow;
    }
  }

  /// APIサーバーのヘルスチェック
  Future<bool> checkHealth() async {
    try {
      final url = '$_baseUrl/api/health';
      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Accept': 'application/json',
        },
      ).timeout(
        const Duration(seconds: 5),
      );

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
