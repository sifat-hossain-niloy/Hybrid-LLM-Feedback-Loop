/*
 * Problem: 2043_C - Let's define
 * Generated: 2025-11-07 06:22:26
 * Workflow: GPT-4 + DeepSeek
 * Solution Model: gpt-4
 * Debugging Critic: deepseek-reasoner
 * Iteration: 2
 * Rating: 1600
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
        int sum = 0, max_val = INT_MIN, min_val = INT_MAX;
        for(int i = 0; i < n; i++) {
            cin >> a[i];
            if(a[i] == 1 || a[i] == -1) {
                sum += a[i];
            } else {
                max_val = max(max_val, a[i]);
                min_val = min(min_val, a[i]);
            }
        }
        set<int> ans;
        for(int i = min(sum, 0); i <= max(sum, 0); i++) {
            ans.insert(i);
        }
        if(max_val != INT_MIN) {
            for(int i = min(sum + min_val, 0); i <= max(sum + min_val, 0); i++) {
                ans.insert(i);
            }
            for(int i = min(sum + max_val, 0); i <= max(sum + max_val, 0); i++) {
                ans.insert(i);
            }
        }
        cout << ans.size() << "\n";
        for(auto it : ans) {
            cout << it << " ";
        }
        cout << "\n";
    }

    return 0;
}