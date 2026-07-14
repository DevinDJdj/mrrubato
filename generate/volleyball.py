import cv2
import torch
import os
import sys
import queue
import argparse
import warnings
import time
import copy
from my_utils import *
from tqdm import tqdm
from datetime import datetime, timedelta
from roboflow import Roboflow

###   supress warnings  ###
warnings.filterwarnings("ignore")
###################


### Parse Arguments ###
parser = argparse.ArgumentParser()

parser.add_argument("--input_path",
                    type=str,
                    default="assets/volleyball_15.mp4",
                    help="path to the video or image with volleyball in it")
parser.add_argument("--input_type",
                    type=str,
                    default='video',
                    choices=['image', 'video'],
                    help="type of the input - video or image")
parser.add_argument("--output_path",
                    type=str,
                    default="",
                    help="path for the output (.mp4 for videos and .jpg/.png for images), default new Output folder")
parser.add_argument("--model",
                    type=str,
                    default='roboflow',
                    choices=['roboflow', 'yolov7'],
                    help="which model to use for prediction")
parser.add_argument("--confidence",
                    type=float,
                    default=0.2,
                    help="prediction confidence")
parser.add_argument("--show",
                    action='store_true',
                    help="watch preview")
parser.add_argument("--marker",
                    type=str,
                    default='circle',
                    choices=['circle', 'box'],
                    help="how to highlight the ball")
parser.add_argument("--color",
                    type=str,
                    default='yellow',
                    choices=['black', 'white', 'red', 'green', 'purple',
                             'blue', 'yellow', 'cyan', 'gray', 'navy'],
                    help="color for highlighting the ball")
parser.add_argument("--no_trace",
                    action='store_true',
                    help="don't draw trajectory of the ball")
parser.add_argument('--gpu', default=False,
                    action='store_true', help='Whether to use GPU')


###################
args = parser.parse_args()

#if args.gpu:
#    torch.cuda.set_device(0)

input_path = args.input_path
output_path = args.output_path
input_type = args.input_type
model_name = args.model
conf = args.confidence
show = args.show
marker = args.marker
no_trace = args.no_trace
color = args.color

if color == 'yellow':
    color = [0, 255, 255]
elif color == 'black':
    color = [0, 0, 0]
elif color == 'white':
    color = [255, 255, 255]
elif color == 'red':
    color = [0, 0, 255]
elif color == 'green':
    color = [0, 255, 0]
elif color == 'blue':
    color = [255, 0, 0]
elif color == 'cyan':
    color = [255, 255, 0]
elif color == 'gray':
    color = [128, 128, 128]
elif color == 'purple':
    color = [128, 0, 128]
elif color == 'navy':
    color = [128, 0, 0]
###################


###    Start Time    ###
t1 = datetime.now()
###################


###    Start Time    ###
t1 = datetime.now()
###################


### Capture Video or Image ###
if input_type == 'video':
    input_data = cv2.VideoCapture(input_path)

    if (input_data.isOpened() == False):
        print("Error reading video file")
else:
    input_data = cv2.imread(input_path)

    if input_data is None:
        print("Error reading image file")
###################


### Output Writer ###
basename = os.path.basename(input_path)
extension = os.path.splitext(output_path)[1]

if output_path == "":  #
    os.makedirs('Output', exist_ok=True)
    if input_type == 'video':
        output_path = os.path.join(
            "Output", model_name + 'Detect' + '_' + basename)
    else:
        output_path = os.path.join(
            "Output", model_name + 'Detect' + '_' + basename.split('.')[0] + '.jpg')
else:  # check if user path exists, create otherwise
    f = os.path.split(output_path)[0]
    if not os.path.isdir(f) and (f != ''):
        os.makedirs(f)

if input_type == 'video':
    if (extension != '.mp4') and (extension != ''):
        raise Exception(
            f"Extention for output video should be `.mp4`, but got {extension}")

    fname = output_path
    fps = input_data.get(5)
    frame_width = int(input_data.get(3))
    frame_height = int(input_data.get(4))
    dims = (frame_width, frame_height)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    total_frames = input_data.get(cv2.CAP_PROP_FRAME_COUNT)
    output_writer = cv2.VideoWriter(fname, fourcc, fps, dims)
else:
    if (extension not in ['.jpg', '.png', '.jpeg']) and (extension != ''):
        raise Exception(
            f"Extension for output image should be .jpg or .png, but got {extension}")

    output_writer = output_path
###################


### Model Selection ###
if model_name == 'roboflow':
    #  API key, if doesn't work, refer -->
    #  https://github.com/shukkkur/VolleyVision/discussions/5#discussioncomment-7737081
    rf = Roboflow(api_key="INSERT YOUR OWN API_KEY")
    project = rf.workspace().project("volleyball-tracking")
    model = project.version(18).model
elif model_name == 'yolov7':
    model = custom(path_or_model='yV7-tiny/weights/best.pt')
    model.conf = conf

model = RoboYOLO(model_name, model, conf)
###################


### Trajectory of volleyball ###
q = queue.deque()  # we need to save the coordinate of previous 7 frames
for i in range(0, 8):
    q.appendleft(None)
###################


if input_type == 'video':
    pbar = tqdm(total=int(total_frames),
                bar_format='Processing: {desc}{percentage:3.0f}%|{bar:10}')




get_date_from_filename = lambda x: os.path.splitext(os.path.basename(x))[0].split('_')[-2]
get_time_from_filename = lambda x: os.path.splitext(os.path.basename(x))[0].split('_')[-1]
get_datetime_from_filename = lambda x: f"{get_date_from_filename(x)}_{get_time_from_filename(x)}"



def getTimestamp(fname, frame_number, fps):
    """
    Get timestamp of the frame
    """
    seconds = frame_number / fps
    try:
        start_date_time = datetime.strptime(get_datetime_from_filename(fname), '%Y%m%d_%H%M%S')
        start_time = start_date_time.timestamp()
    except:
        start_time = 0
    mytime = start_time + seconds
    timestampstr = datetime.fromtimestamp(mytime)
    date_time_str = timestampstr.strftime('%Y%m%d_%H%M%S')
    return date_time_str

#b.txt is ball transcript
transcript_file = output_path.replace('.mp4', 'b.txt') if input_type == 'video' else output_path.replace('.jpg', 'b.txt').replace('.png', 'b.txt')
### Process Video & Write Frames ###

#potentially load from last run..
ball_transcript = []
last_frame_no = 0
if os.path.exists(transcript_file):
    ball = {'..': 0, 'b': [0, 0, 0, 0], ':': 0}
    with open(transcript_file, 'rb') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(b'$$B='):
                bstring = line.decode('utf-8').strip().split('$$B=')[-1]
                stripped = bstring.strip('[]')
                ball['b'] = [float(x) for x in stripped.split(',')]
                #assume we have the same file..
                ball['..'] = getTimestamp(input_path, last_frame_no, fps)
                ball_transcript.append(ball['b'])
            elif line.startswith(b'$$:='):
                ball[':'] = int(line.decode('utf-8').strip().split('$$:=')[-1])
                last_frame_no = ball[':']
            elif line.startswith(b'$$'):
                pass



def get_confidence(prediction):
    try:
        x_min, y_min, x_max, y_max, confidence, class_id = prediction.pred[0].cpu().numpy()[
            0]        
    except:
        return -1
    return confidence

def get_class_id(prediction):
        try:
            x_min, y_min, x_max, y_max, confidence, class_id = prediction.pred[0].cpu().numpy()[
            0]        
        except:
            return -1
        return class_id

if input_type == 'video':

    with open(transcript_file, 'wb') as f:
        while input_data.isOpened():
            frame_no = int(input_data.get(cv2.CAP_PROP_POS_FRAMES))
            ret, image = input_data.read()
            if not ret:
                break
            debug_image = copy.deepcopy(image)

            if input_type == 'video':
                # Update Progress Bar
                pbar.update(1)

            pred = model.predict(image)
            conf = get_confidence(pred)
            class_id = get_class_id(pred)
            bbox = x_y_w_h(pred, model_name)

            if bbox != (0, 0, 0, 0):
                #write transcript of ball location..
                #we think we know..
                normalized_bbox = [bbox[0]/frame_width, bbox[1]/frame_height, bbox[2]/frame_width, bbox[3]/frame_height]
                rounded_bbox = [round(coord, 4) for coord in normalized_bbox]
                f.write(f"$${getTimestamp(input_path, frame_no, fps)}\n$$:={frame_no}\n$$_={class_id}\n$$~={round(conf, 2)}\n$$B={rounded_bbox}\n".encode())

                q.appendleft(bbox)
                q.pop()
            else:
                q.appendleft(None)
                q.pop()

            ### marker, color & trace ###
            for i in range(0, 8):
                if q[i] is not None:

                    if i == 0:  # current detection
                        if marker == 'box':
                            cv2.rectangle(debug_image, q[i], color, thickness=2)
                        elif marker == 'circle':
                            *center, r = get_circle(q[i])
                            cv2.circle(debug_image, center, r, color, 5)
                    elif (i != 0) and (no_trace is False):  # pass detections
                        if marker == 'box':
                            cv2.rectangle(debug_image, q[i], color, thickness=2)
                        elif marker == 'circle':
                            *center, r = get_circle(q[i])
                            try:
                                cv2.circle(debug_image, center, r-10, color, -1)
                            except:
                                cv2.circle(debug_image, center, r, color, -1)
            ###################

            output_writer.write(debug_image)
            ###################
            if show:
                cv2.imshow('preview', debug_image)

else:
    image = input_data
    debug_image = copy.deepcopy(image)

    pred = model.predict(image)
    bbox = x_y_w_h(pred, model_name)

    if bbox != (0, 0, 0, 0):
        q.appendleft(bbox)
        q.pop()
    else:
        q.appendleft(None)
        q.pop()

    ### marker, color & trace ###
    for i in range(0, 8):
        if q[i] is not None:

            if i == 0:  # current detection
                if marker == 'box':
                    cv2.rectangle(debug_image, q[i], color, thickness=2)
                elif marker == 'circle':
                    *center, r = get_circle(q[i])
                    cv2.circle(debug_image, center, r, color, 5)

            elif (i != 0) and (no_trace is False):  # pass detections
                if marker == 'box':
                    cv2.rectangle(debug_image, q[i], color, thickness=2)
                elif marker == 'circle':
                    *center, r = get_circle(q[i])
                    try:
                        cv2.circle(debug_image, center, r-10, color, -1)
                    except:
                        cv2.circle(debug_image, center, r, color, -1)
    ###################

    cv2.imwrite(output_writer, debug_image)


if input_type == 'video':
    input_data.release()
    output_writer.release()
    cv2.destroyAllWindows()
    pbar.close()

###     End Time     ###
t2 = datetime.now()
dt = t2 - t1
###################
print(f'Done - {dt.seconds/60:.2f} minutes')
