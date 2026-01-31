/*
 * Problem: 2101_A
 * Generated: 2025-11-25T22:12:51
 * Workflow: gpt5_groq
 * Solution Model: gpt-5
 * Debugging Critic: llama-3.3-70b-versatile
 * Iteration: 2
 * Rating: 1300
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
        
        long long ans = a[0];
        int left = 0;
        long long currentSum = 0;
        
        for(int right=0; right<n; right++){{
            currentSum += a[right];
            ans = max(ans, currentSum);
            while(currentSum < 0 && left <= right){{
                currentSum -= a[left];
                left++;
            }}
        }}
        cout << ans << "\n";
    }}
    return 0;
}}
