import optuna
import subprocess
import re
import sys

# a.outが受け取るパラメータ名を指定してください。
# 例: "./a.out --start-temp 10000 --end-temp 10" のように引数名が必要な場合
# PARAM_NAMES = ["--start-temp", "--end-temp"]
# 例: "./a.out 10000 10" のように値だけを渡す場合
PARAM_NAMES = []

def objective(trial):
    """Optunaの目的関数です。test4tune.pyを実行し、スコアを返します。"""

    # --- パラメータの探索範囲を指定してください ---
    # 例: trial.suggest_float("パラメータ名", 最小値, 最大値, log=True)
    # a.outの仕様に合わせて、パラメータ名、範囲、型（float or int）を調整してください。
    start_temp = trial.suggest_float("start_temp", 1e3, 1e5, log=True)
    end_temp = trial.suggest_float("end_temp", 1e-1, 1e2, log=True)
    # -----------------------------------------

    # test4tune.pyに渡すコマンドライン引数を作成
    args = []
    if PARAM_NAMES:
        # 引数名と値をペアで渡す場合
        params = {
            "start_temp": start_temp,
            "end_temp": end_temp,
        }
        # PARAM_NAMESの順番通りに引数を構成
        for name in PARAM_NAMES:
            param_key = name.lstrip('-')
            if param_key in params:
                args.extend([name, str(params[param_key])])
    else:
        # 値だけを渡す場合
        args = [str(start_temp), str(end_temp)]

    try:
        # test4tune.py を実行
        command = ["python", "test4tune.py"] + args
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True  # これで戻り値が0以外の場合にCalledProcessErrorを発生させる
        )
    except subprocess.CalledProcessError as e:
        # 実行エラーが発生した場合、エラー内容を出力してtrialを枝刈り
        print(f"Error occurred while running test4tune.py with args: {args}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        raise optuna.TrialPruned()

    # 出力から合計スコアを抽出
    output = result.stdout
    match = re.search(r"sum score\s*:\s*([\d,]+)\s*pt", output)

    if match:
        score_str = match.group(1).replace(",", "")
        score = float(score_str)
        return score
    else:
        # スコアが見つからない場合はエラーとして扱い、trialを枝刈り
        print("Could not find score in the output.", file=sys.stderr)
        print(output, file=sys.stderr)
        raise optuna.TrialPruned()

if __name__ == "__main__":
    study_name = "ahc-param-tuner-study"
    storage = "sqlite:///ahc-param-tuner.db"

    # コマンドライン引数を確認
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        try:
            optuna.delete_study(study_name=study_name, storage=storage)
            print(f"Study '{study_name}' has been deleted.")
        except KeyError:
            print(f"Study '{study_name}' not found.")
        sys.exit()

    # OptunaのStudyオブジェクトを作成
    # SQLiteを使って探索結果を永続化すると、中断・再開が容易になります
    study = optuna.create_study(
        study_name=study_name,
        storage=storage,
        load_if_exists=True,
        direction="maximize"
    )

    # 最適化を実行
    # n_trialsは試行回数です。必要に応じて調整してください。
    try:
        study.optimize(objective, n_trials=100)
    except KeyboardInterrupt:
        print("Optimization stopped by user.")


    # 結果の表示
    print("\n" + "="*30)
    print("Optimization Finished")
    print(f"Number of finished trials: {len(study.trials)}")

    print("Best trial:")
    best_trial = study.best_trial
    print(f"  Value: {best_trial.value:,.2f}")

    print("  Params: ")
    for key, value in best_trial.params.items():
        print(f"    {key}: {value}")

    # 全てのtrialの結果をDataFrameで確認
    df = study.trials_dataframe()
    print("\n" + "="*30)
    print("All Trials:")
    print(df)
