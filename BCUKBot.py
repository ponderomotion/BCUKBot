# Daniel Fletcher 2012
# Twitter bot. Follows users talking about BreastCancerUK

import twitter
import os
import sys
import time

def followTweeters(Searchkeywords='BPA Cancer'):
	LATESTFILE = 'follows_latest.txt'   # keeps latest tweet id
	LOGFILE = 'log.txt'	                # log of tweet id + user
	TWEETRECORD = 'tweetrecord.txt'     # Just user and tweet for human readability

	# Read login info from credentials.txt
	if os.path.exists("credentials.txt"):
		fp = open("credentials.txt")
		creds = fp.readlines()
		consumer_key = creds[0].split('=')[1]
		consumer_secret = creds[1].split('=')[1]
		access_token_key = creds[2].split('=')[1]
		access_token_secret = creds[3].split('=')[1]

	else:
		print "please create a credentials file in the format:"
		print "\t consumer_key=xxxx"
		print "\t consumer_secret=xxxx"
		print "\t access_token_key=xxxx"
		print "\t access_token_secret=xxxx"


	# Access token secret should not be committed to the public github repository
	api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret)

	# Find out when we last tried to follow someone
	if os.path.exists(LATESTFILE):
		fp = open(LATESTFILE)
		lastid = fp.read().strip()
		fp.close()
		if lastid == '':
			lastid = 0
	else:
		lastid = 0
	# Get list of people we've already tried to follow
	fp = open(LOGFILE)
	alreadyFollowed = fp.readlines()
	fp.close()

	print "total follows from this bot = ", len(alreadyFollowed)

	for i in range(len(alreadyFollowed)):
		if alreadyFollowed[i].strip()== '':
			continue
		alreadyFollowed[i] = alreadyFollowed[i].split('|')[1]

	# Dont try to follow ourselves
	alreadyFollowed.append('BreastCancer_UK')

	# Search for people talking about BPA and cancer
	try:
		results = api.GetSearch(Searchkeywords,since_id=lastid)
	except Exception:
		print 'tweet search failed, perhaps twitter is over capacity.'
		return

	if len(results)==0:
		print 'Nobody new to follow for search term: ', Searchkeywords 
		return

	Followed = []

	for statusObj in results:
		postTime = time.mktime(time.strptime(statusObj.created_at[:-6],'%a, %d %b %Y %H:%M:%S'))
		if time.time() - (24*60*60) < postTime and statusObj.user.screen_name not in alreadyFollowed and '@BreastCancer_UK' not in statusObj.text.lower():
			if [True for x in alreadyFollowed if ('@' + x).lower() in statusObj.text.lower()]:
				print 'Skipping because it\'s a mention: @%s - %s' % (statusObj.user.screen_name.encode('ascii', 'replace'), statusObj.text.encode('ascii', 'replace'))
			try:
				print 'Following in reply to @%s: %s' % (statusObj.user.screen_name.encode('ascii', 'replace'), statusObj.text.encode('ascii', 'replace'))
				api.CreateFriendship(statusObj.user.screen_name)
				Followed.append((statusObj.id, statusObj.user.screen_name,statusObj.text.encode('ascii', 'replace')))
				time.sleep(1)
			except Exception:
				print "Unexpected error:", sys.exc_info()[0:2]

	fp = open(LATESTFILE, 'w')
	fp.write(str(max([x.id for x in results])))
	fp.close()

	fp = open(LOGFILE,'a')
	fp.write('\n'.join(['%s|%s' % (x[0], x[1]) for x in Followed]) + '\n')
	fp.write('\n')
	fp.close()

	fp = open(TWEETRECORD,'a')
	fp.write('\n'.join(['%s|%s|%s' % (x[0], x[1], x[2]) for x in Followed]) + '\n')
	fp.write('\n')
	fp.close()


if __name__ == '__main__':
	while(True):
		followTweeters('Breast Cancer uk')
		followTweeters('BPA Cancer')
		#followTweeters('linked breast cancer') # ended up following a load of charletans
		time.sleep(300)
