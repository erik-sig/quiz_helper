#!/usr/bin/env python3
import threading
import sys
import os
from pynput import keyboard
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

HOTKEY = {keyboard.Key.ctrl_l, keyboard.Key.shift, keyboard.KeyCode(char=" ")}


def on_trigger():
    if processing.is_set():
        return
    processing.set()

    overlay.show_loading()

    region = capture_region()

    if region is None:
        overlay.close()
        processing.clear()
        return

    def run():
        try:
            image = take_screenshot(region)
            answer = ask_question(image, selected_provider, selected_model)
            overlay.close()
            overlay.show(answer)
        except Exception as e:
            overlay.close()
            overlay.show(f"Erro: {e}")
        finally:
            processing.clear()

    threading.Thread(target=run, daemon=True).start()


def on_press(key):
    pressed_keys.add(key)
    if all(k in pressed_keys for k in HOTKEY):
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
