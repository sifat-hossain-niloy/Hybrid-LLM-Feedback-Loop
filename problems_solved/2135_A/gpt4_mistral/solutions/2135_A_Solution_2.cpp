/*
 * Problem: 2135_A - In the first test case, the whole array
 * Generated: 2025-11-05 11:06:09
 * Workflow: GPT-4 + Mistral
 * Solution Model: gpt-4
 * Debugging Critic: codestral-2508
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
    while(t--) {
        int n;
        cin >> n;
        vector<int> a(n);
        for(int i = 0; i < n; i++) {
            cin >> a[i];
        }
        map<int, int> freq;
        for(int i = 0; i < n; i++) {
            freq[a[i]]++;
        }
        int ans = 0, cnt = 0;
        for(auto it = freq.begin(); it != freq.end(); it++) {
            cnt += it->second;
            if(cnt >= it->first) {
                ans += it->first;
                cnt = 0;
            }
        }
        cout << ans << "\n";
    }

    return 0;
}