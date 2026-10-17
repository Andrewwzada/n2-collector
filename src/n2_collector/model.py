"""Modelo limitado aos campos necessários ao suporte."""
from dataclasses import dataclass, field
from datetime import datetime

UNKNOWN = "Não identificado"

@dataclass
class Report:
    collected_at: str = field(default_factory=lambda: datetime.now().astimezone().isoformat(timespec="seconds"))
    hostname: str = UNKNOWN
    username: str = UNKNOWN
    domain: str = UNKNOWN
    windows: str = UNKNOWN
    office: str = UNKNOWN
    activation: str = UNKNOWN
    license_type: str = UNKNOWN
    office_email: str = UNKNOWN
    notes: list[str] = field(default_factory=list)

    def rows(self) -> list[tuple[str, str]]:
        return [("Computador", self.hostname), ("Usuário Windows", self.username),
                ("Domínio", self.domain), ("Windows", self.windows),
                ("Office / produtos", self.office), ("Ativação Office", self.activation),
                ("Tipo de licença Office", self.license_type),
                ("E-mail no Office (identidade local)", self.office_email),
                ("Data e horário", self.collected_at), ("Observações", " | ".join(self.notes))]

    @property
    def subject(self) -> str:
        return f"Coletor | {self.hostname} | {self.collected_at[:10]}"

    def text(self) -> str:
        return "Coletor — relatório técnico\n\n" + "\n".join(f"{k}: {v}" for k, v in self.rows())
