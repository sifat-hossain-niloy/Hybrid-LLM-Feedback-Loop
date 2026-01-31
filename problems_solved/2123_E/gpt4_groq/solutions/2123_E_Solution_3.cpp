/*
 * Problem: 2123_E
 * Generated: 2025-11-28T22:49:45
 * Workflow: gpt4_groq
 * Solution Model: gpt-4
 * Debugging Critic: llama-3.3-70b-versatile
 * Iteration: 3
 * Rating: 1400
 */

#include<bits/stdc++.h>
using namespace std;

struct Node {{
    long long sum, prefixMax, suffixMax, maxSum;
}};

Node merge(Node left, Node right){{
    Node result;
    result.sum = left.sum + right.sum;
    result.prefixMax = max(left.prefixMax, left.sum + right.prefixMax);
    result.suffixMax = max(right.suffixMax, right.sum + left.suffixMax);
    result.maxSum = max({{left.maxSum, right.maxSum, left.suffixMax + right.prefixMax}});
    return result;
}}

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
        
        Node result = {{a[0], a[0], a[0], a[0]}};
        for(int i=1;i<n;i++){{
            Node curr = {{a[i], a[i], a[i], a[i]}};
            result = merge(result, curr);
        }}
        cout << result.maxSum << "\n";
    }}
    return 0;
}}
