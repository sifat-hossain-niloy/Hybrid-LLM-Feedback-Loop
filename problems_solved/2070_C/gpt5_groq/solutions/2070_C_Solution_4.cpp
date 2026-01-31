/*
 * Problem: 2070_C
 * Generated: 2025-11-24T01:22:53
 * Workflow: gpt5_groq
 * Solution Model: gpt-5
 * Debugging Critic: llama-3.3-70b-versatile
 * Iteration: 4
 * Rating: 1500
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
        long long total = 0;
        for(int i=0;i<n;i++){{
            cin >> a[i];
            total += a[i];
        }}
        
        long long minPrefix = 0, prefix = 0;
        long long ans = LLONG_MIN;
        
        for(int i=0;i<n;i++){{
            prefix += a[i];
            ans = max(ans, prefix - minPrefix);
            minPrefix = min(minPrefix, prefix);
        }}
        cout << ans << "\n";
    }}
    return 0;
}}
