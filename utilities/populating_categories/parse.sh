cd /Users/sdatta/wikipedia_w251

for filepath in $(ls -1 ./wikipedia/json_out/*/*)
do 
    grep -io "\"id\": .* \"title\": \"[0-9a-z ]*\"" ${filepath} /dev/null|awk -F"[,:]" 'BEGIN{OFS="|";} {print $1,$3,$5":"$6,$8}'|sed -e 's/| /|/g' -e 's/ |/|/g'|sed -e 's/"//g'|cut -d "/" -f4-
done > parse.sh.nohup.out


