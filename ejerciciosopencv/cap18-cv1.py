# build.py - Empaquetador profesional para proyectos AR
import PyInstaller.__main__
import os
import shutil
import sys

class EmpaquetadorAR:
    def __init__(self, nombre_app, script_principal, icono=None):
        self.nombre_app = nombre_app
        self.script_principal = script_principal
        self.icono = icono

    def obtener_datos_adicionales(self):
        """Busca automáticamente la carpeta assets y modelos necesarios"""
        datos = []
        if os.path.exists("assets"):
            for root, _, files in os.walk("assets"):
                for file in files:
                    src = os.path.join(root, file)
                    dst = os.path.join("assets", os.path.relpath(src, "assets"))
                    datos.append(f"{src};{dst}")
        return datos

    def empaquetar(self, modo="onefile"):
        # Limpiar builds anteriores
        for d in ["dist", "build"]:
            if os.path.exists(d):
                shutil.rmtree(d)

        args = [
            self.script_principal,
            f"--name={self.nombre_app}",
            "--noconfirm",
            "--clean",
            "--windowed",          # Sin consola negra
        ]

        if modo == "onefile":
            args.append("--onefile")

        if self.icono and os.path.exists(self.icono):
            args.append(f"--icon={self.icono}")

        for dato in self.obtener_datos_adicionales():
            args.append(f"--add-data={dato}")

        # Hidden imports importantes para AR
        hidden = ["cv2", "mediapipe", "numpy", "PyQt6", "mediapipe.python.solutions"]
        for imp in hidden:
            args.append(f"--hidden-import={imp}")

        print(f"🚀 Empaquetando {self.nombre_app}...")
        PyInstaller.__main__.run(args)
        print(f"\n✅ Ejecutable generado en: dist/{self.nombre_app}.exe")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python build.py <NombreApp> <script.py>")
        print("Ejemplo: python build.py AR_Catcher ejercicioopencv/cap16_reto.py")
        sys.exit(1)

    nombre = sys.argv[1]
    script = sys.argv[2]
    icono = sys.argv[3] if len(sys.argv) > 3 else None

    emp = EmpaquetadorAR(nombre, script, icono)
    emp.empaquetar()