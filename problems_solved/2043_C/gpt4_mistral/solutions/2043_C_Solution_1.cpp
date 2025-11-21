/*
 * Problem: 2043_C - Let's define
 * Generated: 2025-11-07 05:32:52
 * Workflow: GPT-4 + Mistral
 * Solution Model: gpt-4
 * Debugging Critic: codestral-2508
 * Iteration: 1
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
        int x = 0;
        for(int i = 0; i < n; i++) {
            cin >> a[i];
            if(a[i] != -1 && a[i] != 1) {
                x = a[i];
            }
        }

        set<int> sums;
        int sum = 0;
        for(int i = 0; i < n; i++) {
            sum += a[i];
            sums.insert(sum);
        }

        if(x != 0) {
            for(int i = x - 1; i <= x + 1; i++) {
                sums.insert(i);
            }
        }

        for(auto it : sums) {
            cout << it << " ";
        }
        cout << "\n";
    }

    return 0;
}