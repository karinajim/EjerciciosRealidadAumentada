#!/usr/bin/env python3
"""
============================================================
app_mqtt_monitor.py
Proyecto: Monitor MQTT — Potenciómetro ESP32
Autor: Tacho — UTNG

App de escritorio PyQt6 que:
 ① Se suscribe al broker MQTT directamente (tiempo real)
 ② Lee el historial desde SQLite
 ③ Muestra gráfica en tiempo real + estadísticas + histograma

Requiere:
  pip install PyQt6 pyqtgraph numpy paho-mqtt
============================================================
"""

import sys
import json
import sqlite3
import csv
import math
import random
import time
import threading
from pathlib import Path
from datetime import datetime

import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QSpinBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QLineEdit, QStatusBar, QFileDialog, QFrame, QSplitter,
    QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QFont, QColor

import pyqtgraph as pg

# ── Rutas ────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DB_PATH  = BASE_DIR / "potenciometro.db"
CSV_PATH = BASE_DIR / "potenciometro.csv"

# ── MQTT ─────────────────────────────────────────────────────
DEFAULT_BROKER = "test.mosquitto.org"
DEFAULT_PORT   = 1883
TOPIC_SUB      = "kccj/lab/potenciometro"
TOPIC_STATUS   = "kccj/lab/status"

# ── Paleta ───────────────────────────────────────────────────
C = {
    "bg":      "#0d1117", "panel":  "#161b22", "card":   "#21262d",
    "border":  "#30363d", "accent": "#58a6ff", "green":  "#3fb950",
    "yellow":  "#d29922", "red":    "#f85149", "purple": "#bc8cff",
    "orange":  "#e8a838", "cyan":   "#39c5cf",
    "text":    "#e6edf3", "sub":    "#8b949e",
}

QSS = f"""
QMainWindow, QWidget {{ background:{C['bg']}; color:{C['text']};
    font-family:'Segoe UI','Ubuntu',sans-serif; font-size:12px; }}
QGroupBox {{ background:{C['card']}; border:1px solid {C['border']};
    border-radius:8px; margin-top:14px; padding:8px;
    font-weight:bold; font-size:11px; color:{C['accent']}; }}
QGroupBox::title {{ subcontrol-origin:margin; left:10px; padding:0 4px; }}
QPushButton {{ background:{C['accent']}; color:#000; border:none;
    border-radius:6px; padding:6px 14px; font-weight:bold; }}
QPushButton:hover {{ background:#79c0ff; }}
QPushButton#red {{ background:{C['red']}; color:#fff; }}
QPushButton#green {{ background:{C['green']}; color:#000; }}
QLineEdit, QSpinBox, QComboBox {{
    background:{C['panel']}; border:1px solid {C['border']};
    border-radius:4px; padding:4px 8px; color:{C['text']}; }}
QTableWidget {{ background:{C['panel']}; border:1px solid {C['border']};
    border-radius:6px; gridline-color:{C['border']};
    alternate-background-color:{C['card']}; }}
QTableWidget::item {{ padding:3px 8px; }}
QHeaderView::section {{ background:{C['card']}; color:{C['accent']};
    border:1px solid {C['border']}; padding:4px; font-weight:bold; }}
QStatusBar {{ background:{C['panel']}; color:{C['sub']};
    border-top:1px solid {C['border']}; }}
QTabWidget::pane {{ border:1px solid {C['border']};
    background:{C['panel']}; border-radius:6px; }}
QTabBar::tab {{ background:{C['card']}; color:{C['sub']};
    padding:7px 16px; border:1px solid {C['border']};
    border-bottom:none; border-radius:4px 4px 0 0; margin-right:2px; }}
QTabBar::tab:selected {{ background:{C['panel']}; color:{C['text']};
    border-bottom:2px solid {C['accent']}; }}
QProgressBar {{ background:{C['card']}; border:1px solid {C['border']};
    border-radius:4px; text-align:center; color:{C['text']}; height:16px; }}
QProgressBar::chunk {{ background:{C['accent']}; border-radius:3px; }}
"""

# ════════════════════════════════════════════════════════════
#  Worker MQTT  (corre en hilo separado)
# ════════════════════════════════════════════════════════════
class MQTTWorker(QObject):
    dato_recibido  = pyqtSignal(dict)   # payload JSON
    estado_cambio  = pyqtSignal(str, str)  # mensaje, color
    error_signal   = pyqtSignal(str)

    def __init__(self, broker, port):
        super().__init__()
        self.broker = broker
        self.port   = port
        self._client = None
        self._activo = True

    def run(self):
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            self.error_signal.emit("pip install paho-mqtt")
            return

        def on_connect(client, ud, flags, rc, props=None):
            if rc == 0:
                client.subscribe(TOPIC_SUB)
                client.subscribe(TOPIC_STATUS)
                self.estado_cambio.emit(
                    f"● MQTT conectado → {self.broker}", C['green'])
            else:
                self.estado_cambio.emit(f"✗ Error MQTT rc={rc}", C['red'])

        def on_message(client, ud, msg):
            try:
                payload = json.loads(msg.payload.decode())
                if msg.topic == TOPIC_SUB:
                    self.dato_recibido.emit(payload)
                else:
                    self.estado_cambio.emit(
                        f"[STATUS] {payload.get('estado','?')}", C['yellow'])
            except Exception as e:
                self.error_signal.emit(str(e))

        def on_disconnect(client, ud, rc, props=None):
            if rc != 0 and self._activo:
                self.estado_cambio.emit("⚡ Reconectando MQTT…", C['yellow'])

        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"pyqt_monitor_{random.randint(1000,9999)}",
            clean_session=True)
        client.on_connect    = on_connect
        client.on_message    = on_message
        client.on_disconnect = on_disconnect
        self._client = client

        self.estado_cambio.emit(f"⏳ Conectando a {self.broker}…", C['yellow'])
        try:
            client.connect(self.broker, self.port, keepalive=60)
            client.loop_forever()
        except Exception as e:
            self.estado_cambio.emit(f"✗ {e}", C['red'])

    def detener(self):
        self._activo = False
        if self._client:
            try:
                self._client.disconnect()
            except Exception:
                pass

# ════════════════════════════════════════════════════════════
#  Demo Worker  (sin hardware, genera datos cada 5 s)
# ════════════════════════════════════════════════════════════
class DemoWorker(QObject):
    dato_recibido = pyqtSignal(dict)
    estado_cambio = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self._activo = True
        self._muestra = 1

    def run(self):
        self.estado_cambio.emit("▶ MODO DEMO activo", C['purple'])
        t0 = time.time()
        while self._activo:
            t     = time.time() - t0
            base  = (math.sin(t / 20) + 1) / 2
            ruido = random.gauss(0, 0.03)
            pct   = max(0.0, min(100.0, (base + ruido) * 100))
            raw   = int(pct / 100 * 4095)
            volt  = round(raw / 4095 * 3.3, 3)
            self.dato_recibido.emit({
                "muestra": self._muestra,
                "raw":     raw,
                "voltaje": volt,
                "pct":     round(pct, 1),
                "ts_ms":   int((time.time() - t0) * 1000),
                "dispositivo": "DEMO"
            })
            self._muestra += 1
            for _ in range(50):
                if not self._activo:
                    break
                time.sleep(0.1)

    def detener(self):
        self._activo = False

# ════════════════════════════════════════════════════════════
#  Tarjeta de estadístico
# ════════════════════════════════════════════════════════════
class StatCard(QFrame):
    def __init__(self, titulo, color=C['accent']):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{ background:{C['card']}; border:1px solid {C['border']};
                border-left:3px solid {color}; border-radius:6px; padding:2px; }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 5, 10, 5)
        lay.setSpacing(1)
        self.t = QLabel(titulo.upper())
        self.t.setStyleSheet(f"color:{C['sub']};font-size:9px;font-weight:bold;border:none;")
        self.v = QLabel("—")
        self.v.setStyleSheet(f"color:{color};font-size:17px;font-weight:bold;border:none;")
        lay.addWidget(self.t)
        lay.addWidget(self.v)

    def set(self, val): self.v.setText(str(val))

# ════════════════════════════════════════════════════════════
#  Ventana Principal
# ════════════════════════════════════════════════════════════
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor MQTT — Potenciómetro ESP32  |  UTNG")
        self.setMinimumSize(1280, 800)

        # Estado interno
        self.datos_v   = []  # voltaje
        self.datos_raw = []
        self.datos_pct = []
        self.muestras  = []
        self._worker   = None
        self._thread   = None
        self._db_conn  = self._init_db()
        self._total_recibidos = 0

        self._build_ui()
        self._setup_graficas()

    # ── DB ────────────────────────────────────────────────────
    def _init_db(self):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cur  = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS lecturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, raw_value INTEGER,
                voltaje REAL, porcentaje REAL,
                muestra INTEGER, broker TEXT DEFAULT ''
            )
        """)
        conn.commit()
        return conn

    def _guardar(self, raw, voltaje, pct, muestra, broker="mqtt"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur = self._db_conn.cursor()
        cur.execute("""INSERT INTO lecturas
            (timestamp,raw_value,voltaje,porcentaje,muestra,broker)
            VALUES(?,?,?,?,?,?)""",
            (ts, raw, voltaje, pct, muestra, broker))
        self._db_conn.commit()
        nueva = not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if nueva:
                w.writerow(["id","timestamp","raw_value","voltaje",
                            "porcentaje","muestra","broker"])
            w.writerow([cur.lastrowid, ts, raw, round(voltaje,3),
                        round(pct,1), muestra, broker])

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(QSS)
        cw = QWidget()
        self.setCentralWidget(cw)
        root = QVBoxLayout(cw)
        root.setContentsMargins(10,10,10,6)
        root.setSpacing(6)

        # ── Barra superior ────────────────────────────────────
        top = QHBoxLayout()
        lbl_t = QLabel("📡  MONITOR MQTT — POTENCIÓMETRO ESP32")
        lbl_t.setStyleSheet(f"font-size:15px;font-weight:bold;color:{C['accent']};")

        self.lbl_estado = QLabel("○ Desconectado")
        self.lbl_estado.setStyleSheet(f"color:{C['sub']};font-size:11px;")

        self.lbl_topic = QLabel(f"Topic: {TOPIC_SUB}")
        self.lbl_topic.setStyleSheet(f"color:{C['sub']};font-size:10px;")

        top.addWidget(lbl_t)
        top.addStretch()
        top.addWidget(self.lbl_topic)
        top.addWidget(self.lbl_estado)
        root.addLayout(top)

        # ── Panel de conexión ─────────────────────────────────
        conn_grp = QGroupBox("Conexión MQTT")
        conn_lay = QHBoxLayout(conn_grp)

        conn_lay.addWidget(QLabel("Broker:"))
        self.inp_broker = QLineEdit(DEFAULT_BROKER)
        self.inp_broker.setFixedWidth(220)
        conn_lay.addWidget(self.inp_broker)

        conn_lay.addWidget(QLabel("Puerto:"))
        self.inp_port = QSpinBox()
        self.inp_port.setRange(1, 65535)
        self.inp_port.setValue(DEFAULT_PORT)
        self.inp_port.setFixedWidth(70)
        conn_lay.addWidget(self.inp_port)

        self.btn_connect = QPushButton("🔌 Conectar MQTT")
        self.btn_connect.clicked.connect(self._conectar_mqtt)

        self.btn_demo = QPushButton("▶ Modo Demo")
        self.btn_demo.setObjectName("green")
        self.btn_demo.clicked.connect(self._conectar_demo)

        self.btn_stop = QPushButton("⏹ Detener")
        self.btn_stop.setObjectName("red")
        self.btn_stop.clicked.connect(self._detener)
        self.btn_stop.setEnabled(False)

        btn_export = QPushButton("⬇ Exportar CSV")
        btn_export.setObjectName("green")
        btn_export.clicked.connect(self._exportar_csv)

        conn_lay.addWidget(self.btn_connect)
        conn_lay.addWidget(self.btn_demo)
        conn_lay.addWidget(self.btn_stop)
        conn_lay.addSpacing(20)
        conn_lay.addWidget(btn_export)
        conn_lay.addStretch()

        self.lbl_contador = QLabel("Recibidos: 0")
        self.lbl_contador.setStyleSheet(f"color:{C['green']};font-weight:bold;")
        conn_lay.addWidget(self.lbl_contador)
        root.addWidget(conn_grp)

        # ── Valores actuales (cards grandes) ──────────────────
        vals = QHBoxLayout()

        for attr, lbl, color, rng in [
            ("_card_volt",  "Voltaje (V)",   C['accent'],  "0.000 – 3.300"),
            ("_card_raw",   "ADC Raw",       C['green'],   "0 – 4095"),
            ("_card_pct",   "Porcentaje",    C['purple'],  "0.0 – 100.0 %"),
            ("_card_m",     "# Muestra",     C['orange'],  "acumulativo"),
        ]:
            g = QGroupBox(lbl)
            gl = QVBoxLayout(g)
            v = QLabel("—")
            v.setStyleSheet(f"font-size:32px;font-weight:bold;color:{color};")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            s = QLabel(rng)
            s.setStyleSheet(f"color:{C['sub']};font-size:10px;")
            s.setAlignment(Qt.AlignmentFlag.AlignCenter)
            gl.addWidget(v); gl.addWidget(s)
            setattr(self, attr, v)
            vals.addWidget(g)

        # Barra de progreso del potenciómetro
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFormat("%v%")
        self._progress.setFixedHeight(22)

        vals_w = QWidget()
        vals_vl = QVBoxLayout(vals_w)
        vals_vl.setContentsMargins(0,0,0,0)
        vals_vl.setSpacing(4)
        vals_vl.addLayout(vals)
        vals_vl.addWidget(self._progress)
        root.addWidget(vals_w)

        # ── Tabs ──────────────────────────────────────────────
        tabs = QTabWidget()
        root.addWidget(tabs, 1)

        tab_g = QWidget(); tabs.addTab(tab_g, "📈  Tiempo Real")
        self._build_tab_graficas(tab_g)

        tab_s = QWidget(); tabs.addTab(tab_s, "📊  Estadísticas")
        self._build_tab_stats(tab_s)

        tab_t = QWidget(); tabs.addTab(tab_t, "🗃  Historial")
        self._build_tab_tabla(tab_t)

        self.statusBar().showMessage(
            f"DB: {DB_PATH}  |  CSV: {CSV_PATH}  |  Topic: {TOPIC_SUB}")

    def _build_tab_graficas(self, parent):
        lay = QVBoxLayout(parent)
        lay.setContentsMargins(4,4,4,4); lay.setSpacing(4)

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Ventana (muestras):"))
        self.spin_win = QSpinBox()
        self.spin_win.setRange(5, 500); self.spin_win.setValue(60)
        ctrl.addWidget(self.spin_win)
        ctrl.addStretch()
        lay.addLayout(ctrl)

        self.pw = pg.GraphicsLayoutWidget()
        self.pw.setBackground(C['panel'])
        lay.addWidget(self.pw)

    def _build_tab_stats(self, parent):
        lay = QVBoxLayout(parent)
        lay.setContentsMargins(8,8,8,8); lay.setSpacing(6)

        top = QHBoxLayout()
        top.addWidget(QLabel("Variable:"))
        self.combo_var = QComboBox()
        self.combo_var.addItems(["Voltaje (V)", "RAW (0-4095)", "Porcentaje (%)"])
        top.addWidget(self.combo_var); top.addStretch()
        lay.addLayout(top)

        # Grid de cards estadísticos
        from PyQt6.QtWidgets import QGridLayout
        grid = QGridLayout(); grid.setSpacing(6)
        defs = [
            ("N muestras",      C['sub']),    ("Media",         C['accent']),
            ("Mediana",         C['accent']),  ("Moda (bin)",    C['purple']),
            ("Desv. Estándar",  C['yellow']),  ("Varianza",      C['yellow']),
            ("Mínimo",          C['green']),   ("Máximo",        C['red']),
            ("Rango",           C['sub']),     ("Q1  (25%)",     C['purple']),
            ("Q3  (75%)",       C['purple']),  ("IQR",           C['purple']),
            ("C.V. (%)",        C['yellow']),  ("Asimetría",     C['sub']),
        ]
        self._cards = []
        for i, (titulo, color) in enumerate(defs):
            c = StatCard(titulo, color)
            grid.addWidget(c, i // 4, i % 4)
            self._cards.append(c)
        lay.addLayout(grid)

        # Histograma
        grp = QGroupBox("Histograma")
        hl  = QVBoxLayout(grp)
        self.hist_pw = pg.PlotWidget(background=C['panel'])
        self._cfg_plot(self.hist_pw.plotItem, "Valor", "Frecuencia")
        hl.addWidget(self.hist_pw)
        lay.addWidget(grp, 1)

    def _build_tab_tabla(self, parent):
        lay = QVBoxLayout(parent); lay.setContentsMargins(4,4,4,4)
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Últimas:"))
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(10, 2000); self.spin_rows.setValue(50)
        btn_ref = QPushButton("🔄 Refrescar")
        btn_ref.clicked.connect(self._cargar_tabla)
        ctrl.addWidget(self.spin_rows); ctrl.addWidget(btn_ref); ctrl.addStretch()
        lay.addLayout(ctrl)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(
            ["ID","Timestamp","RAW","Voltaje (V)","Porcentaje (%)","Muestra","Broker"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        lay.addWidget(self.tabla)

    # ── Graficas ──────────────────────────────────────────────
    def _cfg_plot(self, p, xl="", yl=""):
        p.showGrid(x=True, y=True, alpha=0.25)
        p.setLabel("bottom", xl, color=C['sub'])
        p.setLabel("left",   yl, color=C['sub'])
        for ax in ("bottom","left"):
            p.getAxis(ax).setPen(pg.mkPen(C['border']))
            p.getAxis(ax).setTextPen(pg.mkPen(C['sub']))

    def _setup_graficas(self):
        pw = self.pw

        # Voltaje
        self.p1 = pw.addPlot(row=0, col=0, title="Voltaje (V)")
        self._cfg_plot(self.p1, "Muestra", "V")
        self.crv_v = self.p1.plot(pen=pg.mkPen(C['accent'], width=2))
        self.p1.setYRange(0, 3.6)
        self.p1.addItem(pg.InfiniteLine(pos=3.3, angle=0,
            pen=pg.mkPen(C['red'], style=Qt.PenStyle.DashLine),
            label="3.3V", labelOpts={"color":C['red'],"position":0.85}))
        self.p1.addItem(pg.InfiniteLine(pos=1.65, angle=0,
            pen=pg.mkPen(C['yellow'], style=Qt.PenStyle.DotLine, width=1)))

        # Porcentaje con relleno
        self.p2 = pw.addPlot(row=1, col=0, title="Porcentaje (%)")
        self._cfg_plot(self.p2, "Muestra", "%")
        self.crv_p = self.p2.plot(
            pen=pg.mkPen(C['purple'], width=2),
            fillLevel=0, brush=pg.mkBrush(188,140,255, 35))
        self.p2.setYRange(0, 105)

        pw.ci.layout.setRowStretchFactor(0, 1)
        pw.ci.layout.setRowStretchFactor(1, 1)

    # ── Conexión ──────────────────────────────────────────────
    def _lanzar_worker(self, worker):
        self._detener()
        self._worker = worker
        self._thread = QThread()
        worker.moveToThread(self._thread)
        self._thread.started.connect(worker.run)
        worker.dato_recibido.connect(self._on_dato)
        worker.estado_cambio.connect(self._on_estado)
        if hasattr(worker, "error_signal"):
            worker.error_signal.connect(
                lambda e: self._on_estado(f"✗ {e}", C['red']))
        self._thread.start()
        self.btn_stop.setEnabled(True)
        self.btn_connect.setEnabled(False)
        self.btn_demo.setEnabled(False)

    def _conectar_mqtt(self):
        b = self.inp_broker.text().strip() or DEFAULT_BROKER
        p = self.inp_port.value()
        self._lanzar_worker(MQTTWorker(b, p))

    def _conectar_demo(self):
        self._lanzar_worker(DemoWorker())

    def _detener(self):
        if self._worker:
            self._worker.detener()
        if self._thread:
            self._thread.quit()
            self._thread.wait(3000)
        self._worker = None
        self._thread = None
        self.btn_stop.setEnabled(False)
        self.btn_connect.setEnabled(True)
        self.btn_demo.setEnabled(True)
        self._on_estado("○ Desconectado", C['sub'])

    # ── Slots de datos ────────────────────────────────────────
    def _on_estado(self, msg, color):
        self.lbl_estado.setText(msg)
        self.lbl_estado.setStyleSheet(f"color:{color};font-size:11px;")

    def _on_dato(self, payload: dict):
        raw     = int(payload.get("raw", 0))
        voltaje = float(payload.get("voltaje", 0.0))
        pct     = float(payload.get("pct", 0.0))
        muestra = int(payload.get("muestra", 0))
        broker  = payload.get("dispositivo", "mqtt")

        # Guardar
        self._guardar(raw, voltaje, pct, muestra, broker)
        self._total_recibidos += 1

        # Acumular
        self.datos_v.append(voltaje)
        self.datos_raw.append(raw)
        self.datos_pct.append(pct)
        self.muestras.append(muestra)

        # Cards grandes
        self._card_volt.setText(f"{voltaje:.3f}")
        self._card_raw.setText(str(raw))
        self._card_pct.setText(f"{pct:.1f}%")
        self._card_m.setText(str(muestra))
        self._progress.setValue(int(pct))
        self.lbl_contador.setText(f"Recibidos: {self._total_recibidos}")

        # Graficas
        n = self.spin_win.value()
        xv = list(range(len(self.datos_v[-n:])))
        self.crv_v.setData(xv, self.datos_v[-n:])
        self.crv_p.setData(xv, self.datos_pct[-n:])

        # Stats y tabla (cada 5 datos o primer dato)
        if self._total_recibidos % 5 == 0 or self._total_recibidos == 1:
            self._actualizar_stats()
            self._cargar_tabla()

        self.statusBar().showMessage(
            f"DB: {DB_PATH}  |  {self._total_recibidos} recibidos  |  "
            f"Último: {datetime.now().strftime('%H:%M:%S')}  |  "
            f"Dispositivo: {broker}")

    # ── Estadísticas ──────────────────────────────────────────
    def _actualizar_stats(self):
        idx = self.combo_var.currentIndex()
        datos = [self.datos_v, self.datos_raw, self.datos_pct][idx]
        unidades = ["V", "raw", "%"][idx]
        if len(datos) < 2:
            return

        a = np.array(datos, dtype=float)
        n = len(a)
        mu    = np.mean(a)
        med   = np.median(a)
        std   = np.std(a, ddof=1)
        var   = std ** 2
        mn    = np.min(a)
        mx    = np.max(a)
        rng   = mx - mn
        q1,q3 = np.percentile(a, [25, 75])
        iqr   = q3 - q1
        cv    = (std / mu * 100) if mu != 0 else 0
        counts, bins = np.histogram(a, bins=min(20,n))
        moda  = (bins[np.argmax(counts)] + bins[np.argmax(counts)+1]) / 2
        skew  = 0.0
        if std > 0 and n > 2:
            skew = (n/((n-1)*(n-2))) * np.sum(((a-mu)/std)**3)

        f = lambda v, d=3: f"{v:.{d}f} {unidades}"
        vals = [str(n), f(mu), f(med), f(moda),
                f(std,4), f(var,4), f(mn), f(mx),
                f(rng), f(q1), f(q3), f(iqr),
                f"{cv:.1f}%", f"{skew:.4f}"]
        for card, val in zip(self._cards, vals):
            card.set(val)

        # Histograma
        self.hist_pw.clear()
        bw = bins[1] - bins[0]
        bar = pg.BarGraphItem(x=bins[:-1], height=counts, width=bw*0.85,
            brush=pg.mkBrush(88,166,255,150), pen=pg.mkPen(C['accent']))
        self.hist_pw.addItem(bar)
        self.hist_pw.addItem(pg.InfiniteLine(pos=mu, angle=90,
            pen=pg.mkPen(C['red'], style=Qt.PenStyle.DashLine, width=2),
            label=f"μ={mu:.3f}", labelOpts={"color":C['red'],"position":0.85}))
        self.hist_pw.addItem(pg.InfiniteLine(pos=med, angle=90,
            pen=pg.mkPen(C['yellow'], style=Qt.PenStyle.DotLine, width=2),
            label=f"M={med:.3f}", labelOpts={"color":C['yellow'],"position":0.70}))

    # ── Tabla ─────────────────────────────────────────────────
    def _cargar_tabla(self):
        n = self.spin_rows.value()
        try:
            cur = self._db_conn.cursor()
            rows = cur.execute(
                "SELECT id,timestamp,raw_value,voltaje,porcentaje,muestra,broker "
                "FROM lecturas ORDER BY id DESC LIMIT ?", (n,)).fetchall()
        except Exception:
            return
        self.tabla.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla.setItem(i, j, item)

    # ── Export ────────────────────────────────────────────────
    def _exportar_csv(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV", str(Path.home()/"potenciometro_export.csv"),
            "CSV (*.csv)")
        if not ruta:
            return
        cur  = self._db_conn.cursor()
        rows = cur.execute(
            "SELECT id,timestamp,raw_value,voltaje,porcentaje,muestra,broker "
            "FROM lecturas ORDER BY id ASC").fetchall()
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id","timestamp","raw_value","voltaje",
                        "porcentaje","muestra","broker"])
            w.writerows(rows)
        self.statusBar().showMessage(f"✓ Exportado: {ruta}  ({len(rows)} registros)")

    def closeEvent(self, event):
        self._detener()
        if self._db_conn:
            self._db_conn.close()
        event.accept()


# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Monitor MQTT — Potenciómetro")
    win = VentanaPrincipal()
    win.show()
    sys.exit(app.exec())