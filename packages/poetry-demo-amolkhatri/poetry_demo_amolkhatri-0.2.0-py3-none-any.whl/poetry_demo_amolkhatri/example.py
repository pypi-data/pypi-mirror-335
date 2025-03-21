from poetry_demo_amolkhatri import MyMath

def demonstrate_math():
    calculator = MyMath()
    sum_result = calculator.add(10, 20)
    print(f"The sum is: {sum_result}")
    
    product_result = calculator.multiply(5, 6)
    print(f"The product is: {product_result}")
    
if __name__ == "__main__":
    demonstrate_math() 