ddns-update
===========
LinuxのPythonで動く簡単なDDNS更新スクリプトです。  
DDNSのサイト毎にプラグインを追加することで多数のDDNSを一度に更新する事ができます。

## 特徴
- pythonで好きにプラグインを書いてどのDDNSサービスでも対応できる
- pythonだから手軽にいじれる(ただしコードが読める人に限る)
- 複数のIPアドレスチェッカーを使える為負荷分散が可能
- IPアドレスが変化していなくても1日に1回のDDNS更新を行う
- セットアップさえしてしまえばDiCEよりも手軽(sasrai談)

## インストール方法
- 好きなディレクトリへ保存 (/home/foo/.ddns_updateなど)
- exampleのddns.cfgを/etcへコピー
- ddns.cfgを適時書き換えの後ddns_update.pyを実行
- DDNSのサイトで更新される事を確認
- cron等で5分おきに実行するようにすれば自動的にDDNSの更新を行います。

## 注意
/var/cache/ddns内へIPアドレスや最終更新日時などの情報がキャッシュされます。  
このキャッシュを削除するとIPアドレスの即時更新を行うことができますが、サービス側であまりに大量の更新が行われた場合にアカウントが制限・削除される事がありますので扱いにはご注意ください。

ライセンス
----------
Code and documentation copyright 2014 sasrai. Code released under [the MIT license](LICENSE). 
