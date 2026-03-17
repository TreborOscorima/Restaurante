"""Backup automático de la base de datos SQLite del sistema POS.

Uso:
    python scripts/backup_db.py               # copia a C:\\Backups_Norkys\\
    python scripts/backup_db.py --dest D:\\mis_backups
    python scripts/backup_db.py --keep 30     # retiene los últimos 30 archivos

Pensado para ejecutarse como Tarea Programada de Windows cada N horas.
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuración por defecto
# ---------------------------------------------------------------------------
DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "restaurante.db"
DEFAULT_DEST = Path("C:/Backups_Norkys")
DEFAULT_KEEP = 14   # días/copias a retener (0 = sin límite)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backup del POS restaurante.")
    parser.add_argument("--db",   default=str(DEFAULT_DB),   help="Ruta de la DB fuente")
    parser.add_argument("--dest", default=str(DEFAULT_DEST), help="Carpeta de destino")
    parser.add_argument("--keep", default=DEFAULT_KEEP, type=int,
                        help="Cuántas copias conservar (0 = todas)")
    return parser.parse_args()


def _online_backup(src: Path, dest_file: Path) -> None:
    """Usa la API de backup de SQLite3 en lugar de copiar el archivo en crudo.

    Esto es seguro incluso mientras la app está corriendo: SQLite coordina el
    backup a través de WAL sin necesidad de bloquear la DB completa.
    """
    src_conn = sqlite3.connect(str(src))
    dst_conn = sqlite3.connect(str(dest_file))
    try:
        src_conn.backup(dst_conn, pages=100)
    finally:
        src_conn.close()
        dst_conn.close()


def _rotate(dest_dir: Path, keep: int) -> None:
    """Elimina copias antiguas conservando solo las últimas `keep`."""
    if keep <= 0:
        return
    copies = sorted(dest_dir.glob("restaurante_*.db"))
    excess = copies[: max(0, len(copies) - keep)]
    for old in excess:
        old.unlink()
        print(f"  [rotación] eliminado {old.name}")


def main() -> int:
    args = _parse_args()
    src  = Path(args.db)
    dest = Path(args.dest)

    if not src.exists():
        print(f"[ERROR] Base de datos no encontrada: {src}", file=sys.stderr)
        return 1

    dest.mkdir(parents=True, exist_ok=True)

    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"restaurante_{timestamp}.db"
    backup_path = dest / backup_name

    print(f"[backup] Origen : {src}")
    print(f"[backup] Destino: {backup_path}")

    _online_backup(src, backup_path)

    size_kb = backup_path.stat().st_size / 1024
    print(f"[backup] OK — {size_kb:.1f} KB")

    _rotate(dest, args.keep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
