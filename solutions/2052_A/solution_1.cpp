/*
 * Problem: 2052_A
 * Generated: 2025-09-13 18:41:29
 * Model: GPT-4
 * Iteration: 1
 */

#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef pair<int,int> pii;
#define F first
#define S second
#define MP make_pair
#define PB push_back
#define INF (int)1e9
#define INFL (ll)1e18
#define PI acos(-1.0)
#define MOD ((int)1e9 + 7)
#define fastIO ios_base::sync_with_stdio(false);cin.tie(NULL);
typedef vector<int> vi;
typedef vector<pii> vii;
typedef vector<vi> vvi;
typedef vector<vii> vvii;

int main(){
    fastIO;
    int n;
    cin>>n;
    vector<int> a(n),b(n);
    for(int i=0;i<n;i++){
        cin>>a[i];
        b[i] = a[i];
    }
    sort(b.begin(),b.end());
    vector<pii> ans;
    for(int i=0;i<n;i++){
        if(a[i] != b[i]){
            for(int j=i+1;j<n;j++){
                if(a[j] == b[i]){
                    for(int k=j;k>i;k--){
                        ans.PB(MP(a[k],a[k-1]));
                        swap(a[k],a[k-1]);
                    }
                    break;
                }
            }
        }
    }
    cout<<ans.size()<<endl;
    for(auto x:ans)
        cout<<x.F<<" "<<x.S<<endl;
    return 0;
}