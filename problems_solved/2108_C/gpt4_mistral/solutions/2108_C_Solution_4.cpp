/*
 * Problem: 2108_C
 * Generated: 2025-11-23T12:02:57
 * Workflow: gpt4_mistral
 * Solution Model: gpt-4
 * Debugging Critic: codestral-2508
 * Iteration: 4
 * Rating: 1500
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
