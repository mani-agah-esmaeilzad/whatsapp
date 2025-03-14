def solve():
    import sys
    data = sys.stdin.read().strip().split()
    
    if not data:
        return
    t = int(data[0])
    MOD = 10**9 + 7
    results = []
    pos = 1
    for _ in range(t):
        n = int(data[pos])
        pos += 1
        # برای n کوچکتر از 10 (چه زوج چه فرد) فرمول یکدست است
        if n < 10:
            ans = pow(2, n - 1, MOD)
        else:
            if n % 2 == 1:
                # اگر n فرد باشد
                ans = pow(2, n - 1, MOD)
            else:
                # n زوج و >= 10
                k = n // 10  # در اینجا k = ⌊n/10⌋
                exp2 = n - k - 3   # نمای 2
                exp3 = 3 * k       # نمای 3
                ans = (pow(2, exp2, MOD) * pow(3, exp3, MOD)) % MOD
        results.append(str(ans))
    sys.stdout.write("\n".join(results))

if __name__ == '__main__':
    solve()
