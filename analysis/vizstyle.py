import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import io, os

SURFACE = "#faf8f2"; INK = "#171714"; INK2 = "#55534c"; MUTED = "#8a877d"; GRID = "#e6e1d6"
BLUE = "#2a78d6"; VERM = "#d9572b"; GREEN = "#1a9e6f"

def setup():
    plt.rcParams.update({
        "font.family": "Segoe UI", "font.size": 11,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK,
        "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 14,
        "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 10, "ytick.labelsize": 10,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "legend.frameon": False, "legend.fontsize": 10, "legend.labelcolor": INK2,
    })

def save(fig, path):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    buf.seek(0)
    Image.open(buf).convert("RGB").save(path, "WEBP", quality=88, method=6)
    print("saved", os.path.basename(path), os.path.getsize(path)//1024, "KB")
