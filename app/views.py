from app import app
from flask import render_template
from flask import request
from camera.facerecognition.VideoCamera import VideoCamera
from flask import Flask, render_template, Response
import face_recognition
import cv2
from flask import Blueprint, current_app, send_file, url_for, jsonify
from flask import Flask, render_template, Response, jsonify, request, redirect
import numpy as np
import os
import requests
import sys
import qrtools
import qrcode
from qrcode import QRCode
from base64 import urlsafe_b64encode, urlsafe_b64decode
from mimetypes import types_map
from io import BytesIO
import cStringIO
# import qrtools
import pyqrcode

import zbar
from PIL import Image

import sys
sys.settrace


UPLOAD_FOLDER = '/home/tushalien/project/app/qrcodes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

video_camera = None
global_frame = None
face_rep = None
constituency = None
face_rep_times = 0
face_verified = None
frames_seen = 0

@app.route('/')
@app.route('/index')
def index():
    return render_template('landing.html')

# Register
@app.route('/preparation_registeration', methods=['GET'])
def preparation_registeration():
    return render_template('preparation_registeration.html')

@app.route('/register', methods=['GET'])
def register():
    global video_camera
    global face_rep_times
    global face_rep

    face_rep = None
    face_rep_times = 0

    if video_camera == None:
        video_camera = VideoCamera()
    face_rep_times = 0

    return render_template('register.html')

def qrcode_image(url):
    """The endpoint for generated QRCode image."""
    #print(url)
    # try:
    #     url = urlsafe_b64decode(url.encode('ascii'))
    # except (ValueError, UnicodeEncodeError):
    #     return jsonify(r=False, error='invalid_data'), 404

    image = make_qrcode_image(url,version=None)
    response = make_image_response(image, kind='png')
    return response

def make_qrcode_image(data, **kwargs):
    """Creates a QRCode image from given data."""
    qrcode = QRCode(**kwargs)
    qrcode.add_data(data)
    return qrcode.make_image()


def make_image_response(image, kind):
    """Creates a cacheable response from given image."""
    mimetype = types_map['.' + kind.lower()]
    io = BytesIO()
    image.save(io, kind.upper())
    io.seek(0)
    return send_file(io, mimetype=mimetype, conditional=True)

def stringifynumpy(p):
    stringify = ""
    shape = p.shape
    if len(p.shape) == 1:
        for i in range(shape[0]-1):
            stringify = stringify + str(p[i]) + ","
        stringify = stringify + str(p[i]) +";"
    else:
        for i in range(shape[0]):
            for j in range(shape[1]-1):
                stringify = stringify + str(p[i][j]) + ","
            stringify = stringify + str(p[i][j]) +";"

    #print(stringify)

    return stringify

@app.route('/qr_gen', methods=['GET'])
def qr_gen():
    global face_rep
    global constituency
    global name
    global ids
    import numpy as np
    import io

    content = stringifynumpy(face_rep)
    print "sdfgsd"
    content = ids+"&"+name + "&" + constituency + "&" + content
    print content
    response = qrcode_image(content)
    #qr = pyqrcode.create(content)
    #reqr.png("qr_"+ids+".png", scale=6)

    return response

@app.route('/complete_registeration', methods=['POST'])
def complete_registeration():
    global face_rep
    global ids
    global constituency
    global name

    ids = request.form['ido']
    constituency = request.form.get('constituency')
    name = request.form['name']

    # POST DATA ONTO BLOCKCHAIN
    return render_template('complete_registeration.html', idi = str(ids))

# Vote
@app.route('/preparation_vote_2', methods=['GET'])
def preparation_vote_2():
    return render_template('preparation_vote_2.html')

@app.route('/preparation_vote', methods=['GET'])
def preparation_vote():
    return render_template('preparation_vote.html')

@app.route('/complete_vote')
def complete_vote():
    global face_verified
    global face_rep_times
    global qrcode_detail

    if qrcode_detail != None:
        face_rep_times = 0

        if face_verified == True:
            # fetch vote
            # POST DATA ONTO BLOCKCHAIN
            return render_template('complete_vote.html',status = True, message = "Please Proceed")
    else:
            return render_template('complete_vote.html',status = False, message = "Failed the Face Verification. Please Retry")

def getConstituency(qrcode_detail):
    try:
        elements = qrcode_detail.split("&")
        return elements[2]
    except Exception as e:
        print(e)
        #print(qrcode_detail)
        return None

def getName(qrcode_detail):
    try:
        elements = qrcode_detail.split("&")
        return elements[1]
    except Exception as e:
        print(e)
        print(qrcode_detail)
        return None
    
def getID(qrcode_detail):
    try:
        elements = qrcode_detail.split("&")
        return elements[0]
    except Exception as e:
        print(e)
        print(qrcode_detail)
        return None
    
def getFaceEncoding(qrcode_detail):
    try:
        elements = qrcode_detail.split("&")
        string_numpy = elements[3]

        if string_numpy[-1]==";":
            string_numpy = string_numpy[:-1]

        rows = string_numpy.split(";")
        print(rows)
        num_rows = len(rows)

        if len(rows)>1:
            print("here")
            columns_row1 = rows[0].split(",")
            num_cols = len(columns_row1)
            numpy_array = np.array(np.zeros([num_rows,num_cols]))

            for row in range(len(rows)):
                columns = row.split(",")
                print(columns)
                for column in range(len(columns)):
                    numpy_array[row][column] = float(columns[column])

        else:
            num_rows = len(rows[0].split(","))
            num_cols = 1
            numpy_array = np.array(np.zeros(num_rows))

            rows = rows[0].split(',')
            for row in range(num_rows):
                try:
                    numpy_array[row] = float(rows[row])
                except Exception as e:
                    print(e)
                    print("ye - "+str(rows[row]))
            

        return numpy_array

    except Exception as e:
        print(e)
        print(qrcode_detail)
        return None

@app.route('/vote', methods=['GET'])
def vote():
    global video_camera
    global face_rep_times
    global qrcode_detail
    global face_verified

    if qrcode_detail != None:
        cons = getConstituency(qrcode_detail)
        ids = getID(qrcode_detail)
        name = getName(qrcode_detail)
        print name
        if video_camera == None:
            video_camera = VideoCamera()
        face_rep_times = 0
        face_verified = False
        return render_template('vote.html', constituency = cons, ids = ids, name = name)
    else:
        redirect('/preparation_vote')

@app.route('/scan_qr', methods=['GET'])
def scan_qr_get():
    global face_rep_times
    global qrcode_detail
    global frames_seen
    global face_verified

    frames_seen = 0
    qrcode_detail = None
    face_verified = False
    qrcode_detail = None
    return render_template('/scan_qr.html')

@app.route('/scan_qr', methods=['POST'])
def scan_qr_post():
    global face_rep_times
    global qrcode_detail
    global frames_seen
    global face_verified

    frames_seen = 0
    qrcode_detail = None
    face_verified = False

    #qrcode_detail = "AC98987878&Tushar Agrawal&Delhi&-0.159224867821,0.0961131304502,0.0806648805737,-0.0190040543675,0.00478628277779,-0.00189683120698,-0.0760209485888,-0.0222772955894,0.12480738014,-0.0947327464819,0.137215003371,0.0406793281436,-0.220997065306,-0.00102177634835,-0.070340000093,0.0954733639956,-0.137289196253,-0.125256210566,-0.0677188187838,-0.138273492455,0.0532022044063,0.043803177774,0.00489089637995,0.0475884824991,-0.137116998434,-0.316078811884,-0.0781381726265,-0.11543083936,-0.0406564325094,-0.0805452466011,0.028474137187,-0.0572183355689,-0.124757274985,0.0444896258414,-0.0289920698851,0.0578845739365,-0.0231432057917,-0.0520578250289,0.194136470556,0.0342295020819,-0.0845594704151,0.00536869000643,0.0336395166814,0.284532248974,0.174878165126,0.0646973848343,0.00684992130846,-0.0530644506216,0.131528690457,-0.28083050251,0.0388191603124,0.190147593617,0.026546234265,0.14211383462,0.0698419585824,-0.0969827473164,0.0510563068092,0.082145281136,-0.125917777419,0.0781889781356,-0.0149715701118,-0.0720971077681,0.00677150953561,-0.0293271094561,0.218069955707,0.101842686534,-0.151010781527,-0.0795929804444,0.0911204144359,-0.195250198245,-0.069269105792,0.0236312001944,-0.087544515729,-0.171684682369,-0.260465472937,0.0995862483978,0.392084568739,0.211553886533,-0.132674798369,0.0294713303447,-0.128424033523,-0.0150609947741,0.0833096504211,0.0616741552949,-0.114379473031,-0.0463977828622,-0.0848779603839,0.0126761011779,0.214710205793,0.0430870726705,-0.0722344741225,0.182654589415,0.0203853882849,0.0773385837674,0.0289880670607,0.0785187035799,-0.131176531315,-0.0361043810844,-0.0844457000494,0.0156937241554,-0.00129470229149,-0.0582292713225,0.00625693053007,0.0664530545473,-0.145363330841,0.146967947483,-0.00600379705429,-0.0319493561983,-0.0105505697429,0.120610244572,-0.162945210934,-0.0516600012779,0.125345110893,-0.224538087845,0.185971796513,0.204392194748,0.0473874993622,0.175246149302,0.11393918097,0.0970177352428,-0.0587824322283,0.00480561330914,-0.0874410569668,-0.0905140191317,0.0157949887216,0.0619117096066,0.0474206395447,0.0474206395447;"
    #img = Image.open(request.files['file'].stream)
    file= request.files['file']
    print file
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'tmp.png'))
    qr = qrtools.QR()
    #print img
    #print filejpeg
    qr.decode(os.path.join(app.config['UPLOAD_FOLDER'], 'tmp.png'))
    #d=qrcode.Decoder()
    #if d.decode(img):
    qrcode_detail="5465465&Tushar&Delhi&-0.0495916120708,0.0765787735581,0.067696288228,-0.00185435637832,-0.0961237177253,-0.0541219860315,-0.0378560200334,-0.0643333941698,0.0635630637407,-0.14944575727,0.190703302622,-0.0849248990417,-0.212411344051,-0.0545779243112,0.00517414230853,0.143908306956,-0.137282684445,-0.0825916975737,-0.117076039314,-0.0204648114741,0.0212376601994,0.0818788185716,-0.0138178169727,0.030203897506,-0.0357807800174,-0.422476023436,-0.100996427238,-0.0276237726212,0.0643376633525,-0.030958879739,-0.0345597788692,0.0907916426659,-0.0795990824699,0.0278644822538,0.0228782799095,0.0887546017766,-0.0802839994431,-0.0952682569623,0.27218323946,0.0287965126336,-0.197294443846,-0.0420974567533,0.0347473062575,0.267834812403,0.187448918819,0.0179196316749,0.0386308729649,-0.039673730731,0.106820292771,-0.183956369758,0.0530693233013,0.176048770547,0.108860686421,0.053188547492,0.0680315941572,-0.10069411993,0.0294233504683,0.0936746001244,-0.202828481793,0.0226983334869,0.063820078969,-0.197274416685,-0.0672511011362,-0.0435261316597,0.19834703207,0.0832170397043,-0.111383184791,-0.134986609221,0.176228433847,-0.232587575912,-0.0723108127713,-0.00347100943327,-0.113417230546,-0.142627000809,-0.332366198301,0.0283896960318,0.362740904093,0.152858451009,-0.159143313766,0.0394917353988,0.0561336576939,-0.0792196542025,0.181763038039,0.189951688051,-0.101901449263,-0.053762268275,-0.100524403155,0.0478805378079,0.17039078474,-0.0205693729222,-0.0590620040894,0.182348653674,0.00624072551727,0.0517818257213,0.0431927442551,-0.0211516208947,-0.0392688624561,-0.0245313458145,-0.0728645026684,0.0663744807243,0.110974699259,-0.130199953914,-0.0134525112808,0.10975651443,-0.114476025105,0.13093277812,-0.0225807335228,0.00758949387819,0.0699433609843,-0.0315348394215,-0.182845130563,-0.0685807392001,0.168767750263,-0.181571349502,0.128408908844,0.139952793717,0.0117177274078,0.132324159145,0.136322125793,0.12081155926,0.00384347885847,-0.0538321994245,-0.235101789236,-0.0691265240312,0.0668738558888,0.0187378935516,0.0782281756401,0.0782281756401;"
    #qrcode_detail = qr.data
    print qrcode_detail
    #else:
     #   print 'error: ' + d.error

    # # try:
    return redirect('/preparation_vote_2')
    # except Exception as e:
    #     print(e)
    #     qrcode_detail = None
    #     return render_template('/scan_qr.html')

    

def video_stream():
    global video_camera 
    global global_frame
    global face_rep
    global face_rep_times
        
    while face_rep_times < 50 and video_camera!= None:
        frame = video_camera.get_frame()
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        # while True:
        #     # Grab a single frame of video
        #     ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)

            face_names = []

            for face_encoding in face_encodings:

                # See if the face is a match for the known face(s)
                # match = face_recognition.compare_faces([obama_face_encoding], face_encoding)
                

                face_rep = face_encoding

                face_rep_times = face_rep_times + 1

                if face_rep_times < 45:
                  name = "Keep on Looking " + str(50 - face_rep_times)
                else:
                  name = "Done"
                face_names.append(name)

                break


        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            if face_rep_times < 45:
              # Draw a box around the face
              cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

              # Draw a label with a name below the face
              cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), -1)
              font = cv2.FONT_HERSHEY_DUPLEX
              cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            else:
              cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

              # Draw a label with a name below the face
              cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), -1)
              font = cv2.FONT_HERSHEY_DUPLEX
              cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            break

        ret, jpeg = cv2.imencode('.jpg', frame)
        #print frame

        if np.any(frame) != None:
            print "sdf"
            #global_frame = frame
            #ret, jpeg = cv2.imencode('.jpg', frame)
            #print ret
            #print type(jpeg)
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        else:
            print "else"
            ret, jpeg = cv2.imencode('.jpg', global_frame)
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + global_frame.tobytes() + b'\r\n\r\n')
    
    video_camera.__del__()
    print "adf"
    video_camera = None
    yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    #yield True

@app.route('/video_viewer')
def video_viewer():
    print "strating"
    view = video_stream()
    print "SFbetweeb"
    print view
    if view == True:
      print "adfagian"
      pass
    else:
      print "failed"
      return Response(view,
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_viewer_face')
def video_viewer_face():
    view = video_stream_find_face()
    if view == True:
      pass
    else:
      return Response(view,
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def video_stream_find_face():
    global video_camera 
    global global_frame
    global qrcode_detail
    global face_rep_times
    global face_verified
        
    while face_rep_times < 50 and video_camera!= None:
        frame = video_camera.get_frame()
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        # while True:
        #     # Grab a single frame of video
        #     ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)

            face_names = []

            for face_encoding in face_encodings:

                # See if the face is a match for the known face(s)
                face_rep = getFaceEncoding(qrcode_detail)
                name = getName(qrcode_detail)

                # if face_rep == None:
                #     text = "Invalid QR Mask"
                #     face_verified = False
                # else:
                match = face_recognition.compare_faces([face_rep], face_encoding)
                

                if match[0]:
                    text = name
                    face_verified = True
                else:
                    text = "Matching... "+str(50 - face_rep_times)
                    face_verified = False

                face_rep = face_encoding

                face_rep_times = face_rep_times + 1

                face_names.append(text)

                break


        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), face_name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            if face_name != name:
              # Draw a box around the face
              cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

              # Draw a label with a name below the face
              cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), -1)
              font = cv2.FONT_HERSHEY_DUPLEX
              cv2.putText(frame, face_name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            else:
              cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

              # Draw a label with a name below the face
              cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), -1)
              font = cv2.FONT_HERSHEY_DUPLEX
              cv2.putText(frame, face_name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            break

        #ret, jpeg = cv2.imencode('.jpg', frame)

        #if frame != None:
        global_frame = frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    # else:
    #         ret, jpeg = cv2.imencode('.jpg', global_frame)
    #         yield (b'--frame\r\n'
    #                         b'Content-Type: image/jpeg\r\n\r\n' + global_frame.tobytes() + b'\r\n\r\n')
    video_camera.__del__()
    video_camera = None
    yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

