from pathlib import Path

class _Paths:

    # Line needs to change if file location changes
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    PWD: Path = Path(__file__).cwd()

    @classmethod
    def geometry(cls) -> Path:
        return cls.ROOT_DIR / "geometry"

    @classmethod
    def outputs(cls) -> Path:
        return cls.wrapper() / "outputs"

    @classmethod
    def wrapper(cls) -> Path:
        return cls.ROOT_DIR / "wrapper"

# Global instance for paths
PATHS = _Paths()

if __name__ == "__main__":

    test = _Paths()

    print(test.ROOT_DIR)