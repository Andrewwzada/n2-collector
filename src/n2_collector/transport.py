"""Fronteira de transporte. Nenhum envio real está implementado nesta versão."""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from .model import Report

RECIPIENT = "andrew@soutechgroup.com"

class DeliveryError(Exception):
    """Erro apresentável de transporte (incluindo futura falha de rede)."""

@dataclass(frozen=True)
class DeliveryResult:
    simulated: bool
    message: str

class Transport(Protocol):
    def send(self, report: Report) -> DeliveryResult: ...

class TestTransport:
    def send(self, report: Report) -> DeliveryResult:
        # Não serializa em disco, abre sockets ou registra conteúdo pessoal.
        return DeliveryResult(True, f"Simulação concluída. Nenhum dado enviado. Destino futuro: {RECIPIENT}")

def load_transport(path: Path) -> Transport:
    if not path.exists():
        return TestTransport()
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DeliveryError("Não foi possível ler config.json. Verifique o arquivo com a TI.") from exc
    if not isinstance(config, dict) or set(config) != {"mode"} or config["mode"] != "test":
        raise DeliveryError("Configuração não suportada. Esta versão aceita somente mode=test.")
    return TestTransport()
