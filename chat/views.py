from django.shortcuts import render,redirect
from django.http import HttpResponse

# Create your views here.

# chatbot_app/views.py
from django.shortcuts import render,redirect
from model import NeuralNet  # Import your chatbot model here
from nltk_utils import bag_of_words, tokenize
import torch
import random
import json
from chat.models import Timetable,Datesheet,CustomUser,Staff,ChatHistory
from django.contrib import messages
from django.utils.safestring import mark_safe
from chat.Email_backen import EmailBackend
from django.contrib.auth import login,logout,authenticate
from  django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import subprocess


# Define global variables for the model and data
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = None
input_size, hidden_size, output_size = None, None, None
all_words, tags, model_state = None, None, None

# Function to load the model and data
def load_model_and_data():
    global model, input_size, hidden_size, output_size, all_words, tags, model_state,intents

    with open('intents.json', 'r') as json_data:
        intents = json.load(json_data)

    FILE = "data.pth"
    data = torch.load(FILE)

    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

# Initial model and data loading
load_model_and_data()

# Your existing code, you can call this function to retrain the model


def Login(request):
    return render(request,'login.html')

def doLOGOUT(request):
    logout(request)
    return redirect('Login')


def Admin_home(request):
    return render(request,'Admin_home.html')



def user_home(request):
    return render(request,'user_home.html')



def doLOGIN(request):
    if request.method == "POST":
        user = EmailBackend.authenticate(request, username=request.POST.get('email'),
                                         password=request.POST.get('password'))
        if user != None:
            login(request, user)
            user_type = user.user_type
            if user_type == '1':
                #return redirect('Home_admin')
                return redirect('Admin_home')
                #return redirect('admin_home')
            elif user_type == '2':
                #return redirect('User_home')
                return redirect('user_home')
                #return redirect('Docter_home')
            else:
                messages.error(request, 'Email or Password is invalid')
                return redirect('Login')
        else:
            messages.error(request, 'Email or Password is invalid')
            return redirect('Login')


def index(request):
    if request.method == 'POST':
        user_message = request.POST['user_message']
        bot_response = get_chatbot_response(user_message)
        user = request.user
        chat_history = ChatHistory(user=user, questions=user_message, responses=bot_response)
        chat_history.save()
        return render(request, 'chatbot.html',
                      {'user_message': user_message, 'bot_response': bot_response})
    return render(request, 'chatbot.html')




def get_chatbot_response(user_message):
    sentence = tokenize(user_message)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        if tag == "timetable":
            timetable_data = Timetable.objects.all()
            if timetable_data:
                response = f"Here is the timetable:<br>"
                response += "<style>table {border-collapse: collapse; width: 100%;} th, td {padding: 8px; text-align: left;} th {background-color: #f2f2f2;} th, td {border-bottom: 1px solid #ddd;}</style>"
                response += "<table>"
                response += "<tr><th>Class</th><th>Course</th><th>Day</th><th>Time</th><th>Location</th></tr>"
                for item in timetable_data:
                    response += f"<tr><td>{item.semester}</td><td>{item.course_name}</td><td>{item.day}</td><td>{item.time}</td><td>{item.location}</td></tr>"
                response += "</table>"
            else:
                response = f"Sorry! I couldn't find the required information."

        elif tag == "datesheet":
            datesheet_data = Datesheet.objects.all()
            if datesheet_data:
                response = f"Here is the datesheet:<br>"
                response += "<style>table {border-collapse: collapse; width: 100%;} th, td {padding: 8px; text-align: left;} th {background-color: #f2f2f2;} th, td {border-bottom: 1px solid #ddd;}</style>"
                response += "<table>"
                response += "<tr><th>Class</th><th>Subject</th><th>Date</th><th>Time</th></tr>"
                for item in datesheet_data:
                    response += f"<tr><td>{item.semester}</td><td>{item.exam_subject}</td><td>{item.exam_date}</td><td>{item.time}</td></tr>"
                response += "</table>"
            else:
                response = f"Sorry! I couldn't find the required information."
        elif tag == "V.C":
            data = Staff.objects.filter(designation='V.C')
            if data:
                response = f"Here is the information:<br>"
                response += "<style>table {border-collapse: collapse; width: 100%;} th, td {padding: 8px; text-align: left;} th {background-color: #f2f2f2;} th, td {border-bottom: 1px solid #ddd;}</style>"
                response += "<table>"
                response += "<tr><th>Name</th><th>Designation</th></tr>"
                for item in data:
                    response += f"<tr><td>{item.name}</td><td>{item.designation}</td></tr>"
                response += "</table>"
            else:
                response = f"Sorry! I couldn't find the required information."
        elif tag == "Basic and Applied Sciences Dean":
            data = Staff.objects.filter(faculty='Basic and Applied Scienes', designation='Dean')
            if data:
                response = f"Here is the information:<br>"
                response += "<style>table {border-collapse: collapse; width: 100%;} th, td {padding: 8px; text-align: left;} th {background-color: #f2f2f2;} th, td {border-bottom: 1px solid #ddd;}</style>"
                response += "<table>"
                response += "<tr><th>Name</th><th>Faculty</th><th>Designation</th></tr>"
                for item in data:
                    response += f"<tr><td>{item.name}</td><td>{item.faculty}</td><td>{item.designation}</td></tr>"
                response += "</table>"
            else:
                response = f"Sorry! I couldn't find the required information."
        elif tag == "CS&IT Chairman":
            data = Staff.objects.filter(department='CS&IT', designation='Chairman')
            if data:
                response = f"Here is the information:<br>"
                response += "<style>table {border-collapse: collapse; width: 100%;} th, td {padding: 8px; text-align: left;} th {background-color: #f2f2f2;} th, td {border-bottom: 1px solid #ddd;}</style>"
                response += "<table>"
                response += "<tr><th>Name</th><th>Faculty</th><th>Department</th><th>Designation</th></tr>"
                for item in data:
                    response += f"<tr><td>{item.name}</td><td>{item.faculty}</td><td>{item.department}</td><td>{item.designation}</td></tr>"
                response += "</table>"
            else:
                response = f"Sorry! I couldn't find the required information."
        elif tag == "CS&IT Staff":
            data = Staff.objects.filter(department='CS&IT')
            if data:
                response = f"Here is the information:<br>"
                response += "<style>table {border-collapse: collapse; width: 100%;} th, td {padding: 8px; text-align: left;} th {background-color: #f2f2f2;} th, td {border-bottom: 1px solid #ddd;}</style>"
                response += "<table>"
                response += "<tr><th>Name</th><th>Faculty</th><th>Department</th><th>Designation</th></tr>"
                for item in data:
                    response += f"<tr><td>{item.name}</td><td>{item.faculty}</td><td>{item.department}</td><td>{item.designation}</td></tr>"
                response += "</table>"
            else:
                response = f"Sorry! I couldn't find the required information."

        else:
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    return random.choice(intent['responses'])
    else:
        response = f"Sorry! I couldn't find the required information."

    return mark_safe(response)


def timetable(request):
    return render(request,'timetable.html')


def datesheet(request):
    return render(request,'datesheet.html')


def add_timetable(request):
    if request.method == "POST":
        semester = request.POST.get('semester')
        day = request.POST.get('day')
        course_name = request.POST.get('course_Name')
        time = request.POST.get('time')
        location = request.POST.get('location')
        timetable = Timetable(
            semester=semester,
            day=day,
            course_name=course_name,
            time=time,
            location=location,
        )
        timetable.save()
        messages.success(request, "Time_table Successfully Created")
        print("Time_table Successfully Created")
        return redirect('timetable')
    return render(request, "timetable.html")


def add_datesheet(request):
    if request.method == "POST":
        semester = request.POST.get('semester')
        date = request.POST.get('date')
        course_name = request.POST.get('course_Name')
        time = request.POST.get('time')
        datesheet = Datesheet(
            semester=semester,
            exam_date=date,
            exam_subject=course_name,
            time=time,
        )
        datesheet.save()
        messages.success(request, "Datesheet Successfully Created")
        print("Datesheet Successfully Created")
        return redirect('datesheet')
    return render(request, "datesheet.html")

def register_user(request):
    return render(request,'register.html')


def add_user(request):
    if request.method == "POST":
        uname = request.POST.get('uname')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            redirect('register_user')
        if CustomUser.objects.filter(username=uname).exists():
            messages.error(request, "username already exists")
            redirect('register_user')
        else:
            user = CustomUser(
                first_name=fname,
                last_name=lname,
                username=uname,
                email=email,
                user_type=2,
            )
            user.set_password(password)
            user.save()
            messages.success(request, fname + " " + "Profile is created")
            redirect('register_user')
    return render(request, 'register.html')


def update_profile(request):
    return render(request,'update_profile.html')

def profile_update(request):
    if request.method == "POST" :
        uname = request.POST.get('uname')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = fname
            customuser.last_name = lname
            if password != "" and password != None:
                customuser.set_password(password)
            customuser.save()
            messages.success(request,"Your Profile is Updated")
            redirect('update_profile')

        except:
            messages.error(request,"Sorry! Some error accured")
            redirect('update_profile')

    return render(request,'update_profile.html')


def view_user(request):
    user = CustomUser.objects.filter(user_type=2)
    context = {
        'user':user,
    }
    return render(request,'view_users.html',context)


def delete_user(request,id):
    user = CustomUser.objects.get(id=id)
    user.delete()
    messages.success(request, "User Successfully Deleted")
    return redirect('view_user')


def view_timetable(request):
    timetable = Timetable.objects.all()
    context = {
        'time':timetable,
    }
    return render(request,'view_timetable.html',context)


def view_datesheet(request):
    datesheet= Datesheet.objects.all()
    context = {
        'date':datesheet,
    }
    return render(request,'view_datesheet.html',context)


def staff(request):
    return render(request,'add_staff.html')


def add_staff(request):
    if request.method == "POST":
        name = request.POST.get('name')
        fac = request.POST.get('faculty')
        dep = request.POST.get('department')
        des = request.POST.get('designation')
        try:
            staff = Staff(
                name=name,
                faculty=fac,
                department=dep,
                designation=des,

            )
            staff.save()
            messages.success(request, "Staff Profile is Created")
            redirect('staff')

        except:
            messages.error(request, "Sorry! Some error accured")
            redirect('staff')

    return render(request, 'add_staff.html')


def view_staff(request):
    staff = Staff.objects.all()
    context = {
        'staff':staff,
    }
    return render(request,'view_staff.html',context)


def delete_timetable(request,id):
    time = Timetable.objects.get(id=id)
    time.delete()
    messages.success(request, "TimeTable Slot Successfully Deleted")
    return redirect('view_timetable')


def delete_datesheet(request,id):
    date = Datesheet.objects.get(id=id)
    date.delete()
    messages.success(request, "DateSheet Slot Successfully Deleted")
    return redirect('view_datesheet')


def delete_staff(request,id):
    staff = Staff.objects.get(id=id)
    staff.delete()
    messages.success(request, "Staff Successfully Deleted")
    return redirect('view_staff')


def view_history(request):
    history = ChatHistory.objects.filter(user=request.user)
    context = {
        'his':history
    }
    return render(request,'user_history.html',context)


def admin_view_history(request):
    history = ChatHistory.objects.filter(responses="Sorry! I couldn't find the required information.",reply="")
    context = {
        'his': history
    }
    return render(request, 'admin_history.html', context)


def delete_history(request,id):
    history = ChatHistory.objects.get(id=id)
    history.delete()
    messages.success(request, "History Successfully Deleted")
    return redirect('view_history')


def admin_reply(request):
    if request.method == "POST":
        id = request.POST.get('id')
        reply = request.POST.get('reply')
        rep = ChatHistory.objects.get(id=id)
        if rep:
            rep.reply = reply
            rep.save()
            messages.success(request, "Replied Successfully")
        else:
            messages.error(request, "Chat history not found")
    return redirect('admin_view_history')


def admin_responses(request):
    history = ChatHistory.objects.filter(responses="Sorry! I couldn't find the required information.").exclude(reply="")
    context = {
        'his': history
    }
    return render(request,'view_admin_responces.html',context)


def bot_responses(request):
    return render(request,'bot_reponces.html')


def append_intent_to_file(new_intent, filename):
    try:
        # Load the existing data from the file
        with open(filename, "r") as intents_file:
            data = json.load(intents_file)

        # Check if the "intents" key exists; if not, create it as an empty list
        intents = data.get("intents", [])

        # Append the new intent to the list
        intents.append(new_intent)

        # Update the "intents" key in the data
        data["intents"] = intents

        # Save the updated data back to the file
        with open(filename, "w") as intents_file:
            json.dump(data, intents_file, indent=2)
    except FileNotFoundError:
        # If the file doesn't exist, create a new file with the new intent
        data = {"intents": [new_intent]}
        with open(filename, "w") as intents_file:
            json.dump(data, intents_file, indent=2)
def add_bot_responses(request):
    if request.method == "POST":
        user_query = request.POST.get("user-query")
        bot_response = request.POST.get("bot-response")
        tag = request.POST.get("tags")

        new_intent = {
            "tag": tag,
            "patterns": user_query.split("\n"),
            "responses": bot_response.split("\n"),
        }
        try:
            append_intent_to_file(new_intent, "intents.json")
            messages.success(request, "New intent saved successfully")
        except Exception as e:
            print(str(e))
            messages.error(request, "An error occurred while saving the new intent")


    return redirect('bot_responses')


def train_model(request):
    global model, input_size, hidden_size, output_size, all_words, tags, model_state

    try:
        # Run a script to train the model (replace with your actual training process)
        subprocess.run(["python", "train.py"], check=True)
    except subprocess.CalledProcessError:
        messages.error(request, "Training process failed")

    # Load the newly trained model
    load_model_and_data()
    messages.success(request, "Model trained and loaded successfully")

    return redirect('bot_responses')


