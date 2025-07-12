import os
import shutil
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import json
from pathlib import Path
import winreg
# 移除了ctypes导入，因为不再需要桌面刷新功能

class DesktopCleaner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("桌面整理工具")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        self.root.minsize(800, 700)
        
        # 获取桌面路径
        self.desktop_path = self.get_desktop_path()
        
        # 配置文件路径
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        
        # 默认配置（增强版，包含图标信息）
        self.config = {
            "excluded_extensions": [".lnk", ".url"],
            "max_file_size_mb": 100,
            "include_folders_in_organize": False,
            "include_folders_in_backup": False,
            "categories": {
                "📄 文档": {
                    "extensions": [".txt", ".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"],
                    "icon": "📄",
                    "color": "#3498db"
                },
                "🖼️ 图片": {
                    "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico"],
                    "icon": "🖼️",
                    "color": "#e74c3c"
                },
                "🎬 视频": {
                    "extensions": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
                    "icon": "🎬",
                    "color": "#9b59b6"
                },
                "🎵 音频": {
                    "extensions": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
                    "icon": "🎵",
                    "color": "#f39c12"
                },
                "📦 压缩包": {
                    "extensions": [".zip", ".rar", ".7z", ".tar", ".gz"],
                    "icon": "📦",
                    "color": "#95a5a6"
                },
                "💻 程序": {
                    "extensions": [".exe", ".msi", ".deb", ".dmg"],
                    "icon": "💻",
                    "color": "#2ecc71"
                },
                "📂 桌面文件夹": {
                    "extensions": ["__FOLDER__"],
                    "icon": "📂",
                    "color": "#f39c12"
                },
                "📁 其他": {
                    "extensions": [],
                    "icon": "📁",
                    "color": "#34495e"
                }
            }
        }
        
        # 加载配置
        self.load_config()
        
        # 备份记录文件
        self.backup_file = os.path.join(os.path.dirname(__file__), "backup_record.json")
        
        self.setup_ui()
        
    def get_desktop_path(self):
        """获取桌面路径"""
        try:
            # 从注册表获取桌面路径
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
            winreg.CloseKey(key)
            return desktop_path
        except:
            # 备用方法
            return os.path.join(os.path.expanduser("~"), "Desktop")
    
    # 移除了refresh_desktop方法，因为桌面刷新功能未能正常工作
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 配置标签页样式
        style = ttk.Style()
        style.configure('TNotebook.Tab', 
                       font=('微软雅黑', 12, 'bold'),
                       padding=[20, 10])
        
        # 主功能页面
        main_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(main_frame, text="🏠 主要功能")
        
        # 分类管理页面
        category_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(category_frame, text="🗂️分类管理")
        
        # 关于页面
        about_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(about_frame, text="ℹ️ 关于")
        
        self.setup_main_tab(main_frame)
        self.setup_category_tab(category_frame)
        self.setup_about_tab(about_frame)
    
    def setup_main_tab(self, parent):
        """设置主功能标签页"""
        # 主标题
        title_frame = tk.Frame(parent, bg="#2c3e50", height=80)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🗂️ 桌面整理工具", 
                              font=("微软雅黑", 20, "bold"), 
                              fg="white", bg="#2c3e50")
        title_label.pack(expand=True)
        
        # subtitle_label = tk.Label(title_frame, text="让您的桌面井然有序", 
        #                          font=("微软雅黑", 10), 
        #                          fg="#bdc3c7", bg="#2c3e50")
        # subtitle_label.pack()
        
        # 创建滚动框架
        canvas = tk.Canvas(parent, bg="#f8f9fa")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8f9fa")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加鼠标滚轮支持
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # 更新canvas窗口位置以居中显示
        def _configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 居中显示内容
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if canvas_width > frame_width:
                x_offset = (canvas_width - frame_width) // 2
                canvas.coords(canvas.find_all()[0], x_offset, 0)
        
        scrollable_frame.bind("<Configure>", _configure_scroll_region)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 主要功能按钮区域
        main_content = tk.Frame(scrollable_frame, bg="#f8f9fa", padx=20, pady=30)
        main_content.pack(fill="both", expand=True, padx=40)
        
        # 功能按钮容器
        button_container = tk.Frame(main_content, bg="#f8f9fa")
        button_container.pack(pady=(0, 30))
        
        # 功能按钮
        button_frame = tk.Frame(button_container, bg="#f8f9fa")
        button_frame.pack()
        
        # 一键整理按钮（修改了文本）
        clean_btn = tk.Button(button_frame, text="🗂️\n一键整理", 
                             font=("微软雅黑", 14, "bold"),
                             bg="#3498db", fg="white", 
                             relief="flat", bd=0,
                             width=12, height=4,
                             cursor="hand2",
                             command=self.clean_desktop)
        clean_btn.grid(row=0, column=0, padx=15, pady=10)
        
        # 一键恢复按钮
        restore_btn = tk.Button(button_frame, text="🔄\n一键恢复", 
                               font=("微软雅黑", 14, "bold"),
                               bg="#2ecc71", fg="white", 
                               relief="flat", bd=0,
                               width=12, height=4,
                               cursor="hand2",
                               command=self.restore_desktop)
        restore_btn.grid(row=0, column=1, padx=15, pady=10)
        
        # 备份桌面按钮
        backup_btn = tk.Button(button_frame, text="💾\n备份桌面", 
                              font=("微软雅黑", 14, "bold"),
                              bg="#e74c3c", fg="white", 
                              relief="flat", bd=0,
                              width=12, height=4,
                              cursor="hand2",
                              command=self.backup_desktop)
        backup_btn.grid(row=0, column=2, padx=15, pady=10)
        
        # 添加按钮悬停效果
        def create_hover_effect(button, normal_color, hover_color):
            def on_enter(e):
                button.config(bg=hover_color)
            def on_leave(e):
                button.config(bg=normal_color)
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        
        create_hover_effect(clean_btn, "#3498db", "#2980b9")
        create_hover_effect(restore_btn, "#2ecc71", "#27ae60")
        create_hover_effect(backup_btn, "#e74c3c", "#c0392b")
        
        # 设置区域
        settings_frame = tk.Frame(main_content, bg="#ffffff", relief="solid", bd=1)
        settings_frame.pack(fill="x", pady=(0, 20))
        
        # 设置标题
        settings_title = tk.Frame(settings_frame, bg="#34495e", height=40)
        settings_title.pack(fill="x")
        settings_title.pack_propagate(False)
        
        tk.Label(settings_title, text="⚙️ 基本设置", 
                font=("微软雅黑", 12, "bold"), 
                fg="white", bg="#34495e").pack(expand=True)
        
        # 设置内容
        settings_content = tk.Frame(settings_frame, bg="#ffffff", padx=20, pady=15)
        settings_content.pack(fill="x")
        
        # 排除扩展名设置
        ext_frame = tk.Frame(settings_content, bg="#ffffff")
        ext_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(ext_frame, text="🚫 排除的文件扩展名", 
                font=("微软雅黑", 10, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        
        # 设置默认值为.lnk
        default_exclude = ", ".join(self.config["excluded_extensions"]) if self.config["excluded_extensions"] else ".lnk"
        self.ext_var = tk.StringVar(value=default_exclude)
        ext_entry = tk.Entry(ext_frame, textvariable=self.ext_var, 
                            font=("微软雅黑", 10),
                            relief="flat", bd=1, 
                            highlightthickness=2, 
                            highlightcolor="#3498db")
        ext_entry.pack(fill="x", ipady=5)
        
        # 文件大小限制设置
        size_frame = tk.Frame(settings_content, bg="#ffffff")
        size_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(size_frame, text="📏 排除大于此大小的文件 (MB)", 
                font=("微软雅黑", 10, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        
        self.size_var = tk.StringVar(value=str(self.config["max_file_size_mb"]))
        size_entry = tk.Entry(size_frame, textvariable=self.size_var, 
                             font=("微软雅黑", 10),
                             relief="flat", bd=1, 
                             highlightthickness=2, 
                             highlightcolor="#3498db",
                             width=15)
        size_entry.pack(anchor="w", ipady=5)
        
        # 文件夹整理选项
        folder_organize_frame = tk.Frame(settings_content, bg="#ffffff")
        folder_organize_frame.pack(fill="x", pady=(0, 10))
        
        self.include_folders_organize_var = tk.BooleanVar(value=self.config.get("include_folders_in_organize", False))
        folder_organize_check = tk.Checkbutton(folder_organize_frame, 
                                              text="📁 整理时包含桌面文件夹", 
                                              variable=self.include_folders_organize_var,
                                              font=("微软雅黑", 10, "bold"), 
                                              fg="#2c3e50", bg="#ffffff",
                                              activebackground="#ffffff",
                                              activeforeground="#2c3e50")
        folder_organize_check.pack(anchor="w")
        
        # 文件夹备份选项
        folder_backup_frame = tk.Frame(settings_content, bg="#ffffff")
        folder_backup_frame.pack(fill="x", pady=(0, 15))
        
        self.include_folders_backup_var = tk.BooleanVar(value=self.config.get("include_folders_in_backup", False))
        folder_backup_check = tk.Checkbutton(folder_backup_frame, 
                                            text="📁 备份时包含桌面文件夹", 
                                            variable=self.include_folders_backup_var,
                                            font=("微软雅黑", 10, "bold"), 
                                            fg="#2c3e50", bg="#ffffff",
                                            activebackground="#ffffff",
                                            activeforeground="#2c3e50")
        folder_backup_check.pack(anchor="w")
        
        # 按钮区域
        button_area = tk.Frame(settings_content, bg="#ffffff")
        button_area.pack(fill="x", pady=(10, 0))
        
        # 保存设置按钮
        save_btn = tk.Button(button_area, text="💾 保存设置", 
                            font=("微软雅黑", 10, "bold"),
                            bg="#16a085", fg="white",
                            relief="flat", bd=0,
                            padx=20, pady=8,
                            cursor="hand2",
                            command=self.save_config)
        save_btn.pack(side="left", padx=(0, 10))
        
        # 导出配置按钮
        export_btn = tk.Button(button_area, text="📤 导出配置", 
                              font=("微软雅黑", 10, "bold"),
                              bg="#3498db", fg="white",
                              relief="flat", bd=0,
                              padx=20, pady=8,
                              cursor="hand2",
                              command=self.export_config)
        export_btn.pack(side="left", padx=(0, 10))
        
        # 导入配置按钮
        import_btn = tk.Button(button_area, text="📥 导入配置", 
                              font=("微软雅黑", 10, "bold"),
                              bg="#e74c3c", fg="white",
                              relief="flat", bd=0,
                              padx=20, pady=8,
                              cursor="hand2",
                              command=self.import_config)
        import_btn.pack(side="left")
        
        # 添加按钮悬停效果
        def create_button_hover(button, normal_color, hover_color):
            def on_enter(e):
                button.config(bg=hover_color)
            def on_leave(e):
                button.config(bg=normal_color)
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        
        create_button_hover(save_btn, "#16a085", "#138d75")
        create_button_hover(export_btn, "#3498db", "#2980b9")
        create_button_hover(import_btn, "#e74c3c", "#c0392b")
        
        # 配置代码说明
        config_info = tk.Frame(settings_content, bg="#ffffff")
        config_info.pack(fill="x", pady=(15, 0))
        
        tk.Label(config_info, text="💡 配置代码功能", 
                font=("微软雅黑", 10, "bold"), 
                fg="#2c3e50", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        
        info_text = "导出配置代码后，可以在任何设备上导入，快速恢复您的个性化设置。\n配置包括：文件分类规则、排除设置、文件大小限制等。"
        tk.Label(config_info, text=info_text, 
                font=("微软雅黑", 9), 
                fg="#7f8c8d", bg="#ffffff",
                justify="left", wraplength=600).pack(anchor="w")
        
        # 状态显示区域（折叠式）
        status_frame = tk.Frame(main_content, bg="#ffffff", relief="solid", bd=1)
        status_frame.pack(fill="x", pady=(0, 20))
        
        # 日志标题（可点击折叠）
        self.log_expanded = tk.BooleanVar(value=False)  # 默认收起
        log_title = tk.Frame(status_frame, bg="#34495e", height=40)
        log_title.pack(fill="x")
        log_title.pack_propagate(False)
        
        self.log_title_label = tk.Label(log_title, text="📋 操作日志 ▶", 
                font=("微软雅黑", 12, "bold"), 
                fg="white", bg="#34495e", cursor="hand2")
        self.log_title_label.pack(expand=True)
        self.log_title_label.bind("<Button-1>", self.toggle_log)
        
        # 日志内容框架（初始隐藏）
        self.log_frame = tk.Frame(status_frame, bg="#ffffff", padx=20, pady=15)
        
        self.status_text = tk.Text(self.log_frame, height=6, 
                                  font=("微软雅黑", 9),
                                  bg="#f8f9fa", fg="#2c3e50",
                                  relief="flat", bd=1,
                                  highlightthickness=1,
                                  highlightcolor="#bdc3c7")
        scrollbar = tk.Scrollbar(self.log_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 初始状态信息
        self.log_message(f"桌面路径: {self.desktop_path}")
        self.log_message("程序已启动，准备就绪！")
    
    def toggle_log(self, event=None):
        """切换日志显示状态"""
        if self.log_expanded.get():
            # 收起日志
            self.log_frame.pack_forget()
            self.log_title_label.config(text="📋 操作日志 ▶")
            self.log_expanded.set(False)
        else:
            # 展开日志
            self.log_frame.pack(fill="x", padx=40, pady=15)
            self.log_title_label.config(text="📋 操作日志 ▼")
            self.log_expanded.set(True)
    
    def setup_category_tab(self, parent):
        """设置分类管理标签页"""
        # 标题
        title_frame = tk.Frame(parent, bg="#2c3e50", height=80)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🗂️分类管理", 
                              font=("微软雅黑", 20, "bold"), 
                              fg="white", bg="#2c3e50")
        title_label.pack(expand=True)
        
        # 创建滚动框架
        canvas = tk.Canvas(parent, bg="#f8f9fa")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8f9fa")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加鼠标滚轮支持
        def _on_mousewheel_category(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel_category)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel_category)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 主内容区域
        content_frame = tk.Frame(scrollable_frame, bg="#f8f9fa", padx=30, pady=30)
        content_frame.pack(fill="both", expand=True)
        
        # 分类列表区域
        list_frame = tk.Frame(content_frame, bg="#ffffff", relief="solid", bd=1)
        list_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # 列表标题
        list_title = tk.Frame(list_frame, bg="#34495e", height=40)
        list_title.pack(fill="x")
        list_title.pack_propagate(False)
        
        tk.Label(list_title, text="📋 当前分类", 
                font=("微软雅黑", 12, "bold"), 
                fg="white", bg="#34495e").pack(expand=True)
        
        # 列表内容
        list_content = tk.Frame(list_frame, bg="#ffffff", padx=15, pady=15)
        list_content.pack(fill="both", expand=True)
        
        # 创建Treeview来显示分类（移除颜色列）
        columns = ("分类名称", "扩展名")
        
        # 配置Treeview样式
        style = ttk.Style()
        style.configure("Treeview", font=("微软雅黑", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("微软雅黑", 12, "bold"))
        
        self.category_tree = ttk.Treeview(list_content, columns=columns, show="headings", height=10)

        
        # 设置列标题和宽度
        self.category_tree.heading("分类名称", text="分类名称")
        self.category_tree.heading("扩展名", text="支持扩展名")
        
        self.category_tree.column("分类名称", width=250)
        self.category_tree.column("扩展名", width=380)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(list_content, orient="vertical", command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.category_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # 操作按钮区域
        button_frame = tk.Frame(content_frame, bg="#f8f9fa")
        button_frame.pack(fill="x")
        
        # 创建居中容器
        button_container = tk.Frame(button_frame, bg="#f8f9fa")
        button_container.pack(expand=True)
        
        add_btn = tk.Button(button_container, text="➕ 添加分类", 
                           font=("微软雅黑", 13, "bold"),
                           bg="#27ae60", fg="white",
                           relief="flat", bd=0,
                           padx=25, pady=12,
                           cursor="hand2",
                           command=self.add_category)
        add_btn.pack(side="left", padx=(0, 15))
        
        edit_btn = tk.Button(button_container, text="✏️ 编辑分类", 
                            font=("微软雅黑", 13, "bold"),
                            bg="#f39c12", fg="white",
                            relief="flat", bd=0,
                            padx=25, pady=12,
                            cursor="hand2",
                            command=self.edit_category)
        edit_btn.pack(side="left", padx=(0, 15))
        
        delete_btn = tk.Button(button_container, text="🗑️ 删除分类", 
                              font=("微软雅黑", 13, "bold"),
                              bg="#e74c3c", fg="white",
                              relief="flat", bd=0,
                              padx=25, pady=12,
                              cursor="hand2",
                              command=self.delete_category)
        delete_btn.pack(side="left")
        
        # 添加按钮悬停效果
        def create_hover_effect(button, normal_color, hover_color):
            def on_enter(e):
                button.config(bg=hover_color)
            def on_leave(e):
                button.config(bg=normal_color)
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        
        create_hover_effect(add_btn, "#27ae60", "#229954")
        create_hover_effect(edit_btn, "#f39c12", "#e67e22")
        create_hover_effect(delete_btn, "#e74c3c", "#c0392b")
        
        # 刷新分类列表
        self.refresh_category_list()
    
    def refresh_category_list(self):
        """刷新分类列表"""
        # 清空现有项目
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        
        # 添加分类项目
        for category_name, category_info in self.config["categories"].items():
            extensions = ", ".join(category_info["extensions"][:5])  # 只显示前5个扩展名
            if len(category_info["extensions"]) > 5:
                extensions += "..."
            
            # 使用原始分类名称，不进行额外的空格处理
            clean_name = category_name
            
            self.category_tree.insert("", "end", values=(
                clean_name,
                extensions
            ))
    
    def add_category(self):
        """添加新分类"""
        self.show_category_dialog()
    
    def edit_category(self):
        """编辑选中的分类"""
        selection = self.category_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的分类")
            return
        
        item = self.category_tree.item(selection[0])
        category_name = item["values"][0]
        self.show_category_dialog(category_name)
    
    def delete_category(self):
        """删除选中的分类"""
        selection = self.category_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的分类")
            return
        
        item = self.category_tree.item(selection[0])
        category_name = item["values"][0]
        
        if category_name == "📁 其他":
            messagebox.showwarning("警告", "不能删除'其他'分类")
            return
        
        if messagebox.askyesno("确认", f"确定要删除分类'{category_name}'吗？"):
            del self.config["categories"][category_name]
            self.save_config()
            self.refresh_category_list()
    
    def show_category_dialog(self, edit_category=None):
        """显示分类编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑分类" if edit_category else "添加分类")
        dialog.geometry("600x700")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg="#f8f9fa")
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"600x700+{x}+{y}")
        
        # 主框架
        main_frame = tk.Frame(dialog, bg="#f8f9fa", padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # 标题
        title_text = "✏️ 编辑分类" if edit_category else "➕ 添加分类"
        title_label = tk.Label(main_frame, text=title_text, 
                              font=("微软雅黑", 18, "bold"), 
                              fg="#2c3e50", bg="#f8f9fa")
        title_label.pack(pady=(0, 20))
        
        # 分类名称
        name_frame = tk.Frame(main_frame, bg="#f8f9fa")
        name_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(name_frame, text="📝 分类名称", 
                font=("微软雅黑", 12, "bold"), 
                fg="#34495e", bg="#f8f9fa").pack(anchor="w", pady=(0, 5))
        
        name_var = tk.StringVar()
        name_entry = tk.Entry(name_frame, textvariable=name_var, 
                             font=("微软雅黑", 11), 
                             relief="flat", bd=1, 
                             highlightthickness=2, 
                             highlightcolor="#3498db")
        name_entry.pack(fill="x", ipady=8)
        
        # 图标选择 - 下拉式
        icon_frame = tk.Frame(main_frame, bg="#f8f9fa")
        icon_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(icon_frame, text="🎨 选择图标", 
                font=("微软雅黑", 12, "bold"), 
                fg="#34495e", bg="#f8f9fa").pack(anchor="w", pady=(0, 5))
        
        icon_var = tk.StringVar()
        
        # 图标选择按钮和下拉面板
        icon_select_frame = tk.Frame(icon_frame, bg="#f8f9fa")
        icon_select_frame.pack(fill="x")
        
        icon_button = tk.Button(icon_select_frame, text="📁 点击选择图标 ▼", 
                               font=("微软雅黑", 11), 
                               bg="#ecf0f1", fg="#2c3e50", 
                               relief="flat", bd=1, 
                               padx=15, pady=8)
        icon_button.pack(fill="x")
        
        # 图标下拉面板（初始隐藏）
        icon_panel = tk.Frame(icon_frame, bg="#ffffff", relief="solid", bd=1)
        icon_panel_visible = False  # 默认收起状态
        
        # 预定义图标库
        icon_library = [
            # 办公文档类
            "📄", "📝", "📋", "📊", "📈", "📉", "📑", "📒", "📓", "📔",
            "📇", "📌", "📍", "📎", "🖇️", "📏", "📐", "✂️", "🗃️", "🗄️",
            "🗂️", "📁", "📂", "📦", "📫", "📪", "📬", "📭", "📮", "✉️",
            
            # 软件应用类
            "💻", "🖥️", "📱", "⌨️", "🖱️", "🖨️", "📠", "☎️", "📞", "📟",
            "💾", "💿", "📀", "💽", "🔌", "🔋", "⚡", "🔗", "⛓️", "🌐",
            "📡", "📶", "📳", "📴", "🔍", "🔎", "💡", "🔦", "🕯️", "🪔",
            
            # 设计创意类
            "🖼️", "🎨", "🖌️", "🖍️", "✏️", "✒️", "🖊️", "🖋️", "📷", "📸",
            "🎭", "🌅", "🌄", "🎪", "🎦", "📺", "🎬", "🎥", "📹", "🎞️",
            "📽️", "📻", "🎙️", "🎚️", "🎛️", "⏱️", "⏰", "⏲️", "🕰️", "⌚",
            
            # 音频媒体类
            "🎵", "🎶", "🎼", "🎤", "🎧", "🔊", "🔉", "🔈", "📢", "📯",
            "🥁", "🎺", "🎷", "🎸", "🎹", "🎻", "🪕", "🪗", "🪘", "🎪",
            
            # 工具系统类
            "🔧", "🔨", "⚙️", "🛠️", "⚒️", "🔩", "⛏️", "🪓", "🔪", "⚔️",
            "🛡️", "🔐", "🔒", "🔓", "🔑", "🗝️", "🔏", "📜", "📃", "📋",
            
            # 学习教育类
            "📚", "📖", "📗", "📘", "📙", "📕", "📰", "🗞️", "🎓", "🏫",
            "✏️", "📝", "📐", "📏", "🧮", "🔬", "🔭", "⚗️", "🧪", "🧬",
            
            # 游戏娱乐类
            "🎮", "🕹️", "🎯", "🎲", "🃏", "🎰", "🎳", "🏀", "⚽", "🏈",
            "🎾", "🏐", "🏓", "🏸", "🥅", "🏒", "🏑", "🥍", "🏏", "⛳",
            
            # 自然元素类
            "🌟", "⭐", "✨", "💫", "🌙", "☀️", "🌈", "☁️", "⛅", "🌤️",
            "🌍", "🌎", "🌏", "🗺️", "🧭", "🏔️", "⛰️", "🌋", "🏕️", "🏖️",
            
            # 食物饮品类
            "🍎", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐", "🍈", "🍒",
            "☕", "🍵", "🧃", "🥤", "🍷", "🍺", "🍻", "🥂", "🍾", "🧊",
            
            # 交通工具类
            "🚗", "🚕", "🚙", "🚌", "🚎", "🏎️", "🚓", "🚑", "🚒", "🚐",
            "✈️", "🛩️", "🚁", "🚂", "🚆", "🚄", "🚅", "🚈", "🚝", "🚞",
            
            # 建筑场所类
            "🏠", "🏡", "🏢", "🏣", "🏤", "🏥", "🏦", "🏨", "🏩", "🏪",
            "🏬", "🏭", "🏯", "🏰", "🗼", "🗽", "⛪", "🕌", "🛕", "🕍",
            
            # 装饰符号类
            "💎", "💍", "👑", "🎁", "🎀", "🎊", "🎉", "🎈", "🎂", "🍰",
            "🔥", "💧", "❄️", "⚡", "🌪️", "🌊", "💨", "☄️", "🌠", "🎆"
        ]
        
        def toggle_icon_panel():
            nonlocal icon_panel_visible
            if icon_panel_visible:
                icon_panel.pack_forget()
                icon_button.config(text=f"{icon_var.get() or '📁'} 点击选择图标 ▼")
                icon_panel_visible = False
            else:
                icon_panel.pack(fill="x", pady=(5, 0))
                icon_button.config(text=f"{icon_var.get() or '📁'} 点击选择图标 ▲")
                icon_panel_visible = True
        
        icon_button.config(command=toggle_icon_panel)
        
        # 创建图标网格容器（带滚动条）
        icon_container = tk.Frame(icon_panel, bg="#ffffff")
        icon_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 创建Canvas和滚动条
        icon_canvas = tk.Canvas(icon_container, bg="#ffffff", height=200)
        icon_scrollbar = tk.Scrollbar(icon_container, orient="vertical", command=icon_canvas.yview)
        icon_grid_frame = tk.Frame(icon_canvas, bg="#ffffff")
        
        icon_grid_frame.bind(
            "<Configure>",
            lambda e: icon_canvas.configure(scrollregion=icon_canvas.bbox("all"))
        )
        
        icon_canvas.create_window((0, 0), window=icon_grid_frame, anchor="nw")
        icon_canvas.configure(yscrollcommand=icon_scrollbar.set)
        
        # 添加鼠标滚轮支持
        def _on_mousewheel_icon(event):
            icon_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        icon_canvas.bind("<MouseWheel>", _on_mousewheel_icon)
        icon_grid_frame.bind("<MouseWheel>", _on_mousewheel_icon)
        
        icon_canvas.pack(side="left", fill="both", expand=True)
        icon_scrollbar.pack(side="right", fill="y")
        
        def select_icon(icon):
            icon_var.set(icon)
            icon_button.config(text=f"{icon} 点击选择图标 ▼")
            toggle_icon_panel()
        
        # 创建图标按钮网格（每行10个图标）
        for i, icon in enumerate(icon_library):
            row = i // 10  # 每行10个图标
            col = i % 10
            btn = tk.Button(icon_grid_frame, text=icon, font=("微软雅黑", 14),
                           width=3, height=1, relief="flat", 
                           bg="#f8f9fa", activebackground="#e8f4fd",
                           command=lambda ic=icon: select_icon(ic))
            btn.grid(row=row, column=col, padx=2, pady=2)
        
        # 移除颜色选择功能，因为没有实际效果
        # 颜色功能已被移除
        
        # 文件扩展名
        ext_frame = tk.Frame(main_frame, bg="#f8f9fa")
        ext_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(ext_frame, text="📎 文件扩展名", 
                font=("微软雅黑", 12, "bold"), 
                fg="#34495e", bg="#f8f9fa").pack(anchor="w", pady=(0, 5))
        
        tk.Label(ext_frame, text="支持的文件扩展名 (用逗号分隔，如: .txt, .doc, .pdf)", 
                font=("微软雅黑", 9), 
                fg="#7f8c8d", bg="#f8f9fa").pack(anchor="w", pady=(0, 5))
        
        ext_text = tk.Text(ext_frame, height=4, font=("微软雅黑", 10),
                          relief="flat", bd=1, 
                          highlightthickness=2, 
                          highlightcolor="#3498db",
                          wrap="word")
        ext_text.pack(fill="x", ipady=5)
        
        # 如果是编辑模式，填充现有数据
        if edit_category:
            # 查找分类信息，支持不同的名称格式
            category_info = None
            if edit_category in self.config["categories"]:
                category_info = self.config["categories"][edit_category]
            else:
                # 尝试查找包含该名称的分类
                for cat_name, cat_info in self.config["categories"].items():
                    if edit_category in cat_name or cat_name in edit_category:
                        category_info = cat_info
                        break
            
            if category_info:
                # 提取纯分类名称（去掉图标）
                clean_name = edit_category
                for emoji in ["📄", "🖼️", "🎬", "🎵", "📦", "💻", "📁"]:
                    clean_name = clean_name.replace(emoji, "").strip()
                
                name_var.set(clean_name)
                # 设置图标但不展开面板
                icon_var.set(category_info["icon"])
                icon_button.config(text=f"{category_info['icon']} 点击选择图标 ▼")
                ext_text.insert("1.0", ", ".join(category_info["extensions"]))
        else:
            # 默认值 - 设置但不展开面板
            icon_var.set("📁")
            icon_button.config(text="📁 点击选择图标 ▼")
        
        # 按钮区域
        button_frame = tk.Frame(main_frame, bg="#f8f9fa")
        button_frame.pack(pady=(20, 0))
        
        def save_category():
            name = name_var.get().strip()
            icon = icon_var.get().strip()
            extensions_text = ext_text.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror("错误", "请输入分类名称")
                return
            
            if not icon:
                icon = "📁"  # 默认图标
            
            # 解析扩展名
            extensions = []
            if extensions_text:
                extensions = [ext.strip() for ext in extensions_text.split(',') if ext.strip()]
                # 确保扩展名以点开头
                extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
            
            # 构建完整的分类名称（图标 + 名称）
            full_name = f"{icon} {name}"
            
            # 如果是编辑模式，删除旧的分类
            if edit_category and edit_category in self.config["categories"]:
                del self.config["categories"][edit_category]
            
            # 保存分类（移除颜色字段）
            self.config["categories"][full_name] = {
                "extensions": extensions,
                "icon": icon
            }
            
            self.save_config()
            self.refresh_category_list()
            messagebox.showinfo("成功", "分类保存成功！")
            dialog.destroy()
        
        # 美化的按钮
        save_btn = tk.Button(button_frame, text="💾 保存分类", 
                            font=("微软雅黑", 12, "bold"),
                            bg="#27ae60", fg="white", 
                            relief="flat", bd=0,
                            padx=30, pady=12,
                            cursor="hand2",
                            command=save_category)
        save_btn.pack(side="left", padx=(0, 15))
        
        cancel_btn = tk.Button(button_frame, text="❌ 取消", 
                              font=("微软雅黑", 12, "bold"),
                              bg="#95a5a6", fg="white", 
                              relief="flat", bd=0,
                              padx=30, pady=12,
                              cursor="hand2",
                              command=dialog.destroy)
        cancel_btn.pack(side="left")
        
        # 添加按钮悬停效果
        def on_enter_save(e):
            save_btn.config(bg="#229954")
        def on_leave_save(e):
            save_btn.config(bg="#27ae60")
        def on_enter_cancel(e):
            cancel_btn.config(bg="#85929e")
        def on_leave_cancel(e):
            cancel_btn.config(bg="#95a5a6")
        
        save_btn.bind("<Enter>", on_enter_save)
        save_btn.bind("<Leave>", on_leave_save)
        cancel_btn.bind("<Enter>", on_enter_cancel)
        cancel_btn.bind("<Leave>", on_leave_cancel)
    
    def setup_about_tab(self, parent):
        """设置关于标签页"""
        # 标题
        title_frame = tk.Frame(parent, bg="#2c3e50", height=80)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="ℹ️ 关于软件", 
                              font=("微软雅黑", 20, "bold"), 
                              fg="white", bg="#2c3e50")
        title_label.pack(expand=True)
        
        # subtitle_label = tk.Label(title_frame, text="让您的桌面井然有序", 
        #                          font=("微软雅黑", 10), 
        #                          fg="#bdc3c7", bg="#2c3e50")
        # subtitle_label.pack()
        
        # 创建滚动框架
        canvas = tk.Canvas(parent, bg="#f8f9fa")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8f9fa")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加鼠标滚轮支持
        def _on_mousewheel_about(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel_about)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel_about)
        
        # 更新canvas窗口位置以居中显示
        def _configure_scroll_region_about(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 居中显示内容
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if canvas_width > frame_width:
                x_offset = (canvas_width - frame_width) // 2
                canvas.coords(canvas.find_all()[0], x_offset, 0)
        
        scrollable_frame.bind("<Configure>", _configure_scroll_region_about)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 主内容区域
        content_frame = tk.Frame(scrollable_frame, bg="#f8f9fa", padx=50, pady=50)
        content_frame.pack(fill="both", expand=True, padx=50)
        
        # 软件信息
        info_frame = tk.Frame(content_frame, bg="#ffffff", relief="solid", bd=1)
        info_frame.pack(fill="both", expand=True)
        
        # 信息标题
        info_title = tk.Frame(info_frame, bg="#34495e", height=40)
        info_title.pack(fill="x")
        info_title.pack_propagate(False)
        
        tk.Label(info_title, text="📋 软件信息", 
                font=("微软雅黑", 12, "bold"), 
                fg="white", bg="#34495e").pack(expand=True)
        
        # 信息内容
        info_content = tk.Frame(info_frame, bg="#ffffff", padx=20, pady=15)
        info_content.pack(fill="both", expand=True)
        
        # 软件介绍
        intro_text = """🗂️ 桌面整理工具

这是一个功能强大的桌面文件整理工具，可以帮助您：

✨ 主要功能：
• 一键整理桌面文件到分类文件夹
• 支持自定义文件分类规则
• 一键恢复原始桌面布局
• 桌面文件备份功能
• 智能文件分类识别

🎨 特色功能：
• 美观的用户界面
• 支持自定义分类图标和颜色
• 智能跳过系统文件和快捷方式
• 支持大文件过滤
• 详细的操作日志记录
• 自动生成带时间戳的整理记录

🔧 技术特性：
• 智能文件夹清理机制
• 支持JSON格式的整理记录
• 完善的错误处理机制
• 高效的文件操作算法

💡 使用建议：
• 首次使用前建议先备份桌面
• 可以根据需要自定义分类规则
• 整理后可随时一键恢复
• 整理记录文件可用于多次恢复

开发者：Bin
版本：v1.9
更新日期：2025年1月

📄 版权信息：
本软件完全免费使用，但请尊重版权，未经许可不得用于商业用途。"""
        
        info_label = tk.Label(info_content, text=intro_text, 
                             font=("微软雅黑", 11), 
                             fg="#2c3e50", bg="#ffffff",
                             justify="left", anchor="nw")
        info_label.pack(fill="both", expand=True)
    
    def log_message(self, message):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        # 简化日志内容，只显示关键操作
        simplified_message = self._simplify_log_message(message)
        try:
            if hasattr(self, 'status_text') and self.status_text:
                self.status_text.insert(tk.END, f"[{timestamp}] {simplified_message}\n")
                self.status_text.see(tk.END)
                if hasattr(self, 'root') and self.root:
                    self.root.update()
            else:
                print(f"[{timestamp}] {simplified_message}")
        except Exception as e:
            print(f"[{timestamp}] {simplified_message}")
    
    def _simplify_log_message(self, message):
        """简化日志消息内容"""
        # 简化常见的冗长消息
        simplifications = {
            "开始整理桌面...": "开始整理",
            "桌面整理完成": "整理完成",
            "开始备份桌面文件...": "开始备份",
            "备份完成": "备份完成",
            "配置已保存": "配置保存",
            "配置代码已生成": "配置导出",
            "配置导入成功": "配置导入",
            "开始从记录文件恢复桌面": "开始恢复",
            "恢复完成": "恢复完成"
        }
        
        # 检查是否有简化版本
        for original, simplified in simplifications.items():
            if original in message:
                return simplified
        
        # 如果消息太长，截断显示
        if len(message) > 50:
            return message[:47] + "..."
        
        return message
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # 合并配置，保持向后兼容
                    if "categories" in saved_config:
                        # 检查是否是旧格式
                        first_category = next(iter(saved_config["categories"].values()))
                        if isinstance(first_category, list):
                            # 转换旧格式到新格式
                            new_categories = {}
                            for name, extensions in saved_config["categories"].items():
                                icon = "📁"
                                if "文档" in name: icon = "📄"
                                elif "图片" in name: icon = "🖼️"
                                elif "视频" in name: icon = "🎬"
                                elif "音频" in name: icon = "🎵"
                                elif "压缩" in name: icon = "📦"
                                elif "程序" in name: icon = "💻"
                                
                                new_categories[f"{icon} {name}"] = {
                                    "extensions": extensions,
                                    "icon": icon
                                }
                            saved_config["categories"] = new_categories
                    
                    self.config.update(saved_config)
                    
                    # 确保新配置项有默认值
                    if "include_folders_in_organize" not in self.config:
                        self.config["include_folders_in_organize"] = False
                    if "include_folders_in_backup" not in self.config:
                        self.config["include_folders_in_backup"] = False
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            # 更新基本配置
            extensions = [ext.strip() for ext in self.ext_var.get().split(',') if ext.strip()]
            self.config["excluded_extensions"] = extensions
            
            try:
                max_size = int(self.size_var.get())
                self.config["max_file_size_mb"] = max_size
            except ValueError:
                messagebox.showerror("错误", "文件大小必须是数字")
                return
            
            # 更新文件夹选项
            if hasattr(self, 'include_folders_organize_var'):
                self.config["include_folders_in_organize"] = self.include_folders_organize_var.get()
            if hasattr(self, 'include_folders_backup_var'):
                self.config["include_folders_in_backup"] = self.include_folders_backup_var.get()
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            self.log_message("设置已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {e}")
    
    def should_skip_file(self, file_path, for_organize=True):
        """判断是否应该跳过文件"""
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # 根据操作类型决定是否跳过文件夹
        if os.path.isdir(file_path):
            if for_organize:
                return not self.config.get("include_folders_in_organize", False)
            else:  # for backup
                return not self.config.get("include_folders_in_backup", False)
        
        # 跳过排除的扩展名
        if file_ext in self.config["excluded_extensions"]:
            return True
        
        # 跳过大文件
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > self.config["max_file_size_mb"]:
                return True
        except:
            pass
        
        return False
    
    def get_file_category(self, file_path):
        """获取文件分类"""
        # 如果是文件夹且启用了文件夹整理，返回桌面文件夹分类
        if os.path.isdir(file_path) and self.config.get("include_folders_in_organize", False):
            return "📂 桌面文件夹"
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        for category_name, category_info in self.config["categories"].items():
            if file_ext in category_info["extensions"]:
                return category_name
        
        # 返回"其他"分类
        for category_name in self.config["categories"]:
            if "其他" in category_name:
                return category_name
        
        return "📁 其他"  # 默认分类
    
    def create_desktop_ini(self, folder_path, category_info):
        """为文件夹创建desktop.ini文件以设置图标"""
        try:
            desktop_ini_path = os.path.join(folder_path, "desktop.ini")
            
            # 创建desktop.ini内容
            ini_content = f"""[.ShellClassInfo]
IconResource=shell32.dll,3
InfoTip={category_info['icon']} 分类文件夹
[ViewState]
Mode=
Vid=
FolderType=Generic
"""
            
            with open(desktop_ini_path, 'w', encoding='utf-8') as f:
                f.write(ini_content)
            
            # 只设置desktop.ini文件为隐藏和系统文件，不设置文件夹属性
            os.system(f'attrib +h +s "{desktop_ini_path}"')
            
        except Exception as e:
            print(f"创建desktop.ini失败: {e}")
    
    def clean_desktop(self):
        """整理桌面 - 直接在桌面创建分类文件夹"""
        try:
            # 生成整理记录的时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 首先让用户选择JSON文件保存位置
            # 生成默认文件名（包含日期和时间）
            default_filename = f"桌面整理记录_{timestamp}.json"
            save_path = filedialog.asksaveasfilename(
                title="保存整理记录文件",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialfile=default_filename
            )
            
            if not save_path:
                self.log_message("用户取消选择保存位置，整理操作已取消")
                return
            
            self.log_message("开始整理桌面...")
            
            # 记录移动的文件，用于恢复
            moved_files = []
            
            # 遍历桌面文件
            for item in os.listdir(self.desktop_path):
                item_path = os.path.join(self.desktop_path, item)
                
                # 跳过已存在的分类文件夹
                if item in self.config["categories"].keys():
                    continue
                
                # 跳过不需要整理的文件
                if self.should_skip_file(item_path, for_organize=True):
                    continue
                
                # 获取文件分类
                category = self.get_file_category(item_path)
                
                # 直接在桌面创建分类文件夹
                category_folder = os.path.join(self.desktop_path, category)
                if not os.path.exists(category_folder):
                    os.makedirs(category_folder)
                    # 为分类文件夹设置图标
                    if category in self.config["categories"]:
                        self.create_desktop_ini(category_folder, self.config["categories"][category])
                
                # 移动文件或文件夹
                dest_path = os.path.join(category_folder, item)
                
                # 处理重名文件/文件夹
                counter = 1
                original_dest = dest_path
                while os.path.exists(dest_path):
                    if os.path.isdir(item_path):
                        # 文件夹重名处理
                        dest_path = f"{original_dest}_{counter}"
                    else:
                        # 文件重名处理
                        name, ext = os.path.splitext(original_dest)
                        dest_path = f"{name}_{counter}{ext}"
                    counter += 1
                
                shutil.move(item_path, dest_path)
                moved_files.append({
                    "original": item_path,
                    "new": dest_path,
                    "category": category,
                    "timestamp": timestamp
                })
                
                item_type = "文件夹" if os.path.isdir(dest_path) else "文件"
                self.log_message(f"移动{item_type}: {item} -> {category}")
            
            # 保存整理记录到用户选择的位置
            record_data = {
                "timestamp": timestamp,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_files": len(moved_files),
                "categories_created": list(set([f["category"] for f in moved_files])),
                "files": moved_files
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(record_data, f, ensure_ascii=False, indent=2)
            
            self.log_message(f"整理记录已保存: {save_path}")
            
            # 同时保存到默认备份文件（保持兼容性）
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                json.dump(moved_files, f, ensure_ascii=False, indent=2)
            
            self.log_message(f"整理完成！共整理了 {len(moved_files)} 个文件")
            
            messagebox.showinfo("完成", f"桌面整理完成！\n共整理了 {len(moved_files)} 个文件\n分类文件夹已直接创建在桌面")
            
        except Exception as e:
            self.log_message(f"整理失败: {e}")
            messagebox.showerror("错误", f"整理失败: {e}")
    
    def restore_desktop(self):
        """恢复桌面 - 让用户选择JSON记录文件"""
        try:
            # 让用户选择要恢复的JSON文件
            file_path = filedialog.askopenfilename(
                title="选择要恢复的整理记录文件",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir=os.path.expanduser("~")  # 默认从用户主目录开始
            )
            
            if file_path:
                self._restore_from_file(file_path)
            else:
                # 如果用户取消选择，尝试使用默认备份文件
                if os.path.exists(self.backup_file):
                    result = messagebox.askyesno("提示", "未选择恢复文件，是否使用默认备份记录恢复？")
                    if result:
                        self._restore_from_file(self.backup_file)
                else:
                    messagebox.showinfo("提示", "未选择恢复文件，操作已取消")
                
        except Exception as e:
            self.log_message(f"恢复失败: {e}")
            messagebox.showerror("错误", f"恢复失败: {e}")
    
    def _restore_from_file(self, record_file_path):
        """从指定的记录文件恢复桌面"""
        try:
            self.log_message(f"开始从记录文件恢复桌面: {os.path.basename(record_file_path)}")
            
            # 读取记录文件
            with open(record_file_path, 'r', encoding='utf-8') as f:
                record_data = json.load(f)
            
            # 兼容新旧格式
            if isinstance(record_data, dict) and "files" in record_data:
                moved_files = record_data["files"]
                restore_info = f"恢复时间: {record_data.get('datetime', '未知')}\n文件数量: {record_data.get('total_files', len(moved_files))}"
            else:
                moved_files = record_data
                restore_info = f"文件数量: {len(moved_files)}"
            
            restored_count = 0
            categories_to_clean = set()
            
            for file_info in moved_files:
                if os.path.exists(file_info["new"]):
                    # 恢复文件到原位置
                    original_name = os.path.basename(file_info["original"])
                    restore_path = os.path.join(self.desktop_path, original_name)
                    
                    # 处理重名文件
                    counter = 1
                    original_restore = restore_path
                    while os.path.exists(restore_path):
                        name, ext = os.path.splitext(original_restore)
                        restore_path = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    shutil.move(file_info["new"], restore_path)
                    restored_count += 1
                    categories_to_clean.add(file_info["category"])
                    self.log_message(f"恢复: {original_name}")
            
            # 删除空的分类文件夹（直接在桌面的）
            for category in categories_to_clean:
                category_path = os.path.join(self.desktop_path, category)
                if os.path.exists(category_path) and os.path.isdir(category_path):
                    try:
                        # 先删除desktop.ini文件（如果存在）
                        desktop_ini = os.path.join(category_path, "desktop.ini")
                        if os.path.exists(desktop_ini):
                            try:
                                # 移除隐藏和系统属性
                                os.system(f'attrib -h -s "{desktop_ini}"')
                                os.remove(desktop_ini)
                                self.log_message(f"删除desktop.ini: {category}")
                            except Exception as ini_e:
                                self.log_message(f"删除desktop.ini失败: {category} - {ini_e}")
                        
                        # 检查文件夹是否为空（再次检查，因为可能有其他隐藏文件）
                        try:
                            folder_contents = os.listdir(category_path)
                            if not folder_contents:  # 文件夹为空
                                os.rmdir(category_path)
                                self.log_message(f"删除空分类文件夹: {category}")
                            else:
                                self.log_message(f"分类文件夹不为空，保留: {category} (包含: {folder_contents})")
                        except Exception as list_e:
                            self.log_message(f"检查文件夹内容失败: {category} - {list_e}")
                            
                    except Exception as e:
                        self.log_message(f"删除分类文件夹失败: {category} - {e}")
            
            self.log_message(f"恢复完成！共恢复了 {restored_count} 个文件")
            
            messagebox.showinfo("完成", f"桌面恢复完成！\n{restore_info}\n共恢复了 {restored_count} 个文件")
            
        except Exception as e:
            self.log_message(f"从文件恢复失败: {e}")
            messagebox.showerror("错误", f"从文件恢复失败: {e}")
    
    def backup_desktop(self):
        """备份桌面"""
        try:
            # 选择保存位置
            save_path = filedialog.askdirectory(title="选择备份保存位置")
            if not save_path:
                return
            
            self.log_message("开始备份桌面...")
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"桌面备份_{timestamp}.zip"
            backup_filepath = os.path.join(save_path, backup_filename)
            
            # 创建进度窗口
            progress_window = tk.Toplevel(self.root)
            progress_window.title("备份进度")
            progress_window.geometry("400x150")
            progress_window.resizable(False, False)
            progress_window.grab_set()
            progress_window.transient(self.root)
            
            # 居中显示
            progress_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
            
            # 进度标签
            progress_label = tk.Label(progress_window, text="正在扫描文件...", font=("微软雅黑", 10))
            progress_label.pack(pady=10)
            
            # 进度条
            from tkinter import ttk
            progress_bar = ttk.Progressbar(progress_window, mode='determinate')
            progress_bar.pack(pady=10, padx=20, fill='x')
            
            # 详细信息标签
            detail_label = tk.Label(progress_window, text="", font=("微软雅黑", 9), fg="#666")
            detail_label.pack(pady=5)
            
            progress_window.update()
            
            # 先扫描所有需要备份的文件
            all_files = []
            for item in os.listdir(self.desktop_path):
                item_path = os.path.join(self.desktop_path, item)
                
                # 跳过桌面整理文件夹
                if item == "桌面整理":
                    continue
                
                # 检查是否应该跳过
                if self.should_skip_file(item_path, for_organize=False):
                    continue
                
                if os.path.isfile(item_path):
                    all_files.append((item_path, item))
                elif os.path.isdir(item_path) and self.config.get("include_folders_in_backup", False):
                    # 备份文件夹
                    for root, dirs, files in os.walk(item_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # 检查文件大小
                            if not self.should_skip_file(file_path, for_organize=False):
                                arcname = os.path.relpath(file_path, self.desktop_path)
                                all_files.append((file_path, arcname))
            
            total_files = len(all_files)
            progress_label.config(text=f"准备备份 {total_files} 个文件...")
            progress_bar.config(maximum=total_files)
            progress_window.update()
            
            # 创建ZIP文件
            with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                backup_count = 0
                
                for i, (file_path, arcname) in enumerate(all_files):
                    try:
                        zipf.write(file_path, arcname)
                        backup_count += 1
                        
                        # 更新进度
                        progress_bar.config(value=i + 1)
                        progress_label.config(text=f"正在备份: {os.path.basename(file_path)}")
                        detail_label.config(text=f"已完成 {i + 1}/{total_files} 个文件")
                        progress_window.update()
                        
                        self.log_message(f"备份: {os.path.basename(file_path)}")
                    except Exception as e:
                        self.log_message(f"备份文件失败: {os.path.basename(file_path)} - {e}")
            
            progress_window.destroy()
            
            self.log_message(f"备份完成！文件保存至: {backup_filepath}")
            self.log_message(f"共备份了 {backup_count} 个文件")
            messagebox.showinfo("完成", f"桌面备份完成！\n文件保存至: {backup_filepath}\n共备份了 {backup_count} 个文件")
            
        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            self.log_message(f"备份失败: {e}")
            messagebox.showerror("错误", f"备份失败: {e}")
    
    def export_config(self):
        """导出配置代码"""
        try:
            # 生成配置代码
            config_code = {
                "app": "DesktopCleaner",
                "version": "2.0",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "config": {
                    "categories": self.config["categories"],
                    "excluded_extensions": self.config["excluded_extensions"],
                    "max_file_size_mb": self.config["max_file_size_mb"]
                }
            }
            
            # 转换为JSON字符串
            config_json = json.dumps(config_code, ensure_ascii=False, indent=2)
            
            # 创建显示窗口
            export_window = tk.Toplevel(self.root)
            export_window.title("导出配置代码")
            export_window.geometry("600x500")
            export_window.resizable(True, True)
            export_window.grab_set()
            
            # 居中显示
            export_window.transient(self.root)
            export_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 50))
            
            # 标题
            tk.Label(export_window, text="📤 配置代码已生成", 
                    font=("微软雅黑", 14, "bold"), fg="#2c3e50").pack(pady=10)
            
            # 说明文本
            info_text = "复制下方配置代码，在其他设备上使用'导入配置'功能即可快速恢复设置"
            tk.Label(export_window, text=info_text, 
                    font=("微软雅黑", 10), fg="#7f8c8d", wraplength=550).pack(pady=(0, 10))
            
            # 文本框架
            text_frame = tk.Frame(export_window)
            text_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # 文本框和滚动条
            text_widget = tk.Text(text_frame, font=("Consolas", 10), wrap="word")
            scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # 插入配置代码
            text_widget.insert("1.0", config_json)
            text_widget.config(state="disabled")  # 只读
            
            # 按钮框架
            button_frame = tk.Frame(export_window)
            button_frame.pack(pady=10)
            
            def copy_to_clipboard():
                export_window.clipboard_clear()
                export_window.clipboard_append(config_json)
                messagebox.showinfo("成功", "配置代码已复制到剪贴板！")
            
            def save_to_file():
                file_path = filedialog.asksaveasfilename(
                    title="保存配置文件",
                    defaultextension=".json",
                    filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                    initialname=f"desktop_cleaner_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(config_json)
                    messagebox.showinfo("成功", f"配置已保存到: {file_path}")
            
            # 按钮
            copy_btn = tk.Button(button_frame, text="📋 复制到剪贴板", command=copy_to_clipboard,
                               bg="#3498db", fg="white", font=("微软雅黑", 12, "bold"),
                               padx=30, pady=30, height=10, relief="flat", bd=0, cursor="hand2")
            copy_btn.pack(side="left", padx=15)
            
            save_btn = tk.Button(button_frame, text="💾 保存到文件", command=save_to_file,
                               bg="#2ecc71", fg="white", font=("微软雅黑", 12, "bold"),
                               padx=30, pady=20, height=4, relief="flat", bd=0, cursor="hand2")
            save_btn.pack(side="left", padx=15)
            
            close_btn = tk.Button(button_frame, text="关闭", command=export_window.destroy,
                                bg="#95a5a6", fg="white", font=("微软雅黑", 12, "bold"),
                                padx=30, pady=20, height=4, relief="flat", bd=0, cursor="hand2")
            close_btn.pack(side="left", padx=15)
            
            # 添加按钮悬停效果
            def create_hover_effect(button, normal_color, hover_color):
                def on_enter(e):
                    button.config(bg=hover_color)
                def on_leave(e):
                    button.config(bg=normal_color)
                button.bind("<Enter>", on_enter)
                button.bind("<Leave>", on_leave)
            
            create_hover_effect(copy_btn, "#3498db", "#2980b9")
            create_hover_effect(save_btn, "#2ecc71", "#27ae60")
            create_hover_effect(close_btn, "#95a5a6", "#7f8c8d")
            
            self.log_message("配置代码已生成")
            
        except Exception as e:
            self.log_message(f"导出配置失败: {e}")
            messagebox.showerror("错误", f"导出配置失败: {e}")
    
    def import_config(self):
        """导入配置代码"""
        try:
            # 创建导入窗口
            import_window = tk.Toplevel(self.root)
            import_window.title("导入配置代码")
            import_window.geometry("600x500")
            import_window.resizable(True, True)
            import_window.grab_set()
            
            # 居中显示
            import_window.transient(self.root)
            import_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 50))
            
            # 标题
            tk.Label(import_window, text="📥 导入配置代码", 
                    font=("微软雅黑", 14, "bold"), fg="#2c3e50").pack(pady=10)
            
            # 说明文本
            info_text = "请粘贴配置代码到下方文本框，或选择配置文件进行导入"
            tk.Label(import_window, text=info_text, 
                    font=("微软雅黑", 10), fg="#7f8c8d", wraplength=550).pack(pady=(0, 10))
            
            # 文本框架
            text_frame = tk.Frame(import_window)
            text_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # 文本框和滚动条
            text_widget = tk.Text(text_frame, font=("Consolas", 10), wrap="word")
            scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # 按钮框架
            button_frame = tk.Frame(import_window)
            button_frame.pack(pady=10)
            
            def load_from_file():
                file_path = filedialog.askopenfilename(
                    title="选择配置文件",
                    filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
                )
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        text_widget.delete("1.0", tk.END)
                        text_widget.insert("1.0", content)
                    except Exception as e:
                        messagebox.showerror("错误", f"读取文件失败: {e}")
            
            def apply_config():
                try:
                    config_text = text_widget.get("1.0", tk.END).strip()
                    if not config_text:
                        messagebox.showwarning("警告", "请输入配置代码")
                        return
                    
                    # 解析JSON
                    config_data = json.loads(config_text)
                    
                    # 验证配置格式
                    if not isinstance(config_data, dict) or "config" not in config_data:
                        messagebox.showerror("错误", "配置代码格式不正确")
                        return
                    
                    imported_config = config_data["config"]
                    
                    # 验证必要字段
                    required_fields = ["categories", "excluded_extensions", "max_file_size_mb"]
                    for field in required_fields:
                        if field not in imported_config:
                            messagebox.showerror("错误", f"配置代码缺少必要字段: {field}")
                            return
                    
                    # 确认导入
                    app_info = config_data.get("app", "未知应用")
                    version_info = config_data.get("version", "未知版本")
                    timestamp_info = config_data.get("timestamp", "未知时间")
                    
                    confirm_text = f"确定要导入以下配置吗？\n\n应用: {app_info}\n版本: {version_info}\n时间: {timestamp_info}\n\n导入后将覆盖当前配置！"
                    
                    if messagebox.askyesno("确认导入", confirm_text):
                        # 更新配置
                        self.config.update(imported_config)
                        
                        # 保存配置
                        with open(self.config_file, 'w', encoding='utf-8') as f:
                            json.dump(self.config, f, ensure_ascii=False, indent=2)
                        
                        # 更新UI
                        self.ext_var.set(','.join(self.config["excluded_extensions"]))
                        self.size_var.set(str(self.config["max_file_size_mb"]))
                        
                        # 刷新分类管理界面
                        if hasattr(self, 'category_tree'):
                            self.refresh_category_list()
                        
                        self.log_message("配置导入成功")
                        messagebox.showinfo("成功", "配置导入成功！")
                        import_window.destroy()
                    
                except json.JSONDecodeError:
                    messagebox.showerror("错误", "配置代码格式不正确，请检查JSON格式")
                except Exception as e:
                    messagebox.showerror("错误", f"导入配置失败: {e}")
            
            # 按钮
            load_btn = tk.Button(button_frame, text="📁 从文件加载", command=load_from_file,
                               bg="#f39c12", fg="white", font=("微软雅黑", 12, "bold"),
                               padx=30, pady=20, height=4, relief="flat", bd=0, cursor="hand2")
            load_btn.pack(side="left", padx=15)
            
            apply_btn = tk.Button(button_frame, text="✅ 应用配置", command=apply_config,
                                bg="#2ecc71", fg="white", font=("微软雅黑", 12, "bold"),
                                padx=30, pady=20, height=4, relief="flat", bd=0, cursor="hand2")
            apply_btn.pack(side="left", padx=15)
            
            cancel_btn = tk.Button(button_frame, text="取消", command=import_window.destroy,
                                 bg="#95a5a6", fg="white", font=("微软雅黑", 12, "bold"),
                                 padx=30, pady=20, height=4, relief="flat", bd=0, cursor="hand2")
            cancel_btn.pack(side="left", padx=15)
            
            # 添加按钮悬停效果
            def create_hover_effect(button, normal_color, hover_color):
                def on_enter(e):
                    button.config(bg=hover_color)
                def on_leave(e):
                    button.config(bg=normal_color)
                button.bind("<Enter>", on_enter)
                button.bind("<Leave>", on_leave)
            
            create_hover_effect(load_btn, "#f39c12", "#e67e22")
            create_hover_effect(apply_btn, "#2ecc71", "#27ae60")
            create_hover_effect(cancel_btn, "#95a5a6", "#7f8c8d")
            
        except Exception as e:
            self.log_message(f"打开导入窗口失败: {e}")
            messagebox.showerror("错误", f"打开导入窗口失败: {e}")
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DesktopCleaner()
    app.run()