#!/bin/bash
save_name=$1
tmp_save_name=$save_name'_tmp'
touch "$tmp_save_name"
for i in `cat "$save_name"`; do
	if [ $i = '"inventory":' ]; then
		echo found inventory >&2
		in_inventory=true
		echo \"hot_bar_inventory\": >> "$tmp_save_name"
		echo added hot bar inventory >&2
		counter=0
	elif [ -n "$in_inventory" ]; then
		if [ "$counter" = 19 ]; then # each cell contains two values
			echo ${i%?} >> "$tmp_save_name"
			echo \], \"main_inventory\": \[ >> "$tmp_save_name"
			echo added main inventory >&2
			counter=$((counter + 1))
		else
			echo $i >> "$tmp_save_name"
			counter=$((counter + 1))
		fi
	else
		echo $i >> "$tmp_save_name"
	fi
done
mv "$tmp_save_name" "$save_name"
echo renamed file to actual save name >&2
echo done >&2
