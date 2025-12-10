import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import PyPDF2
import os
import re
import random
from pathlib import Path


class ExamenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Exámenes - CSI")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f0f0f0")
        
        self.preguntas = {}  # {tema: [lista de preguntas]}
        self.respuestas = {}  # {tema: {num_pregunta: respuesta o lista}}
        self.preguntas_examen = []  # Preguntas seleccionadas para el examen
        self.indice_actual = 0
        self.respuestas_usuario = {}
        self.carpeta_pdfs = ""
        self.widgets_respuesta = []  # Para guardar los widgets de respuesta actuales
        
        self.crear_pantalla_inicio()
    
    def crear_pantalla_inicio(self):
        """Pantalla inicial para seleccionar carpeta y configurar examen"""
        self.limpiar_pantalla()
        
        frame_principal = tk.Frame(self.root, bg="#f0f0f0")
        frame_principal.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        titulo = tk.Label(
            frame_principal, 
            text="📚 Sistema de Exámenes CSI",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        titulo.pack(pady=20)
        
        # Frame para selección de carpeta
        frame_carpeta = tk.LabelFrame(
            frame_principal, 
            text="1. Seleccionar carpeta con PDFs",
            font=("Arial", 12),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        frame_carpeta.pack(fill="x", pady=10)
        
        self.label_carpeta = tk.Label(
            frame_carpeta,
            text="No se ha seleccionado carpeta",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        self.label_carpeta.pack(side="left", padx=10)
        
        btn_carpeta = tk.Button(
            frame_carpeta,
            text="Seleccionar Carpeta",
            command=self.seleccionar_carpeta,
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            padx=15,
            pady=5
        )
        btn_carpeta.pack(side="right", padx=10)
        
        # Frame para configuración
        frame_config = tk.LabelFrame(
            frame_principal,
            text="2. Configuración del examen",
            font=("Arial", 12),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        frame_config.pack(fill="x", pady=10)
        
        # Selección de temas
        tk.Label(
            frame_config,
            text="Seleccionar temas:",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(anchor="w")
        
        self.frame_temas = tk.Frame(frame_config, bg="#f0f0f0")
        self.frame_temas.pack(fill="x", pady=5)
        
        self.vars_temas = {}  # {tema: BooleanVar}
        
        # Número de preguntas
        frame_num = tk.Frame(frame_config, bg="#f0f0f0")
        frame_num.pack(fill="x", pady=10)
        
        tk.Label(
            frame_num,
            text="Número de preguntas:",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(side="left")
        
        self.spin_num_preguntas = tk.Spinbox(
            frame_num,
            from_=5,
            to=100,
            width=5,
            font=("Arial", 10)
        )
        self.spin_num_preguntas.pack(side="left", padx=10)
        self.spin_num_preguntas.delete(0, "end")
        self.spin_num_preguntas.insert(0, "20")
        
        # Checkbox para aleatorizar
        self.var_aleatorio = tk.BooleanVar(value=True)
        tk.Checkbutton(
            frame_config,
            text="Aleatorizar orden de preguntas",
            variable=self.var_aleatorio,
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(anchor="w")
        
        # Botón iniciar
        self.btn_iniciar = tk.Button(
            frame_principal,
            text="🚀 Iniciar Examen",
            command=self.iniciar_examen,
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white",
            padx=30,
            pady=10,
            state="disabled"
        )
        self.btn_iniciar.pack(pady=30)
        
        # Info
        self.label_info = tk.Label(
            frame_principal,
            text="",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        self.label_info.pack()
    
    def seleccionar_carpeta(self):
        """Seleccionar carpeta con los PDFs"""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta con PDFs")
        if carpeta:
            self.carpeta_pdfs = carpeta
            self.label_carpeta.config(text=carpeta, fg="#27ae60")
            self.cargar_pdfs()
    
    def cargar_pdfs(self):
        """Cargar los PDFs de preguntas y respuestas"""
        self.preguntas = {}
        self.respuestas = {}
        
        # Limpiar checkboxes de temas anteriores
        for widget in self.frame_temas.winfo_children():
            widget.destroy()
        self.vars_temas = {}
        
        archivos = os.listdir(self.carpeta_pdfs)
        
        # Buscar archivos de preguntas
        archivos_preguntas = [f for f in archivos if f.lower().startswith("preguntas tema") and f.endswith(".pdf")]
        archivos_respuestas = [f for f in archivos if f.lower().startswith("respuestas tema") and f.endswith(".pdf")]
        
        temas_encontrados = []
        
        for archivo_p in archivos_preguntas:
            # Extraer número de tema
            match = re.search(r'tema\s*(\d+)', archivo_p, re.IGNORECASE)
            if match:
                num_tema = match.group(1)
                temas_encontrados.append(num_tema)
                
                # Cargar preguntas
                ruta_preguntas = os.path.join(self.carpeta_pdfs, archivo_p)
                self.preguntas[num_tema] = self.extraer_preguntas_pdf(ruta_preguntas)
                
                # Buscar archivo de respuestas correspondiente
                for archivo_r in archivos_respuestas:
                    if f"tema {num_tema}" in archivo_r.lower() or f"tema{num_tema}" in archivo_r.lower():
                        ruta_respuestas = os.path.join(self.carpeta_pdfs, archivo_r)
                        self.respuestas[num_tema] = self.extraer_respuestas_pdf(ruta_respuestas)
                        break
        
        # Crear checkboxes para cada tema
        temas_encontrados.sort(key=int)
        
        for i, tema in enumerate(temas_encontrados):
            var = tk.BooleanVar(value=True)
            self.vars_temas[tema] = var
            
            num_pregs = len(self.preguntas.get(tema, []))
            cb = tk.Checkbutton(
                self.frame_temas,
                text=f"Tema {tema} ({num_pregs} preguntas)",
                variable=var,
                font=("Arial", 10),
                bg="#f0f0f0"
            )
            cb.grid(row=i//3, column=i%3, sticky="w", padx=10)
        
        # Actualizar info
        total_preguntas = sum(len(p) for p in self.preguntas.values())
        self.label_info.config(
            text=f"✅ Cargados {len(temas_encontrados)} temas con {total_preguntas} preguntas en total"
        )
        
        if temas_encontrados:
            self.btn_iniciar.config(state="normal")
        else:
            messagebox.showwarning(
                "Aviso",
                "No se encontraron archivos PDF con el formato esperado.\n"
                "Los archivos deben llamarse 'Preguntas Tema X.pdf' y 'Respuestas Tema X.pdf'"
            )
    
    def limpiar_texto_pdf(self, texto):
        """Eliminar headers, footers y texto basura de los PDFs"""
        if not texto:
            return texto
        
        # Patrones de texto basura comunes en PDFs (headers/footers)
        patrones_basura = [
            # Formato: "Internet y Negocio Electrónico, 202 5-2026 Tema X - Preguntas/Respuestas"
            r'Internet\s+y\s+Negocio\s+Electr[óo]nico[,.]?\s*\d*\s*\d*[-–]\d*\s*Tema\s*\d+\s*[-–]?\s*(Preguntas|Respuestas)?',
            # Números de página sueltos
            r'\b\d+\s*$',
            # Otros patrones de encabezado/pie de página comunes
            r'Tema\s+\d+\s*[-–]\s*(Preguntas|Respuestas)',
            r'P[áa]gina\s+\d+\s*(de\s+\d+)?',
            # Texto tipo "202 5-2026" (año partido)
            r'\b20\d\s+\d[-–]\d{4}\b',
        ]
        
        resultado = texto
        for patron in patrones_basura:
            resultado = re.sub(patron, '', resultado, flags=re.IGNORECASE)
        
        # Limpiar espacios extras resultantes
        resultado = re.sub(r'\s+', ' ', resultado).strip()
        
        return resultado
    
    def extraer_preguntas_pdf(self, ruta_pdf):
        """Extraer preguntas del PDF"""
        preguntas = []
        try:
            with open(ruta_pdf, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                texto_completo = ""
                for page in reader.pages:
                    texto_completo += page.extract_text() + "\n"
                
                # Dividir por números de pregunta (1. 2. 3. etc.)
                patron_pregunta = r'(?:^|\n)\s*(\d+)\.\s+'
                
                partes = re.split(patron_pregunta, texto_completo)
                
                # partes[0] es texto antes de la primera pregunta
                # partes[1] es el número, partes[2] es el contenido, etc.
                
                i = 1
                while i < len(partes) - 1:
                    num_pregunta = int(partes[i])
                    contenido = partes[i + 1].strip()
                    
                    # Limpiar el contenido (quitar saltos de línea extras y texto basura)
                    contenido = ' '.join(contenido.split())
                    contenido = self.limpiar_texto_pdf(contenido)
                    
                    # Determinar tipo de pregunta
                    pregunta_data = self.parsear_pregunta(num_pregunta, contenido)
                    if pregunta_data:
                        preguntas.append(pregunta_data)
                    
                    i += 2
                    
        except Exception as e:
            print(f"Error al leer {ruta_pdf}: {e}")
            import traceback
            traceback.print_exc()
        
        return preguntas
    
    def parsear_pregunta(self, numero, contenido):
        """Parsear una pregunta y determinar su tipo"""
        
        # Verificar si tiene huecos con opciones [ opción1 | opción2 ]
        patron_hueco = r'\[\s*([^\]]+)\s*\]'
        huecos = re.findall(patron_hueco, contenido)
        
        # Verificar si los huecos tienen opciones separadas por |
        huecos_con_opciones = []
        for hueco in huecos:
            if '|' in hueco:
                opciones = [op.strip() for op in hueco.split('|')]
                huecos_con_opciones.append(opciones)
        
        if huecos_con_opciones:
            # Es una pregunta de completar huecos
            return {
                'numero': numero,
                'texto': contenido,
                'tipo': 'huecos',
                'huecos': huecos_con_opciones
            }
        
        # Verificar si es tipo test (tiene viñetas con •)
        if '•' in contenido:
            # Separar el enunciado de las opciones
            partes = contenido.split('•')
            enunciado = partes[0].strip()
            opciones = []
            
            letras = ['A', 'B', 'C', 'D', 'E', 'F']
            for idx, opcion in enumerate(partes[1:]):
                opcion = opcion.strip()
                if opcion and idx < len(letras):
                    opciones.append({
                        'letra': letras[idx],
                        'texto': opcion
                    })
            
            if opciones:
                return {
                    'numero': numero,
                    'texto': enunciado,
                    'tipo': 'test',
                    'opciones': opciones
                }
        
        # Si no tiene formato reconocido, tratarla como pregunta simple
        return {
            'numero': numero,
            'texto': contenido,
            'tipo': 'simple',
            'opciones': []
        }
    
    def extraer_respuestas_pdf(self, ruta_pdf):
        """Extraer respuestas del PDF"""
        respuestas = {}
        try:
            with open(ruta_pdf, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                texto_completo = ""
                for page in reader.pages:
                    texto_completo += page.extract_text() + "\n"
                
                # Dividir por números de pregunta igual que en las preguntas
                patron_pregunta = r'(?:^|\n)\s*(\d+)\.\s+'
                partes = re.split(patron_pregunta, texto_completo)
                
                i = 1
                while i < len(partes) - 1:
                    num = int(partes[i])
                    contenido = partes[i + 1].strip()
                    contenido = ' '.join(contenido.split())  # Limpiar espacios
                    contenido = self.limpiar_texto_pdf(contenido)  # Limpiar texto basura
                    
                    # Por ahora guardamos el contenido completo
                    # y lo procesaremos al corregir
                    respuestas[num] = contenido
                    
                    i += 2
                    
        except Exception as e:
            print(f"Error al leer {ruta_pdf}: {e}")
            import traceback
            traceback.print_exc()
        
        return respuestas
    
    def iniciar_examen(self):
        """Iniciar el examen con las configuraciones seleccionadas"""
        # Obtener temas seleccionados
        temas_seleccionados = [t for t, v in self.vars_temas.items() if v.get()]
        
        if not temas_seleccionados:
            messagebox.showwarning("Aviso", "Selecciona al menos un tema")
            return
        
        # Recopilar preguntas de temas seleccionados
        todas_preguntas = []
        for tema in temas_seleccionados:
            for pregunta in self.preguntas.get(tema, []):
                pregunta_copia = pregunta.copy()
                pregunta_copia['tema'] = tema
                todas_preguntas.append(pregunta_copia)
        
        if not todas_preguntas:
            messagebox.showwarning("Aviso", "No hay preguntas disponibles")
            return
        
        # Seleccionar número de preguntas
        num_preguntas = min(int(self.spin_num_preguntas.get()), len(todas_preguntas))
        
        # Aleatorizar si está seleccionado
        if self.var_aleatorio.get():
            random.shuffle(todas_preguntas)
        
        self.preguntas_examen = todas_preguntas[:num_preguntas]
        self.indice_actual = 0
        self.respuestas_usuario = {}
        
        self.mostrar_pregunta()
    
    def mostrar_pregunta(self):
        """Mostrar la pregunta actual"""
        self.limpiar_pantalla()
        self.widgets_respuesta = []
        
        pregunta = self.preguntas_examen[self.indice_actual]
        
        # Frame principal con scroll
        frame_principal = tk.Frame(self.root, bg="#f0f0f0")
        frame_principal.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Barra de progreso
        frame_progreso = tk.Frame(frame_principal, bg="#f0f0f0")
        frame_progreso.pack(fill="x", pady=5)
        
        progreso_texto = f"Pregunta {self.indice_actual + 1} de {len(self.preguntas_examen)} | Tema {pregunta['tema']}"
        tk.Label(
            frame_progreso,
            text=progreso_texto,
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#7f8c8d"
        ).pack(side="left")
        
        # Barra de progreso visual
        progreso = (self.indice_actual + 1) / len(self.preguntas_examen)
        frame_barra = tk.Frame(frame_progreso, bg="#ecf0f1", height=10)
        frame_barra.pack(side="right", fill="x", expand=True, padx=10)
        
        barra_llena = tk.Frame(frame_barra, bg="#3498db", height=10)
        barra_llena.place(relwidth=progreso, relheight=1)
        
        # Frame de la pregunta
        frame_pregunta = tk.LabelFrame(
            frame_principal,
            text=f"Pregunta {pregunta['numero']}",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        frame_pregunta.pack(fill="both", expand=True, pady=10)
        
        # Mostrar según el tipo de pregunta
        if pregunta['tipo'] == 'huecos':
            self.mostrar_pregunta_huecos(frame_pregunta, pregunta)
        elif pregunta['tipo'] == 'test':
            self.mostrar_pregunta_test(frame_pregunta, pregunta)
        else:
            self.mostrar_pregunta_simple(frame_pregunta, pregunta)
        
        # Botones de navegación
        frame_botones = tk.Frame(frame_principal, bg="#f0f0f0")
        frame_botones.pack(fill="x", pady=10)
        
        if self.indice_actual > 0:
            btn_anterior = tk.Button(
                frame_botones,
                text="← Anterior",
                command=self.pregunta_anterior,
                font=("Arial", 11),
                bg="#95a5a6",
                fg="white",
                padx=20,
                pady=8
            )
            btn_anterior.pack(side="left")
        
        # Botón para ir a cualquier pregunta
        btn_ir = tk.Button(
            frame_botones,
            text="Ir a pregunta...",
            command=self.mostrar_navegacion,
            font=("Arial", 10),
            bg="#9b59b6",
            fg="white",
            padx=15,
            pady=5
        )
        btn_ir.pack(side="left", padx=20)
        
        if self.indice_actual < len(self.preguntas_examen) - 1:
            btn_siguiente = tk.Button(
                frame_botones,
                text="Siguiente →",
                command=self.pregunta_siguiente,
                font=("Arial", 11),
                bg="#3498db",
                fg="white",
                padx=20,
                pady=8
            )
            btn_siguiente.pack(side="right")
        else:
            btn_finalizar = tk.Button(
                frame_botones,
                text="✓ Finalizar Examen",
                command=self.finalizar_examen,
                font=("Arial", 11, "bold"),
                bg="#27ae60",
                fg="white",
                padx=20,
                pady=8
            )
            btn_finalizar.pack(side="right")
    
    def mostrar_pregunta_huecos(self, frame, pregunta):
        """Mostrar pregunta con huecos y desplegables"""
        texto = pregunta['texto']
        huecos = pregunta['huecos']
        
        # Frame para el texto con desplegables
        frame_texto = tk.Frame(frame, bg="white")
        frame_texto.pack(fill="both", expand=True, pady=10)
        
        # Dividir el texto por los huecos [ ... ]
        patron_hueco = r'\[\s*[^\]]+\s*\]'
        partes = re.split(patron_hueco, texto)
        
        # Recuperar respuestas anteriores si existen
        respuestas_previas = self.respuestas_usuario.get(self.indice_actual, [])
        if not isinstance(respuestas_previas, list):
            respuestas_previas = []
        
        # Usar un Text widget para mejor control del flujo del texto
        text_widget = tk.Text(
            frame_texto, 
            wrap="word", 
            font=("Arial", 11),
            bg="white",
            relief="flat",
            height=15,
            cursor="arrow"
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        combos = []
        
        for i, parte in enumerate(partes):
            # Insertar texto
            text_widget.insert("end", parte)
            
            # Añadir desplegable si hay más huecos
            if i < len(huecos):
                var = tk.StringVar()
                
                # Recuperar respuesta previa
                if i < len(respuestas_previas):
                    var.set(respuestas_previas[i])
                
                opciones_hueco = huecos[i]
                # Añadir opción en blanco al principio
                opciones_con_blanco = [""] + opciones_hueco
                
                combo = ttk.Combobox(
                    text_widget,
                    textvariable=var,
                    values=opciones_con_blanco,
                    font=("Arial", 10),
                    state="readonly",
                    width=max(len(max(opciones_hueco, key=len)) + 2, 15)
                )
                
                # Insertar el combo en el texto
                text_widget.window_create("end", window=combo)
                combos.append(var)
        
        # Deshabilitar edición del texto
        text_widget.config(state="disabled")
        
        self.widgets_respuesta = combos
    
    def mostrar_pregunta_test(self, frame, pregunta):
        """Mostrar pregunta tipo test con radiobuttons"""
        
        # Enunciado
        tk.Label(
            frame,
            text=pregunta['texto'],
            font=("Arial", 12),
            bg="white",
            wraplength=900,
            justify="left"
        ).pack(anchor="w", pady=10)
        
        # Opciones
        var_respuesta = tk.StringVar()
        
        # Recuperar respuesta anterior si existe
        respuesta_previa = self.respuestas_usuario.get(self.indice_actual, "")
        if respuesta_previa:
            var_respuesta.set(respuesta_previa)
        
        frame_opciones = tk.Frame(frame, bg="white")
        frame_opciones.pack(fill="x", pady=10, padx=20)
        
        for opcion in pregunta['opciones']:
            frame_opcion = tk.Frame(frame_opciones, bg="white", pady=3)
            frame_opcion.pack(fill="x")
            
            rb = tk.Radiobutton(
                frame_opcion,
                text=f"{opcion['letra']})  {opcion['texto']}",
                variable=var_respuesta,
                value=opcion['letra'],
                font=("Arial", 11),
                bg="white",
                activebackground="#e8f4f8",
                anchor="w",
                padx=10,
                pady=8,
                indicatoron=1,
                selectcolor="#d5f4e6"
            )
            rb.pack(fill="x")
        
        # Opción para dejar en blanco
        frame_blanco = tk.Frame(frame_opciones, bg="white", pady=3)
        frame_blanco.pack(fill="x")
        
        rb_blanco = tk.Radiobutton(
            frame_blanco,
            text="     Dejar en blanco",
            variable=var_respuesta,
            value="",
            font=("Arial", 11, "italic"),
            bg="white",
            fg="#7f8c8d",
            activebackground="#f8f8f8",
            anchor="w",
            padx=10,
            pady=8,
            indicatoron=1,
            selectcolor="#f0f0f0"
        )
        rb_blanco.pack(fill="x")
        
        self.widgets_respuesta = [var_respuesta]
    
    def mostrar_pregunta_simple(self, frame, pregunta):
        """Mostrar pregunta simple con entrada de texto"""
        
        tk.Label(
            frame,
            text=pregunta['texto'],
            font=("Arial", 12),
            bg="white",
            wraplength=900,
            justify="left"
        ).pack(anchor="w", pady=10)
        
        tk.Label(
            frame,
            text="Tu respuesta:",
            font=("Arial", 10),
            bg="white"
        ).pack(anchor="w", pady=5)
        
        var_respuesta = tk.StringVar()
        
        # Recuperar respuesta anterior
        respuesta_previa = self.respuestas_usuario.get(self.indice_actual, "")
        if respuesta_previa:
            var_respuesta.set(respuesta_previa)
        
        entry = tk.Entry(
            frame,
            textvariable=var_respuesta,
            font=("Arial", 12),
            width=50
        )
        entry.pack(anchor="w", pady=5)
        
        self.widgets_respuesta = [var_respuesta]
    
    def guardar_respuesta_actual(self):
        """Guardar la respuesta actual del usuario"""
        if not self.widgets_respuesta:
            return
        
        pregunta = self.preguntas_examen[self.indice_actual]
        
        if pregunta['tipo'] == 'huecos':
            # Guardar lista de respuestas de los combos
            respuestas = [var.get() for var in self.widgets_respuesta]
            if any(respuestas):
                self.respuestas_usuario[self.indice_actual] = respuestas
        else:
            # Guardar respuesta única
            if self.widgets_respuesta[0].get():
                self.respuestas_usuario[self.indice_actual] = self.widgets_respuesta[0].get()
    
    def pregunta_anterior(self):
        """Ir a la pregunta anterior"""
        self.guardar_respuesta_actual()
        self.indice_actual -= 1
        self.mostrar_pregunta()
    
    def pregunta_siguiente(self):
        """Ir a la siguiente pregunta"""
        self.guardar_respuesta_actual()
        self.indice_actual += 1
        self.mostrar_pregunta()
    
    def mostrar_navegacion(self):
        """Mostrar ventana para ir a una pregunta específica"""
        self.guardar_respuesta_actual()
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Ir a pregunta")
        ventana.geometry("450x350")
        ventana.configure(bg="#f0f0f0")
        
        tk.Label(
            ventana,
            text="Selecciona una pregunta:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).pack(pady=10)
        
        # Frame con scroll para las preguntas
        frame_scroll = tk.Frame(ventana, bg="#f0f0f0")
        frame_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(frame_scroll, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
        frame_preguntas = tk.Frame(canvas, bg="#f0f0f0")
        
        frame_preguntas.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=frame_preguntas, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for i, pregunta in enumerate(self.preguntas_examen):
            respondida = "✓" if i in self.respuestas_usuario else "○"
            color = "#27ae60" if i in self.respuestas_usuario else "#95a5a6"
            
            btn = tk.Button(
                frame_preguntas,
                text=f"{respondida} Pregunta {i+1} (Tema {pregunta['tema']}, #{pregunta['numero']})",
                command=lambda idx=i, v=ventana: self.ir_a_pregunta(idx, v),
                font=("Arial", 10),
                bg="white",
                fg=color,
                anchor="w",
                width=45
            )
            btn.pack(fill="x", pady=2)
    
    def ir_a_pregunta(self, indice, ventana):
        """Ir a una pregunta específica"""
        ventana.destroy()
        self.indice_actual = indice
        self.mostrar_pregunta()
    
    def finalizar_examen(self):
        """Finalizar el examen y mostrar resultados"""
        self.guardar_respuesta_actual()
        
        # Confirmar
        if not messagebox.askyesno("Confirmar", "¿Deseas finalizar el examen?"):
            return
        
        self.mostrar_resultados()
    
    def mostrar_resultados(self):
        """Mostrar los resultados del examen"""
        self.limpiar_pantalla()
        
        # Calcular puntuación
        correctas = 0
        incorrectas = 0
        sin_responder = 0
        
        resultados_detalle = []
        
        for i, pregunta in enumerate(self.preguntas_examen):
            tema = pregunta['tema']
            num_pregunta = pregunta['numero']
            respuesta_correcta_raw = self.respuestas.get(tema, {}).get(num_pregunta, "?")
            respuesta_usuario = self.respuestas_usuario.get(i, "" if pregunta['tipo'] != 'huecos' else [])
            
            # Evaluar según tipo
            if pregunta['tipo'] == 'huecos':
                if not respuesta_usuario or not any(respuesta_usuario):
                    sin_responder += 1
                    estado = "sin_responder"
                    respuesta_correcta_display = respuesta_correcta_raw
                else:
                    # Para huecos, la respuesta correcta es el texto completo con las palabras correctas
                    # Necesitamos extraer las palabras de los huecos de la respuesta
                    # Las respuestas del usuario son las palabras elegidas en cada desplegable
                    
                    # Estrategia: usar el texto original de la pregunta con los huecos [...]
                    # y compararlo estructuralmente con la respuesta completa
                    huecos = pregunta.get('huecos', [])
                    respuestas_correctas = []
                    
                    # Obtener el texto de la pregunta con los huecos
                    texto_pregunta = pregunta.get('texto', '')
                    texto_respuesta = respuesta_correcta_raw
                    
                    # Extraer las respuestas correctas comparando estructuralmente
                    respuestas_correctas = self._extraer_respuestas_huecos(texto_pregunta, texto_respuesta, huecos)
                    
                    # Comparar respuestas del usuario con las correctas
                    todas_correctas = True
                    if len(respuesta_usuario) == len(respuestas_correctas):
                        for u, c in zip(respuesta_usuario, respuestas_correctas):
                            if u.strip().lower() != c.strip().lower():
                                todas_correctas = False
                                break
                    else:
                        todas_correctas = False
                    
                    if todas_correctas and respuestas_correctas:
                        correctas += 1
                        estado = "correcta"
                    else:
                        incorrectas += 1
                        estado = "incorrecta"
                    
                    respuesta_correcta_display = ", ".join(respuestas_correctas) if respuestas_correctas else respuesta_correcta_raw
                    
            elif pregunta['tipo'] == 'test':
                if not respuesta_usuario:
                    sin_responder += 1
                    estado = "sin_responder"
                    respuesta_correcta_display = respuesta_correcta_raw
                else:
                    # Para tipo test, la respuesta del usuario es la letra (A, B, C, D)
                    # Buscar el texto de la opción seleccionada
                    texto_respuesta_usuario = ""
                    for opcion in pregunta.get('opciones', []):
                        if opcion['letra'] == respuesta_usuario:
                            texto_respuesta_usuario = opcion['texto']
                            break
                    
                    # La respuesta correcta del PDF es el texto de la opción correcta
                    # Buscar qué letra corresponde a ese texto
                    letra_correcta = "?"
                    texto_correcto = str(respuesta_correcta_raw).strip().lower()
                    # Limpiar el texto correcto de puntuación final
                    texto_correcto = texto_correcto.rstrip('.').rstrip(',').strip()
                    texto_correcto = re.sub(r'\s+', ' ', texto_correcto)
                    
                    for opcion in pregunta.get('opciones', []):
                        texto_opcion = opcion['texto'].strip().lower()
                        texto_opcion_limpio = texto_opcion.rstrip('.').rstrip(',').strip()
                        texto_opcion_limpio = re.sub(r'\s+', ' ', texto_opcion_limpio)
                        
                        # Comparaciones en orden de prioridad
                        # 1. Comparación exacta
                        if texto_opcion_limpio == texto_correcto:
                            letra_correcta = opcion['letra']
                            break
                        # 2. Comparación de similitud estricta
                        if self._textos_similares(texto_opcion_limpio, texto_correcto):
                            letra_correcta = opcion['letra']
                            break
                    
                    if respuesta_usuario == letra_correcta:
                        correctas += 1
                        estado = "correcta"
                    else:
                        incorrectas += 1
                        estado = "incorrecta"
                    
                    respuesta_correcta_display = f"{letra_correcta}"
            else:
                # Pregunta simple
                if not respuesta_usuario:
                    sin_responder += 1
                    estado = "sin_responder"
                elif str(respuesta_usuario).strip().lower() == str(respuesta_correcta_raw).strip().lower():
                    correctas += 1
                    estado = "correcta"
                else:
                    incorrectas += 1
                    estado = "incorrecta"
                respuesta_correcta_display = respuesta_correcta_raw
            
            resultados_detalle.append({
                'pregunta': pregunta,
                'respuesta_usuario': respuesta_usuario,
                'respuesta_correcta': respuesta_correcta_display,
                'respuesta_correcta_raw': respuesta_correcta_raw,
                'estado': estado
            })
        
        # Frame principal
        frame_principal = tk.Frame(self.root, bg="#f0f0f0")
        frame_principal.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        tk.Label(
            frame_principal,
            text="📊 Resultados del Examen",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Puntuación
        total = len(self.preguntas_examen)
        porcentaje = (correctas / total) * 100 if total > 0 else 0
        
        # Calcular nota final: +1 por acierto, -0.5 por fallo
        puntos = correctas * 1.0 - incorrectas * 0.5
        puntos = max(0, puntos)  # No permitir puntuación negativa
        nota_maxima = total * 1.0
        nota_sobre_10 = (puntos / nota_maxima) * 10 if nota_maxima > 0 else 0
        
        frame_puntuacion = tk.Frame(frame_principal, bg="white", padx=30, pady=20)
        frame_puntuacion.pack(fill="x", pady=10)
        
        color_nota = "#27ae60" if nota_sobre_10 >= 5 else "#e74c3c"
        
        # Mostrar nota sobre 10
        tk.Label(
            frame_puntuacion,
            text=f"{nota_sobre_10:.2f} / 10",
            font=("Arial", 48, "bold"),
            bg="white",
            fg=color_nota
        ).pack()
        
        # Mostrar desglose de puntos
        tk.Label(
            frame_puntuacion,
            text=f"Puntos obtenidos: {puntos:.1f} de {nota_maxima:.0f} posibles",
            font=("Arial", 11),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=5)
        
        tk.Label(
            frame_puntuacion,
            text=f"(+1 por acierto, -0.5 por fallo)",
            font=("Arial", 9, "italic"),
            bg="white",
            fg="#95a5a6"
        ).pack()
        
        tk.Label(
            frame_puntuacion,
            text=f"✓ Correctas: {correctas} (+{correctas} pts)  |  ✗ Incorrectas: {incorrectas} (-{incorrectas * 0.5:.1f} pts)  |  ○ Sin responder: {sin_responder}",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        ).pack(pady=10)
        
        # Detalle de respuestas
        frame_detalle = tk.LabelFrame(
            frame_principal,
            text="Detalle de respuestas",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        frame_detalle.pack(fill="both", expand=True, pady=10)
        
        # Canvas con scroll
        canvas = tk.Canvas(frame_detalle, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(frame_detalle, orient="vertical", command=canvas.yview)
        frame_scroll = tk.Frame(canvas, bg="#f0f0f0")
        
        frame_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for i, resultado in enumerate(resultados_detalle):
            if resultado['estado'] == 'correcta':
                color = "#27ae60"
                icono = "✓"
            elif resultado['estado'] == 'incorrecta':
                color = "#e74c3c"
                icono = "✗"
            else:
                color = "#95a5a6"
                icono = "○"
            
            frame_item = tk.Frame(frame_scroll, bg="white", padx=10, pady=5)
            frame_item.pack(fill="x", pady=2, padx=5)
            
            resp_usuario = resultado['respuesta_usuario']
            if isinstance(resp_usuario, list):
                resp_usuario = ", ".join(resp_usuario) if resp_usuario else "-"
            
            resp_correcta = resultado['respuesta_correcta']
            if isinstance(resp_correcta, list):
                resp_correcta = ", ".join(resp_correcta)
            
            texto = f"{icono} P{i+1} (Tema {resultado['pregunta']['tema']}, #{resultado['pregunta']['numero']}): "
            texto += f"Tu respuesta: {resp_usuario or '-'} | Correcta: {resp_correcta}"
            
            tk.Label(
                frame_item,
                text=texto,
                font=("Arial", 10),
                bg="white",
                fg=color,
                anchor="w"
            ).pack(fill="x")
        
        # Botones
        frame_botones = tk.Frame(frame_principal, bg="#f0f0f0")
        frame_botones.pack(fill="x", pady=10)
        
        tk.Button(
            frame_botones,
            text="🔄 Nuevo Examen",
            command=self.crear_pantalla_inicio,
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10
        ).pack(side="left", padx=5)
        
        tk.Button(
            frame_botones,
            text="📋 Revisar Respuestas",
            command=lambda: self.revisar_respuestas(resultados_detalle),
            font=("Arial", 12),
            bg="#9b59b6",
            fg="white",
            padx=20,
            pady=10
        ).pack(side="left", padx=5)
        
        tk.Button(
            frame_botones,
            text="💾 Guardar Reporte",
            command=lambda: self.guardar_reporte(resultados_detalle, correctas, incorrectas, sin_responder, nota_sobre_10, puntos),
            font=("Arial", 12),
            bg="#f39c12",
            fg="white",
            padx=20,
            pady=10
        ).pack(side="left", padx=5)
        
        tk.Button(
            frame_botones,
            text="❌ Salir",
            command=self.root.quit,
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=10
        ).pack(side="right", padx=5)
    
    def revisar_respuestas(self, resultados):
        """Revisar las respuestas detalladamente"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Revisión de Respuestas")
        ventana.geometry("900x650")
        ventana.configure(bg="#f0f0f0")
        
        # Canvas con scroll
        canvas = tk.Canvas(ventana, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
        frame_scroll = tk.Frame(canvas, bg="#f0f0f0")
        
        frame_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for i, resultado in enumerate(resultados):
            pregunta = resultado['pregunta']
            
            if resultado['estado'] == 'correcta':
                color_bg = "#d5f4e6"
                color_borde = "#27ae60"
            elif resultado['estado'] == 'incorrecta':
                color_bg = "#fadbd8"
                color_borde = "#e74c3c"
            else:
                color_bg = "#f4f4f4"
                color_borde = "#95a5a6"
            
            frame_pregunta = tk.LabelFrame(
                frame_scroll,
                text=f"Pregunta {i+1} - Tema {pregunta['tema']} (#{pregunta['numero']})",
                font=("Arial", 10, "bold"),
                bg=color_bg,
                fg=color_borde,
                padx=10,
                pady=10
            )
            frame_pregunta.pack(fill="x", padx=10, pady=5)
            
            tk.Label(
                frame_pregunta,
                text=pregunta['texto'],
                font=("Arial", 10),
                bg=color_bg,
                wraplength=800,
                justify="left"
            ).pack(anchor="w")
            
            # Mostrar opciones si es tipo test
            if pregunta['tipo'] == 'test' and pregunta.get('opciones'):
                resp_correcta_raw = resultado.get('respuesta_correcta_raw', resultado['respuesta_correcta'])
                resp_usuario = str(resultado['respuesta_usuario']).upper() if resultado['respuesta_usuario'] else ""
                
                # Primero encontrar la letra correcta comparando textos
                letra_correcta = None
                texto_correcto = str(resp_correcta_raw).strip().lower().rstrip('.').rstrip(',').strip()
                texto_correcto = re.sub(r'\s+', ' ', texto_correcto)
                
                for opcion in pregunta['opciones']:
                    texto_opcion = opcion['texto'].strip().lower().rstrip('.').rstrip(',').strip()
                    texto_opcion = re.sub(r'\s+', ' ', texto_opcion)
                    
                    # Comparación exacta primero
                    if texto_opcion == texto_correcto:
                        letra_correcta = opcion['letra']
                        break
                    # Comparación de similitud estricta
                    if self._textos_similares(texto_opcion, texto_correcto):
                        letra_correcta = opcion['letra']
                        break
                
                for opcion in pregunta['opciones']:
                    es_correcta = (opcion['letra'] == letra_correcta)
                    es_usuario = opcion['letra'] == resp_usuario
                    
                    if es_correcta:
                        texto = f"✓ {opcion['letra']}) {opcion['texto']}"
                        fg = "#27ae60"
                    elif es_usuario and not es_correcta:
                        texto = f"✗ {opcion['letra']}) {opcion['texto']}"
                        fg = "#e74c3c"
                    else:
                        texto = f"   {opcion['letra']}) {opcion['texto']}"
                        fg = "#2c3e50"
                    
                    tk.Label(
                        frame_pregunta,
                        text=texto,
                        font=("Arial", 10),
                        bg=color_bg,
                        fg=fg,
                        wraplength=750,
                        justify="left"
                    ).pack(anchor="w", padx=20)
            
            # Mostrar respuestas
            resp_usuario = resultado['respuesta_usuario']
            resp_correcta = resultado['respuesta_correcta']
            
            if isinstance(resp_usuario, list):
                resp_usuario = ", ".join(resp_usuario) if resp_usuario else "Sin responder"
            if isinstance(resp_correcta, list):
                resp_correcta = ", ".join(resp_correcta)
            
            tk.Label(
                frame_pregunta,
                text=f"Tu respuesta: {resp_usuario or 'Sin responder'} | Correcta: {resp_correcta}",
                font=("Arial", 9, "italic"),
                bg=color_bg,
                fg="#7f8c8d"
            ).pack(anchor="w", pady=5)
    
    def _textos_similares(self, texto1, texto2):
        """Comparar dos textos de forma flexible pero precisa"""
        # Limpiar textos
        t1 = texto1.lower().strip().rstrip('.').rstrip(',').strip()
        t2 = texto2.lower().strip().rstrip('.').rstrip(',').strip()
        
        # Eliminar caracteres especiales y espacios extras
        t1 = re.sub(r'\s+', ' ', t1)
        t2 = re.sub(r'\s+', ' ', t2)
        
        # Comparación exacta después de limpiar
        if t1 == t2:
            return True
        
        # Para textos cortos (respuestas de una palabra o dos), comparar directamente
        if len(t1.split()) <= 2 or len(t2.split()) <= 2:
            # Si alguno es corto, ver si está contenido en el otro
            if t1 in t2 or t2 in t1:
                return True
            return False
        
        # Para textos largos (tipo opciones de test), ser más estrictos
        # Solo considerar similares si comparten palabras SIGNIFICATIVAS
        # Ignorar palabras funcionales comunes
        palabras_ignorar = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
            'de', 'del', 'al', 'a', 'en', 'con', 'por', 'para',
            'que', 'cual', 'quien', 'como', 'donde', 'cuando',
            'y', 'o', 'pero', 'sino', 'ni', 'e', 'u',
            'es', 'son', 'ser', 'está', 'están', 'estar',
            'tiene', 'tienen', 'tener', 'hay',
            'se', 'su', 'sus', 'lo', 'le', 'les',
            'este', 'esta', 'estos', 'estas', 'ese', 'esa',
            'más', 'menos', 'muy', 'tan', 'tanto',
            'si', 'no', 'sí', 'ya', 'aún', 'todavía'
        }
        
        # Extraer palabras significativas
        palabras1 = set(p for p in t1.split() if p not in palabras_ignorar and len(p) > 2)
        palabras2 = set(p for p in t2.split() if p not in palabras_ignorar and len(p) > 2)
        
        # Para ser similares, deben compartir al menos el 80% de las palabras significativas
        if len(palabras1) > 0 and len(palabras2) > 0:
            interseccion = palabras1.intersection(palabras2)
            ratio = len(interseccion) / min(len(palabras1), len(palabras2))
            if ratio >= 0.8:
                return True
        
        return False
    
    def _extraer_respuestas_huecos(self, texto_pregunta, texto_respuesta, huecos):
        """
        Extrae las respuestas correctas de una pregunta de huecos
        comparando estructuralmente la pregunta con la respuesta.
        
        Args:
            texto_pregunta: Texto original con [opción1 | opción2 | ...]
            texto_respuesta: Texto completo de respuesta
            huecos: Lista de listas de opciones por cada hueco
        
        Returns:
            Lista de las opciones correctas para cada hueco
        """
        import re
        
        # Normalizar textos
        texto_pregunta_norm = texto_pregunta.lower().strip()
        texto_pregunta_norm = re.sub(r'\s+', ' ', texto_pregunta_norm)
        texto_respuesta_norm = texto_respuesta.lower().strip()
        texto_respuesta_norm = re.sub(r'\s+', ' ', texto_respuesta_norm)
        
        # Estrategia: Construir una expresión regular a partir de la pregunta
        # donde cada hueco se convierte en un grupo de captura con las opciones posibles
        
        patron_hueco = r'\[\s*[^\]]+\s*\]'
        partes_fijas = re.split(patron_hueco, texto_pregunta_norm)
        
        # Construir el patrón regex
        patron_partes = []
        for i, parte in enumerate(partes_fijas):
            # Escapar caracteres especiales de regex en el texto fijo
            parte_escapada = re.escape(parte.strip())
            # Hacer el patrón más flexible con espacios
            parte_escapada = re.sub(r'\\ ', r'\\s+', parte_escapada)
            patron_partes.append(parte_escapada)
            
            # Añadir grupo de captura para el hueco (excepto después de la última parte)
            if i < len(huecos):
                opciones_hueco = huecos[i]
                # Crear alternativas para las opciones del hueco
                opciones_escapadas = [re.escape(op.lower().strip()) for op in opciones_hueco]
                grupo_opciones = '(' + '|'.join(opciones_escapadas) + ')'
                patron_partes.append(grupo_opciones)
        
        # Unir el patrón con espacios flexibles
        patron_completo = r'\s*'.join(patron_partes)
        
        try:
            match = re.search(patron_completo, texto_respuesta_norm, re.IGNORECASE)
            if match:
                # Extraer las respuestas de los grupos capturados
                respuestas_correctas = []
                for i, grupo in enumerate(match.groups()):
                    if grupo and i < len(huecos):
                        # Buscar la opción original (con mayúsculas/minúsculas originales)
                        for opcion in huecos[i]:
                            if opcion.lower().strip() == grupo.lower().strip():
                                respuestas_correctas.append(opcion)
                                break
                        else:
                            respuestas_correctas.append(grupo)
                return respuestas_correctas
        except re.error as e:
            print(f"Error en regex: {e}")
        
        # Fallback: método simple buscando cada opción en orden
        respuestas_correctas = []
        pos_busqueda = 0
        
        for opciones_hueco in huecos:
            opcion_encontrada = None
            mejor_pos = len(texto_respuesta_norm)
            
            for opcion in opciones_hueco:
                opcion_norm = opcion.lower().strip()
                pos = texto_respuesta_norm.find(opcion_norm, pos_busqueda)
                if pos != -1 and pos < mejor_pos:
                    mejor_pos = pos
                    opcion_encontrada = opcion
            
            if opcion_encontrada:
                respuestas_correctas.append(opcion_encontrada)
                # Mover la posición de búsqueda después de esta opción encontrada
                pos_busqueda = mejor_pos + len(opcion_encontrada)
            else:
                respuestas_correctas.append(opciones_hueco[0] if opciones_hueco else "")
        
        return respuestas_correctas

    def guardar_reporte(self, resultados, correctas, incorrectas, sin_responder, nota, puntos):
        """Guardar un reporte del intento en formato HTML"""
        from datetime import datetime
        import json
        
        # Pedir ubicación para guardar
        archivo = filedialog.asksaveasfilename(
            title="Guardar Reporte",
            defaultextension=".html",
            filetypes=[("Archivo HTML", "*.html"), ("Todos los archivos", "*.*")],
            initialfile=f"reporte_examen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        if not archivo:
            return
        
        # Generar HTML
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Examen - CSI</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
        }}
        .fecha {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        .resumen {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .nota {{
            font-size: 48px;
            font-weight: bold;
            color: {"#27ae60" if nota >= 5 else "#e74c3c"};
        }}
        .detalles {{
            color: #7f8c8d;
            margin-top: 10px;
        }}
        .pregunta {{
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #95a5a6;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .pregunta.correcta {{
            border-left-color: #27ae60;
            background: #d5f4e6;
        }}
        .pregunta.incorrecta {{
            border-left-color: #e74c3c;
            background: #fadbd8;
        }}
        .pregunta.sin-responder {{
            border-left-color: #95a5a6;
            background: #f4f4f4;
        }}
        .pregunta-header {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        .pregunta-texto {{
            margin-bottom: 10px;
        }}
        .opcion {{
            padding: 5px 10px;
            margin: 3px 0;
        }}
        .opcion.correcta {{
            color: #27ae60;
            font-weight: bold;
        }}
        .opcion.usuario-incorrecta {{
            color: #e74c3c;
            text-decoration: line-through;
        }}
        .respuesta-info {{
            font-style: italic;
            color: #7f8c8d;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-num {{
            font-size: 24px;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 12px;
            color: #7f8c8d;
        }}
        .correcta-num {{ color: #27ae60; }}
        .incorrecta-num {{ color: #e74c3c; }}
        .blanco-num {{ color: #95a5a6; }}
    </style>
</head>
<body>
    <h1>📊 Reporte de Examen - CSI</h1>
    <p class="fecha">Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    
    <div class="resumen">
        <div class="nota">{nota:.2f} / 10</div>
        <div class="detalles">
            Puntos obtenidos: {puntos:.1f} de {len(resultados):.0f} posibles<br>
            (+1 por acierto, -0.5 por fallo)
        </div>
        <div class="stats">
            <div class="stat">
                <div class="stat-num correcta-num">{correctas}</div>
                <div class="stat-label">Correctas (+{correctas} pts)</div>
            </div>
            <div class="stat">
                <div class="stat-num incorrecta-num">{incorrectas}</div>
                <div class="stat-label">Incorrectas (-{incorrectas * 0.5:.1f} pts)</div>
            </div>
            <div class="stat">
                <div class="stat-num blanco-num">{sin_responder}</div>
                <div class="stat-label">Sin responder</div>
            </div>
        </div>
    </div>
    
    <h2>Detalle de Respuestas</h2>
"""
        
        for i, resultado in enumerate(resultados):
            pregunta = resultado['pregunta']
            estado = resultado['estado']
            clase_estado = estado.replace('_', '-')
            
            resp_usuario = resultado['respuesta_usuario']
            resp_correcta = resultado['respuesta_correcta']
            resp_correcta_raw = resultado.get('respuesta_correcta_raw', resp_correcta)
            
            if isinstance(resp_usuario, list):
                resp_usuario_str = ", ".join(resp_usuario) if any(resp_usuario) else "Sin responder"
            else:
                resp_usuario_str = resp_usuario if resp_usuario else "Sin responder"
            
            if isinstance(resp_correcta, list):
                resp_correcta_str = ", ".join(resp_correcta)
            else:
                resp_correcta_str = str(resp_correcta)
            
            icono = "✓" if estado == "correcta" else ("✗" if estado == "incorrecta" else "○")
            
            html += f"""
    <div class="pregunta {clase_estado}">
        <div class="pregunta-header">{icono} Pregunta {i+1} - Tema {pregunta['tema']} (#{pregunta['numero']})</div>
        <div class="pregunta-texto">{pregunta['texto']}</div>
"""
            
            # Mostrar opciones si es tipo test
            if pregunta['tipo'] == 'test' and pregunta.get('opciones'):
                texto_correcto = str(resp_correcta_raw).strip().lower().rstrip('.').rstrip(',').strip()
                texto_correcto = re.sub(r'\s+', ' ', texto_correcto)
                resp_usuario_upper = str(resp_usuario).upper() if resp_usuario else ""
                
                # Encontrar la letra de la opción correcta
                letra_correcta = None
                for opcion in pregunta['opciones']:
                    texto_opcion = opcion['texto'].strip().lower().rstrip('.').rstrip(',').strip()
                    texto_opcion = re.sub(r'\s+', ' ', texto_opcion)
                    
                    # Comparación exacta primero
                    if texto_opcion == texto_correcto:
                        letra_correcta = opcion['letra']
                        break
                    # Comparación de similitud estricta
                    if self._textos_similares(texto_opcion, texto_correcto):
                        letra_correcta = opcion['letra']
                        break
                
                for opcion in pregunta['opciones']:
                    es_correcta = (opcion['letra'] == letra_correcta)
                    es_usuario = (opcion['letra'] == resp_usuario_upper)
                    
                    clase_opcion = ""
                    if es_correcta:
                        clase_opcion = "correcta"
                    elif es_usuario and not es_correcta:
                        clase_opcion = "usuario-incorrecta"
                    
                    prefijo = "✓ " if es_correcta else ("✗ " if es_usuario and not es_correcta else "")
                    html += f'        <div class="opcion {clase_opcion}">{prefijo}{opcion["letra"]}) {opcion["texto"]}</div>\n'
                
                # Mostrar respuesta correcta con letra
                if letra_correcta:
                    resp_correcta_str = f"{letra_correcta}"
            
            html += f"""        <div class="respuesta-info">Tu respuesta: {resp_usuario_str} | Correcta: {resp_correcta_str}</div>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(html)
            
            messagebox.showinfo("Éxito", f"Reporte guardado correctamente en:\n{archivo}")
            
            # Preguntar si desea abrir el archivo
            if messagebox.askyesno("Abrir reporte", "¿Deseas abrir el reporte en el navegador?"):
                import webbrowser
                webbrowser.open(archivo)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el reporte:\n{e}")
    
    def limpiar_pantalla(self):
        """Limpiar todos los widgets de la pantalla"""
        for widget in self.root.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    app = ExamenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
