import fire

from .anysqldiag import anysqldiag


def main():
    fire.Fire(anysqldiag)


if __name__ == "__main__":
    main()
