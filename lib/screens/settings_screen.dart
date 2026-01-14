import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 通知設定画面
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  // 通知対象路線の設定
  final Map<String, Map<String, bool>> _selectedLines = {
    'JR西日本': {
      '京都線': true,
      '奈良線': true,
      '嵯峨野線': true,
      '湖西線': true,
      '学研都市線': true,
    },
    '京阪電車': {
      '本線': true,
    },
    '近畿日本鉄道': {
      '京都線': true,
    },
    '阪急電車': {
      '京都線': true,
    },
    '京都市営地下鉄': {
      '烏丸線': true,
      '東西線': true,
    },
  };

  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  /// 設定を読み込み
  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    
    setState(() {
      for (final company in _selectedLines.keys) {
        for (final line in _selectedLines[company]!.keys) {
          final key = 'notify_${company}_$line';
          _selectedLines[company]![line] = prefs.getBool(key) ?? true;
        }
      }
      _isLoading = false;
    });
  }

  /// 設定を保存
  Future<void> _saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    
    for (final company in _selectedLines.keys) {
      for (final line in _selectedLines[company]!.keys) {
        final key = 'notify_${company}_$line';
        await prefs.setBool(key, _selectedLines[company]![line]!);
      }
    }
    
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('設定を保存しました'),
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  /// 路線の通知設定を切り替え
  void _toggleLine(String company, String line) {
    setState(() {
      _selectedLines[company]![line] = !_selectedLines[company]![line]!;
    });
    _saveSettings();
  }

  /// 会社ごとの全路線を切り替え
  void _toggleCompany(String company, bool value) {
    setState(() {
      for (final line in _selectedLines[company]!.keys) {
        _selectedLines[company]![line] = value;
      }
    });
    _saveSettings();
  }

  /// 会社カラーを取得
  Color _getCompanyColor(String company) {
    switch (company) {
      case '京阪電車':
        return const Color(0xFF006837);
      case 'JR西日本':
        return const Color(0xFF0066B3);
      case '近畿日本鉄道':
        return const Color(0xFFE60012);
      case '阪急電車':
        return const Color(0xFF8B0000);
      case '京都市営地下鉄':
        return const Color(0xFF008000);
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('通知設定'),
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // 説明テキスト
          Card(
            color: Colors.blue[50],
            child: const Padding(
              padding: EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.blue),
                      SizedBox(width: 8),
                      Text(
                        '通知する路線を選択',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 8),
                  Text(
                    'チェックした路線で遅延・運転見合わせが発生した場合に通知します。',
                    style: TextStyle(fontSize: 14),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 路線選択リスト
          ..._selectedLines.entries.map((companyEntry) {
            final company = companyEntry.key;
            final lines = companyEntry.value;
            final allSelected = lines.values.every((v) => v);

            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: ExpansionTile(
                leading: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: _getCompanyColor(company).withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.train,
                    color: _getCompanyColor(company),
                  ),
                ),
                title: Text(
                  company,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                subtitle: Text(
                  '${lines.values.where((v) => v).length}/${lines.length}路線',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
                trailing: Checkbox(
                  value: allSelected,
                  tristate: true,
                  onChanged: (value) {
                    _toggleCompany(company, value ?? true);
                  },
                ),
                children: lines.entries.map((lineEntry) {
                  final line = lineEntry.key;
                  final isSelected = lineEntry.value;

                  return CheckboxListTile(
                    title: Text(line),
                    value: isSelected,
                    onChanged: (value) {
                      _toggleLine(company, line);
                    },
                    contentPadding: const EdgeInsets.symmetric(horizontal: 32),
                  );
                }).toList(),
              ),
            );
          }),
        ],
      ),
    );
  }
}
