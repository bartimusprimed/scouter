from firebase import firebase

fireBaseUrl = "https://project-6747688871085580068.firebaseio.com"
firebase = firebase.FirebaseApplication(fireBaseUrl, None)
sentenceLocation = "/sentences"


def queryFirebase(query):
    result = firebase.get(url="/", name="sentences")
    print(result)
    total = 0
    for r in result:
        if query in r:
            print(r)
            total += result[r]['connotation']
    print(total)

queryFirebase("skate")