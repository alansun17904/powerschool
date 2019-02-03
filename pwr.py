from bs4 import BeautifulSoup
import requests
import hmac, hashlib, base64


class PowerSchool:
    def __init__(self, url):
        """

        :param url:
        """
        self.url = url
        self.session = requests.session()

    def _getCookies(self, username, pw):
        """

        :param username:
        :param pw:
        :return:
        """
        authData = {}
        r = self.session.get(self.url)
        if r.status_code != requests.codes.ok:
            raise Exception('Unable to get authentication data from login page.')
        soup = BeautifulSoup(r.text, 'html.parser')
        for form in soup.find_all('input'):
            if form.get('name') == 'pstoken':
                authData['pstoken'] = form.get('value')
            elif form.get('id') == 'contextData':
                authData['contextData'] = form.get('value')

        authData['credentialType'] = 'User Id and Password Credential'
        authData['account'] = username
        authData['dbpw'] = hmac.new(authData['contextData'].encode('ascii'), pw.lower().encode('ascii'), hashlib.md5).hexdigest()
        authData['ldappassword'] = pw
        authData['pw'] = hmac.new(authData['contextData'].encode('ascii'), base64.b64encode(hashlib.md5(pw.encode('ascii')).digest()).replace(b"=", b""), hashlib.md5).hexdigest()
        self.authData = authData
        return authData

    def login(self, username, password):
        """

        :param username:
        :param password:
        :return:
        """
        authData = self._getCookies(username, password)
        r = self.session.post(self.url + 'guardian/home.html', data=authData)
        return r.text

    def searchClassLink(self):
        """

        :return:
        """
        if not hasattr(self, 'authData'):
            raise Exception('User did not log in.')
        r = self.session.post(self.url + 'guardian/home.html', data=self.authData)
        soup = BeautifulSoup(r.text, 'html.parser')
        classDict = {}
        className = ''
        for row in soup.find_all('tr'):
            linkCount = 0
            for cell in row.find_all('td'):
                if cell.get('align') == 'left':
                    className = cell.contents[0].strip()
                    classDict[className] = ''
                elif cell.a:
                    linkCount += 1
                    if linkCount % 3 == 0:
                        classDict[className] = self.url + 'guardian/' + cell.a.get('href')
        self.classLinks = classDict
        return classDict

    def getSchedule(self):
        """

        :return: 
        """
        r = self.session.get(self.url + 'guardian/myschedule.html')
        print(r.text)




fin = open('meta.txt', 'r')
usr = fin.readline().strip()
pwd = fin.readline().strip()
p = PowerSchool('https://sis.isb.bj.edu.cn/')
p.login(usr, pwd)
# print(p.getSchedule())
print(p.searchClassLink())

