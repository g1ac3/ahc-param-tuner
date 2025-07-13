# AHC Parameter Tuner

AHC（AtCoder Heuristic Contest）などのヒューリスティック系コンテストで用いられる**焼きなまし法（Simulated Annealing）**のパラメタを、**Optuna**を使って自動でチューニングするツールです。

## 🔧 機能
- 焼きなまし法の初期温度や冷却率などのパラメタを自動探索
- AHCのローカルスコア評価を使った目的関数設計が可能
- 繰り返し試行により、ベストスコアを得るパラメタ構成を提案

## 🛠 使用技術
- Python 3.x
- [Optuna](https://optuna.org/)（パラメタチューニングライブラリ）

## 🚀 使い方（例）
下記の記事で詳しく解説しています。<br>
URL：（作成予定）
```bash
git clone https://github.com/g1ac3/ahc-param-tuner.git

python param_tune.py
python param_tune.py reset #reset your study.
```

~~ comming soon ~~
