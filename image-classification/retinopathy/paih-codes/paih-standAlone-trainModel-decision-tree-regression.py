from sparkdl import readImages
from pyspark.sql import Row
import os.path
from pyspark.ml.regression import DecisionTreeRegressor
from pyspark.ml.classification import OneVsRest
#from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from sparkdl import DeepImageFeaturizer

#sc = SparkContext()
#spark = SparkSession(sc)

imageDir = "/media/prateek/2A8BEA421AC55874/PAIH/work/"
#imageDir = "hdfs://192.168.65.188:8020/paih/"
#imageDir = "hdfs://10.0.0.7:8020/paih/"


def getFileName (filePath) :
	fileName = os.path.basename(filePath).split(".")[0]
	return fileName

# Prepare Train Data
tmpTrainDf = readImages(imageDir + "train25")
#tmpTrainDf = readImages(imageDir + "/test1")
tmpTrainRDD = tmpTrainDf.rdd.map(lambda x : Row(filepath = x[0], image = x[1], fileName = getFileName(x[0])))
tmpTrainX = tmpTrainRDD.toDF()
csvTrainTmp = spark.read.format("csv").option("header", "true").load(imageDir + "train25.csv")
#csvTrainTmp = spark.read.format("csv").option("header", "true").load(imageDir + "/test1.csv")
csvTrainRDD = csvTrainTmp.rdd.map(lambda x : Row(image = x[0], label = int(x[1])))
csvTrain = csvTrainRDD.toDF()
finalTrainDataFrame = tmpTrainX.join(csvTrain, tmpTrainX.fileName == csvTrain.image, 'inner').drop(csvTrain.image)


featurizer = DeepImageFeaturizer(inputCol="image",outputCol="features", modelName="InceptionV3")

#method = DecisionTreeRegressor(featuresCol="indexedFeatures")
method = DecisionTreeRegressor(featuresCol="features",labelCol="label")
ovr = OneVsRest(classifier = method)
featureVector = featurizer.transform(finalTrainDataFrame).persist()
model_dr = ovr.fit(featureVector)
model_dr.write().overwrite().save(imageDir + 'model-dicision-tree-regression')

predictions = model_dr.transform(featureVector)
predictionAndLabels = predictions.select("prediction", "label")

evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
print("Train Data set accuracy with Decision Tree Regression = " + str(evaluator.evaluate(predictionAndLabels)) + " and error " + str(1 - evaluator.evaluate(predictionAndLabels)))
#regression evaluator
#evaluator = RegressionEvaluator(
 #   labelCol="label", predictionCol="prediction", metricName="rmse")
#rmse = evaluator.evaluate(predictions)
#print("Root Mean Squared Error (RMSE) on test data = %g" % rmse)
#predictions.show()

#apply evaluator on constructed model for training data.

#apply deep learning for feature extraction
#apply genetic algo for feature selection
#apply ml model(eg. lr)
#apply genetic algorithm for feature selection


#A. evaluate training and test data by lrand other 10 methods.
#B. Tensoflow and spark cocktail


#p = Pipeline(stages=[featurizer,ovr])
#feature = p.fit(finalTrainDataFrame)
#featureObj.show()
#pModel = p.fit(finalTrainDataFrame)
#p = Pipeline(stages=[ovr])
#pModel = p.fit(finalTrainDataFrame)

#predictions = pModel.transform(finalTestDataFrame)

#predictions.select("filePath", "prediction").show(truncate=False)
#from pyspark.ml.evaluation import MulticlassClassificationEvaluator

#predictionAndLabels = predictions.select("prediction", "label")
#predictionAndLabels.show()

#evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
#print("Test Data set accuracy = " + str(evaluator.evaluate(predictionAndLabels)) + " and error " + str(1 - evaluator.evaluate(predictionAndLabels)))
