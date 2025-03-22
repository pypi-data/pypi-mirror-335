from microwave_usb_fan_fork import Program, TextMessage, Device


def main():
    f = Program(
        (
            TextMessage("Hello, mmh World!"),
            TextMessage("How is everyone going?"),
        )
    )
    d = Device()
    d.program(f)


if __name__ == "__main__":
    main()
