#include <iostream>
#include <set>
#include <vector>
using namespace std;
#define R 3
// Linear Scan Register Allocation

void expireOldIntervals(pair<int,int> interval, set <pair <int, int>> &active,vector<pair<int,int>>& registers);
void displayRegisters(vector<pair<int,int>>& registers);
void linearScanRegisterAllocation(set <pair <int, int>> &LiveIntervals, vector<pair<int,int>>& registers);
void spillAtInterval(pair <int, int> interval, set <pair <int, int>> &active,vector<pair<int,int>>& registers);


void displayRegisters(vector<pair<int,int>>& registers){
    for(int i=0;i<registers.size();i++){
        cout<<"Register "<<i+1<<" contains "<<registers[i].first<<" "<<registers[i].second<<endl;
    }
    cout<<endl;
}

void linearScanRegisterAllocation(set <pair <int, int>> &LiveIntervals, vector<pair<int,int>>& registers){
    set <pair <int, int>> active;
    
    for(auto it = LiveIntervals.begin(); it != LiveIntervals.end(); it++){
        expireOldIntervals(*it,active,registers);

        if(active.size() == R){
            spillAtInterval(*it, active, registers);
        }
        else{
            for(int i=0;i<registers.size();i++){
                if(registers[i] == make_pair(-1,-1)){
                    registers[i] = *it;
                    active.insert(*it);
                    break;
                }
            }
        }
        displayRegisters(registers);
    }
    
}

void expireOldIntervals(pair<int,int> interval, set <pair <int, int>> &active,vector<pair<int,int>>& registers){
    for(auto it = active.begin(); it != active.end(); it++){
        pair<int,int> temp = *it;
        if(it->second <= interval.first){
            active.erase(*it);
            for(int i=0;i<registers.size();i++){
                if(registers[i] == temp){
                    registers[i] = make_pair(-1,-1);
                }
            }
        }
    }
}


void spillAtInterval(pair <int, int> interval, set <pair <int, int>> &active,vector<pair<int,int>>& registers){

    int max = interval.second;

    bool flag = false;

    pair<int,int> spillInterval = interval;
    for(auto it = active.begin(); it != active.end(); it++){
        if(it->second > max){
            max = it->second;
            spillInterval = *it;
            flag = true;
        }
    }

    if(flag){
        
        active.erase(spillInterval);
        cout<<"Spilled "<<spillInterval.first<<" "<<spillInterval.second<<"to memory"<<endl;
        int index=-1;
        for(int i=0;i<registers.size();i++){
            if(registers[i] == spillInterval){
                registers[i] = make_pair(-1,-1);
                index = i;
                break;
            }
        }
        active.insert(interval);
        registers[index] = interval;
    }else{
        cout<<"Spilled "<<interval.first<<" "<<interval.second<<" to memory"<<endl;
    }

}

    
int main(){
    
    set <pair <int, int>> LiveIntervals = {{1,3}, {2,5}, {3,10}, {4,8}, {5,7}};
    vector<pair<int,int>> registers(R, make_pair(-1,-1));
    //iterate through the set

    for (auto it = LiveIntervals.begin(); it != LiveIntervals.end(); it++){
        cout<< it -> first <<" "<< it -> second << endl;
    }

    linearScanRegisterAllocation(LiveIntervals, registers);


    
  
  return 0;
}