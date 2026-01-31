/*
 * Problem: 2152_C
 * Generated: 2025-11-26T14:49:45
 * Workflow: gpt4_groq
 * Solution Model: gpt-4
 * Debugging Critic: llama-3.3-70b-versatile
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
                ans =  prefix[j] - prefix[i]);
            }}
        }}
        cout << ans << "\n";
    }}
    return 0;
}}
