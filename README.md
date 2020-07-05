# ドローンエンジニア養成塾第 9 期 課題

## draw_circle.py

縦方向もしくは水平方向に円を描くスクリプト。

--connect 接続文字列
--horizontal true 水平方向に円を描く

実行方法:

```bash
$ ./draw_circle.py --connect 127.0.0.1:14551
```

参考: DroneKit Python mission_basic.py

## mission_import_autopilot.py

指定された URL のミッションを実行するスクリプト。
DroneKit Python の mission_import_export.py を追加・修正して --url, --file オプションを追加。

--url mission_waipoints_url     指定された URL からミッションファイルをダウンロードし実行
--file mission_waipoints_file   指定されたミッションファイルを実行

準備:

```bash
$ pip2 install requests # モジュールインストール
$ sim_vehicle.py -v ArduCopter --custom-location=35.68407150,139.75523470,17,353 --map # SITL 起動
```

実行方法:

```bash
$ ./mission_import_autopilot.py --connect 127.0.0.1:14551
```
