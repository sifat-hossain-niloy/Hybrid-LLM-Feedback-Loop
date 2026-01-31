/*
 * Problem: 2089_A
 * Generated: 2025-11-21T21:01:25
 * Workflow: gpt4_deepseek
 * Solution Model: gpt-4
 * Debugging Critic: deepseek-r1-0528
 * Iteration: 3
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
