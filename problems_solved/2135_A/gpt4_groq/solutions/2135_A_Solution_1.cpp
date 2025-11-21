/*
 * Problem: 2135_A - In the first test case, the whole array
 * Generated: 2025-11-05 11:16:37
 * Workflow: GPT-4 + Groq
 * Solution Model: gpt-4
 * Debugging Critic: llama-3.3-70b-versatile
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
        vector<int> cnt(n + 1, 0);
        for(int i = 0; i < n; i++) {
            cnt[a[i]]++;
        }
        sort(cnt.begin(), cnt.end());
        int max1 = cnt[n], max2 = cnt[n - 1];
        if(max1 == max2) {
            cout << max1 << "\n";
        } else {
            cout << min(max1 - 1, max2) + 1 << "\n";
        }
    }

    return 0;
}