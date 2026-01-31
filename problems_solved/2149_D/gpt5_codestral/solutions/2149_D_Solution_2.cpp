/*
 * Problem: 2149_D
 * Generated: 2025-11-27T17:02:13
 * Workflow: gpt5_codestral
 * Solution Model: gpt-5
 * Debugging Critic: codestral-2508
 * Iteration: 2
 * Rating: 1200
 */

#include<bits/stdc++.h>
using namespace std;

int main(){{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int t;
    cin >> t;
    while(t--){{
        int n;
        cin >> n;
        vector<long long> a(n);
        for(int i=0;i<n;i++) cin >> a[i];
        
        // Kadane's algorithm
        long long maxSum = a[0], currentSum = a[0];
        for(int i=1;i<n;i++){{
            currentSum = max(a[i], currentSum + a[i]);
            maxSum = max(maxSum, currentSum);
        }}
        cout << maxSum << "\n";
    }}
    return 0;
}}
