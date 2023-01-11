__all__ = ['log', 'Color', 'Default', 'ActivityRank']


from datetime import datetime

def log(title: str, message: str, error: bool = False):
	if error:
		raise Exception(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] [{title.upper()}]: {message}")

	margin = ""
	if len(title) < 8:
		margin = int(8 - len(title)) * " "

	print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] [{title.upper()}{margin}]: {message}")


from dataclasses import dataclass

from discord import Object as D_Object


@dataclass
class Color:
	BLURPLE: int = int("5261f8", 16)
	GREEN: int = int("77DD77", 16)
	NEON: int = int("1aff79", 16)

@dataclass
class Default:
	SERVER: D_Object = D_Object(id=1060218266670346370)
	COLOR: int = Color.NEON
	FOOTER: str = "Dynamo © 2023"
	MULTIPLIER: float = 10.0
	PREFIX: str = "dyn."
	AD_EMBED_TITLE: str = "CLICK HERE TO JOIN!"

@dataclass
class ActivityRank:
	SUPERACTIVE: int = 3.0
	ACTIVE: int = 1.5
	ONLINE: int = 1