import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ================= 0. 網頁基本設定 =================
st.set_page_config(page_title="麥克森干涉儀模擬", layout="wide")
st.title("🔬 麥克森干涉儀：雙模式互動模擬器")
st.markdown("透過左側控制面板調整參數，觀察實體儀器佈局與干涉圖紋的即時變化。")

# ================= 1. 核心計算函數 =================
def get_wl_color(wl):
    if 400 <= wl < 440: return 'purple'
    elif 440 <= wl < 490: return 'blue'
    elif 490 <= wl < 570: return 'green'
    elif 570 <= wl < 590: return 'yellow'
    elif 590 <= wl < 620: return 'orange'
    elif 620 <= wl <= 750: return 'red'
    return 'red'

@st.cache_data # Streamlit 加速神器，避免重複計算相同的數值
def calculate_intensity(wl, d_mm, D_m, mode, screen_size, resolution=400):
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

# ================= 2. 動態佈局繪製函數 =================
def draw_layout(wl, d, D, mode):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title(f"{mode} Setup & Parameters", fontsize=14, fontweight='bold')
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    
    if mode == 'Visible Light':
        beam_color = get_wl_color(wl)
        tx_name = "Laser"
        m2_max_d = 2.0  
        m1_name = "M1 (Fixed Mirror)"
        m2_name = "M2 (Movable Mirror)"
        screen_name = "Screen"
        wl_unit = "nm"
    else:
        beam_color = 'orange'
        tx_name = "Microwave Tx"
        m2_max_d = 150.0 
        m1_name = "M1 (Fixed Plate)"
        m2_name = "M2 (Movable Plate)"
        screen_name = "Detector Plane"
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
    return fig

# ================= 3. Streamlit 側邊欄 UI =================
with st.sidebar:
    st.header("⚙️ 參數控制面板")
    mode = st.radio("選擇實驗模式", ('Visible Light', 'Microwave'))
    st.divider()
    
    if mode == 'Visible Light':
        screen_size = 0.05
        wl = st.slider('Wavelength (波長, nm)', 400.0, 750.0, 632.8, step=0.1)
        d = st.slider('Path Diff (路徑差 d, mm)', 0.0, 2.0, 0.5, step=0.01)
        D = st.slider('Distance (螢幕距離 D, m)', 0.1, 3.0, 1.0, step=0.1)
    else:
        screen_size = 1.5
        wl = st.slider('Wavelength (波長, mm)', 10.0, 50.0, 28.5, step=0.1)
        d = st.slider('Path Diff (路徑差 d, mm)', 0.0, 150.0, 50.0, step=0.1)
        D = st.slider('Distance (螢幕距離 D, m)', 0.2, 3.0, 1.0, step=0.1)

# ================= 4. 主畫面佈局與渲染 =================
col1, col2 = st.columns(2)

# 左半部：佈局圖
with col1:
    fig_layout = draw_layout(wl, d, D, mode)
    st.pyplot(fig_layout)

# 右半部：干涉圖紋
with col2:
    fig_pattern, ax_pattern = plt.subplots(figsize=(6, 6))
    intensity = calculate_intensity(wl, d, D, mode, screen_size)
    ext = [-screen_size/2*100, screen_size/2*100, -screen_size/2*100, screen_size/2*100]
    
    if mode == 'Visible Light':
        current_color = get_wl_color(wl)
        custom_cmap = LinearSegmentedColormap.from_list('dynamic_laser', ['black', current_color])
        im = ax_pattern.imshow(intensity, cmap=custom_cmap, extent=ext)
    else:
        im = ax_pattern.imshow(intensity, cmap='viridis', extent=ext)
        
    ax_pattern.set_xlabel("X (cm)")
    ax_pattern.set_ylabel("Y (cm)")
    ax_pattern.set_title("Interference Pattern", fontsize=14, fontweight='bold')
    st.pyplot(fig_pattern)