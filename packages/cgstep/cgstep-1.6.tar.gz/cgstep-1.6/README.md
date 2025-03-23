## 概要
Indoor Corgi製Raspberry Pi用 高機能ステッピングモータードライバー基板RPZ-Stepper、
および搭載モータードライバーIC TMC5240を制御するソフトウェアです。
Pythonパッケージを使うことでご自身のプログラムからモーターを制御できるほか、
コマンドでの操作も可能です。

## 必要環境
ハードウェア: 40ピン端子を持つRaspberry Piシリーズ \
OS: Raspberry Pi OS (SPI有効化) \
拡張基板: [RPZ-Stepper](https://www.indoorcorgielec.com/products/rpz-stepper/) (Raspberry Pi用 高機能ステッピングモータードライバー)

## インストール
以下のコマンドでインストール/アップグレードできます。

`sudo python3 -m pip install -U cgstep --break-system-packages`

## 使い方
使い方は、以下の解説記事と[TMC5240データシート](https://www.analog.com/en/products/tmc5240.html)をご参照下さい。

- [RPZ-Stepper使い方記事一覧](https://www.indoorcorgielec.com/products/rpz-stepper#usage)