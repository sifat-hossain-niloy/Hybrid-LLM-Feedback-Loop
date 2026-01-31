/*
 * Problem: 2038_C
 * Generated: 2025-11-28T16:56:49
 * Workflow: gpt4_groq
 * Solution Model: gpt-4
 * Debugging Critic: llama-3.3-70b-versatile
 * Iteration: 4
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
        vector<int> a(n);
        for(int i=0;i<n;i++) cin >> a[i];
        
        int maxVal = *max_element(a.begin(), a.end());
        int minVal = *min_element(a.begin(), a.end());
        
        if(maxVal <= 0){{
            cout << maxVal << "\n";
        }} else {{
            long long sum = 0;
            for(int x : a) if(x > 0) sum += x;
            cout << sum << "\n";
        }}
    }}
    return 0;
}}
