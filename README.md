\# Smart Traffic \& Road Safety Monitoring System



A real-time computer vision system for traffic monitoring using YOLOv8, DeepSORT, and Streamlit.



\## Features

\- Vehicle detection and classification

\- Multi-object tracking with persistent IDs

\- Vehicle counting with direction tracking

\- Traffic density analysis

\- Speed estimation

\- Lane violation detection

\- Traffic heatmaps

\- Analytics dashboard



\## Tech Stack

\- Python, OpenCV, PyTorch, YOLOv8, DeepSORT

\- Streamlit Dashboard

\- SQLite Database



\## Run Locally



```bash

git clone https://github.com/ChidengeAnesu12/smart-traffic-monitor

cd smart-traffic-monitor

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

streamlit run dashboard/app.py

```



\## Project Structure



```

smart-traffic-monitor/

├── src/

│   ├── detection/      # YOLOv8 detector

│   ├── tracking/       # DeepSORT tracker

│   ├── counting/       # Vehicle counter

│   ├── analytics/      # Density, speed, heatmap

│   └── database/       # SQLite handler

├── dashboard/          # Streamlit app

├── tests/              # pytest test suite

└── configs/            # Configuration

```

