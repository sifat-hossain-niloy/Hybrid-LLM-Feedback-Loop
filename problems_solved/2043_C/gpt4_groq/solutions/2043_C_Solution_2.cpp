/*
 * Problem: 2043_C - Let's define
 * Generated: 2025-11-07 05:36:58
 * Workflow: GPT-4 + Groq
 * Solution Model: gpt-4
 * Debugging Critic: llama-3.3-70b-versatile
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
        set<int> sums;
        sums.insert(0); // Initialize with 0 for the empty subarray

        for(int i=0; i<n; i++) {
            cin >> a[i];
        }

        for(int i=0; i<n; i++) {
            int sum = 0;
            for(int j=i; j<n; j++) {
                sum += a[j];
                sums.insert(sum);
            }
        }

        vector<int> result(sums.begin(), sums.end());
        sort(result.begin(), result.end());

        cout << result.size() << "\n";
        for(int num : result) {
            cout << num << " ";
        }
        cout << "\n";
    }

    return 0;
}