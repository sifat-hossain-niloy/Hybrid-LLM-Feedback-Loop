/*
 * Problem: 2111_D
 * Generated: 2025-11-25T22:12:59
 * Workflow: gpt5_deepseek
 * Solution Model: gpt-5
 * Debugging Critic: deepseek-r1-0528
 * Iteration: 1
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
