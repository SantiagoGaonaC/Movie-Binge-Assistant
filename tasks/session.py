def createSession(request,iduser):
        request.session['user'] = iduser


def updateSession(request):
        request.session['user'] ='new_value'

def getSession(request):
    if 'user' in request.session:
        return request.session['user'] 
    else:
        return "no"

def deleteSession(request):
    request.session.pop("user", None)