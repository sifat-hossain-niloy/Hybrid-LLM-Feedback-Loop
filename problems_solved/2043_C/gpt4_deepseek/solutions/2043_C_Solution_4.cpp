/*
 * Problem: 2043_C
 * Generated: 2025-11-23T03:10:34
 * Workflow: gpt4_deepseek
 * Solution Model: gpt-4
 * Debugging Critic: deepseek-r1-0528
 * Iteration: 4
 * Rating: 1600
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
