# これは何か?

デジタルカメラ用のFTPサーバーです。

デジタルカメラには撮影したファイルをFTPでサーバーにアップロードする機能があるものがありますが、そのための超簡単なFTPサーバーです。  
ソニーのαシリーズでの動作を確認しています。  
通常のFTPサーバーとは異なり、直前に受信した写真のプレビュー画像を表示します。

# つかいかた

pyftpdlib, pillow, pillow-heifを使用しているので、pipでインストールしてください。  
PhotoFtpServer.iniを適当なテキストエディタで開き、  
・受信した写真を保存するフォルダー  
・サーバーのIPアドレス  
・サーバーのポート番号  
・FTPでログインする時のユーザー名  
・そのパスワード  
を記載し、main.pyを実行してください。



