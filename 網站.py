import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ================= 1. Streamlit 網頁基本設定 =================
st.set_page_config(page_title="麥克森干涉儀模擬", layout="wide")
st.title("麥克森干涉儀雙模式互動模擬")

# ================= 2. 核心計算與輔助函數 (保留你的原始邏輯) =================
def calculate_intensity(wl, d_mm, D_m, mode, screen_size):
    resolution = 400
    if mode == 'Visible Light':
        wavelength = wl * 1e-9  
    else:
        wavelength = wl * 1e-3  
        
    d = d_mm * 1e-3             
    D = D_m                     
    
    x = np.linspace(-screen_size/2, screen_size/2, resolution)
    y = np.linspace(-screen_size/2, screen_size/2, resolution)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    
    theta = np.arctan(R / D)
    delta_L = 2 * d * np.cos(theta)
    phase_diff = (2 * np.pi / wavelength) * delta_L
    
    intensity = 2 + 2 * np.cos(phase_diff) 
    return intensity / 4.0

def get_wl_color(wl):
    if 400 <= wl < 440: return 'purple'
    elif 440 <= wl < 490: return 'blue'
    elif 490 <= wl < 570: return 'green'
    elif 570 <= wl < 590: return 'yellow'
    elif 590 <= wl < 620: return 'orange'
    elif 620 <= wl <= 750: return 'red'
    return 'red'

def draw_layout(ax, wl, d, D, mode):
    ax.clear()
    ax.set_title(f"{mode} Setup & Parameters", fontsize=12, fontweight='bold')
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    
    if mode == 'Visible Light':
        beam_color = get_wl_color(wl)
        tx_name = "Laser"
        m2_max_d = 2.0  
        m1_name = "M1 (Fixed)"
        m2_name = "M2 (Movable)"
        screen_name = "Screen"
        wl_unit = "nm"
    else:
        beam_color = 'orange'
        tx_name = "Microwave Tx"
        m2_max_d = 150.0 
        m1_name = "M1 (Fixed Plate)"
        m2_name = "M2 (Movable Plate)"
        screen_name = "Detector"
        wl_unit = "mm"
        
    ax.add_patch(plt.Rectangle((0.2, 4.5), 1.8, 1.0, facecolor='gray', edgecolor='black', zorder=3))
    ax.text(1.1, 5.0, tx_name, ha='center', va='center', color='white', fontweight='bold', fontsize=9)
    ax.plot([2.0, 4.5], [5.0, 5.0], color=beam_color, lw=3, zorder=1)
    
    ax.plot([4.1, 4.9], [4.6, 5.4], color='cyan', lw=5, alpha=0.7, zorder=3)
    ax.text(3.7, 5.4, "BS", fontweight='bold', color='darkcyan')
    
    ax.plot([4.0, 5.0], [8.0, 8.0], color='black', lw=4, zorder=3)
    ax.text(4.5, 8.3, m1_name, ha='center', fontweight='bold', fontsize=9)
    ax.plot([4.5, 4.5], [5.0, 8.0], color=beam_color, lw=3, zorder=1)
    
    m2_x = 6.2 + (d / m2_max_d) * 1.6
    ax.plot([m2_x, m2_x], [4.5, 5.5], color='black', lw=4, zorder=3)
    ax.text(m2_x, 5.8, m2_name, ha='center', fontweight='bold', fontsize=9)
    ax.plot([4.5, m2_x], [5.0, 5.0], color=beam_color, lw=3, zorder=1)
    
    ax.annotate('', xy=(8.2, 4.0), xytext=(6.0, 4.0), arrowprops=dict(arrowstyle='<->', color='orange', lw=1.5))
    ax.text(7.1, 3.5, "Path Diff $d$", ha='center', color='orange', fontsize=9)
    
    D_min, D_max = (0.1, 3.0) if mode == 'Visible Light' else (0.2, 3.0)
    screen_y = 3.2 - ((D - D_min) / (D_max - D_min)) * 2.0
    ax.plot([3.5, 5.5], [screen_y, screen_y], color='darkred', lw=4, zorder=3)
    ax.text(5.8, screen_y, screen_name, va='center', fontweight='bold', color='darkred', fontsize=9)
    ax.plot([4.5, 4.5], [5.0, screen_y], color=beam_color, lw=3, linestyle='--', zorder=1)
    
    ax.annotate('', xy=(3.0, 5.0), xytext=(3.0, screen_y), arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
    ax.text(2.2, (5.0 + screen_y)/2, "Dist $D$", va='center', color='green', fontsize=9)
    
    ax.text(0.5, 2.2, f"λ = {wl:.1f} {wl_unit}", fontsize=11, color='blue', fontweight='bold')
    ax.text(0.5, 1.5, f"d = {d:.3f} mm", fontsize=11, color='orange', fontweight='bold')
    ax.text(0.5, 0.8, f"D = {D:.2f} m", fontsize=11, color='green', fontweight='bold')


# ================= 3. Streamlit 介面與控制項 =================
# 將控制面版放在左側的 Sidebar
with st.sidebar:
    st.header("⚙️ 參數設定")
    mode = st.radio("選擇波長模式", ['Visible Light', 'Microwave'])
    
    st.markdown("---")
    
    # 根據不同模式，顯示不同的滑桿範圍
    if mode == 'Visible Light':
        wl = st.slider('Wavelength (nm)', 400.0, 750.0, 632.8, step=0.1)
        d = st.slider('Path Diff d (mm)', 0.0, 2.0, 0.5, step=0.01)
        D = st.slider('Dist D (m)', 0.1, 3.0, 1.0, step=0.1)
        screen_size = 0.05
        cmap = 'gray'
    else:
        wl = st.slider('Wavelength (mm)', 10.0, 50.0, 28.5, step=0.1)
        d = st.slider('Path Diff d (mm)', 0.0, 150.0, 50.0, step=0.1)
        D = st.slider('Dist D (m)', 0.2, 3.0, 1.0, step=0.1)
        screen_size = 1.5
        cmap = 'viridis'

# ================= 4. 繪圖與顯示 =================
# 建立 Matplotlib 畫布 (不保留原本 UI 的空間，純粹畫圖)
fig, (ax_layout, ax_pattern) = plt.subplots(1, 2, figsize=(12, 6))

# 畫左圖：佈局圖
draw_layout(ax_layout, wl, d, D, mode)

# 畫右圖：干涉條紋
intensity = calculate_intensity(wl, d, D, mode, screen_size)
ext = [-screen_size/2*100, screen_size/2*100, -screen_size/2*100, screen_size/2*100]
ax_pattern.imshow(intensity, cmap=cmap, extent=ext)
ax_pattern.set_xlabel("X (cm)")
ax_pattern.set_ylabel("Y (cm)")
ax_pattern.set_title("Interference Pattern", fontsize=12, fontweight='bold')

# 將設定好的 Matplotlib 圖表顯示到 Streamlit 網頁上
st.pyplot(fig)