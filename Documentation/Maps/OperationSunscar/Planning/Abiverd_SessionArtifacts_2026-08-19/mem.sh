#!/bin/sh
P=$(pgrep -f UnrealEditor | head -1)
UE=$(ps -o rss= -p "$P" 2>/dev/null | awk '{printf "%.2f",$1/1048576}')
sysctl -n vm.swapusage | awk -v ue="$UE" '{gsub(/M/,"");
  printf "UE RSS %s GB | swap %.1f/%.1f GB", ue, $6/1024, $3/1024}'
vm_stat | awk '/page size/{gsub(/[^0-9]/,"",$8); ps=$8} /Pages free/{gsub(/\./,"",$3); f=$3} /Pages occupied by compressor/{gsub(/\./,"",$5); c=$5} END{printf " | free %.2f GB | compressed %.2f GB\n", f*ps/1073741824, c*ps/1073741824}'
