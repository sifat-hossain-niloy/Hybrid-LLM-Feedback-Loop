/*
 * Problem: 2065_C2
 * Generated: 2025-11-23T15:00:51
 * Workflow: gpt4_deepseek
 * Solution Model: gpt-4
 * Debugging Critic: deepseek-r1-0528
 * Iteration: 4
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
        
        stack<pair<long long, long long>> st;
        long long ans = LLONG_MIN;
        long long currentSum = 0;
        
        for(int i=0;i<n;i++){{
            currentSum += a[i];
            long long minBefore = currentSum;
            while(!st.empty() && st.top().first >= currentSum){{
                minBefore = min(minBefore, st.top().second);
                st.pop();
            }}
            if(!st.empty()) minBefore = min(minBefore, st.top().second);
            st.push({{currentSum, minBefore}});
            ans = max(ans, currentSum - minBefore + a[i]);
        }}
        cout << max(ans, *max_element(a.begin(), a.end())) << "\n";
    }}
    return 0;
}}
