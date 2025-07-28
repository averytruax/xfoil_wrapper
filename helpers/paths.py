from pathlib import Path

class _Paths:

    # Line needs to change if file location changes
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent

    @classmethod
    def get_geometry_path(cls) -> Path:
        """Example: Return the geometry folder path."""
        return cls.ROOT_DIR / "geometry"

    @classmethod
    def get_outputs_path(cls) -> Path:
        """Example: Return the outputs folder path."""
        return cls.ROOT_DIR / "outputs"


if __name__ == "__main__":

    test = _Paths()

    print(test.ROOT_DIR)