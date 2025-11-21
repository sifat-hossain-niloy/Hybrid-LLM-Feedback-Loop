/*
 * Problem: 2043_C - Let's define
 * Generated: 2025-11-07 05:34:30
 * Workflow: GPT-4 + Mistral
 * Solution Model: gpt-4
 * Debugging Critic: codestral-2508
 * Iteration: 3
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
        int ones = 0, minus_ones = 0;
        for(int i = 0; i < n; i++) {
            cin >> a[i];
            if(a[i] != -1 && a[i] != 1) {
                x = a[i];
            } else if(a[i] == 1) {
                ones++;
            } else if(a[i] == -1) {
                minus_ones++;
            }
        }

        set<int> sums;
        sums.insert(0);
        for(int i = 1; i <= ones; i++) {
            sums.insert(i);
        }
        for(int i = 1; i <= minus_ones; i++) {
            sums.insert(-i);
        }

        if(x != 0) {
            vector<int> temp(sums.begin(), sums.end());
            for(int i = 0; i < temp.size(); i++) {
                sums.insert(temp[i] + x);
            }
        }

        for(auto it : sums) {
            cout << it << " ";
        }
        cout << "\n";
    }

    return 0;
}