/*
 * Problem: 2135_A - In the first test case, the whole array
 * Generated: 2025-11-05 11:05:24
 * Workflow: GPT-4 + Mistral
 * Solution Model: gpt-4
 * Debugging Critic: codestral-2508
 * Iteration: 1
 * Rating: 1200
 */

#include<bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;
    while(t--) {
        int n;
        cin >> n;
        vector<int> a(n);
        for(int i = 0; i < n; i++) {
            cin >> a[i];
        }
        sort(a.begin(), a.end());
        int cnt = 1, ans = 0;
        for(int i = 1; i < n; i++) {
            if(a[i] == a[i-1]) {
                cnt++;
            } else {
                ans = max(ans, min(cnt, a[i-1]));
                cnt = 1;
            }
        }
        ans = max(ans, min(cnt, a[n-1]));
        cout << ans << "\n";
    }

    return 0;
}