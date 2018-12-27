FROM mongo

COPY init.json /init.json
CMD mongoimport --host mongodb --db reach-engine --collection questions --type json --file /init.json --jsonArray