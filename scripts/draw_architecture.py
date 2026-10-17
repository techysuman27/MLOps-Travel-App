"""Draw the implemented capstone architecture with deterministic, readable labels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/diagrams'
OUT.mkdir(exist_ok=True)
im = Image.new('RGB', (2500, 1830), '#f5f7fb')
d = ImageDraw.Draw(im)
regular = 'C:/Windows/Fonts/segoeui.ttf'
bold = 'C:/Windows/Fonts/segoeuib.ttf'
def font(size, strong=False): return ImageFont.truetype(bold if strong else regular, size)
def text(x,y,s,size=29,color='#334155',strong=False):
    d.text((x,y),s,font=font(size,strong),fill=color,spacing=12)
def label(x,y,s,color):
    bounds=d.textbbox((x,y),s,font=font(25))
    d.rectangle((bounds[0]-6,bounds[1]-4,bounds[2]+6,bounds[3]+4),fill='#f5f7fb')
    text(x,y,s,25,color)
def box(x,y,title,lines,color='#197b87',h=220):
    d.rounded_rectangle((x,y,x+500,y+h),radius=20,fill='white',outline='#d3dce8',width=2)
    d.rounded_rectangle((x,y,x+9,y+h),radius=4,fill=color)
    text(x+28,y+21,title,34,color,True)
    for i,line in enumerate(lines): text(x+28,y+78+i*37,line,27)
def arrow(points,color='#53657d',dashed=False,both=False):
    for a,b in zip(points,points[1:]):
        if not dashed: d.line([a,b],fill=color,width=5)
        else:
            length=math.dist(a,b)
            for n in range(0,int(length),22):
                p=n/length;q=min(n+12,length)/length
                d.line([(a[0]+(b[0]-a[0])*p,a[1]+(b[1]-a[1])*p),(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q)],fill=color,width=4)
    def head(a,b):
        angle=math.atan2(b[1]-a[1],b[0]-a[0])
        d.polygon([b,(b[0]-19*math.cos(angle-.48),b[1]-19*math.sin(angle-.48)),(b[0]-19*math.cos(angle+.48),b[1]-19*math.sin(angle+.48))],fill=color)
    head(points[-2],points[-1])
    if both: head(points[1],points[0])

text(70,45,'VOYAGE ANALYTICS',52,'#102b49',True)
text(70,115,'End-to-end architecture  |  Train once, serve many requests, improve through reviewed releases',30)
text(70,190,'A. MODEL DEVELOPMENT  •  Shared Python code, explained in three Colab notebooks',28,'#197b87',True)
box(70,245,'Course datasets',['flights.csv • users.csv','hotels.csv','Link users and trips safely.'])
box(680,245,'Validate & prepare',['Check schema; explore data.','Split train / validation / test.','Fit preprocessing on training.'])
box(1290,245,'Train & evaluate',['Flight-price regression','Educational label classification','Hotel recommendation ranking'])
box(1900,245,'Approve & save',['Select using validation scores.','Evaluate on the held-out test.','joblib + version + checksum'])
for x in [570,1180,1790]: arrow([(x,355),(x+110,355)])
text(70,600,'B. AUTOMATION & RELEASE  •  Administrative services run locally',28,'#7853a5',True)
box(70,655,'Airflow + PostgreSQL',['Weekly regression DAG','Validate → train → approve','New candidate stays isolated.'],'#7853a5')
box(680,655,'MLflow tracking',['Parameters, metrics, run IDs','Model versions and artifacts','Experiment record, not the API'],'#7853a5')
box(1290,655,'GitHub release source',['Application + shared code','Reviewed, approved bundles','Notebooks + infrastructure'],'#7853a5')
box(1900,655,'Jenkins + Docker',['Checkout → 13 tests → build','Image includes pinned models.','Run real prediction checks.'],'#7853a5')
arrow([(70,710),(15,710),(15,530),(930,530),(930,465)],'#7853a5',True)
text(80,485,'Orchestrates regression pipeline',25,'#7853a5')
arrow([(1540,465),(930,655)],'#7853a5',True)
label(1110,540,'Log experiments','#7853a5')
arrow([(2150,465),(1540,655)],'#b27618',True)
label(1770,540,'Reviewed handoff','#98600b')
arrow([(1790,765),(1900,765)])
text(70,980,'C. RUNNING APPLICATION  •  A user request performs inference; it does not retrain models',28,'#2563a6',True)
box(70,1040,'User',['Enter journey details','or hotel preferences.','Read the returned result.'],'#2563a6')
box(680,1040,'Streamlit interface',['Public: Community Cloud','Flights • hotels • insights','Educational classification lab'],'#2563a6')
box(1290,1040,'Flask prediction API',['Validate incoming JSON.','Load saved models at startup.','Return result + model version.'],'#2563a6')
box(1900,1010,'Deployment environments',['PUBLIC: Render Docker API','LOCAL: Jenkins Docker release','LOCAL: Kubernetes replicas','Kubernetes scaled manually.'],'#2563a6',h=285)
arrow([(2150,875),(2150,1010)])
text(1955,925,'Local CD verified',25,'#2563a6')
arrow([(1900,1150),(1790,1150)])
arrow([(570,1150),(680,1150)],both=True)
arrow([(1180,1150),(1290,1150)],both=True)
text(70,1310,'Input → Streamlit → Flask → saved model → result on screen',27,'#2563a6')
d.rounded_rectangle((680,1410,1790,1610),radius=20,fill='#e8eff7',outline='#bacbdf',width=2)
text(710,1430,'MONITOR, REVIEW & IMPROVE',33,'#102b49',True)
text(710,1480,'Request latency, errors and model version; historical drift reports.',27)
text(710,1520,'Actual later outcomes are needed to measure prediction accuracy.',27)
text(710,1560,'A reviewed retraining decision starts the next model-development cycle.',26)
arrow([(1540,1260),(1540,1410)])
arrow([(680,1510),(35,1510),(35,765),(70,765)],'#7853a5',True)
text(75,1430,'Human review',26,'#7853a5',True)
text(75,1470,'informs retraining',25,'#7853a5')
text(70,1660,'READ THE CONNECTIONS',27,'#102b49',True)
text(70,1704,'Solid arrows: data / software / requests.   Dashed arrows: orchestration, tracking or a reviewed handoff.',27)
text(70,1749,'Render is a separate public deployment. Jenkins-to-Kubernetes CD and automatic HPA scaling are not verified.',27,'#79551c')
im.save(OUT/'voyage-architecture.png',optimize=True)
im.save(OUT/'voyage-architecture.pdf','PDF',resolution=150)
print(OUT/'voyage-architecture.png')
