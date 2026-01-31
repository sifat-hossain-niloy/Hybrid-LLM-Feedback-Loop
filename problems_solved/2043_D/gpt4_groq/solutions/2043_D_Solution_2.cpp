/*
 * Problem: 2043_D
 * Generated: 2025-11-25T08:54:22
 * Workflow: gpt4_groq
 * Solution Model: gpt-4
 * Debugging Critic: llama-3.3-70b-versatile
 * Iteration: 2
 * Rating: 1800
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
        vector<int> a(n);
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
