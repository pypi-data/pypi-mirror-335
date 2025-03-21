from poetry_demo_amolkhatri.mymath import MyMath

def main():
    print("Hello, World!")
    math = MyMath()
    print(math.add(1, 2))
    print(math.subtract(1, 2))
    print(math.multiply(1, 2))
    print(math.divide(1, 2))

if __name__ == "__main__":
    main()

