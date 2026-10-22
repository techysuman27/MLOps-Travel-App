"""Render a plain-language map of the implemented workflow (PNG and PDF)."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/diagrams'
OUT.mkdir(exist_ok=True)
im = Image.new('RGB', (2200, 2260), '#f3f6fb')
d = ImageDraw.Draw(im)

def text(x, y, value, size=27, color='#334155', bold=False):
    name = 'segoeuib.ttf' if bold else 'segoeui.ttf'
    f = ImageFont.truetype('C:/Windows/Fonts/' + name, size)
    d.text((x, y), value, font=f, fill=color, spacing=10)

def panel(y, height, heading, color):
    d.rounded_rectangle((45, y, 2155, y + height), 24, fill='white', outline='#dce3ee', width=2)
    text(75, y + 22, heading, 34, color, True)

def box(x, y, title, lines, color='#167a70', width=455, height=190):
    d.rounded_rectangle((x, y, x + width, y + height), 16, fill='#f8fafc', outline=color, width=2)
    text(x + 20, y + 17, title, 30, color, True)
    for n, line in enumerate(lines):
        text(x + 20, y + 67 + n * 35, line, 25)

def arrow(points, color='#64748b'):
    d.line(points, fill=color, width=4)
    a, b = points[-2:]
    angle = math.atan2(b[1]-a[1], b[0]-a[0])
    d.polygon([b, (b[0]-17*math.cos(angle-.5), b[1]-17*math.sin(angle-.5)),
               (b[0]-17*math.cos(angle+.5), b[1]-17*math.sin(angle+.5))], fill=color)

xs = [80, 605, 1130, 1655]
text(65, 35, 'VOYAGE ANALYTICS', 49, '#15304f', True)
text(65, 105, 'How data becomes a working travel application', 33)
text(65, 155, 'Read from top to bottom. Within each numbered row, follow the arrows from left to right.', 26)

panel(220, 510, 'A. PREPARE AND TRAIN  |  Build the models before users make predictions', '#167a70')
box(xs[0], 300, '1. Collect the data', ['Flights: journeys and prices', 'Users: age, company, labels', 'Hotels: stays and bookings'])
box(xs[1], 300, '2. Check and prepare', ['Check columns and values.', 'Record the dataset version.', 'Split training / validation / test.'])
box(xs[2], 300, '3. Train and compare', ['Predict flight prices.', 'Classify source gender labels.*', 'Rank hotel suggestions.'])
box(xs[3], 300, '4. Evaluate and save', ['Choose using validation data.', 'Measure final test results.', 'Save model + preprocessing.'])
for x in xs[:-1]: arrow([(x+455, 395), (x+525, 395)])
text(85, 515, 'REUSABLE PYTHON CODE: src/voyage', 27, '#167a70', True)
text(85, 555, 'The notebooks and Airflow call the same training functions, so the logic stays consistent.', 26)
box(80, 610, 'Airflow: runs regression steps 2–4 in order', [], '#7853a5', 990, 80)
box(1120, 610, 'MLflow: records experiments and model versions', [], '#7853a5', 990, 80)

arrow([(1100, 730), (1100, 815)], '#b07820')
text(1140, 746, 'Human review: select the approved model for release', 25, '#936018')

panel(815, 610, 'B. PACKAGE AND DEPLOY  |  Turn the approved model into a running service', '#2563a6')
box(xs[0], 900, '5. GitHub repository', ['Approved model files', 'Flask API + Streamlit code', 'Tests + deployment settings'], '#2563a6')
box(xs[1], 900, '6. Jenkins checks', ['Get the repository code.', 'Run automated tests.', 'Start the Docker image build.'], '#2563a6')
box(xs[2], 900, '7. DOCKER image', ['Package API code, libraries', 'and approved model together.', 'Test predictions in a container.'], '#2563a6')
box(xs[3], 900, '8. Local deployment', ['Jenkins runs the tested image.', 'A local Flask API is available.', 'This deployment was verified.'], '#2563a6')
for x in xs[:-1]: arrow([(x+455, 995), (x+525, 995)])
text(85, 1120, 'SEPARATE DEPLOYMENT PATHS  |  These are not automatic stages of the verified Jenkins run', 26, '#2563a6', True)
box(80, 1170, 'Public demonstration', ['GitHub → Render builds/runs the Docker API.', 'GitHub → Streamlit Community Cloud runs the UI.', 'The public UI calls the public Render API.'], '#2563a6', 990, 200)
box(1120, 1170, 'Local Kubernetes demonstration', ['Load the API Docker image → run API replicas.', 'Verified: manually scale from 2 to 3 replicas.', 'Jenkins → Kubernetes and autoscaling: not verified.'], '#2563a6', 990, 200)

arrow([(1100, 1425), (1100, 1500)])
text(1140, 1440, 'Once deployed, the application can answer requests', 25)

panel(1500, 430, 'C. USE THE APPLICATION  |  What happens each time a user clicks Predict', '#a45d20')
box(xs[0], 1585, '9. User enters details', ['Journey details for a price,', 'or preferences for hotels.', 'Click the action button.'], '#a45d20')
box(xs[1], 1585, '10. Streamlit screen', ['Collect the form inputs.', 'Send a request to Flask.', 'Wait for the result.'], '#a45d20')
box(xs[2], 1585, '11. Flask API', ['Check the incoming inputs.', 'Use the saved model pipeline.', 'Create the prediction response.'], '#a45d20')
box(xs[3], 1585, '12. Result on screen', ['Flask sends the result back.', 'Streamlit displays the estimate', 'or hotel recommendations.'], '#a45d20')
for x in xs[:-1]: arrow([(x+455, 1680), (x+525, 1680)])
text(85, 1810, 'Request → saved model → response. This flow does not train a new model.', 29, '#a45d20', True)
text(85, 1860, 'Docker provides the API environment. The hosting service keeps the API running.', 26)

panel(1980, 170, 'D. OBSERVE AND IMPROVE', '#7853a5')
text(85, 2045, 'API logs: errors, response time and model version. Review data changes and later real outcomes.', 27)
text(85, 2090, 'Human review → decide whether to retrain → repeat A → review and release through B.', 27)
text(65, 2190, '* Classification is an educational source-label benchmark; it is not a reliable identity prediction.', 25)
im.save(OUT / 'voyage-architecture.png', optimize=True)
im.save(OUT / 'voyage-architecture.pdf', 'PDF', resolution=150)
print(OUT / 'voyage-architecture.png')
