micro_wyckoff_sniffer.py
import pandas as pd

def detect_exhaustion_retest(df: pd.DataFrame):
    """
    Detects exhaustion and retest candles using high volume wicks.
    Expects DataFrame with columns: OPEN, HIGH, LOW, CLOSE, TICKVOL, DATE, TIME
    """

    df = df.copy()
    df['datetime'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'])

    df['upper_wick'] = df['HIGH'] - df[['OPEN', 'CLOSE']].max(axis=1)
    df['lower_wick'] = df[['OPEN', 'CLOSE']].min(axis=1) - df['LOW']
    df['body_size'] = (df['CLOSE'] - df['OPEN']).abs()

    exhaustion_idx = (df['TICKVOL'] * df['upper_wick']).idxmax()
    retest_idx = (df['TICKVOL'] * df['lower_wick']).idxmax()

    exhaustion = df.loc[exhaustion_idx]
    retest = df.loc[retest_idx]

    return exhaustion, retest