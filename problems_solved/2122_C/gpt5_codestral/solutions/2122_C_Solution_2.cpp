/*
 * Problem: 2122_C
 * Generated: 2025-11-26T08:38:16
 * Workflow: gpt5_codestral
 * Solution Model: gpt-5
 * Debugging Critic: codestral-2508
 * Iteration: 2
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
        
        vector<long long> dp(n);
        dp[0] = a[0];
        long long ans = dp[0];
        
        for(int i=1;i<n;i++){{
            dp[i] = max(a[i], dp[i-1] + a[i]);
            ans = max(ans, dp[i]);
        }}
        cout << ans << "\n";
    }}
    return 0;
}}
