from django.db import models
#from django.utils import timezone
import datetime
# Create your models here.
class postData ( models.Model ):
	postId = models.IntegerField()
	postReference = models.CharField( max_length = 255 )
	postSource = models.CharField( max_length = 255 )
	postName = models.CharField( max_length = 100 )
	imageUrl = models.CharField( max_length = 255 )
	postCaption = models.CharField( max_length = 255 ) 
	postDate = models.DateField( default= datetime.date.today() )
	lastActivity = models.DateField(default = datetime.date.today() )


# model for storing access_token
class accessToken (models.Model):
	postSource = models.CharField( max_length = 255 )
	accessToken = models.CharField( max_length = 255 )

# activityType can be 1 of the following
# 1 --- > Like
# 2 --- > Comment
# 3 --- > Share

class activityLog (models.Model):
	postId = models.ForeignKey(postData)
	activityType = models.IntegerField()
	accountId = models.BigIntegerField()
	activityDate = models.DateField(default = datetime.date.today())
	activityTimeStamp = models.DateTimeField( default = datetime.datetime.today())
	commentText = models.TextField()
