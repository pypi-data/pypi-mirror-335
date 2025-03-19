from midas.api import midasctl


def main():
    midasctl.main(["-v", "run", "midasmv"])


if __name__ == "__main__":
    main()
