#title           :BikeNetworkEvaluator_June20_2015.py
#description     :Manipulates street dataset to produce cycling suitability evaluation model
#author          :Riley D. Champine
#date            :June 23rd, 2015
#version         :1.5
#usage           :python arcpy ArcGIS
#==============================================================================

#Import arcpy module
import arcpy

#Import time module
import time

#Retrieve and store current time from time module
ts = time.time()

#Import datetime module
import datetime

#Create variable that stores a formatted time stamp
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

#Input dataset
#It may be necessary to alter the following path based on access to Shared Folder
bikefc = "//cas-fs-geog/infographics/Projects/CampusMapping/Experiments/RileyExperiments/Riley_Champine_Final_Project/Data.gdb/BikeFacility_Raw"



##------New Fields------##

#Create field to store slope proxy variable
arcpy.AddField_management(bikefc, "slope", "FLOAT", "", "", "", "Slope Proxy")

#Calculate value of slope proxy using the sum of elevation gain and loss divided by segment length
arcpy.CalculateField_management(bikefc, "slope",'(!dzp! + !dzn!) / !Shape_Length!', "PYTHON")

#Create text field called Qualified Feature Type
arcpy.AddField_management(bikefc, "qual_type", "TEXT", "", "", "50", "Qualified Feature Type")

#Create field to store bike facility ranking variable
arcpy.AddField_management(bikefc, "facility_r", "FLOAT", "", "", "", "Facility Rank")

#Create field to store slope ranking variable
arcpy.AddField_management(bikefc, "slope_r", "FLOAT", "", "", "", "Slope Rank")

#Create field to store traffic ranking variable
arcpy.AddField_management(bikefc, "traffic_r", "FLOAT", "", "", "", "Traffic Volume Rank")

#Create field to store traffic volume variable
arcpy.AddField_management(bikefc, "traffic_v", "Text", "", "", "50", "Traffic Level")

#Create field to store speed limit ranking variable
arcpy.AddField_management(bikefc, "speed_r", "FLOAT", "", "", "", "Speed Limit Rank")

#Create field to flag null values in speed or traffic fields
arcpy.AddField_management(bikefc, "null_flag", "FLOAT", "", "", "", "Null Flag")

#Create field to store evaluation of relevent variables 
arcpy.AddField_management(bikefc, "eval", "FLOAT", "", "", "", "Raw Evaluation")

#Create field to store qualitative equivalent of evaluation
arcpy.AddField_management(bikefc, "condition", "TEXT", "", "", "50", "Condition")



##------Generate Null Flag------##

#List fields for fields parameter in cursor
null_fields = ('est_vol', 'speed', 'null_flag')

#Define update cursor that determines whether the speed or traffic variables are null
#Determines whether segment will be evaluated because it has sufficient data for ranking
null_cursor = arcpy.da.UpdateCursor(bikefc, null_fields)

#For each segment in the cursor...
for row in null_cursor:
    if (row[0] == None or row[1] == None): #if either the traffic or speed columns have null values
        row[2] = 1 #set flag to 1 indicating nulls
    else:
        row[2] = 0 #othersise 0 = no nulls
        
    null_cursor.updateRow(row)    




##------Feature Type Qualifer------##

#List fields for fields parameter in cursor
qualify_fields = ('bik_rest','bikefac','est_vol', 'speed', 'qual_type')

#Define update cursor that qualifies each feature based on type
qualify_cursor = arcpy.da.UpdateCursor(bikefc, qualify_fields)

#For each segment in the cursor...
for row in qualify_cursor:

    #determine whether segment has a restriction on cycling
    if (row[0] == 1):
        row[4] = "Prohibited" #if bik_rest = 1, classify as Prohibited 

    #determine whether segment is a multi-use path
    elif (row[1] == "rmup"):
        row[4] = "Multi-Use Path" #if bikefac = rmup, classify as Multi-Use Path
        
        
    #determine whether segment is a bike blvd 
    elif (row[1] == "blvd"):
        row[4] = "Bike Boulevard" #if bikefac = blvd, classify as Bike Bouldevard

    ##determine whether segment has any bike lane in any direction
    elif (row[1] == "bike lane FT" or row[1] == "bike lane TF" or row[1] == "bike lanes"):
        row[4] = "Bike Lanes" #if bikefac = any of the bike lane codes, classify as Bike Lanes   
        
    ##oherwise, classify as Street
    else:
        row[4] = "Street"
        
        if ((row[4] == "Street") and row[2] == None or row[3] == None):
            row[4] = "Unqualified" #if speed or traffic are null for streets, classify as Unqualified
        
    qualify_cursor.updateRow(row)

#Delete cursor and row  
del qualify_cursor, row



##------Traffic Evaluator------##

#List fields for traffic cursor
traffic_fields = ('est_vol', 'traffic_r')

#Define update cursor that ranks each segment based on traffic volume
traffic_cursor = arcpy.da.UpdateCursor(bikefc, traffic_fields)
               
#For each segment in cursor, rank traffic volume based on following thresholds...
for row in traffic_cursor:
    if (row[0] > 0 and row[0] < 1500): 
        row[1] = 9

    elif (row[0] >= 1500 and row[0] < 3000):
        row[1] = 8
        
    elif (row[0] >= 3000 and row[0] < 5000):
        row[1] = 7
        
    elif (row[0] >= 5000 and row[0] < 10000):
        row[1] = 6
        
    elif (row[0] >= 10000 and row[0] < 20000):
        row[1] = 5

    elif (row[0] >= 20000):
        row[1] = 4

    #otherwise traffic rank is Null    
    else:
        row[1] = None 
        
    traffic_cursor.updateRow(row)

#Delete cursor and row  
del traffic_cursor, row

##------Traffic Volume------##

#List fields for traffic cursor
trafficv_fields = ('est_vol', 'traffic_v')

#Define update cursor that ranks each segment based on traffic volume
trafficv_cursor = arcpy.da.UpdateCursor(bikefc, trafficv_fields)
               
#For each segment in cursor, rank traffic volume based on following thresholds...
for row in trafficv_cursor:
    if (row[0] > 0 and row[0] < 1500): 
        row[1] = "Very Light"

    elif (row[0] >= 1500 and row[0] < 3000):
        row[1] = "Light"
        
    elif (row[0] >= 3000 and row[0] < 5000):
        row[1] = "Moderate"
        
    elif (row[0] >= 5000 and row[0] < 10000):
        row[1] = "Heavy"
        
    elif (row[0] >= 10000 and row[0] < 20000):
        row[1] = "Very Heavy"

    elif (row[0] >= 20000):
        row[1] = "Extremely Heavy"

    #otherwise traffic rank is Null    
    else:
        row[1] = None 
        
    trafficv_cursor.updateRow(row)

#Delete cursor and row  
del trafficv_cursor, row


##------Speed Evaluator------##

#List fields for speed cursor
speed_fields = ('speed', 'speed_r')

#Define update cursor that ranks each segment based on speed limit
speed_cursor = arcpy.da.UpdateCursor(bikefc, speed_fields)
               
#For each segment in cursor, rank speed limit by following thresholds...
for row in speed_cursor:
    if (row[0] > 0 and row[0] < 25): 
        row[1] = 10

    elif (row[0] >= 25 and row[0] < 30):
        row[1] = 8
        
    elif (row[0] >= 30 and row[0] < 35):
        row[1] = 7
        
    elif (row[0] >= 35 and row[0] < 40):
        row[1] = 6
        
    elif (row[0] >= 40):
        row[1] = 5

    #otherwise speed rank is Null    
    else:
        row[1] = None     
        
    speed_cursor.updateRow(row)

#Delete cursor and row  
del speed_cursor, row




##------Slope Evaluator------##

#List fields for slope cursor
slope_fields = ('slope', 'slope_r')

#Define update cursor that ranks each segment based on slope proxy 
slope_cursor = arcpy.da.UpdateCursor(bikefc, slope_fields)
               
#For each segment in cursor, rank slope proxy based on following thresolds...
for row in slope_cursor:
    if (row[0] < .01):
        row[1] = 10
    
    elif (row[0] >= .01 and row[0] < .02):
        row[1] = 9

    elif (row[0] >= .02 and row[0] < .03):
        row[1] = 8

    elif (row[0] >= .03 and row[0] < .04):
        row[1] = 7        

    elif (row[0] >= .04 and row[0] < .05):
        row[1] = 6          

    #otherwise, slope proxy above .03 is ranked as 5
    else:
        row[1] = 5
        
    slope_cursor.updateRow(row)

#Delete cursor and row  
del slope_cursor, row




##------Bike Facility Evaluator------##

#List fields for fields parameter in cursor
facility_fields = ('qual_type', 'facility_r')

#Define update cursor that segments based on presense and type of bike facility
facility_cursor = arcpy.da.UpdateCursor(bikefc, facility_fields)

#For each segment in cursor, assign bike facility rank based on type of facility...
for row in facility_cursor:
    
    if (row[0] == "Multi-Use Path"):
        row[1] = 10
        
    elif (row[0] == "Bike Boulevard"):
        row[1] = 9

    elif (row[0] == "Bike Lanes"):
        row[1] = 8

    #otherwise, any other street is ranked as a 7   
    else:
        row[1] = 7           
        
    facility_cursor.updateRow(row)

#Delete cursor and row  
del facility_cursor, row




##------Multi-Use Path Evaluator------##

#List fields for fields parameter in cursor
path_fields = ('qual_type', 'eval')

#Define update cursor that evaluates multi-use paths
path_cursor = arcpy.da.UpdateCursor(bikefc, path_fields)

#For each multi-use path in cursor...
for row in path_cursor:
    if (row[0] == "Multi-Use Path"):
        row[1] = 10 #all multi-use paths are evaluated as 10 out of 10

    path_cursor.updateRow(row)

#Delete cursor and row  
del path_cursor, row




##------Prohibited Segment Evaluator------##

#List fields for fields parameter in cursor
prohibit_fields = ('bik_rest', 'eval')

#Define update cursor that evaluates segments prohibited for biking
prohibit_cursor = arcpy.da.UpdateCursor(bikefc, prohibit_fields)

#For each segment path in cursor...
for row in prohibit_cursor:
    if (row[0] == 1):
        row[1] = 0 #all prohibited segments are evaluated as 0 out of 10

    prohibit_cursor.updateRow(row)

#Delete cursor and row  
del prohibit_cursor, row





##------Bike Boulevard Evaluator------##

#List fields for fields parameter in cursor
blvd_fields = ('qual_type', 'null_flag', 'traffic_r', 'speed_r', 'slope_r', 'facility_r', 'eval')

#Define update cursor that evaluates bike boulevards
blvd_cursor = arcpy.da.UpdateCursor(bikefc, blvd_fields)

#For each segment in cursor, evaluate only bike boulevards with data based on traffic, slope, and facility...
for row in blvd_cursor:
    if (row[0] == "Bike Boulevard" and row[1] == 0):
        row[6] = ((row[2]*.2) + (row[3]*.2) + (row[4]*.1) + (row[5]*.5)) #evaluation is the mean ranking of above variables

    blvd_cursor.updateRow(row)

#delete cursor and row  
del blvd_cursor, row




##------Bike Lane Evaluator------##

#List fields for fields parameter in cursor
lane_fields = ('qual_type', 'null_flag', 'traffic_r', 'speed_r', 'slope_r', 'facility_r', 'eval')

#Define update cursor that evaluates bike lanes
lane_cursor = arcpy.da.UpdateCursor(bikefc, lane_fields)

#For each segment in cursor, evaluate bike lanes with data based on traffic, speed, slope, and facility...
for row in lane_cursor:
    if (row[0] == "Bike Lanes" and row[1] == 0):
        row[6] = ((row[2]*.2) + (row[3]*.2) + (row[4]*.1) + (row[5]*.5)) #evaluation is the mean ranking of above variables

    lane_cursor.updateRow(row)

#Delete cursor and row  
del lane_cursor, row




##------Street Evaluator------##

#List fields for fields parameter in cursor
street_fields = ('qual_type', 'null_flag', 'traffic_r', 'speed_r', 'slope_r', 'facility_r', 'eval')

#Define update cursor that evaluates streets
street_cursor = arcpy.da.UpdateCursor(bikefc, street_fields)

#for each segment in cursor, evaluate street with data based on traffic, speed, and slope
for row in street_cursor:
    if (row[0] == "Street" and row[1] == 0): 
        row[6] = ((row[2]*.4) + (row[3]*.3) + (row[4]*.1) + (row[5]*.2)) #evaluation is the mean ranking of above variables

    street_cursor.updateRow(row)

#Delete cursor and row  
del street_cursor, row



##------Condition Evaluator------##

#List fields for fields parameter in cursor
condition_fields = ('eval', 'condition')

#Define update cursor that segments based on presense and type of bike facility
condition_cursor = arcpy.da.UpdateCursor(bikefc, condition_fields)

#For each segment in cursor, assign bike facility rank based on type of facility...
for row in condition_cursor:
    
    if (row[0] >= 9):
        row[1] = "Kids with Training"
        
    elif (row[0] >= 8):
        row[1] = "Most Adults"

    elif (row[0] >= 7):
        row[1] = "Confident and Enthused"

    elif (row[0] < 7 and row[0] > 0):
        row[1] = "Strong and Fearless"

    #otherwise, segment ranking for bike facility is Null    
    else:
        row[1] = "No Data"           
        
    condition_cursor.updateRow(row)

#Delete cursor and row  
del condition_cursor, row

print "Executed at..."
print st
