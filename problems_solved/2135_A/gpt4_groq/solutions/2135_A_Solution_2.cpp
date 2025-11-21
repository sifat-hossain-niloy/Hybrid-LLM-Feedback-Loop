/*
 * Problem: 2135_A - In the first test case, the whole array
 * Generated: 2025-11-05 11:17:14
 * Workflow: GPT-4 + Groq
 * Solution Model: gpt-4
 * Debugging Critic: llama-3.3-70b-versatile
 * Iteration: 2
 * Rating: 1200
 */

#include<bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;
    while (t--) {
        int n;
        cin >> n;
        vector<int> a(n);
        for (int i = 0; i < n; i++) {
            cin >> a[i];
        }

        vector<int> dp(n + 1, 0);
        dp[0] = 0;

        for (int i = 1; i <= n; i++) {
            dp[i] = dp[i - 1];

            int blockLength = a[i - 1];
            int blockCount = 0;
            for (int j = i; j <= min(i + blockLength - 1, n); j++) {
                if (a[j - 1] == blockLength) {
                    blockCount++;
                } else {
                    break;
                }
            }

            if (blockCount == blockLength) {
                dp[i] = max(dp[i], dp[i - blockLength] + blockLength);
            }
        }

        cout << dp[n] << "\n";
    }

    return 0;
}