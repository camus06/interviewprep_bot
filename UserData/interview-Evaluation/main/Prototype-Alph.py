import streamlit as st
import json, os, random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def user_exists(uid):
    return os.path.exists(f"data/user_{uid}.json")

#User id and data 
def genId(l=6):
 chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
 return "".join(random.choice(chars) for _ in range(l))

def loadUsr(u):
 path=f"data/user_{u}.json"
 if os.path.exists(path):
  with open(path) as f:
   return json.load(f)
 return {"history":[]} 

# new user no data

def saveUsr(u,d):
 if not os.path.exists("data"): os.mkdir("data")
 with open(f"data/user_{u}.json","w") as f: json.dump(d,f,indent=2)


#Dummy score, to be replaced by groq
def evalAns(q,a):
 s={"Clarity":random.randint(5,9),
    "Tech":random.randint(5,9),
    "Comm":random.randint(5,9)}
 f={"Good":["nice structure","readable"],"Bad":["examples?","edges missed"],"Tips":["numbers?","details pls"]}
 t="maybe add small proj"
 return s,f,t

#Creation of PDF

def makePDF(fn,scores,fb,tip):
 c=canvas.Canvas(fn,pagesize=letter)
 w,h=letter
 y=h-50
 c.setFont("Helvetica-Bold",18)
 c.drawString(50,y,"Interview Feedback")
 y-=40
 c.setFont("Helvetica-Bold",14)
 c.drawString(50,y,"Scores:")
 c.setFont("Helvetica",12)
 for k,v in scores.items():
  y-=20
  c.drawString(70,y,f"{k}: {v}/10")
 for sec,its in fb.items():
  y-=30
  c.setFont("Helvetica-Bold",14)
  c.drawString(50,y,str(sec))
  c.setFont("Helvetica",12)
  for i in its:
   y-=20
   c.drawString(70,y,"- "+i)
 y-=30
 c.setFont("Helvetica-Bold",14)
 c.drawString(50,y,"Tip:")
 y-=20
 c.setFont("Helvetica",12)
 c.drawString(70,y,tip)
 c.save()

# main
st.title("Interview Helper")

# Login Page

if "usr" not in st.session_state:
    uid = st.text_input("User ID || leave blank for new")
    
    def user_exists(uid):
        return os.path.exists(f"data/user_{uid}.json")
    
    if st.button("Login"):
        if not uid:  # create new User id
            uid = genId()
            st.success("New ID generated: " + uid)
            st.session_state.usr = uid
            st.session_state.data = {"history": []}
            saveUsr(uid, st.session_state.data)
        else:
            if user_exists(uid):  # Existing User id
                st.success("Welcome back " + uid)
                st.session_state.data = loadUsr(uid)
                st.session_state.usr = uid
            else:  # user ID does not exist
                st.error("User ID does not exist. Please leave blank for new user or enter a valid ID.")
        
        if "usr" in st.session_state:  # proceed if login successful
            st.rerun()

else:
 usr=st.session_state.usr
 data=st.session_state.data
 st.write(f"logged in as {usr}")

 # Interview Questions

 if "qList" not in st.session_state:
  st.session_state.qList=[
   "Have you solved my hard problems?",
   "Can you fix things?",
   "what are your proud projects?"
  ]

  # Answers and Feedback
 if "idx" not in st.session_state: st.session_state.idx=0
 if "ansList" not in st.session_state: st.session_state.ansList=[]
 if "fbList" not in st.session_state: st.session_state.fbList=[]

 # resume
 if data["history"]:
  last=data["history"][-1]
  if not last.get("done",True):
   st.session_state.qList=last["questions"]
   st.session_state.idx=last.get("idx",0)
   st.session_state.ansList=last.get("answers",[])
   st.session_state.fbList=last.get("feedback",[])

 tab1,tab2=st.tabs(["Current session","History"])

 # current
 with tab1:
  if st.session_state.idx < len(st.session_state.qList):
    q = st.session_state.qList[st.session_state.idx]
    st.subheader(f"Q{st.session_state.idx+1}")
    st.write(q)
    # Persist answer in session state
    ans_key = f"a{st.session_state.idx}"
    if ans_key not in st.session_state:
        st.session_state[ans_key] = ""
    a = st.text_area("Please Answer here", value=st.session_state[ans_key], key=ans_key)
    # Submit Answer button logic
    if st.button("Submit Answer"):
        if not a.strip():
            st.warning("Please enter a non-empty answer before submitting.")
        else:
            s, f, t = evalAns(q, a)
            st.session_state.ansList.append(a)
            st.session_state.fbList.append((s, f, t))
            st.session_state.idx += 1
            # Save partial session
            snap = {
                "questions": st.session_state.qList,
                "answers": st.session_state.ansList,
                "feedback": st.session_state.fbList,
                "idx": st.session_state.idx,
                "done": False,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            if data["history"] and not data["history"][-1].get("done", True):
                data["history"][-1] = snap
            else:
                data["history"].append(snap)
            saveUsr(usr, data)
            st.session_state.data = data
            st.rerun()

  #-----------------#
  #PDF Downloader
  #-----------------#
  else:
         st.success("done with interview yay! 🎉")
         if data["history"]:
            data["history"][-1]["done"] = True
            saveUsr(usr, data)
         st.subheader("Feedback and Scores Summary")

         #Feedback and Scores

         for i, (s, f, t) in enumerate(st.session_state.fbList):
            st.write(f"Q{i+1}: {st.session_state.qList[i]}")
            st.write(f"A: {st.session_state.ansList[i]}")
            st.write("Scores:")
            col1, col2, col3 = st.columns(3)
            col1.metric("Clarity", f"{s.get('Clarity', s.get('Tech', 0))} / 10")
            col2.metric("Technical", f"{s.get('Tech', s.get('Clarity', 0))} / 10")
            col3.metric("Communication", f"{s.get('Comm', 0)} / 10")
            for k, v in s.items():
             st.write(f"**{k}**")
             st.progress(v / 10.0)
            st.write("Feedback:")
            for sec, its in f.items():
             st.write(f"{sec}:")
             for item in its:
                st.write(f"- {item}")
            st.write(f"Tip: {t}")
            st.write("______________________________________________________________")


         if st.button("Download PDF"):
            # Use last answer's scores/feedback/tip for PDF
            if st.session_state.fbList:
             s, f, t = st.session_state.fbList[-1]
             makePDF("rep.pdf", s, f, t)
             with open("rep.pdf", "rb") as fi:
                st.download_button("Download", fi, "Report.pdf")

 # history
 with tab2:
  st.subheader("Old sessions")
  if data["history"]:
   for i,sess in enumerate(data["history"]):
    avg=0
    try: avg=round(sum(sum(x[0].values())/len(x[0]) for x in sess["feedback"])/len(sess["feedback"]),2)
    except: pass
    st.write(f"Session {i+1} ({sess['date']}) avg={avg}")
    with st.expander(f"View"):
     for qi,(a,(s,f,t)) in enumerate(zip(sess["answers"],sess["feedback"])):
      st.write(f"Q{qi+1}: {sess['questions'][qi]}")
      st.write(f"Ans:{a}")
      st.write(f"Scores:{s}")
      st.write(f"Feedback:{f}")
      st.write(f"Tips:{t}")
  else: st.write("no old sessions yet")
