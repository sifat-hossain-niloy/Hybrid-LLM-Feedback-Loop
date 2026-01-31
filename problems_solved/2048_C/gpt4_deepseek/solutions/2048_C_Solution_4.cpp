/*
 * Problem: 2048_C
 * Generated: 2025-11-24T09:50:58
 * Workflow: gpt4_deepseek
 * Solution Model: gpt-4
 * Debugging Critic: deepseek-r1-0528
 * Iteration: 4
 * Rating: 1200
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
