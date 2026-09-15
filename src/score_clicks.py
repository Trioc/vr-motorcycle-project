import pandas as pd
import math
from pathlib import Path

# ===== 1. 設定「最外層資料夾」路徑 =====
# 把這行改成你實際放所有受試者資料夾的位置
ROOT_DIR = Path(__file__).resolve().parents[1] / "click_log"

# ===== 2. 每支影片的 hazard onset（秒） =====
HAZARD_ONSETS = {
    1: [3.80],           # video 1: 1 個 hazard
    2: [9.80],           # video 2: 1 個 hazard
    3: [10.85],          # video 3: 1 個 hazard
    4: [5.45, 12.49],    # video 4: 2 個 hazard
    5: [4.00, 9.03],     # video 5: 2 個 hazard
}

# ===== 3. 給分規則：|誤差| 每 0.1 秒少 1 分 =====
def score_from_error(err: float) -> int:
    """
    err: click_time_sec - onset_sec 的誤差（秒，可以為正或負）
    規則：
        |err| <= 0.1  → 20 分
        0.1 < |err| <= 0.2 → 19 分
        0.2 < |err| <= 0.3 → 18 分
        ...
        1.9 < |err| <= 2.0 → 1 分
        |err| > 2.0 → 0 分
    """
    e = abs(err)
    if e == 0:
        return 20

    band = math.ceil(e / 0.1)  # 第幾個 0.1 區間
    score = 21 - band          # band=1→20, band=2→19, ...
    if score < 0:
        score = 0
    return score

# ===== 4. 計算單一影片、單一受試者的 hazard 得分 =====
def compute_scores_for_video(df: pd.DataFrame, video_id: int):
    """
    df: 該受試者 + 該影片的所有 click 記錄
        需要有 'time_sec' 或 'time_ms' 欄位之一定義
    回傳：list，每個 hazard 一個分數（該 hazard 下所有點擊中的最高分）
    """
    # 處理時間欄位
    if "time_sec" in df.columns:
        times = pd.to_numeric(df["time_sec"], errors="coerce").dropna()
    elif "time_ms" in df.columns:
        times = pd.to_numeric(df["time_ms"], errors="coerce").dropna() / 1000.0
    else:
        raise ValueError(f"找不到 'time_sec' 或 'time_ms' 欄位：{df.columns}")

    # 這個受試者這支影片完全沒點 → 所有 hazard 都 0 分
    if times.empty:
        return [0] * len(HAZARD_ONSETS[video_id])

    scores = []
    for onset in HAZARD_ONSETS[video_id]:
        # 對每一個點擊計算誤差 → 算分 → 取最高
        errors = times - onset
        click_scores = errors.apply(score_from_error)
        max_score = int(click_scores.max()) if not click_scores.empty else 0
        scores.append(max_score)

    return scores

# ===== 5. 主程式：掃描每個受試者資料夾 =====
def main():
    all_rows = {}  # key: subject_id, value: dict of scores

    # 每個子資料夾視為一個受試者
    for subj_dir in ROOT_DIR.iterdir():
        if not subj_dir.is_dir():
            continue

        subject_id = subj_dir.name  # 直接用資料夾名稱當 subject ID
        row = {"subject": subject_id}

        # 逐一處理 1~5 影片
        for video_id in range(1, 6):
            csv_path = subj_dir / f"click_log_{video_id}.csv"
            if not csv_path.exists():
                # 這個受試者沒做這支影片 → 全部 hazard 0 分
                for idx in range(1, len(HAZARD_ONSETS[video_id]) + 1):
                    col_name = f"v{video_id}_h{idx}"
                    row[col_name] = 0
                continue

            df = pd.read_csv(csv_path)
            video_scores = compute_scores_for_video(df, video_id)

            for idx, sc in enumerate(video_scores, start=1):
                col_name = f"v{video_id}_h{idx}"  # e.g. v4_h2
                row[col_name] = sc

        all_rows[subject_id] = row

    # 組成 DataFrame
    result_df = pd.DataFrame.from_dict(all_rows, orient="index")

    # 找出所有 hazard 欄位
    score_cols = [c for c in result_df.columns if c.startswith("v")]
    result_df[score_cols] = result_df[score_cols].fillna(0).astype(int)

    # 計算總分（7 個 hazard，滿分 140）
    result_df["total_score"] = result_df[score_cols].sum(axis=1)

    # 依 subject 排序
    result_df = result_df.sort_values("subject")

    # 存成 CSV
    out_path = ROOT_DIR / "scores_summary.csv"
    result_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"已輸出：{out_path}")

if __name__ == "__main__":
    main()
