/*
 * Problem: 2117_E
 * Generated: 2025-11-24T18:21:24
 * Workflow: gpt4_mistral
 * Solution Model: gpt-4
 * Debugging Critic: codestral-2508
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
        
        stack<pair<long long, long long>> st;
        long long ans = LLONG_MIN;
        long long currentSum = 0;
        
        for(int i=0;i<n;i++){{
            currentSum -= a[i];
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
