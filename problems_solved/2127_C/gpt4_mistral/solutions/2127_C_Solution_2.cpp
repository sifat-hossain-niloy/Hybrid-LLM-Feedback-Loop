/*
 * Problem: 2127_C
 * Generated: 2025-11-29T03:12:33
 * Workflow: gpt4_mistral
 * Solution Model: gpt-4
 * Debugging Critic: codestral-2508
 * Iteration: 2
 * Rating: 1400
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
