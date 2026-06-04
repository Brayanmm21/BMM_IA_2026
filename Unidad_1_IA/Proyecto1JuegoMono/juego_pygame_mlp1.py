import os
import csv
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

import matplotlib

try:
    matplotlib.use("TkAgg")
except Exception:
    try:
        matplotlib.use("Qt5Agg")
    except Exception:
        pass

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

plt.ion()

BASE_W, BASE_H = 1080, 720
WINDOW_FRACTION = 0.97
EXTRA_SCALE = 1.1


@dataclass
class Sample:
    velocidad_bala: float
    distancia: float
    tipo_bala: int
    salto: int
    agachar: int


class Juego:
    def __init__(self) -> None:
        pygame.init()

        self._flags = 0
        self._fullscreen = False

        start_w = BASE_W
        start_h = BASE_H
        self.pantalla = pygame.display.set_mode((start_w, start_h), self._flags)
        pygame.display.set_caption("Mono vs Tanque - IA MLP")

        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.GRIS = (200, 200, 200)
        self.AMARILLO = (255, 220, 120)

        self.corriendo = True
        self.modo_auto = False

        self.datos_modelo: List[Sample] = []
        self.modelo: Optional[MLPClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.modelo_entrenado = False
        self.clase_unica: Optional[int] = None
        self.ultima_proba_salto: Optional[float] = None
        self.ultima_proba_agachar: Optional[float] = None

        self.decision_window = 500
        self._decision_frame_counter = 0

        self.w, self.h = start_w, start_h
        self.scale = 1.0
        self.margin = 50
        self.ground_y = self.h - 100

        self.player_size = (32, 48)
        self.player_size_agachado = (32, 24)
        self.bullet_size = (16, 16)
        self.ship_size = (64, 64)
        self.fondo_speed = 3

        self.salto = False
        self.en_suelo = True
        self.salto_vel_inicial = 15.0
        self.gravedad = 1.0
        self.salto_vel = self.salto_vel_inicial

        self.agachado = False
        self.agachar_timer = 0

        self.velocidad_bala = -12
        self.bala_disparada = False
        self.tipo_bala_actual = 0

        self.fondo_x1 = 0
        self.fondo_x2 = start_w

        self._apply_resolution(start_w, start_h, reset_positions=True)
        self._reset_estado_juego()

    def _apply_resolution(self, w: int, h: int, reset_positions: bool) -> None:
        self.w, self.h = int(w), int(h)

        self.scale = min(self.w / BASE_W, self.h / BASE_H) * EXTRA_SCALE
        self.scale = max(1.0, self.scale)

        self.margin = int(50 * self.scale)
        self.ground_y = self.h - int(100 * self.scale)

        self.player_size = (int(40 * self.scale), int(58 * self.scale))
        self.player_size_agachado = (int(40 * self.scale), int(45 * self.scale))
        self.bullet_size = (int(18 * self.scale), int(18 * self.scale))
        self.ship_size = (int(90 * self.scale), int(55 * self.scale))
        self.fondo_speed = max(1, int(2 * self.scale))

        self.salto_vel_inicial = 15 * self.scale
        self.gravedad = 1 * self.scale
        self.salto_vel = self.salto_vel_inicial

        self.decision_window = int(500 * self.scale)

        self.fuente = pygame.font.SysFont("Arial", int(24 * self.scale))
        self.fuente_chica = pygame.font.SysFont("Arial", int(18 * self.scale))

        if reset_positions or not hasattr(self, "jugador"):
            self.jugador = pygame.Rect(
                self.margin,
                self.ground_y,
                self.player_size[0],
                self.player_size[1],
            )

            self.bala = pygame.Rect(
                self.w - self.margin,
                self.ground_y + int(10 * self.scale),
                self.bullet_size[0],
                self.bullet_size[1],
            )

            self.nave = pygame.Rect(
                self.w - int(120 * self.scale),
                self.ground_y,
                self.ship_size[0],
                self.ship_size[1],
            )

    def _toggle_fullscreen(self) -> None:
        self._fullscreen = not self._fullscreen

        if self._fullscreen:
            info = pygame.display.Info()
            w = info.current_w or self.w
            h = info.current_h or self.h
            self.pantalla = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
            self._apply_resolution(w, h, reset_positions=True)
        else:
            self.pantalla = pygame.display.set_mode((BASE_W, BASE_H), self._flags)
            self._apply_resolution(BASE_W, BASE_H, reset_positions=True)

        self._reset_estado_juego()

    def _reset_estado_juego(self) -> None:
        self.jugador.x = self.margin
        self.jugador.y = self.ground_y
        self.jugador.width = self.player_size[0]
        self.jugador.height = self.player_size[1]

        self.nave.x = self.w - int(120 * self.scale)
        self.nave.y = self.ground_y

        self.bala.x = self.w - self.margin
        self.bala.y = self.ground_y + int(10 * self.scale)

        self.bala_disparada = False
        self.tipo_bala_actual = 0
        self.velocidad_bala = int(-10 * self.scale)

        self.salto = False
        self.en_suelo = True
        self.salto_vel = self.salto_vel_inicial
        self.agachado = False
        self.agachar_timer = 0

        self._decision_frame_counter = 0
        self.fondo_x1 = 0
        self.fondo_x2 = self.w

    def _reset_modelo(self) -> None:
        self.modelo = None
        self.scaler = None
        self.modelo_entrenado = False
        self.clase_unica = None

    def exportar_datos_csv(self) -> str:
        if not self.datos_modelo:
            return "No hay datos para exportar."

        base = os.path.dirname(__file__)
        ruta = os.path.join(base, "datos_mlp.csv")

        try:
            with open(ruta, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["velocidad_bala", "distancia", "tipo_bala", "salto", "agachar"])

                for s in self.datos_modelo:
                    writer.writerow([
                        s.velocidad_bala,
                        s.distancia,
                        s.tipo_bala,
                        s.salto,
                        s.agachar,
                    ])

        except Exception as e:
            return f"Error al guardar CSV: {e}"

        return f"CSV guardado en datos_mlp.csv ({len(self.datos_modelo)} filas)."

    def graficar_datos_2d(self) -> str:
        if not self.datos_modelo:
            return "No hay datos para graficar."

        xs = [s.distancia for s in self.datos_modelo]
        ys = [s.velocidad_bala for s in self.datos_modelo]

        def color(s: Sample) -> str:
            if s.salto == 1:
                return "red"
            if s.agachar == 1:
                return "orange"
            return "blue"

        cs = [color(s) for s in self.datos_modelo]

        fig_num = plt.figure("Datos MLP - 2D", figsize=(8, 6)).number
        plt.figure(fig_num)
        plt.clf()

        ax = plt.gca()
        ax.scatter(xs, ys, c=cs, alpha=0.6, edgecolors="k", s=30)
        ax.set_xlabel("Distancia jugador-bala")
        ax.set_ylabel("Velocidad bala")
        ax.set_title("Datos MLP: rojo=salto, naranja=agachar, azul=nada")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show(block=False)
        plt.draw()

        return "Mostrando gráfica 2D."

    def graficar_datos_3d(self) -> str:
        if not self.datos_modelo:
            return "No hay datos para graficar."

        xs = [s.distancia for s in self.datos_modelo]
        ys = [s.velocidad_bala for s in self.datos_modelo]
        zs = list(range(len(self.datos_modelo)))

        def color(s: Sample) -> str:
            if s.salto == 1:
                return "red"
            if s.agachar == 1:
                return "orange"
            return "blue"

        cs = [color(s) for s in self.datos_modelo]

        fig = plt.figure("Datos MLP - 3D", figsize=(8, 6))
        plt.clf()

        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(xs, ys, zs, c=cs, alpha=0.6, edgecolors="k", s=30)
        ax.set_xlabel("Distancia")
        ax.set_ylabel("Velocidad bala")
        ax.set_zlabel("Índice")
        ax.set_title("Datos MLP 3D")

        plt.tight_layout()
        plt.show(block=False)
        plt.draw()

        return "Mostrando gráfica 3D."

    def _y_bala_segun_tipo(self, tipo: int) -> int:
        if tipo == 0:
            return self.ground_y + int(10 * self.scale)
        else:
            return self.ground_y - self.player_size[1] + self.player_size_agachado[1]

    def disparar_bala(self) -> None:
        if not self.bala_disparada:
            self.velocidad_bala = int(random.randint(-12, -6) * self.scale)
            self.tipo_bala_actual = random.randint(0, 1)

            self.bala.x = self.w - self.margin
            self.bala.y = self._y_bala_segun_tipo(self.tipo_bala_actual)

            self.bala_disparada = True

    def reset_bala(self) -> None:
        self.bala.x = self.w - self.margin
        self.bala_disparada = False

    def iniciar_salto(self) -> None:
        if self.en_suelo and not self.agachado:
            self.salto = True
            self.en_suelo = False

    def manejar_salto(self) -> None:
        if self.salto:
            self.jugador.y -= int(self.salto_vel)
            self.salto_vel -= self.gravedad

            if self.jugador.y >= self.ground_y:
                self.jugador.y = self.ground_y
                self.salto = False
                self.salto_vel = self.salto_vel_inicial
                self.en_suelo = True

    def iniciar_agacharse(self) -> None:
        """Hace una agachada corta por pulsación.

        Esta es la parte importante tomada del código que sí te funcionaba:
        agacharse ya NO depende de mantener presionada la tecla.
        Cada vez que se manda la acción, el mono se agacha unos frames
        y luego se levanta solo. Así puede repetir: agacha, levanta,
        agacha, levanta... desde que sale la bala.
        """
        if self.en_suelo and not self.salto and not self.agachado:
            self.agachado = True
            self.agachar_timer = int(14 * self.scale)
            self.jugador.height = self.player_size_agachado[1]
            self.jugador.y = self.ground_y + (
                self.player_size[1] - self.player_size_agachado[1]
            )

    def manejar_agacharse(self) -> None:
        """Cuenta los frames de la agachada y luego levanta al personaje."""
        if not self.agachado:
            return

        self.agachar_timer -= 1

        if self.agachar_timer <= 0:
            self.terminar_agacharse()

    def terminar_agacharse(self) -> None:
        if self.agachado:
            self.agachado = False
            self._restaurar_hitbox_normal()

    def _restaurar_hitbox_normal(self) -> None:
        self.jugador.height = self.player_size[1]
        self.jugador.y = self.ground_y

    def registrar_decision_manual(self) -> None:
        if not self.bala_disparada:
            return

        distancia = abs(self.jugador.x - self.bala.x)
        salto_label = 0 if self.en_suelo else 1
        agachar_label = 1 if self.agachado else 0

        self.datos_modelo.append(
            Sample(
                velocidad_bala=float(self.velocidad_bala),
                distancia=float(distancia),
                tipo_bala=int(self.tipo_bala_actual),
                salto=salto_label,
                agachar=agachar_label,
            )
        )

    def entrenar_modelo(self) -> Tuple[bool, str]:
        samples = list(self.datos_modelo)

        if len(samples) < 80:
            return False, "Necesitas más datos (>= 80). Juega en MANUAL."

        X = [
            [s.velocidad_bala, s.distancia, s.tipo_bala]
            for s in samples
        ]

        y = []

        for s in samples:
            if s.salto == 1:
                y.append(1)
            elif s.agachar == 1:
                y.append(2)
            else:
                y.append(0)

        clases = sorted(set(y))

        if len(clases) < 2:
            self._reset_modelo()
            self.clase_unica = int(clases[0])
            self.modelo_entrenado = True

            nombres = {
                0: "NADA",
                1: "SIEMPRE SALTA",
                2: "SIEMPRE AGACHA",
            }

            return True, f"Modelo trivial: {nombres.get(self.clase_unica, '?')}."

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        clf = MLPClassifier(
            hidden_layer_sizes=(8, 8),
            activation="relu",
            solver="adam",
            max_iter=300000,
            random_state=42,
        )

        clf.fit(X_train, y_train)

        acc = clf.score(X_test, y_test)

        self._reset_modelo()
        self.scaler = scaler
        self.modelo = clf
        self.modelo_entrenado = True

        return True, f"MLP entrenado. Accuracy test ≈ {acc:.3f}"

    def decision_auto(self) -> int:
        if not self.modelo_entrenado:
            return 0

        if not self.bala_disparada or not self.en_suelo:
            return 0

        distancia = abs(self.jugador.x - self.bala.x)

        if self.clase_unica is not None and self.modelo is None:
            return int(self.clase_unica)

        if self.modelo is None or self.scaler is None:
            return 0

        X = [[
            float(self.velocidad_bala),
            float(distancia),
            float(self.tipo_bala_actual),
        ]]

        Xs = self.scaler.transform(X)

        if hasattr(self.modelo, "predict_proba"):
            probas = self.modelo.predict_proba(Xs)[0]
            clases = list(self.modelo.classes_)

            p = {c: 0.0 for c in [0, 1, 2]}

            for i, c in enumerate(clases):
                p[c] = float(probas[i])

            self.ultima_proba_salto = p.get(1, 0.0)
            self.ultima_proba_agachar = p.get(2, 0.0)

            decision = int(self.modelo.predict(Xs)[0])

        else:
            decision = int(self.modelo.predict(Xs)[0])
            self.ultima_proba_salto = 1.0 if decision == 1 else 0.0
            self.ultima_proba_agachar = 1.0 if decision == 2 else 0.0

        return decision

    def dibujar_fondo(self) -> None:
        self.pantalla.fill((135, 206, 235))

        pygame.draw.circle(
            self.pantalla,
            (255, 230, 90),
            (int(90 * self.scale), int(80 * self.scale)),
            int(45 * self.scale),
        )

        pygame.draw.polygon(
            self.pantalla,
            (80, 140, 90),
            [
                (0, self.ground_y + int(80 * self.scale)),
                (int(260 * self.scale), self.ground_y - int(190 * self.scale)),
                (int(560 * self.scale), self.ground_y + int(80 * self.scale)),
            ],
        )

        pygame.draw.polygon(
            self.pantalla,
            (55, 115, 75),
            [
                (int(380 * self.scale), self.ground_y + int(80 * self.scale)),
                (int(710 * self.scale), self.ground_y - int(230 * self.scale)),
                (self.w, self.ground_y + int(80 * self.scale)),
            ],
        )

        pygame.draw.rect(
            self.pantalla,
            (75, 170, 80),
            (0, self.ground_y + self.player_size[1], self.w, self.h),
        )

        pygame.draw.rect(
            self.pantalla,
            (110, 75, 40),
            (0, self.ground_y + self.player_size[1] + int(25 * self.scale), self.w, self.h),
        )

    def dibujar_mono(self) -> None:
        x = self.jugador.x
        y = self.jugador.y

        if self.agachado:
            cuerpo_h = self.player_size_agachado[1]
        else:
            cuerpo_h = self.player_size[1]

        pygame.draw.ellipse(
            self.pantalla,
            (120, 75, 35),
            (x, y + int(12 * self.scale), self.player_size[0], cuerpo_h),
        )

        pygame.draw.circle(
            self.pantalla,
            (150, 95, 45),
            (x + self.player_size[0] // 2, y + int(8 * self.scale)),
            int(16 * self.scale),
        )

        pygame.draw.circle(
            self.pantalla,
            (110, 70, 35),
            (x + int(5 * self.scale), y + int(8 * self.scale)),
            int(8 * self.scale),
        )

        pygame.draw.circle(
            self.pantalla,
            (110, 70, 35),
            (x + self.player_size[0] - int(5 * self.scale), y + int(8 * self.scale)),
            int(8 * self.scale),
        )

        pygame.draw.circle(
            self.pantalla,
            (230, 180, 120),
            (x + self.player_size[0] // 2, y + int(13 * self.scale)),
            int(9 * self.scale),
        )

        pygame.draw.circle(
            self.pantalla,
            (0, 0, 0),
            (x + self.player_size[0] // 2 - int(5 * self.scale), y + int(5 * self.scale)),
            int(2 * self.scale),
        )

        pygame.draw.circle(
            self.pantalla,
            (0, 0, 0),
            (x + self.player_size[0] // 2 + int(5 * self.scale), y + int(5 * self.scale)),
            int(2 * self.scale),
        )

        pygame.draw.arc(
            self.pantalla,
            (120, 75, 35),
            (
                x - int(26 * self.scale),
                y + int(20 * self.scale),
                int(38 * self.scale),
                int(38 * self.scale),
            ),
            1.3,
            5.5,
            int(4 * self.scale),
        )

    def dibujar_tanque(self) -> None:
        x = self.nave.x
        y = self.ground_y + int(35 * self.scale)

        pygame.draw.rect(
            self.pantalla,
            (55, 85, 45),
            (x, y, int(90 * self.scale), int(35 * self.scale)),
            border_radius=8,
        )

        pygame.draw.rect(
            self.pantalla,
            (40, 70, 35),
            (
                x + int(20 * self.scale),
                y - int(25 * self.scale),
                int(45 * self.scale),
                int(32 * self.scale),
            ),
            border_radius=8,
        )

        pygame.draw.rect(
            self.pantalla,
            (30, 50, 30),
            (
                x - int(45 * self.scale),
                y - int(12 * self.scale),
                int(70 * self.scale),
                int(10 * self.scale),
            ),
        )

        pygame.draw.circle(
            self.pantalla,
            (25, 25, 25),
            (x + int(20 * self.scale), y + int(38 * self.scale)),
            int(12 * self.scale),
        )

        pygame.draw.circle(
            self.pantalla,
            (25, 25, 25),
            (x + int(65 * self.scale), y + int(38 * self.scale)),
            int(12 * self.scale),
        )

    def dibujar_bala(self) -> None:
        color_bala = (230, 60, 60) if self.tipo_bala_actual == 1 else (90, 60, 230)

        pygame.draw.circle(
            self.pantalla,
            color_bala,
            self.bala.center,
            self.bullet_size[0] // 2,
        )

        pygame.draw.circle(
            self.pantalla,
            (255, 230, 130),
            self.bala.center,
            self.bullet_size[0] // 4,
        )

    def _dibujar_menu(self, msg: str = "") -> None:
        self.pantalla.fill(self.NEGRO)

        titulo = self.fuente.render("MENÚ", True, self.BLANCO)
        self.pantalla.blit(
            titulo,
            (self.w // 2 - titulo.get_width() // 2, int(60 * self.scale)),
        )

        opciones = [
            "M - Manual (reinicia dataset y borra modelo)",
            "A - Auto (usa MLP)",
            "T - Entrenar MLP",
            "C - Exportar datos a CSV",
            "F - Fullscreen",
            "Q - Salir",
            "",
            "En juego: ESPACIO = saltar | flecha abajo = agacharse una vez",
        ]

        x0 = int(80 * self.scale)
        y = int(140 * self.scale)
        line_h = self.fuente.get_linesize()
        pad = max(6, int(6 * self.scale))

        for op in opciones:
            t = self.fuente.render(op, True, self.BLANCO)
            self.pantalla.blit(t, (x0, y))
            y += line_h + pad

        y += int(8 * self.scale)

        estado = [
            f"Memoria: {len(self.datos_modelo)} | Modelo: {'sí' if self.modelo_entrenado else 'no'}",
            f"Resolución: {self.w}x{self.h} | scale≈{self.scale:.2f}",
        ]

        for line in estado:
            t = self.fuente_chica.render(line, True, self.GRIS)
            self.pantalla.blit(t, (x0, y))
            y += self.fuente_chica.get_linesize()

        if msg:
            mm = self.fuente_chica.render(msg, True, self.AMARILLO)
            self.pantalla.blit(mm, (x0, y + int(12 * self.scale)))

        pygame.display.flip()

    def mostrar_menu(self) -> None:
        msg = ""
        esperando = True
        self._decision_frame_counter = 0

        while esperando and self.corriendo:
            self._dibujar_menu(msg)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.corriendo = False
                    esperando = False
                    break

                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_m:
                        self.modo_auto = False
                        self.datos_modelo.clear()
                        self._reset_modelo()
                        self._reset_estado_juego()
                        esperando = False
                        break

                    if e.key == pygame.K_a:
                        self.modo_auto = True
                        self._reset_estado_juego()
                        esperando = False
                        break

                    if e.key == pygame.K_t:
                        ok, info = self.entrenar_modelo()
                        msg = info if ok else f"Error: {info}"

                    if e.key == pygame.K_c:
                        msg = self.exportar_datos_csv()

                    if e.key == pygame.K_f:
                        self._toggle_fullscreen()

                    if e.key == pygame.K_q:
                        self.corriendo = False
                        esperando = False
                        return

    def _update_frame(self) -> None:
        self.dibujar_fondo()
        self.dibujar_tanque()

        if self.bala_disparada:
            self.bala.x += self.velocidad_bala

        if self.bala.x < -self.bullet_size[0]:
            self.reset_bala()

        self.dibujar_bala()
        self.dibujar_mono()

        if self.jugador.colliderect(self.bala):
            self._reset_estado_juego()

        if self.modelo_entrenado and self.modo_auto:
            lineas_hud = []

            if self.ultima_proba_salto is not None:
                lineas_hud.append(f"p(salto)≈{self.ultima_proba_salto:.2f}")

            if self.ultima_proba_agachar is not None:
                lineas_hud.append(f"p(agachar)≈{self.ultima_proba_agachar:.2f}")

            for i, txt in enumerate(lineas_hud):
                surf = self.fuente_chica.render(txt, True, self.AMARILLO)
                self.pantalla.blit(
                    surf,
                    (10, 10 + i * (self.fuente_chica.get_linesize() + 2)),
                )

        if self.bala_disparada:
            tipo_txt = (
                "Bala ALTA: agachate"
                if self.tipo_bala_actual == 1
                else "Bala BAJA: salta"
            )

            color_txt = (
                (255, 100, 100)
                if self.tipo_bala_actual == 1
                else (100, 200, 255)
            )

            surf = self.fuente_chica.render(tipo_txt, True, color_txt)
            self.pantalla.blit(
                surf,
                (self.w // 2 - surf.get_width() // 2, 10),
            )

    def loop(self) -> None:
        reloj = pygame.time.Clock()
        self.mostrar_menu()

        while self.corriendo:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.corriendo = False

                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        self.corriendo = False

                    elif e.key in (pygame.K_ESCAPE, pygame.K_p):
                        self._reset_estado_juego()
                        self.mostrar_menu()

                    elif e.key == pygame.K_f:
                        self._toggle_fullscreen()

                    elif e.key == pygame.K_SPACE and not self.modo_auto and self.en_suelo:
                        self.iniciar_salto()

                    elif e.key == pygame.K_DOWN and not self.modo_auto:
                        self.iniciar_agacharse()

            if not self.corriendo:
                break

            if self.modo_auto:
                decision = self.decision_auto()

                if decision == 1:
                    self.iniciar_salto()

                elif decision == 2:
                    self.iniciar_agacharse()

            else:
                self.registrar_decision_manual()

            if self.salto:
                self.manejar_salto()

            if self.agachado:
                self.manejar_agacharse()

            if not self.bala_disparada:
                self.disparar_bala()

            self._update_frame()
            pygame.display.flip()
            reloj.tick(45)

        pygame.quit()


def main() -> None:
    Juego().loop()


if __name__ == "__main__":
    main()