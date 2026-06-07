import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
# === 修改點 1：在最上方引入漸層色表工具 ===
from matplotlib.colors import LinearSegmentedColormap 

def interactive_dual_mode_michelson():
    # ================= 1. 初始狀態與變數 =================
    state = {
        'mode': 'Visible Light',
        'screen_size': 0.05,       
        'updating': False
    }
    
    resolution = 400   
    fig, (ax_layout, ax_pattern) = plt.subplots(1, 2, figsize=(13, 7.5))
    plt.subplots_adjust(top=0.85, bottom=0.22, left=0.05, right=0.95, wspace=0.25) 

    # ================= 2. 核心計算函數 =================
    def calculate_intensity(wl, d_mm, D_m, mode):
        if mode == 'Visible Light':
            wavelength = wl * 1e-9  
        else:
            wavelength = wl * 1e-3  
            
        d = d_mm * 1e-3             
        D = D_m                     
        
        x = np.linspace(-state['screen_size']/2, state['screen_size']/2, resolution)
        y = np.linspace(-state['screen_size']/2, state['screen_size']/2, resolution)
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

    # ================= 3. 動態佈局繪製函數 =================
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

    # ================= 4. 初始化繪圖與影像 =================
    ax_pattern.set_xlabel("X (cm)")
    ax_pattern.set_ylabel("Y (cm)")
    ax_pattern.set_title("Interference Pattern", fontsize=12, fontweight='bold')

    # ================= 5. 建立滑條控制項 (動態重建機制) =================
    ax_wl = plt.axes([0.15, 0.12, 0.70, 0.025])
    ax_d  = plt.axes([0.15, 0.07, 0.70, 0.025])
    ax_D  = plt.axes([0.15, 0.02, 0.70, 0.025])
    
    # 用一個字典來儲存當前的滑條物件
    controls = {}

    def update(val):
        if state['updating']: return
        
        current_wl = controls['wl'].val
        current_d = controls['d'].val
        current_D = controls['D'].val
        
        new_intensity = calculate_intensity(current_wl, current_d, current_D, state['mode'])
        im.set_data(new_intensity)
        
        # === 動態顏色邏輯 ===
        if state['mode'] == 'Visible Light':
            current_color = get_wl_color(current_wl)
            custom_cmap = LinearSegmentedColormap.from_list('dynamic_laser', ['black', current_color])
            im.set_cmap(custom_cmap)
        # ==========================
            
        draw_layout(ax_layout, current_wl, current_d, current_D, state['mode'])
        fig.canvas.draw_idle()

    def create_sliders(mode):
        """徹底清除舊滑條，重新繪製新的滑條，避免 Matplotlib 狀態錯亂"""
        ax_wl.clear()
        ax_d.clear()
        ax_D.clear()
        
        if mode == 'Visible Light':
            controls['wl'] = Slider(ax_wl, 'Wavelength (nm)', 400.0, 750.0, valinit=632.8, color='cyan')
            controls['d']  = Slider(ax_d,  'Path Diff $d$ (mm)', 0.0, 2.0, valinit=0.5, color='orange')
            controls['D']  = Slider(ax_D,  'Dist $D$ (m)', 0.1, 3.0, valinit=1.0, color='lightgreen')
        else:
            controls['wl'] = Slider(ax_wl, 'Wavelength (mm)', 10.0, 50.0, valinit=28.5, color='cyan')
            controls['d']  = Slider(ax_d,  'Path Diff $d$ (mm)', 0.0, 150.0, valinit=50.0, color='orange')
            controls['D']  = Slider(ax_D,  'Dist $D$ (m)', 0.2, 3.0, valinit=1.0, color='lightgreen')

        # 【介面美化】去除拉條邊框
        for key in ['wl', 'd', 'D']:
            slider = controls[key]
            slider.poly.set_edgecolor('none')
            if hasattr(slider, 'track'):
                slider.track.set_linewidth(0)
            # 重新綁定事件
            slider.on_changed(update)

        # 綁定到 fig 避免被記憶體回收
        fig.widgets = list(controls.values())

    # 首次啟動：建立可見光初始畫面
    create_sliders(state['mode'])
    init_intensity = calculate_intensity(controls['wl'].val, controls['d'].val, controls['D'].val, state['mode'])
    ext = [-state['screen_size']/2*100, state['screen_size']/2*100, -state['screen_size']/2*100, state['screen_size']/2*100]
    
    # === 修改點 2：讓程式一開啟就是完美的彩色漸層 ===
    init_color = get_wl_color(controls['wl'].val)
    init_cmap = LinearSegmentedColormap.from_list('dynamic_laser', ['black', init_color])
    im = ax_pattern.imshow(init_intensity, cmap=init_cmap, extent=ext)
    
    draw_layout(ax_layout, controls['wl'].val, controls['d'].val, controls['D'].val, state['mode'])

    # ================= 6. 建立模式切換單選鈕 =================
    ax_radio = plt.axes([0.4, 0.88, 0.2, 0.08], facecolor='lightgray')
    radio = RadioButtons(ax_radio, ('Visible Light', 'Microwave'), active=0)
    fig.radio_widget = radio  

    def change_mode(label):
        state['updating'] = True  # 開啟阻擋更新
        state['mode'] = label
        
        if label == 'Visible Light':
            state['screen_size'] = 0.05  
            # === 修改點 3：不再強制鎖死黑白，交給 update 去控制色彩 ===
        else: # Microwave
            state['screen_size'] = 1.5   
            im.set_cmap('viridis') 
            
        # 呼叫函數「重建滑條」
        create_sliders(label)
        
        # 更新右側影像的坐標軸邊界
        ext = [-state['screen_size']/2*100, state['screen_size']/2*100, -state['screen_size']/2*100, state['screen_size']/2*100]
        im.set_extent(ext)
        ax_pattern.set_xlim(ext[0], ext[1])
        ax_pattern.set_ylim(ext[2], ext[3])
        
        state['updating'] = False 
        update(None)              

    radio.on_clicked(change_mode)
    plt.show()

if __name__ == "__main__":
    interactive_dual_mode_michelson()