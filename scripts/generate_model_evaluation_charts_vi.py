from pathlib import Path

import matplotlib.pyplot as plt


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def setup_style():
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.titleweight"] = "bold"


def style_axis(ax):
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)


def ve_bieu_do_do_tre(output_dir: Path) -> Path:
    mo_hinh = ["SVM", "Vector RAG", "PageIndex"]
    do_tre_ms = [50.0, 321.6, 2255.6]
    mau = ["#0A9396", "#EE9B00", "#AE2012"]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(mo_hinh, do_tre_ms, color=mau)
    style_axis(ax)
    ax.set_title("So sanh do tre mo hinh")
    ax.set_ylabel("Thoi gian (ms) - cang thap cang tot")

    for bar, value in zip(bars, do_tre_ms):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(do_tre_ms) * 0.02, f"{value:.1f}", ha="center", va="bottom")

    fig.tight_layout()
    out = output_dir / "02_do_tre_ms_vi.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def ve_bieu_do_chat_luong(output_dir: Path) -> Path:
    mo_hinh = ["SVM", "Vector RAG", "PageIndex"]
    chi_so = [60.0, 80.8, 95.0]
    ghi_chu = ["Test accuracy", "Top similarity", "Reasoning confidence"]
    mau = ["#005F73", "#0A9396", "#CA6702"]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(mo_hinh, chi_so, color=mau)
    style_axis(ax)
    ax.set_ylim(0, 100)
    ax.set_title("Chi so chat luong cua cac mo hinh")
    ax.set_ylabel("Ty le (%)")

    for bar, value, note in zip(bars, chi_so, ghi_chu):
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()
        ax.text(x, y + 1.8, f"{value:.1f}%", ha="center", va="bottom")
        ax.text(x, 2.0, note, ha="center", va="bottom", fontsize=8, rotation=90, color="#444")

    fig.tight_layout()
    out = output_dir / "03_chat_luong_vi.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def ve_bieu_do_dung_luong(output_dir: Path) -> Path:
    mo_hinh = ["Vector RAG", "PageIndex"]
    dung_luong = [5.9, 1.2]
    mau = ["#E9D8A6", "#0A9396"]

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    bars = ax.bar(mo_hinh, dung_luong, color=mau)
    style_axis(ax)
    ax.set_title("Dung luong luu tru index/cache")
    ax.set_ylabel("Dung luong (MB)")

    for bar, value in zip(bars, dung_luong):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.1, f"{value:.1f} MB", ha="center", va="bottom")

    fig.tight_layout()
    out = output_dir / "04_dung_luong_vi.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def ve_bieu_do_ngu_canh(output_dir: Path) -> Path:
    phuong_phap = ["Vector RAG", "PageIndex"]
    so_ket_qua = [3, 6]
    mau = ["#BB3E03", "#0A9396"]

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    bars = ax.bar(phuong_phap, so_ket_qua, color=mau)
    style_axis(ax)
    ax.set_title("Do rong ngu canh truy hoi")
    ax.set_ylabel("So ket qua lien quan")

    for bar, value in zip(bars, so_ket_qua):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.08, str(value), ha="center", va="bottom")

    fig.tight_layout()
    out = output_dir / "05_do_rong_ngu_canh_vi.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def ve_bieu_do_so_sanh_rag_tong_hop(output_dir: Path) -> Path:
    """So sanh tong hop Vector RAG vs PageIndex tren cac tieu chi da co so lieu."""
    tieu_chi = [
        "Toc do\n(chuan hoa)",
        "Chat luong\ntruy hoi",
        "Hieu qua\ndung luong",
        "Do rong\nngu canh",
    ]

    # Nguon: PAGEINDEX_DOCUMENTATION.md
    vector_latency = 321.6
    pageindex_latency = 2255.6
    vector_storage = 5.9
    pageindex_storage = 1.2
    vector_context = 3
    pageindex_context = 6

    # Chuan hoa ve thang 0-100, gia tri cao hon la tot hon
    diem_vector = [
        100.0 * min(vector_latency, pageindex_latency) / vector_latency,
        80.8,
        100.0 * min(vector_storage, pageindex_storage) / vector_storage,
        100.0 * vector_context / max(vector_context, pageindex_context),
    ]
    diem_pageindex = [
        100.0 * min(vector_latency, pageindex_latency) / pageindex_latency,
        95.0,
        100.0 * min(vector_storage, pageindex_storage) / pageindex_storage,
        100.0 * pageindex_context / max(vector_context, pageindex_context),
    ]

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    x = range(len(tieu_chi))
    width = 0.36

    bars1 = ax.bar([i - width / 2 for i in x], diem_vector, width=width, color="#BB3E03", label="Vector RAG")
    bars2 = ax.bar([i + width / 2 for i in x], diem_pageindex, width=width, color="#0A9396", label="PageIndex")

    style_axis(ax)
    ax.set_ylim(0, 110)
    ax.set_xticks(list(x), tieu_chi)
    ax.set_title("So sanh tong hop hai mo hinh RAG (thang diem 0-100)")
    ax.set_ylabel("Diem chuan hoa")
    ax.legend(loc="upper right")

    for bars in [bars1, bars2]:
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x() + b.get_width() / 2, h + 1.2, f"{h:.1f}", ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    out = output_dir / "06_so_sanh_rag_tong_hop_vi.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def ve_bieu_do_mo_hinh_duoc_su_dung(output_dir: Path) -> Path:
    """Bieu do the hien cac mo hinh duoc dua vao phan so sanh."""
    mo_hinh = ["SVM", "BM25", "Vector RAG", "PageIndex"]
    su_dung = [1, 1, 1, 1]
    mau = ["#0A9396", "#CA6702", "#005F73", "#AE2012"]

    fig, ax = plt.subplots(figsize=(10, 5.4))
    bars = ax.bar(mo_hinh, su_dung, color=mau)
    ax.set_ylim(0, 1.25)
    ax.set_yticks([0, 1], ["Khong", "Co"])
    ax.set_title("Cac mo hinh duoc dua vao phan so sanh")
    ax.set_ylabel("Trang thai dua vao so sanh")
    style_axis(ax)

    for bar in bars:
        x = bar.get_x() + bar.get_width() / 2
        ax.text(x, 1.05, "Co trong phan so sanh", ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    out = output_dir / "01_mo_hinh_duoc_su_dung_vi.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def main():
    setup_style()
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "reports" / "model_evaluation"
    ensure_dir(out_dir)

    files = [
        ve_bieu_do_do_tre(out_dir),
        ve_bieu_do_chat_luong(out_dir),
        ve_bieu_do_dung_luong(out_dir),
        ve_bieu_do_ngu_canh(out_dir),
        ve_bieu_do_so_sanh_rag_tong_hop(out_dir),
        ve_bieu_do_mo_hinh_duoc_su_dung(out_dir),
    ]

    print("Da tao xong cac bieu do (ban tieng Viet):")
    for f in files:
        print(f"- {f}")


if __name__ == "__main__":
    main()
