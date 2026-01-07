/// 列車運行情報のデータモデル
class TrainInfo {
  final String company;
  final String line;
  final String status;
  final int delayMinutes;
  final String details;
  final DateTime updatedAt;

  TrainInfo({
    required this.company,
    required this.line,
    required this.status,
    required this.delayMinutes,
    required this.details,
    required this.updatedAt,
  });

  /// 各鉄道会社の運行情報ページURLを取得
  String get officialUrl {
    switch (company) {
      case '京阪電車':
        return 'https://www.keihan.co.jp/traffic/information/';
      case 'JR西日本':
        return 'https://trafficinfo.westjr.co.jp/kinki.html';
      case '近畿日本鉄道':
        return 'https://www.kintetsu.jp/unkou/unkou.html';
      default:
        return '';
    }
  }

  /// JSONからTrainInfoオブジェクトを作成
  factory TrainInfo.fromJson(Map<String, dynamic> json) {
    return TrainInfo(
      company: json['company'] as String,
      line: json['line'] as String,
      status: json['status'] as String,
      delayMinutes: json['delay_minutes'] as int,
      details: json['details'] as String,
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  /// TrainInfoオブジェクトをJSONに変換
  Map<String, dynamic> toJson() {
    return {
      'company': company,
      'line': line,
      'status': status,
      'delay_minutes': delayMinutes,
      'details': details,
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// 運行状況が正常かどうか
  bool get isNormal => status == '平常運転';

  /// 遅延があるかどうか
  bool get hasDelay => status == '遅延あり' && delayMinutes > 0;

  /// 運転見合わせかどうか
  bool get isSuspended => status == '運転見合わせ';

  /// エラー状態かどうか
  bool get isError => status == '情報取得エラー';
}
