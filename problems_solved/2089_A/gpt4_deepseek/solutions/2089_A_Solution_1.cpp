/*
 * Problem: 2089_A
 * Generated: 2025-11-21T20:53:39
 * Workflow: gpt4_deepseek
 * Solution Model: gpt-4
 * Debugging Critic: deepseek-r1-0528
 * Iteration: 1
 * Rating: 1700
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
