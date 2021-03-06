#!/bin/bash

echo $1 > productname.txt

if [ -z "$1" ] 
	then
	echo "Please specify PRODUCT name"
	exit;
fi

if [ -z "$2" ] 
	then
	echo "Please specify HADOOP path name"
	exit
else
	if [ ! -d "$2"."/sbin" ] 
		then
		echo "Path $2 is not valid"
		exit
	fi
fi

cp publicmapper.py $2
cp publicreducer.py $2
mkdir $2/hadoop_mongo
cp -r hadoop_mongo/* $2/hadoop_mongo/
cp productname.txt $2

chmod +x $2"publicmapper.py"
chmod +x $2"publicreducer.py"
cp hadoop-streaming-2.6.1.jar $2
cp mongo-hadoop-streaming-1.4.0.jar $2
cp TwitterAnalysisUI.html $2
cp index.png $2

echo "*******Making ready the data******"
echo "Fetching Tweets for $1"
python data_load.py "$1 deals"
python data_load.py "$1 vs"
python data_load.py "vs $1"
python data_load.py "$1 place:96683cc9126741d1"
python data_load.py "$1 place:3376992a082d67c7"
python data_load.py "$1 place:3f14ce28dc7c4566"
python data_load.py "$1 place:6416b8512febefc9"
python data_load.py "$1 place:b850c1bfd38f30e0"

echo "Done fetching tweets. Inserted to mongodb in test database under the collection 'product'"

echo "About to start Hadoop Program"

cd $2

bin/hadoop jar 
hadoop-streaming-2.6.1.jar -libjars mongo-hadoop-streaming-1.4.0.jar -io mongodb -jobconf mongo.input.uri=mongodb://127.0.0.1/test.product -jobconf stream.io.identifier.resolver.class=com.mongodb.hadoop.streaming.io.MongoIdentifierResolver 
-mapper publicmapper.py -reducer publicreducer.py -input input -inputformat com.mongodb.hadoop.mapred.MongoInputFormat -output output12101

echo "Open TwitterAnalysisUI.html and select $1"

