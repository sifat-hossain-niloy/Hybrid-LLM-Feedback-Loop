/*
 * Problem: 2091_F
 * Generated: 2025-11-28T18:17:03
 * Workflow: gpt4_groq
 * Solution Model: gpt-4
 * Debugging Critic: llama-3.3-70b-versatile
 * Iteration: 1
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
        
        // Brute force O(n^2) approach
        int ans = 0;
        for(int i=0;i<n;i++){{
            for(int j=i;j<n;j++){{
                int sum = 0;
                for(int k=i;k<=j;k++) sum += a[k];
                ans = max(ans, sum);
            }}
        }}
        cout << ans << "\n";
    }}
    return 0;
}}
