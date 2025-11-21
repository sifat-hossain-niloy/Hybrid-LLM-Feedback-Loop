/*
 * Problem: 2135_A - In the first test case, the whole array
 * Generated: 2025-11-05 11:07:08
 * Workflow: GPT-4 + Mistral
 * Solution Model: gpt-4
 * Debugging Critic: codestral-2508
 * Iteration: 3
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
        vector<int> cnt;
        int c = 1;
        for(int i = 1; i < n; i++) {
            if(a[i] == a[i-1]) {
                c++;
            } else {
                cnt.push_back(c);
                c = 1;
            }
        }
        cnt.push_back(c);
        sort(cnt.begin(), cnt.end());
        int ans = 0, sum = 0;
        for(int i = cnt.size()-1; i >= 0; i--) {
            if(sum + cnt[i] >= cnt[i]) {
                sum += cnt[i];
                ans = max(ans, sum);
            } else {
                break;
            }
        }
        cout << ans << "\n";
    }

    return 0;
}