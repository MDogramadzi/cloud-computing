kubectl apply -f googlecloud_ssd.yaml
gcloud compute disks create --size 30GB --type pd-ssd pd-ssd-disk-1,2,3,4....
kubectl apply -f gce-ssd-persistentvolume1.yaml
kubectl apply -f mongodb-service.yaml
kubectl exec -it mongod-0 -c mongod-container bash
enter mongo shell
rs.initiate({_id: "MainRepSet", version: 1, members: [ 
       { _id: 0, host : "mongod-0.mongodb-service.default.svc.cluster.local:27017" },
       { _id: 1, host : "mongod-1.mongodb-service.default.svc.cluster.local:27017" },
       { _id: 2, host : "mongod-2.mongodb-service.default.svc.cluster.local:27017" },
       .....
 ]});
done
