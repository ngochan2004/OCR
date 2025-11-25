def clean_text(s: str):
    return " ".join((s or "").split())

def levenshtein(a, b):
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1): dp[i][0] = i
    for j in range(m+1): dp[0][j] = j
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = 0 if a[i-1]==b[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[-1][-1]

def char_accuracy(gt, pred):
    gt = gt or ""; pred = pred or ""
    dist = levenshtein(gt, pred)
    max_len = max(1, len(gt))
    acc = max(0.0, 1.0 - dist/max_len)
    return acc, dist
