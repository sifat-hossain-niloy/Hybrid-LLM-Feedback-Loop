/*
 * Problem: 2043_C - Let's define
 * Generated: 2025-11-07 05:37:58
 * Workflow: GPT-4 + Groq
 * Solution Model: gpt-4
 * Debugging Critic: llama-3.3-70b-versatile
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
        set<int> sums;
        sums.insert(0); // Initialize with 0 for the empty subarray

        for(int i=0; i<n; i++) {
            cin >> a[i];
        }

        // Use a more efficient approach to generate the possible sums
        // by considering the prefix sums of the array
        vector<int> prefixSums(n + 1, 0);
        for(int i=0; i<n; i++) {
            prefixSums[i + 1] = prefixSums[i] + a[i];
        }

        for(int i=0; i<n; i++) {
            for(int j=i; j<=n; j++) {
                sums.insert(prefixSums[j] - prefixSums[i]);
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