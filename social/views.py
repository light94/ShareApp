# django modules
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
# utility functions
import requests,json

# app specific functions
from social.models import *
from social.forms import PostForm
from awesomeapp import settings
# global variables declarations
g_accessToken = {'fb' : '','linkedin':''}
g_loginUrls = {}
g_fbUserId = ""
fbTokenExpired = False
liTokenExpired = False
### ENTER FACEBOOK PAGE ID HERE
fbPageId = ""

def index(request):
	global g_loginUrls
	# function to render the first page, showing fb and linkedin logins
	checkAccessToken()
	return render (request, 'login.html', {'urls' : g_loginUrls})


def fblogin(request,code):
	# the returned data contains a 'code' keyword
	global g_accessToken, g_loginUrls ,fbTokenExpired
	if 'code' in request.GET:
		code = request.GET['code']
		### FILL IN DETAILS HERE
	 	payload = {'client_id':'','redirect_uri':'','client_secret':'','code':code}
	 	data = requests.get('https://graph.facebook.com/oauth/access_token',params = payload)
		# extract token from returned string
		token = data.text[13:]
		userData = requests.get("https://graph.facebook.com/me",params={'access_token':token})
		userId = userData.json()['id']

		permissions = requests.get('https://graph.facebook.com/v2.3/' + userId + '/accounts',params={'access_token':token})
		jPermission = json.loads(json.dumps(permissions.json()['data']))
		
		# get page access token for the desired page
		for account in jPermission:
			if account['name'] == 'TestPage':
				g_accessToken['fb'] = account['access_token']
				break

		try:
			tokenObject = accessToken.objects.get(postSource = "fb")
			tokenObject.accessToken = g_accessToken["fb"]
		except ObjectDoesNotExist:
			tokenObject = accessToken(postSource = "fb" , accessToken = g_accessToken["fb"])

		tokenObject.save()
		fbTokenExpired = False
		del g_loginUrls['facebook']
		return HttpResponse("Logged into Facebook, You may close the window.")
		
	elif 'error' in request.GET:
		return HttpResponse(request.GET['error_description'])
def display(request):
	return HttpResponse("redirected!!")


def lilogin(request):
	if 'code' in request.GET:
		code = request.GET['code']
		### FILL IN DETAILS HERE
		data = {'grant_type':'authorization_code','code':code,'redirect_uri':'lilogin','client_id':'','client_secret':''}
		post = requests.post('https://www.linkedin.com/uas/oauth2/accessToken',data = data)
		g_accessToken['li'] = post.json()['access_token'] 
		try:
			tokenObject = accessToken.objects.get(postSource = "li")
			tokenObject.accessToken = g_accessToken["li"]
		except ObjectDoesNotExist:
			tokenObject = accessToken(postSource = "li" , accessToken = g_accessToken["li"])

		tokenObject.save()
		liTokenExpired = False
		del g_loginUrls['linkedin']
		return HttpResponse("Logged in to Linkedin. You may close this window.")
	elif 'error' in request.GET:
		return HttpResponse(request.GET['error_description'])

def showForm (request):
	response = ""
	# show a single form for all the media
	if request.method == 'POST':
		post = PostForm(request.POST, request.FILES)
		if post.is_valid() :
			postName = post.cleaned_data['postName']
			imageUrl = post.cleaned_data['imageUrl']
			postCaption = post.cleaned_data['postCaption']
			postSource = post.cleaned_data['postSource']
			lastPost = postData.objects.order_by('postId').last()
			if lastPost:
				lastPostId = lastPost.postId
			else:
				lastPostId = 0

			# select an image if present
			#if imageUrl == "" and "imageFile" in request.FILES:
			#	image = settings.MEDIA_ROOT + "" +request.FILES['imageFile'].name
			#	imageUrl = "http://"+request.get_host()+settings.MEDIA_URL+request.FILES['imageFile'].name
			#	with open(image, 'wb') as destination:
			#		for chunk in request.FILES['imageFile'].chunks():
			#			destination.write(chunk)
			for source in postSource:
				response += postUpdate(source, postName, imageUrl, postCaption, lastPostId + 1)
		
			#postUpdate("li", postName, imageUrl, postCaption)
			return HttpResponse(response)
		else:
			# error occured in validation
			form = PostForm()
			return render(request, 'postForm.html', {'form':form,'msg':post.errors})
	else:
		form = PostForm()
		return render(request, 'postForm.html', {'form':form})

def postUpdate(postSource, postName, imageUrl, postCaption, postId):
	if postSource == "fb" and not fbTokenExpired:
	### ADD FACEBOOK PAGE ID HERE
		fbpost = requests.post('',data={'access_token':g_accessToken['fb'],'url':imageUrl,'caption':postCaption})
		postJson = json.loads(json.dumps(fbpost.json()))

		if 'post_id' in postJson:
			newPost = postData(postId = postId, postReference = postJson['post_id'],postSource = "fb",postName = postName, imageUrl = imageUrl, postCaption = postCaption).save()
			return "posted to fb "
		else:
			return "Unable to post to fb "
	elif postSource == "li" and not liTokenExpired:
		jsonData = {
					    "visibility": {
					        "code": "anyone"
					    },
					    "content": {
					        "submitted-url": "https://www.example.com/content.html",
					        "title": "Test Title",
					        "description": postCaption,
					        "submitted-image-url": imageUrl
					    }
					}
		headers = {"Content-Type" : "application/json", "x-li-format": "json"}
		lipost = requests.post('https://api.linkedin.com/v1/companies/2414183/shares?oauth2_access_token='+g_accessToken['li']+'&format=json',headers = headers,data=json.dumps(jsonData))
		postJson = json.loads(json.dumps(lipost.json()))
		newPost = postData(postId = postId, postReference = postJson["updateKey"],postSource = "li",postName = postName, imageUrl = imageUrl, postCaption = postCaption).save()

		return "posted to Linkedin"

def retrieveData(request):
	# update facebook data
	fbPosts = postData.objects.filter(postSource = "fb")
	data = ""
	for post in fbPosts:
		#return HttpResponse('https://graph.facebook.com/v2.3/'+post.postId)
		getLastActivity = requests.get('https://graph.facebook.com/v2.3/'+"845807965496801_8672095633566412",params = {"access_token":g_accessToken["fb"],"fields":"updated_time"})
		return HttpResponse(getLastActivity.text)

		#the returned data has date and time both. we need only the date
		post.lastActivity = lastActivityJson["updated_time"][:10]
		post.save()
	return HttpResponse("Data retireved. Check database")

def checkAccessToken():
	global g_accessToken, fbTokenExpired, liTokenExpired

	try:
		g_accessToken["fb"] = accessToken.objects.get(postSource = "fb").accessToken
	except ObjectDoesNotExist as e:
		g_accessToken["fb"] = "randomstring"

	pageData = requests.get('https://graph.facebook.com/v2.3/'+ fbPageId,params={'fields':'about','access_token' : g_accessToken["fb"]})
	
	if 'error' in pageData.json():
		fbTokenExpired = True
	elif 'about' in pageData.json():
		fbTokenExpired = False

	try:
		g_accessToken["li"] = accessToken.objects.get(postSource = "li").accessToken
	except ObjectDoesNotExist as e:
		g_accessToken["li"] = "randomstring"

	pageData = requests.get('https://api.linkedin.com/v1/companies/2414183/is-company-share-enabled',params={'format':'json','oauth2_access_token':g_accessToken["li"]})
	
	if pageData.text == "true":
		liTokenExpired = False
	elif 'status' in pageData.json():
		liTokenExpired = True
	
	if fbTokenExpired or liTokenExpired:
		return getNewTokens()

def getNewTokens():
	global g_loginUrls
	
	if fbTokenExpired:
	### ADD DETAILS HERE
		g_loginUrls['facebook'] = "https://www.facebook.com/dialog/oauth?client_id=&redirect_uri="	
	if liTokenExpired:
		g_loginUrls['linkedin'] = "https://www.linkedin.com/uas/oauth2/authorization?response_type=code&client_id=&redirect_uri=&state="
		

def showReport (request):
	pass

def getAnalyticsForPost ( source = "fb"):
### 
	postId = ''
	#if source == "fb":
	postsData = requests.get('https://graph.facebook.com/v2.3/'+postId+'/likes',params={'access_token':g_accessToken['fb']})
	return HttpResponse(postsData.json()['data'])
