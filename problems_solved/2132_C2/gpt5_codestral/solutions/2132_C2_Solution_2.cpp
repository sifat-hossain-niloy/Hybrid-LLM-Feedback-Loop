/*
 * Problem: 2132_C2
 * Generated: 2025-11-25T03:56:07
 * Workflow: gpt5_codestral
 * Solution Model: gpt-5
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
        vector<long long> a(n), prefix(n+1, 0);
        for(int i=0;i<n;i++){{
            cin >> a[i];
            prefix[i+1] = prefix[i] + a[i];
        }}
        
        long long ans = LLONG_MIN;
        for(int i=0;i<n;i++){{
            for(int j=i+1;j<=n;j++){{
                ans = max(ans, prefix[j] - prefix[i]);
            }}
        }}
        cout << ans << "\n";
    }}
    return 0;
}}
