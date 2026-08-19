#!/usr/bin/env python3
import threading
import sys
import os
from dotenv import load_dotenv
from pynput import keyboard

load_dotenv()
from capture import capture_region, take_screenshot
from overlay import AnswerOverlay
from ai import ask_question, PROVIDERS


def select_provider_and_model() -> tuple[str, str] | None:
    """Interactive menu to select provider and model."""
    providers = list(PROVIDERS.keys())

    print("╔══════════════════════════════╗")
    print("║        Quiz Helper           ║")
    print("╚══════════════════════════════╝\n")
    print("Selecione o provider:\n")

    available = []
    for i, name in enumerate(providers, 1):
        key = PROVIDERS[name]["env_key"]
        has_key = bool(os.environ.get(key))
        status = "✓" if has_key else "✗ sem chave"
        print(f"  [{i}] {name:<12} ({status})")
        if has_key:
            available.append(name)

    print()
    while True:
        try:
            choice = input("Escolha [1-3]: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(providers):
                provider = providers[idx]
                break
        except (ValueError, KeyboardInterrupt):
            pass
        print("Opção inválida. Tente novamente.")

    if provider not in available:
        key_name = PROVIDERS[provider]["env_key"]
        print(f"\n⚠ Chave {key_name} não encontrada.")
        print(f"  Configure com: export {key_name}=sua_chave")
        cont = input("\nContinuar mesmo assim? [s/N]: ").strip().lower()
        if cont != "s":
            return None

    models = PROVIDERS[provider]["models"]
    model_names = list(models.keys())

    print(f"\nModelos disponíveis para {provider}:\n")
    for i, name in enumerate(model_names, 1):
        print(f"  [{i}] {name}")

    print()
    while True:
        try:
            choice = input(f"Escolha [1-{len(model_names)}]: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(model_names):
                model_label = model_names[idx]
                model_id = models[model_label]
                break
        except (ValueError, KeyboardInterrupt):
            pass
        print("Opção inválida. Tente novamente.")

    print(f"\n✓ Usando {provider} — {model_label}")
    return provider, model_id


overlay = AnswerOverlay()
pressed_keys = set()
processing = threading.Event()
selected_provider: str = ""
selected_model: str = ""

def _is_ctrl(key):
    return key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r)

def _is_shift(key):
    return key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r)

def _is_space(key):
    return key == keyboard.Key.space or (hasattr(key, "char") and key.char == " ")

def _hotkey_active():
    return (
        any(_is_ctrl(k) for k in pressed_keys)
        and any(_is_shift(k) for k in pressed_keys)
        and any(_is_space(k) for k in pressed_keys)
    )


def on_trigger():
    if processing.is_set():
        return
    processing.set()

    print("[INFO] Abrindo seleção de região...")
    region = capture_region()

    if region is None:
        print("[INFO] Seleção cancelada.")
        processing.clear()
        return

    print(f"[INFO] Região capturada: {region}")
    overlay.show_loading()

    def run():
        try:
            print("[INFO] Capturando screenshot...")
            image = take_screenshot(region)
            print("[INFO] Enviando para a IA...")
            answer = ask_question(image, selected_provider, selected_model)
            print(f"[INFO] Resposta recebida:\n{answer}")
            overlay.update(answer)
        except Exception as e:
            print(f"[ERRO] {type(e).__name__}: {e}")
            overlay.update(f"Erro: {type(e).__name__}\n{e}")
        finally:
            processing.clear()

    threading.Thread(target=run, daemon=True).start()


def on_press(key):
    pressed_keys.add(key)
    if _hotkey_active():
        threading.Thread(target=on_trigger, daemon=True).start()


def on_release(key):
    pressed_keys.discard(key)


def main():
    global selected_provider, selected_model

    result = select_provider_and_model()
    if result is None:
        sys.exit(0)

    selected_provider, selected_model = result

    print("\nAtivado! Pressione Ctrl + Shift + Espaço para capturar uma questão.")
    print("Pressione Ctrl+C para encerrar.\n")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nEncerrado.")
            sys.exit(0)


if __name__ == "__main__":
    main()
