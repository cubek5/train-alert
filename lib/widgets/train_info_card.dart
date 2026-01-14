import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/train_info.dart';

/// 列車運行情報を表示するカードウィジェット
class TrainInfoCard extends StatelessWidget {
  final TrainInfo trainInfo;

  const TrainInfoCard({
    super.key,
    required this.trainInfo,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 6.0),
      elevation: 2,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(4),
          border: Border(
            left: BorderSide(
              color: _getStatusColor(),
              width: 6,
            ),
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 鉄道会社名と路線名
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: _getCompanyColor(),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      trainInfo.company,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      trainInfo.line,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              // 運行状況
              Row(
                children: [
                  Icon(
                    _getStatusIcon(),
                    color: _getStatusColor(),
                    size: 24,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    trainInfo.status,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: _getStatusColor(),
                    ),
                  ),
                  if (trainInfo.hasDelay) ...[
                    const SizedBox(width: 8),
                    Text(
                      '約${trainInfo.delayMinutes}分遅れ',
                      style: TextStyle(
                        fontSize: 14,
                        color: _getStatusColor(),
                      ),
                    ),
                  ],
                ],
              ),
              // 運転再開見込み時刻（遅延・運転見合わせ時）
              if (trainInfo.resumeTime != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.amber[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.amber),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.schedule, color: Colors.amber, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        '再開見込み: ${trainInfo.resumeTime}',
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              // 詳細情報
              if (trainInfo.detailsWithoutResumeTime.isNotEmpty) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    trainInfo.detailsWithoutResumeTime,
                    style: const TextStyle(fontSize: 14),
                  ),
                ),
              ],
              // 運行障害時のリンクボタン
              if (!trainInfo.isNormal && trainInfo.officialUrl.isNotEmpty) ...[
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () => _launchUrl(trainInfo.officialUrl),
                    icon: const Icon(Icons.open_in_new, size: 18),
                    label: const Text('詳細を確認（公式サイト）'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: _getStatusColor(),
                      side: BorderSide(color: _getStatusColor()),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  /// URLを開く
  Future<void> _launchUrl(String urlString) async {
    final url = Uri.parse(urlString);
    if (await canLaunchUrl(url)) {
      await launchUrl(
        url,
        mode: LaunchMode.externalApplication,
      );
    }
  }

  /// 運行状況に応じた色を取得
  Color _getStatusColor() {
    if (trainInfo.isNormal) {
      return Colors.green;
    } else if (trainInfo.hasDelay) {
      return Colors.orange;
    } else if (trainInfo.isSuspended) {
      return Colors.red;
    } else if (trainInfo.isError) {
      return Colors.grey;
    }
    return Colors.blue;
  }

  /// 運行状況に応じたアイコンを取得
  IconData _getStatusIcon() {
    if (trainInfo.isNormal) {
      return Icons.check_circle;
    } else if (trainInfo.hasDelay) {
      return Icons.warning;
    } else if (trainInfo.isSuspended) {
      return Icons.cancel;
    } else if (trainInfo.isError) {
      return Icons.error_outline;
    }
    return Icons.info;
  }

  /// 鉄道会社に応じた色を取得
  Color _getCompanyColor() {
    switch (trainInfo.company) {
      case '京阪電車':
        return const Color(0xFF006837); // 京阪グリーン
      case 'JR西日本':
        return const Color(0xFF0066B3); // JRブルー
      case '近畿日本鉄道':
        return const Color(0xFFE60012); // 近鉄レッド
      case '阪急電車':
        return const Color(0xFF8B0000); // 阪急マルーン
      case '京都市営地下鉄':
        return const Color(0xFF008000); // 地下鉄グリーン
      default:
        return Colors.blue;
    }
  }
}
