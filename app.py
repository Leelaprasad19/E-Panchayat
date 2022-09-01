from flask import Flask, flash, render_template, redirect, url_for, request
import mysql.connector
import os

app = Flask(__name__)

def getDetails():

    mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
    myCursor = mydb.cursor()
    myCursor.execute("select * from Users")
    users = myCursor.fetchall()

    return users

@app.route('/')
def login():
    return render_template('login.html')

currentUser = [[]]

@app.route('/', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    users = getDetails()

    val = [0, []]
    for user in users:
        if(user[1]==username and user[2]==password):
            val[0] = 1
            val[1] = list(user)
            break
    
    if(val[0]==1):
        currentUser[0] = val[1]

        if(val[1][4]=='user'):
            return redirect(url_for('home'))
        elif(val[1][4]=='pdo'):
            return redirect(url_for('pdo'))
        elif(val[1][4]=='admin'):
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))



@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():

    username = request.form['username']
    password = request.form['password']
    rpassword = request.form['rpassword']
    address = request.form['address']

    if(username=="" or password=="" or rpassword=="" or address==""):
        return render_template('tempAll.html', pagename='Warning', content="Please fill all the details", urlName="Click to try again", url="/signup")
    elif(password!=rpassword):
        return render_template('tempAll.html', pagename='Warning', content="Password Mismatch", urlName="Click to try again", url="/signup")
    else:
        mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
        myCursor = mydb.cursor()
        myCursor.execute("select * from Users")
        users = myCursor.fetchall()

        userId = int(users[-1][0]) + 1

        check = [0]
        for user in users:
            if(user[1]==username):
                check[0] = 1
        
        if(check[0]!=1):
            inetID = str(userId)

            query = "INSERT INTO `Users` (`InetID`, `username`, `password`, `address`, `type`) VALUES ('{}', '{}', '{}', '{}', 'user');".format(inetID, username, password, address)
            myCursor.execute(query)
            mydb.commit()
            return render_template('tempAll.html', pagename='Success', content="Account Created Successfully", urlName="Click to login", url="/")
        else:
            return render_template('tempAll.html', pagename='Warning', content="Username Already Exists", urlName="Click to try again", url="/signup")



@app.route('/home')
def home():
    return render_template('home.html')

currentComplaint = [0]
@app.route('/home', methods=['POST'])
def home_post():

    compID = request.form['CompID']
    currentComplaint[0] = compID

    mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
    myCursor = mydb.cursor()
    query = "select * from Complaints where CompId='"+compID.capitalize()+"';"
    myCursor.execute(query)
    res = myCursor.fetchall()
    query = "select pdoImage from ComplaintImages where CompId='"+compID.capitalize()+"';"
    myCursor.execute(query)
    cimage = myCursor.fetchall()
    

    if(len(res)==0):
        return render_template('tempAll.html', pagename='Warning', content="Invalid Complaint ID - "+ compID, url="/home", urlName="Click to go home")
    else:

        myImg = cimage[0][0]

        if(not myImg):
            myImg = ""

        if(res[0][6]=='resolved'):
            return render_template('status.html', info = res, flag = 1, resolvedImage = myImg)
        else:
            return render_template('status.html', info = res, flag = 0, resolvedImage = myImg)



@app.route('/PDO')
def pdo():

    address = currentUser[0][3]

    mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
    myCursor = mydb.cursor()
    myCursor.execute("select * from Complaints where address='"+ address +"' and status='resolved';")
    resolvedcomplaints = myCursor.fetchall()
    myCursor.execute("select * from Complaints where address='"+ address +"' and status!='resolved';")
    unresolvedcomplaints = myCursor.fetchall()

    return render_template('pdo.html', rcomplaints = resolvedcomplaints, ucomplaints = unresolvedcomplaints,cres = len(resolvedcomplaints), cunres = len(unresolvedcomplaints))



@app.route('/complaint')
def complaint():
    return render_template('complaint.html')

def upload_complaintImage(file, UPLOAD_FOLDER):
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    n = os.listdir(UPLOAD_FOLDER)
    fileName = str(len(n)+1)+'.jpg'
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], fileName))
    return fileName

@app.route('/complaint', methods=['POST'])
def complaint_post():
    compName = request.form['CompName']
    compDetails = request.form['CompDetails']
    compLocation = request.form['CompLocation']
    file = request.files['CompImage']
    loc = request.files['locationImage']
    address = currentUser[0][3]
    userID = currentUser[0][0]

    mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
    myCursor = mydb.cursor()
    myCursor.execute("select * from Complaints")
    complaints = myCursor.fetchall()

    noOfComplaints = len(complaints) + 1

    if(noOfComplaints < 10):
        compID = "C00" + str(noOfComplaints)
    elif(noOfComplaints < 100):
        compID = "C0" + str(noOfComplaints)
    else:
        compID = "C" + str(noOfComplaints)

    query = "INSERT INTO `Complaints` (`CompID`, `CompName`, `CompDetails`, `CompLocation`, `address`, `UserID`, `PDOID`, `status`) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '', 'unresolved');".format(compID, compName, compDetails, compLocation, address, userID)
    
    if(compName!="" and compDetails!="" and file.filename!="" and compLocation!="" and loc.filename!=""):
        fileName = upload_complaintImage(file, './static/complaint images')
        locName = upload_complaintImage(loc, './static/location images')
        query2 = "INSERT INTO `ComplaintImages` (`CompID`, `userImage`, `locationImage`) VALUES ('{}', '{}', '{}');".format(compID, fileName, locName)
        myCursor.execute(query)
        myCursor.execute(query2)
        mydb.commit()
        return render_template('tempAll.html', pagename='Success', content="Note your ID for future reference - " + compID, url="/home", urlName="Click to go home")
    else:
        return render_template('tempAll.html', pagename='Empty Entries', content="Please fill all the details", url="/home", urlName="Click to go home")



@app.route('/complaintStatus/<Complaintid>')
def complaintStatus(Complaintid):
    mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
    myCursor = mydb.cursor()
    myCursor.execute("select * from Complaints where CompID='"+ Complaintid +"';")
    res = myCursor.fetchall()
    myCursor.execute("select * from ComplaintImages where CompID='"+ Complaintid +"';")
    cimage = myCursor.fetchall()

    print("\n", cimage[0][3], "\n")

    return render_template('complaintStatus.html', info=res, compImage = cimage[0][1], locImage=cimage[0][3])
    
def upload_ResolvingImage(file, filename):
    UPLOAD_FOLDER = './static/resolving images'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    n = os.listdir(UPLOAD_FOLDER)
    fileName = str(len(n)+1)+'.jpg'
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], fileName))
    return fileName

@app.route('/complaintStatus/<Complaintid>', methods=['POST'])
def complaintStatus_post(Complaintid):

    status = request.form['status']
    file = request.files['CompImage']

    if(status!="" and file.filename!=""):
        fileName = upload_ResolvingImage(file, file.filename)
        mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
        myCursor = mydb.cursor()
        myCursor.execute("UPDATE Complaints SET status='"+ status +"', PDOID='"+ currentUser[0][0] +"' WHERE CompID='"+ Complaintid +"';")
        myCursor.execute("UPDATE ComplaintImages SET pdoImage='"+ fileName +"' WHERE CompID='"+ Complaintid +"';")
        mydb.commit()
        return render_template('tempAll.html', pagename='Success', content="Status Updated Successfully", url="/PDO", urlName="Click to go home")
    else:
        return render_template('tempAll.html', pagename='Warning', content="Nothing To Update", url="/PDO", urlName="Click to go home")


@app.route('/admin')
def admin():

    mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
    myCursor = mydb.cursor()
    myCursor.execute("select * from Users where type='pdo';")
    pdos = myCursor.fetchall()
    myCursor.execute("select * from Users where type='user';")
    users = myCursor.fetchall()

    return render_template('admin.html', pdos = pdos, users = users, cpdos=len(pdos), cusers = len(users))



@app.route('/details')
def details():
    return render_template('details.html')

@app.route('/details', methods=['POST'])
def detailsPost():

    username = request.form['username']
    password = request.form['password']
    rpassword = request.form['rpassword']
    address = request.form['address']

    if(username=="" or password=="" or rpassword=="" or address==""):
        return render_template('tempAll.html', pagename='Warning', content="Please fill all the details", url="/details", urlName="Try again")
    elif(password!=rpassword):
        return render_template('tempAll.html', pagename='Warning', content="Password Mismatch", urlName="Try again", url="/details")
    else:
        mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
        myCursor = mydb.cursor()
        myCursor.execute("select * from Users")
        users = myCursor.fetchall()

        userId = int(users[-1][0]) + 1

        check = [0]
        for user in users:
            if(user[1]==username):
                check[0] = 1
        
        if(check[0]!=1):

            inetID = str(userId)

            query = "INSERT INTO `Users` (`InetID`, `username`, `password`, `address`, `type`) VALUES ('{}', '{}', '{}', '{}', 'pdo');".format(inetID, username, password, address)
            myCursor.execute(query)
            mydb.commit()
            return render_template('tempAll.html', pagename='Success', content="Successfully Added", url="/admin", urlName="Click to go home")
        else:
            return render_template('tempAll.html', pagename='Warning', content="Username Already Exists", urlName="Try again", url="/details")



@app.route('/delete/<InetID>')
def deleteUser(InetID):
    mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
    myCursor = mydb.cursor()

    myCursor.execute("select * from Users where InetId='"+ InetID +"';")
    user = myCursor.fetchall()

    myCursor.execute("UPDATE Users SET type='["+ user[0][4] +"]', username='__"+ user[0][1] +"__', address='__"+ user[0][3] +"__' WHERE InetID='"+ InetID +"';")

    mydb.commit()

    return render_template('tempAll.html', pagename='Success', content="Successfully Deleted", url="/admin", urlName="Click to go home")



@app.route('/feedback', methods=['POST'])
def feedback():
    feedback = request.form['feedback']

    mydb = mysql.connector.connect(host='db4free.net', database='epanchayat', user='epanchayat', password='epanchayat')
    myCursor = mydb.cursor()

    myCursor.execute("UPDATE Complaints SET feedback='"+ feedback +"' WHERE CompID='"+ currentComplaint[0] +"';")

    mydb.commit()
    return render_template('tempAll.html', pagename='Thank you', content="Thank you for your valuable feedback", url="/home", urlName="Click to go home")

app.run(host='0.0.0.0', debug=True)
